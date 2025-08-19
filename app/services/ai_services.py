import google.generativeai as genai
from google.cloud import texttospeech, speech
from app.core.config import settings
import logging
import os
import json
from typing import Optional, Dict, AsyncGenerator

from sqlalchemy.orm import Session

from app import crud

# Configure logging
logger = logging.getLogger(__name__)

# Global clients, to be initialized on startup
TTS_CLIENT = None
STT_CLIENT = None
GEMINI_MODEL = None

def initialize_ai_clients():
    """
    Initializes the AI clients (TTS, STT, Gemini).
    This function should be called during the application startup.
    """
    global TTS_CLIENT, STT_CLIENT, GEMINI_MODEL

    # Check and initialize Google Cloud Speech/Text-to-Speech
    if settings.GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
        try:
            TTS_CLIENT = texttospeech.TextToSpeechAsyncClient()
            STT_CLIENT = speech.SpeechAsyncClient()
            logger.info("Google Cloud TTS and STT clients initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud clients: {e}")
    else:
        logger.warning(
            f"Google Cloud credentials not found or path is invalid: {settings.GOOGLE_APPLICATION_CREDENTIALS}. "
            f"Speech-to-Text and Text-to-Speech will be disabled."
        )

    # Configure Google AI (Gemini)
    if settings.GOOGLE_API_KEY:
        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            GEMINI_MODEL = genai.GenerativeModel('gemini-pro')
            logger.info("Google Generative AI (Gemini) initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Google Generative AI: {e}")
    else:
        logger.warning("GOOGLE_API_KEY not set. Gemini AI features will be disabled.")

async def get_gemini_response(prompt: str) -> str:
    """
    Gets a response from the Gemini model.
    """
    if not GEMINI_MODEL:
        return "AI model is not configured."
    
    try:
        response = await GEMINI_MODEL.generate_content_async(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error getting response from Gemini: {e}")
        return "An error occurred while communicating with the AI model."

async def synthesize_speech(text: str, language_code: str = "en-US") -> Optional[bytes]:
    """
    Synthesizes speech from the input text asynchronously.
    """
    if not TTS_CLIENT:
        logger.warning("TTS client is not initialized.")
        return None

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    try:
        response = await TTS_CLIENT.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        return response.audio_content
    except Exception as e:
        logger.error(f"Error during speech synthesis: {e}")
        return None

async def transcribe_speech(audio_bytes: bytes, language_code: str = "en-US") -> Optional[str]:
    """
    Transcribes speech from the input audio bytes asynchronously.
    """
    if not STT_CLIENT:
        logger.warning("STT client is not initialized.")
        return None

    audio = speech.RecognitionAudio(content=audio_bytes)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16, # Assuming WAV format
        sample_rate_hertz=16000,
        language_code=language_code,
    )

    try:
        response = await STT_CLIENT.recognize(config=config, audio=audio)
        if response.results:
            return response.results[0].alternatives[0].transcript
        return ""
    except Exception as e:
        logger.error(f"Error during speech transcription: {e}")
        return None


async def analyze_user_answer(question: str, correct_answer: str, user_answer: str) -> Optional[Dict]:
    """
    Analyzes the user's answer and provides detailed feedback asynchronously.
    """
    prompt = f"""\
    You are an English teacher. A student was asked the following question:
    Question: "{question}"
    The expected correct answer is: "{correct_answer}"
    The student's answer was: "{user_answer}"

    Please analyze the student's answer. Provide feedback on grammar, vocabulary, and relevance.
    Determine if the answer is correct, partially correct, or incorrect.
    Provide a corrected version of the student's answer if it's wrong.
    Your response should be in JSON format with the following keys:
    - "is_correct": boolean
    - "feedback": string (detailed explanation)
    - "corrected_answer": string (the corrected version of the student's answer)
    """
    try:
        response_text = await get_gemini_response(prompt)
        return json.loads(response_text)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Failed to analyze user answer: {e}")
        return {
            "is_correct": False,
            "feedback": "Could not analyze the answer due to a technical issue.",
            "corrected_answer": ""
        }

async def analyze_exercise_attempt(db: Session, exercise_attempt_id: int):
    """Analyzes a user's incorrect exercise attempt using AI and updates the feedback."""
    attempt = crud.exercise_attempt.get(db, id=exercise_attempt_id)
    if not attempt or attempt.is_correct:
        return

    exercise = attempt.exercise
    prompt = f"""\
    An English language learner attempted an exercise.
    The exercise question was: "{exercise.question}"
    The correct answer is: "{exercise.correct_answer}"
    The student's incorrect answer was: "{attempt.user_answer}"

    Please provide a concise, helpful explanation (in Uzbek) for the student, explaining why their answer is incorrect and what the correct answer is. The explanation should be simple and encouraging.
    Your response should be a single string of text.
    """
    try:
        feedback_text = await get_gemini_response(prompt)
        # Update the attempt in the database with the AI-generated feedback
        update_data = {"ai_feedback": feedback_text}
        crud.exercise_attempt.update(db, db_obj=attempt, obj_in=update_data)
        logger.info(f"Successfully provided AI feedback for attempt {exercise_attempt_id}")
    except Exception as e:
        logger.error(f"Failed to get or save AI feedback for attempt {exercise_attempt_id}: {e}")

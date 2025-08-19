import logging
import os
import google.generativeai as genai
from google.cloud import speech, texttospeech
from app.core.config import settings

logger = logging.getLogger(__name__)

# --- Google Gemini Client --- #
def get_gemini_model():
    """Initializes and returns the Gemini Pro model."""
    try:
        if not settings.GOOGLE_API_KEY:
            logger.warning("GOOGLE_API_KEY is not set. Gemini AI functionality will be disabled.")
            return None
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        return model
    except Exception as e:
        logger.error(f"Error initializing Gemini Pro model: {e}")
        return None

gemini_model = get_gemini_model()

async def get_gemini_response(prompt: str) -> str:
    """Generates a response from the Gemini model."""
    if not gemini_model:
        return "AI service is not configured."
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error getting response from Gemini: {e}")
        return f"Error from AI service: {e}"

# --- Google Cloud Speech-to-Text Client --- #
def get_google_speech_client():
    """Initializes and returns the Google Cloud Speech client."""
    try:
        if not settings.GOOGLE_APPLICATION_CREDENTIALS or not os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
            logger.warning(f"Google Cloud credentials not found or path is invalid: {settings.GOOGLE_APPLICATION_CREDENTIALS}. Speech-to-Text will be disabled.")
            return None
        return speech.SpeechClient()
    except Exception as e:
        logger.error(f"Google Cloud Speech client initialization failed: {e}")
        return None

speech_client = get_google_speech_client()

# --- Google Cloud Text-to-Speech Client --- #
def get_google_tts_client():
    """Initializes and returns the Google Cloud Text-to-Speech client."""
    try:
        if not settings.GOOGLE_APPLICATION_CREDENTIALS or not os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
            logger.warning(f"Google Cloud credentials not found. TTS will be disabled. {settings.GOOGLE_APPLICATION_CREDENTIALS}")
            return None
        return texttospeech.TextToSpeechClient()
    except Exception as e:
        logger.error(f"Google Cloud TTS client initialization failed: {e}")
        return None

tts_client = get_google_tts_client()

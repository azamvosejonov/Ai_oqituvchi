import os
import wave
import uuid
import numpy as np
import io
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
import speech_recognition as sr
from fastapi import HTTPException, UploadFile, status
from pydub import AudioSegment
from google.cloud import speech
from google.api_core.exceptions import GoogleAPICallError, RetryError

# Constants for pronunciation assessment
PRONUNCIATION_SCORE_WEIGHTS = {
    'accuracy': 0.4,      # How accurate the pronunciation is
    'fluency': 0.3,       # How fluent the speech is
    'completeness': 0.3   # How complete the speech is compared to reference text
}

# Mapping of language codes to reference language for pronunciation assessment
LANGUAGE_CODE_MAP = {
    'en': 'en-US',
    'uz': 'uz-UZ',
    'ru': 'ru-RU',
    'tr': 'tr-TR',
    'kz': 'kk-KZ',
    'kk': 'kk-KZ',
    'az': 'az-AZ',
    'tk': 'tk-TM',
    'kg': 'ky-KG',
    'ky': 'ky-KG',
}

def normalize_language_code(language_code: str) -> str:
    """Normalize language code to standard format."""
    lang = language_code.lower().split('-')[0]
    return LANGUAGE_CODE_MAP.get(lang, 'en-US')

class STTService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_formats = ["wav", "mp3", "ogg", "flac"]
        
        # Initialize Google Cloud Speech client if credentials are available
        self.google_client = None
        try:
            self.google_client = speech.SpeechClient()
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Google Cloud Speech client initialization failed: {e}")
            self.google_client = None
    
    async def save_audio_file(self, file: UploadFile) -> str:
        try:
            # Create uploads directory if not exists
            os.makedirs("uploads/audio", exist_ok=True)
            
            # Generate unique filename
            file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'wav'
            filename = f"{uuid.uuid4()}.{file_ext}"
            filepath = os.path.join("uploads/audio", filename)
            
            # Save the file
            with open(filepath, "wb") as buffer:
                buffer.write(await file.read())
                
            return filepath
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Audio faylni saqlashda xatolik: {str(e)}"
            )
    
    def convert_to_wav(self, filepath: str) -> str:
        try:
            if not filepath.lower().endswith('.wav'):
                audio = AudioSegment.from_file(filepath)
                wav_path = f"{os.path.splitext(filepath)[0]}.wav"
                audio.export(wav_path, format="wav")
                os.remove(filepath)  # Remove original file
                return wav_path
            return filepath
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Audio formatini o'zgartirishda xatolik: {str(e)}"
            )
    
    async def recognize_speech(self, audio_file: UploadFile) -> Dict[str, str]:
        try:
            # Save the uploaded file
            filepath = await self.save_audio_file(audio_file)
            
            # Convert to WAV if needed
            wav_path = self.convert_to_wav(filepath)
            
            # Recognize speech using Google Web Speech API
            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language="uz-UZ")
            
            # Clean up
            os.remove(wav_path)
            
            return {"text": text, "status": "success"}
            
        except sr.UnknownValueError:
            raise HTTPException(
                status_code=400,
                detail="Audio tushunarsiz. Iltimos, aniqroq gapiring."
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Nutqni tushunishda xatolik: {str(e)}"
            )
    
    async def assess_pronunciation(self, audio_file: UploadFile, expected_text: str) -> Dict[str, float]:
        try:
            # Save the uploaded file
            filepath = await self.save_audio_file(audio_file)
            
            # Convert to WAV if needed
            wav_path = self.convert_to_wav(filepath)
            
            # Recognize speech
            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)
                recognized_text = self.recognizer.recognize_google(audio_data, language="uz-UZ")
            
            # Clean up
            os.remove(wav_path)
            
            # Simple pronunciation assessment (can be enhanced)
            score = self._calculate_pronunciation_score(recognized_text, expected_text)
            
            return {
                "recognized_text": recognized_text,
                "pronunciation_score": score,
                "status": "success"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Talaffuzni baholashda xatolik: {str(e)}"
            )
    
    def _calculate_pronunciation_score(self, recognized: str, expected: str) -> float:
        # Simple word-level comparison (can be enhanced with phoneme analysis)
        recognized_words = set(recognized.lower().split())
        expected_words = set(expected.lower().split())
        
        if not expected_words:
            return 0.0
            
        intersection = recognized_words.intersection(expected_words)
        return len(intersection) / len(expected_words)

stt_service = STTService()

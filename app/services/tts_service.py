from typing import Optional, Union
import os
import uuid
import logging
from fastapi import HTTPException
from pydantic import HttpUrl
from app.core.config import settings

# Set up logging
logger = logging.getLogger(__name__)

# Try to import Google Cloud TTS
GOOGLE_TTS_AVAILABLE = False
try:
    from google.cloud import texttospeech
    from google.api_core.exceptions import GoogleAPIError, Unauthenticated
    from google.auth.exceptions import DefaultCredentialsError
    GOOGLE_TTS_AVAILABLE = True
except (ImportError, DefaultCredentialsError) as e:
    logger.warning(f"Google Cloud TTS client not available: {e}. TTS functionality will be limited.")

class TTSService:
    def __init__(self):
        self.client = None
        self.audio_config = None
        self.voice = None
        
        if not GOOGLE_TTS_AVAILABLE:
            logger.warning("Google Cloud TTS is not available. TTS functionality will be disabled.")
            return
            
        try:
            # Try to initialize Google Cloud TTS client
            self.client = texttospeech.TextToSpeechClient()
            self.audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            self.voice = texttospeech.VoiceSelectionParams(
                language_code="uz-UZ",
                name="uz-UZ-Wavenet-A",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            logger.info("Google Cloud TTS initialized successfully")
        except DefaultCredentialsError as e:
            logger.warning(f"Google Cloud credentials not found. TTS will be disabled. {e}")
            self.client = None
        except (GoogleAPIError, Unauthenticated) as e:
            logger.error(f"Failed to initialize Google Cloud TTS: {e}")
            logger.warning("TTS functionality will be disabled due to authentication error.")
            self.client = None
        except Exception as e:
            logger.error(f"Unexpected error initializing TTS service: {e}", exc_info=True)
            logger.warning("TTS functionality will be disabled due to initialization error.")
            self.client = None

    async def text_to_speech(self, text: str) -> Union[str, None]:
        """
        Convert text to speech and return URL to the audio file.
        Returns None if TTS is not available.
        """
        if not self.client or not GOOGLE_TTS_AVAILABLE:
            logger.warning("TTS service is not available. Text was not converted to speech.")
            return None
            
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config
            )
            
            # Ensure the tts directory exists
            tts_dir = os.path.join(settings.STATIC_FILES_DIR, "tts")
            os.makedirs(tts_dir, exist_ok=True)
            
            # Save audio to file
            filename = f"{uuid.uuid4()}.mp3"
            filepath = os.path.join(tts_dir, filename)
            
            with open(filepath, "wb") as out:
                out.write(response.audio_content)
                
            return f"{settings.API_V1_STR}/static/tts/{filename}"
            
        except Exception as e:
            logger.error(f"TTS conversion failed: {str(e)}", exc_info=True)
            return None

tts_service = TTSService()

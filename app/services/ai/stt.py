import logging
import io
import wave
import json
from typing import Tuple, Optional, Dict, Any
import speech_recognition as sr
from pydub import AudioSegment
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

class STTService:
    """
    Speech-to-Text service for converting user's spoken language into text.
    Supports multiple recognition engines and handles various audio formats.
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Minimum audio energy for speech detection
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Seconds of non-speaking audio before a phrase is considered complete
        
        # Configure supported languages
        self.supported_languages = {
            'en-US': 'English (US)',
            'en-GB': 'English (UK)',
            'ru-RU': 'Russian',
            'uz-UZ': 'Uzbek',
            'tr-TR': 'Turkish',
            'kk-KZ': 'Kazakh',
            'ky-KG': 'Kyrgyz',
            'tg-TJ': 'Tajik'
        }
    
    async def transcribe(
        self,
        audio_data: bytes,
        language: str = 'en-US',
        format: str = 'wav',
        sample_rate: int = 16000,
        channels: int = 1
    ) -> Tuple[str, float]:
        """
        Convert speech to text with confidence score.
        
        Args:
            audio_data: Raw audio data in the specified format
            language: Language code (e.g., 'en-US')
            format: Audio format ('wav', 'mp3', 'ogg', etc.)
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            
        Returns:
            Tuple of (transcribed_text, confidence_score)
        """
        try:
            # Convert audio to the right format if needed
            audio = self._preprocess_audio(audio_data, format, sample_rate, channels)
            
            # Try different recognition methods with fallbacks
            text, confidence = await self._recognize_with_fallback(audio, language)
            
            logger.info(f"STT recognized: {text[:100]}... (confidence: {confidence:.2f})")
            return text, confidence
            
        except Exception as e:
            logger.error(f"STT Error: {str(e)}", exc_info=True)
            return "", 0.0
    
    def _preprocess_audio(
        self, 
        audio_data: bytes, 
        format: str,
        sample_rate: int,
        channels: int
    ) -> sr.AudioData:
        """Convert audio data to the format needed for speech recognition"""
        try:
            # Convert to WAV if needed
            if format.lower() != 'wav':
                audio = AudioSegment.from_file(io.BytesIO(audio_data), format=format)
                audio = audio.set_frame_rate(sample_rate).set_channels(channels)
                wav_data = audio.export(format="wav").read()
            else:
                wav_data = audio_data
            
            # Convert to the format expected by speech_recognition
            audio_file = io.BytesIO(wav_data)
            
            with wave.open(audio_file, 'rb') as wav_file:
                frame_rate = wav_file.getframerate()
                frames = wav_file.readframes(wav_file.getnframes())
                
            return sr.AudioData(
                frame_data=frames,
                sample_rate=frame_rate,
                sample_width=2  # 16-bit audio
            )
            
        except Exception as e:
            logger.error(f"Error preprocessing audio: {str(e)}")
            raise ValueError(f"Could not process audio data: {str(e)}")
    
    async def _recognize_with_fallback(
        self, 
        audio: sr.AudioData, 
        language: str
    ) -> Tuple[str, float]:
        """Try different recognition methods with fallbacks"""
        methods = [
            self._recognize_google,
            self._recognize_whisper,
            self._recognize_sphinx
        ]
        
        last_error = None
        
        for method in methods:
            try:
                return await method(audio, language)
            except Exception as e:
                last_error = e
                logger.warning(f"STT method {method.__name__} failed: {str(e)}")
                continue
        
        # If all methods failed, raise the last error
        raise last_error or Exception("All STT methods failed")
    
    async def _recognize_google(
        self, 
        audio: sr.AudioData, 
        language: str
    ) -> Tuple[str, float]:
        """Use Google Web Speech API for recognition"""
        try:
            text = self.recognizer.recognize_google(audio, language=language)
            # Google doesn't return confidence, so we'll use a default high value
            return text, 0.95
        except sr.UnknownValueError:
            return "", 0.0
        except sr.RequestError as e:
            logger.error(f"Google Web Speech API request failed: {e}")
            raise
    
    async def _recognize_whisper(
        self, 
        audio: sr.AudioData, 
        language: str
    ) -> Tuple[str, float]:
        """Use OpenAI Whisper for recognition (if configured)"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
            
        try:
            # In a real implementation, you would call the Whisper API here
            # This is a placeholder that simulates the behavior
            import openai
            
            # Save audio to a file (required by Whisper API)
            with open("temp_audio.wav", "wb") as f:
                f.write(audio.get_wav_data())
            
            # Call Whisper API
            with open("temp_audio.wav", "rb") as audio_file:
                result = openai.Audio.transcribe(
                    "whisper-1",
                    audio_file,
                    language=language.split('-')[0]  # Convert 'en-US' to 'en'
                )
            
            text = result["text"]
            # Whisper doesn't provide confidence, so we'll use a high default
            return text, 0.95
            
        except ImportError:
            logger.warning("OpenAI package not installed")
            raise
        except Exception as e:
            logger.error(f"Whisper recognition failed: {str(e)}")
            raise
    
    async def _recognize_sphinx(
        self, 
        audio: sr.AudioData, 
        language: str
    ) -> Tuple[str, float]:
        """Use CMU Sphinx as a fallback (works offline but less accurate)"""
        try:
            # Sphinx requires language packs to be installed
            if not language.startswith('en'):
                raise ValueError(f"Sphinx doesn't support language: {language}")
                
            text = self.recognizer.recognize_sphinx(audio, language=language)
            # Sphinx doesn't provide confidence, so we'll use a medium default
            return text, 0.7
            
        except Exception as e:
            logger.error(f"Sphinx recognition failed: {str(e)}")
            raise
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get a dictionary of supported language codes and names"""
        return self.supported_languages

# Singleton instance
stt_service = STTService()

import logging
import io
import os
import tempfile
from typing import Optional, Dict, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import requests
import json

from pydub import AudioSegment
from pydub.playback import play
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

class VoiceGender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class AudioFormat(str, Enum):
    MP3 = "mp3"
    WAV = "wav"
    PCM = "pcm"
    OGG = "ogg"
    WEBM = "webm"

@dataclass
class TTSOptions:
    """Configuration options for text-to-speech synthesis"""
    voice_id: str = "en-US-GuyNeural"
    language: str = "en-US"
    gender: VoiceGender = VoiceGender.MALE
    speaking_rate: float = 1.0  # 0.5 to 2.0
    pitch: float = 1.0  # 0.5 to 2.0
    volume: float = 1.0  # 0.0 to 2.0
    format: AudioFormat = AudioFormat.MP3
    sample_rate: int = 24000  # Hz
    bit_rate: int = 128  # kbps

class TTSService:
    """
    Text-to-Speech service for converting text into natural-sounding speech.
    Supports multiple TTS providers with fallback mechanisms.
    """
    
    def __init__(self):
        self.providers = [
            self._azure_tts,
            self._google_tts,
            self._espeak_tts  # Fallback: local eSpeak
        ]
        
        # Voice mapping for different languages and genders
        self.voice_mapping = {
            'en-US': {
                VoiceGender.MALE: 'en-US-GuyNeural',
                VoiceGender.FEMALE: 'en-US-JennyNeural',
                VoiceGender.NEUTRAL: 'en-US-AriaNeural'
            },
            'ru-RU': {
                VoiceGender.MALE: 'ru-RU-DmitryNeural',
                VoiceGender.FEMALE: 'ru-RU-SvetlanaNeural',
                VoiceGender.NEUTRAL: 'ru-RU-DariyaNeural'
            },
            'uz-UZ': {
                VoiceGender.MALE: 'uz-UZ-SardorNeural',
                VoiceGender.FEMALE: 'uz-UZ-MadinaNeural',
                VoiceGender.NEUTRAL: 'uz-UZ-MadinaNeural'
            },
            'tr-TR': {
                VoiceGender.MALE: 'tr-TR-AhmetNeural',
                VoiceGender.FEMALE: 'tr-TR-EmelNeural',
                VoiceGender.NEUTRAL: 'tr-TR-EmelNeural'
            }
        }
        
        # Default voice if no specific mapping is found
        self.default_voice = 'en-US-GuyNeural'
    
    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: str = "en-US",
        gender: Union[VoiceGender, str] = VoiceGender.MALE,
        format: Union[AudioFormat, str] = AudioFormat.MP3,
        **kwargs
    ) -> bytes:
        """
        Convert text to speech audio.
        
        Args:
            text: The text to convert to speech
            voice_id: Specific voice ID to use (overrides language/gender)
            language: Language code (e.g., 'en-US')
            gender: Voice gender (male, female, neutral)
            format: Output audio format
            **kwargs: Additional options for the TTS service
            
        Returns:
            bytes: Audio data in the specified format
        """
        # Parse enums if strings are provided
        if isinstance(gender, str):
            gender = VoiceGender(gender.lower())
        if isinstance(format, str):
            format = AudioFormat(format.lower())
        
        # Get voice ID if not specified
        if not voice_id:
            voice_id = self.get_voice_for_language(language, gender)
        
        # Prepare options
        options = TTSOptions(
            voice_id=voice_id,
            language=language,
            gender=gender,
            format=format,
            **{k: v for k, v in kwargs.items() if k in TTSOptions.__annotations__}
        )
        
        # Try different TTS providers until one succeeds
        last_error = None
        
        for provider in self.providers:
            try:
                audio_data = await provider(text, options)
                if audio_data:
                    logger.info(f"TTS generated {len(audio_data)} bytes of audio")
                    return audio_data
            except Exception as e:
                last_error = e
                logger.warning(f"TTS provider {provider.__name__} failed: {str(e)}")
                continue
        
        # If all providers failed, raise the last error
        raise last_error or Exception("All TTS providers failed")
    
    def get_voice_for_language(
        self, 
        language: str, 
        gender: Union[VoiceGender, str] = VoiceGender.MALE
    ) -> str:
        """
        Get the best available voice for a given language and gender.
        
        Args:
            language: Language code (e.g., 'en-US')
            gender: Voice gender (male, female, neutral)
            
        Returns:
            str: Voice ID for the TTS service
        """
        if isinstance(gender, str):
            gender = VoiceGender(gender.lower())
        
        # Try exact language match first
        if language in self.voice_mapping:
            if gender in self.voice_mapping[language]:
                return self.voice_mapping[language][gender]
            # Fallback to any gender if specific gender not available
            first_gender = next(iter(self.voice_mapping[language].values()))
            return first_gender
        
        # Try language family match (e.g., 'en' for 'en-US')
        lang_family = language.split('-')[0]
        for lang_code, voices in self.voice_mapping.items():
            if lang_code.startswith(lang_family):
                if gender in voices:
                    return voices[gender]
                return next(iter(voices.values()))
        
        # Default fallback
        return self.default_voice
    
    async def _azure_tts(self, text: str, options: TTSOptions) -> bytes:
        """Use Azure Cognitive Services for TTS"""
        if not settings.AZURE_SPEECH_KEY or not settings.AZURE_SPEECH_REGION:
            raise ValueError("Azure Speech Service credentials not configured")
        
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            # Configure speech config
            speech_config = speechsdk.SpeechConfig(
                subscription=settings.AZURE_SPEECH_KEY,
                region=settings.AZURE_SPEECH_REGION
            )
            
            # Set voice
            speech_config.speech_synthesis_voice_name = options.voice_id
            
            # Configure audio format
            if options.format == AudioFormat.MP3:
                speech_config.set_speech_synthesis_output_format(
                    speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
                )
            elif options.format == AudioFormat.WAV:
                speech_config.set_speech_synthesis_output_format(
                    speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
                )
            else:
                # Default to MP3
                speech_config.set_speech_synthesis_output_format(
                    speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
                )
            
            # Use a temporary file to store the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{options.format}") as temp_file:
                temp_path = temp_file.name
            
            # Configure audio output
            audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_path)
            
            # Create speech synthesizer
            speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            # Synthesize text
            result = speech_synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Read the generated audio file
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                
                # Clean up the temporary file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                
                return audio_data
            else:
                raise Exception(f"Azure TTS failed: {result.reason}")
                
        except ImportError:
            logger.warning("Azure Cognitive Services SDK not installed")
            raise
        except Exception as e:
            logger.error(f"Azure TTS error: {str(e)}")
            raise
    
    async def _google_tts(self, text: str, options: TTSOptions) -> bytes:
        """Use Google Cloud Text-to-Speech API"""
        if not settings.GOOGLE_CLOUD_CREDENTIALS_JSON:
            raise ValueError("Google Cloud credentials not configured")
            
        try:
            from google.cloud import texttospeech
            
            # Initialize client
            client = texttospeech.TextToSpeechClient.from_service_account_json(
                settings.GOOGLE_CLOUD_CREDENTIALS_JSON
            )
            
            # Set the text input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Build the voice request
            voice = texttospeech.VoiceSelectionParams(
                language_code=options.language,
                name=options.voice_id if hasattr(options, 'voice_id') else None,
                ssml_gender=texttospeech.SsmlVoiceGender[options.gender.upper()]
            )
            
            # Select the audio format
            if options.format == AudioFormat.MP3:
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=options.speaking_rate,
                    pitch=options.pitch,
                    volume_gain_db=20 * np.log10(options.volume) if options.volume != 1.0 else 0.0,
                    sample_rate_hertz=options.sample_rate
                )
            else:
                # Default to LINEAR16 (WAV)
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                    speaking_rate=options.speaking_rate,
                    pitch=options.pitch,
                    volume_gain_db=20 * np.log10(options.volume) if options.volume != 1.0 else 0.0,
                    sample_rate_hertz=options.sample_rate
                )
            
            # Generate speech
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return response.audio_content
            
        except ImportError:
            logger.warning("Google Cloud TTS client not installed")
            raise
        except Exception as e:
            logger.error(f"Google TTS error: {str(e)}")
            raise
    
    async def _espeak_tts(self, text: str, options: TTSOptions) -> bytes:
        """Use eSpeak as a fallback TTS (offline, lower quality)"""
        try:
            from gtts import gTTS
            import tempfile
            
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech using gTTS (which can use eSpeak as a backend)
            tts = gTTS(
                text=text,
                lang=options.language.split('-')[0],  # Convert 'en-US' to 'en'
                slow=False
            )
            
            # Save to temp file
            tts.save(temp_path)
            
            # Read the file
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up
            try:
                os.unlink(temp_path)
            except:
                pass
            
            return audio_data
            
        except ImportError:
            logger.warning("gTTS not installed")
            raise
        except Exception as e:
            logger.error(f"eSpeak/gTTS error: {str(e)}")
            raise

# Singleton instance
tts_service = TTSService()

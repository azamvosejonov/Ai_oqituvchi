import os
import logging
import tempfile
from typing import Dict, List, Optional, Tuple
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
from pydub.silence import split_on_silence

from app.core.config import settings

logger = logging.getLogger(__name__)

class SpeechService:
    def __init__(self):
        self.speech_config = speechsdk.SpeechConfig(
            subscription=settings.AZURE_SPEECH_KEY,
            region=settings.AZURE_SPEECH_REGION
        )
        self.speech_config.speech_recognition_language = "en-US"
        self.speech_config.request_word_level_timestamps()
        self.speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceResponse_RequestSentenceLevelTiming,
            "true"
        )
    
    async def transcribe_audio(self, audio_file_path: str) -> Dict:
        """Convert speech to text with pronunciation assessment"""
        audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )
        
        result = speech_recognizer.recognize_once_async().get()
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return {
                "text": result.text,
                "confidence": result.confidence,
                "pronunciation_assessment": self._extract_pronunciation_assessment(result)
            }
        else:
            raise Exception(f"Speech recognition failed: {result.reason}")
    
    def _extract_pronunciation_assessment(self, result) -> Dict:
        """Extract pronunciation assessment details from the result"""
        pronunciation_result = speechsdk.PronunciationAssessmentResult(result)
        return {
            "accuracy_score": pronunciation_result.accuracy_score,
            "pronunciation_score": pronunciation_result.pronunciation_score,
            "completeness_score": pronunciation_result.completeness_score,
            "fluency_score": pronunciation_result.fluency_score,
            "words": [
                {
                    "word": word.word,
                    "accuracy_score": word.accuracy_score,
                    "error_type": word.error_type,
                    "syllables": [
                        {
                            "syllable": syllable.syllable,
                            "accuracy_score": syllable.accuracy_score
                        } for syllable in word.syllables
                    ]
                } for word in pronunciation_result.words
            ]
        }
    
    async def assess_pronunciation(
        self, 
        audio_file_path: str, 
        reference_text: str
    ) -> Dict:
        """Assess pronunciation against a reference text"""
        # Configure pronunciation assessment
        pronunciation_config = speechsdk.PronunciationAssessmentConfig(
            reference_text=reference_text,
            grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
            granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
            enable_miscue=True
        )
        
        # Configure audio
        audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
        
        # Create speech recognizer
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )
        
        # Apply pronunciation assessment
        pronunciation_config.apply_to(speech_recognizer)
        
        # Perform recognition
        result = speech_recognizer.recognize_once_async().get()
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return {
                "text": result.text,
                "assessment": self._extract_pronunciation_assessment(result)
            }
        else:
            raise Exception(f"Pronunciation assessment failed: {result.reason}")
    
    async def process_audio_segments(
        self, 
        audio_file_path: str, 
        segment_duration_ms: int = 5000
    ) -> List[Dict]:
        """Split audio into segments and process each one"""
        # Load audio file
        audio = AudioSegment.from_file(audio_file_path)
        
        # Split on silence
        chunks = split_on_silence(
            audio,
            min_silence_len=500,
            silence_thresh=audio.dBFS-14,
            keep_silence=500
        )
        
        results = []
        
        # Process each chunk
        for i, chunk in enumerate(chunks):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                chunk.export(temp_file.name, format="wav")
                try:
                    result = await self.transcribe_audio(temp_file.name)
                    results.append({
                        "segment_id": i + 1,
                        "start_time": i * segment_duration_ms / 1000,  # in seconds
                        "end_time": (i + 1) * segment_duration_ms / 1000,
                        "result": result
                    })
                except Exception as e:
                    logger.error(f"Error processing segment {i}: {e}")
                finally:
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
        
        return results

# Initialize the service conditionally
speech_service: Optional[SpeechService] = None
if settings.AZURE_SPEECH_KEY and settings.AZURE_SPEECH_REGION:
    try:
        speech_service = SpeechService()
        logger.info("Azure Speech Service initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Azure Speech Service: {e}")
else:
    logger.warning("Azure Speech Service is not configured. Speech functionality will be disabled. Please set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION.")

__all__ = ["speech_service"]

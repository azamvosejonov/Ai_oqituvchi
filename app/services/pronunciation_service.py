import logging
import difflib
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from pydub import AudioSegment
import speech_recognition as sr
from scipy.spatial.distance import cosine
import Levenshtein

logger = logging.getLogger(__name__)

@dataclass
class PronunciationMistake:
    word: str
    expected: str
    actual: str
    error_type: str  # 'omission', 'insertion', 'substitution', 'mispronunciation'
    confidence: float
    suggested_correction: str

class PronunciationAnalyzer:
    """Uzbek language pronunciation analysis service"""
    
    def __init__(self):
        self.phonetic_dict = self._load_phonetic_dictionary()
        self.common_errors = {
            'q': 'k', 'g': 'k', 'h': 'x', 'oʻ': 'o', 'gʻ': 'g',
            'sh': 's', 'ch': 's', 'ng': 'n'
        }
    
    def _load_phonetic_dictionary(self) -> Dict[str, List[str]]:
        """Load Uzbek phonetic dictionary"""
        # This is a simplified version - in production, use a comprehensive dictionary
        return {
            'salom': ['s a l o m'],
            'xayr': ['x a y r'],
            'qanday': ['q a n d a y'],
            'yaxshi': ['y a x sh i'],
            'rahmat': ['r a x m a t'],
            'kechirasiz': ['k e ch i r a s i z'],
            'ha': ['h a'],
            'yoq': ['y o q'],
            'bilmadim': ['b i l m a d i m'],
            'tushundim': ['t u sh u n d i m'],
        }
    
    async def analyze_pronunciation(
        self, 
        audio_data: bytes, 
        expected_text: str,
        language: str = 'uz-UZ'
    ) -> Dict:
        """
        Analyze pronunciation of spoken text
        
        Args:
            audio_data: Raw audio data in WAV format
            expected_text: The expected text that was spoken
            language: Language code (default: 'uz-UZ' for Uzbek)
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Convert audio data to text
            recognized_text = await self._speech_to_text(audio_data, language)
            
            # Compare with expected text
            mistakes = self._compare_texts(expected_text, recognized_text)
            
            # Calculate pronunciation score
            score = self._calculate_pronunciation_score(expected_text, recognized_text, mistakes)
            
            return {
                'success': True,
                'score': score,
                'recognized_text': recognized_text,
                'expected_text': expected_text,
                'mistakes': [mistake.__dict__ for mistake in mistakes],
                'feedback': self._generate_feedback(mistakes, score)
            }
            
        except Exception as e:
            logger.error(f"Error in pronunciation analysis: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _speech_to_text(self, audio_data: bytes, language: str) -> str:
        """Convert speech to text using Google's speech recognition"""
        recognizer = sr.Recognizer()
        
        # Convert bytes to AudioData
        audio = AudioSegment.from_wav(audio_data)
        audio.export("temp.wav", format="wav")
        
        with sr.AudioFile("temp.wav") as source:
            audio_data = recognizer.record(source)
            
        try:
            text = recognizer.recognize_google(audio_data, language=language)
            return text.lower()
        except sr.UnknownValueError:
            raise ValueError("Audio could not be understood")
        except sr.RequestError as e:
            raise Exception(f"Could not request results from Google Speech Recognition service; {e}")
    
    def _compare_texts(self, expected: str, actual: str) -> List[PronunciationMistake]:
        """Compare expected and actual text to find pronunciation mistakes"""
        expected_words = re.findall(r"\w+['-]?\w*", expected.lower())
        actual_words = re.findall(r"\w+['-]?\w*", actual.lower())
        
        matcher = difflib.SequenceMatcher(None, expected_words, actual_words)
        mistakes = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                continue
                
            expected_part = ' '.join(expected_words[i1:i2])
            actual_part = ' '.join(actual_words[j1:j2])
            
            if tag == 'replace':
                # Substitution or mispronunciation
                mistake_type = self._determine_mistake_type(expected_part, actual_part)
                confidence = self._calculate_confidence(expected_part, actual_part)
                
                mistakes.append(PronunciationMistake(
                    word=actual_part,
                    expected=expected_part,
                    actual=actual_part,
                    error_type=mistake_type,
                    confidence=confidence,
                    suggested_correction=expected_part
                ))
                
            elif tag == 'delete':
                # Omission
                mistakes.append(PronunciationMistake(
                    word=expected_part,
                    expected=expected_part,
                    actual="[omitted]",
                    error_type='omission',
                    confidence=0.9,
                    suggested_correction=expected_part
                ))
                
            elif tag == 'insert':
                # Insertion
                mistakes.append(PronunciationMistake(
                    word=actual_part,
                    expected="[extra]",
                    actual=actual_part,
                    error_type='insertion',
                    confidence=0.8,
                    suggested_correction=""
                ))
        
        return mistakes
    
    def _determine_mistake_type(self, expected: str, actual: str) -> str:
        """Determine the type of pronunciation mistake"""
        # Check for common Uzbek pronunciation errors
        for error, correction in self.common_errors.items():
            if error in actual and correction in expected:
                return 'mispronunciation'
                
        # If no common error pattern found, consider it a substitution
        return 'substitution'
    
    def _calculate_confidence(self, expected: str, actual: str) -> float:
        """Calculate confidence score for a potential mistake"""
        # Simple Levenshtein distance-based confidence
        distance = Levenshtein.distance(expected, actual)
        max_len = max(len(expected), len(actual))
        similarity = 1 - (distance / max_len)
        return max(0.0, min(1.0, similarity))
    
    def _calculate_pronunciation_score(
        self, 
        expected: str, 
        actual: str, 
        mistakes: List[PronunciationMistake]
    ) -> float:
        """Calculate overall pronunciation score (0-100)"""
        if not expected.strip():
            return 0.0
            
        # Base score starts at 100 and is reduced for each mistake
        score = 100.0
        
        for mistake in mistakes:
            if mistake.error_type == 'omission':
                score -= 20  # Heavy penalty for omissions
            elif mistake.error_type == 'insertion':
                score -= 10  # Medium penalty for insertions
            else:  # substitution or mispronunciation
                score -= 15 * (1 - mistake.confidence)  # Penalty based on confidence
        
        # Ensure score is within bounds
        return max(0.0, min(100.0, score))
    
    def _generate_feedback(self, mistakes: List[PronunciationMistake], score: float) -> str:
        """Generate human-readable feedback based on pronunciation analysis"""
        if score >= 90:
            return "Ajoyib talaffuz! Siz juda yaxshi aytasiz."
        elif score >= 70:
            return "Yaxshi ish! Biroz mashq qilish kerak."
        elif score >= 50:
            return "Yaxshi harakat! Ko'proq mashq qilishingiz kerak."
        else:
            return "Iltimos, talaffuzga ko'proq e'tibor bering. Ko'proq mashq qiling."

# Singleton instance
pronunciation_analyzer = PronunciationAnalyzer()

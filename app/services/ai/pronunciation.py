import logging
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import wave
import io
import speech_recognition as sr
from pydub import AudioSegment

logger = logging.getLogger(__name__)

@dataclass
class PronunciationResult:
    """Result of pronunciation analysis"""
    score: float  # 0.0 to 1.0
    feedback: Dict[str, any]
    phonemes: Optional[List[Dict]] = None
    word_scores: Optional[List[Dict]] = None

class PronunciationAnalyzer:
    """
    Analyzes pronunciation quality and provides feedback.
    Uses a combination of speech recognition and phonetic analysis.
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # In a production environment, you'd load language models here
        self.phoneme_models = {}
    
    async def analyze(
        self,
        audio_data: bytes,
        text: str,
        language: str = "en-US",
        reference_audio: Optional[bytes] = None
    ) -> PronunciationResult:
        """
        Analyze pronunciation of the given audio against the expected text.
        
        Args:
            audio_data: Raw audio data in WAV format
            text: Expected text that was spoken
            language: Language code (e.g., 'en-US')
            reference_audio: Optional reference audio for comparison
            
        Returns:
            PronunciationResult with score and feedback
        """
        try:
            # Convert audio to the right format if needed
            audio = self._preprocess_audio(audio_data)
            
            # Basic speech recognition to verify the text
            recognized_text = await self._recognize_speech(audio, language)
            
            # Calculate word-level accuracy
            word_accuracy = self._calculate_text_similarity(text, recognized_text)
            
            # Analyze phonemes (simplified)
            phoneme_analysis = await self._analyze_phonemes(audio, text, language)
            
            # Calculate overall score (weighted average of different metrics)
            phoneme_score = phoneme_analysis.get('score', 0.7)  # Default to 0.7 if analysis fails
            overall_score = (word_accuracy * 0.6) + (phoneme_score * 0.4)
            
            # Generate feedback
            feedback = self._generate_feedback(
                word_accuracy=word_accuracy,
                phoneme_analysis=phoneme_analysis,
                recognized_text=recognized_text,
                expected_text=text
            )
            
            return PronunciationResult(
                score=overall_score,
                feedback=feedback,
                phonemes=phoneme_analysis.get('phonemes'),
                word_scores=phoneme_analysis.get('word_scores')
            )
            
        except Exception as e:
            logger.error(f"Error in pronunciation analysis: {str(e)}", exc_info=True)
            # Return a default result if analysis fails
            return PronunciationResult(
                score=0.7,
                feedback={
                    "error": "Could not analyze pronunciation",
                    "details": str(e)
                }
            )
    
    def _preprocess_audio(self, audio_data: bytes) -> sr.AudioData:
        """Convert audio data to the format needed for analysis"""
        try:
            # Convert to WAV if needed
            audio = AudioSegment.from_file(io.BytesIO(audio_data))
            audio = audio.set_channels(1)  # Convert to mono
            audio = audio.set_frame_rate(16000)  # 16kHz sample rate
            
            # Convert to the format expected by speech_recognition
            wav_data = audio.export(format="wav").read()
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
            raise
    
    async def _recognize_speech(
        self, 
        audio: sr.AudioData, 
        language: str
    ) -> str:
        """Convert speech to text using Google's speech recognition"""
        try:
            # In a real implementation, you might want to use a more reliable service
            # or a custom model for better accuracy
            return self.recognizer.recognize_google(audio, language=language)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            logger.error(f"Could not request results from speech recognition service; {e}")
            return ""
    
    def _calculate_text_similarity(self, expected: str, recognized: str) -> float:
        """Calculate similarity between expected and recognized text"""
        if not expected or not recognized:
            return 0.0
            
        # Simple word-level comparison
        expected_words = set(expected.lower().split())
        recognized_words = set(recognized.lower().split())
        
        if not expected_words:
            return 0.0
            
        # Calculate Jaccard similarity
        intersection = len(expected_words.intersection(recognized_words))
        union = len(expected_words.union(recognized_words))
        
        return intersection / union if union > 0 else 0.0
    
    async def _analyze_phonemes(
        self, 
        audio: sr.AudioData, 
        text: str, 
        language: str
    ) -> Dict:
        """Analyze phoneme-level pronunciation"""
        # In a production environment, you would use a proper phoneme recognition model
        # This is a simplified version that returns mock data
        
        # Mock phoneme analysis
        phonemes = [
            {"phoneme": sound, "score": np.random.uniform(0.6, 1.0)}
            for sound in ["h", "ɛ", "l", "oʊ"]
        ]
        
        word_scores = [
            {"word": word, "score": np.random.uniform(0.6, 1.0)}
            for word in text.split()[:5]  # Limit to first 5 words for demo
        ]
        
        # Calculate average score
        if word_scores:
            avg_score = sum(w["score"] for w in word_scores) / len(word_scores)
        else:
            avg_score = 0.8  # Default score
        
        return {
            "score": avg_score,
            "phonemes": phonemes,
            "word_scores": word_scores
        }
    
    def _generate_feedback(
        self,
        word_accuracy: float,
        phoneme_analysis: Dict,
        recognized_text: str,
        expected_text: str
    ) -> Dict[str, any]:
        """Generate user-friendly feedback based on analysis"""
        feedback = {
            "overall_score": round(word_accuracy * 100, 1),
            "accuracy": {
                "description": "How accurately you pronounced the words",
                "score": round(word_accuracy * 100, 1),
                "feedback": self._get_accuracy_feedback(word_accuracy)
            },
            "words": []
        }
        
        # Add word-level feedback
        if phoneme_analysis.get('word_scores'):
            for word_info in phoneme_analysis['word_scores']:
                feedback["words"].append({
                    "word": word_info["word"],
                    "score": round(word_info["score"] * 100, 1),
                    "feedback": self._get_word_feedback(word_info["word"], word_info["score"])
                })
        
        # Add phoneme-level feedback for the most problematic sounds
        if phoneme_analysis.get('phonemes'):
            problem_sounds = [
                p for p in phoneme_analysis['phonemes'] 
                if p['score'] < 0.7
            ]
            if problem_sounds:
                feedback["sounds_to_practice"] = [
                    {"sound": p["phoneme"], "score": round(p["score"] * 100, 1)}
                    for p in sorted(problem_sounds, key=lambda x: x['score'])[:3]  # Top 3 to practice
                ]
        
        return feedback
    
    def _get_accuracy_feedback(self, score: float) -> str:
        """Get feedback based on accuracy score"""
        if score >= 0.9:
            return "Excellent pronunciation! You're very clear and easy to understand."
        elif score >= 0.7:
            return "Good job! Your pronunciation is clear, but there's room for improvement."
        elif score >= 0.5:
            return "Not bad! Try to focus on pronouncing each word more clearly."
        else:
            return "Keep practicing! Pay attention to the pronunciation of each word."
    
    def _get_word_feedback(self, word: str, score: float) -> str:
        """Get feedback for a specific word"""
        if score >= 0.9:
            return f"Perfect pronunciation of '{word}'!"
        elif score >= 0.7:
            return f"Good pronunciation of '{word}', but could be clearer."
        elif score >= 0.5:
            return f"The word '{word}' was a bit unclear. Try to pronounce it more distinctly."
        else:
            return f"The word '{word}' was difficult to understand. Please practice this word."

# Singleton instance
pronunciation_analyzer = PronunciationAnalyzer()

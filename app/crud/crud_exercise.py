from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi.encoders import jsonable_encoder

from app import models, schemas
from app.crud.base import CRUDBase
from app.core.text_utils import normalize_text, levenshtein_distance, semantic_similarity
from app.models.exercise import (
    Exercise,
    ExerciseAttempt,
    ExerciseSet,
    ExerciseSetItem,
    TestSession,
    TestResponse,
)
from app.models.pronunciation import PronunciationAttempt
from app.models.user_level import UserProgress
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseSetCreate,
    ExerciseSetUpdate,
    TestSessionCreate,
    TestSessionUpdate,
    TestResponseCreate,
    TestResponseUpdate,
    UserProgressUpdate,
    ExerciseAttemptCreate,
)
from app.schemas.interactive_lesson import PronunciationAttemptCreate


class CRUDExercise(CRUDBase[Exercise, ExerciseCreate, ExerciseUpdate]):
    """CRUD operations for Exercise model."""
    
    def get_by_lesson(self, db: Session, *, lesson_id: int, skip: int = 0, limit: int = 100) -> List[Exercise]:
        """Get all exercises for a specific lesson."""
        return db.query(self.model).filter(Exercise.lesson_id == lesson_id).offset(skip).limit(limit).all()
    
    def get_by_difficulty(self, db: Session, *, difficulty: str, skip: int = 0, limit: int = 100) -> List[Exercise]:
        """Get exercises by difficulty level."""
        return db.query(self.model).filter(Exercise.difficulty == difficulty).offset(skip).limit(limit).all()
    
    def get_by_type(self, db: Session, *, exercise_type: str, skip: int = 0, limit: int = 100) -> List[Exercise]:
        """Get exercises by type."""
        return db.query(self.model).filter(Exercise.exercise_type == exercise_type).offset(skip).limit(limit).all()
    
    def get_multi_filtered(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        lesson_id: Optional[int] = None,
        difficulty: Optional[str] = None,
        exercise_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        tags: Optional[List[str]] = None
    ) -> List[Exercise]:
        """Get exercises with multiple filters."""
        query = db.query(self.model)
        
        if lesson_id is not None:
            query = query.filter(Exercise.lesson_id == lesson_id)
        if difficulty is not None:
            query = query.filter(Exercise.difficulty == difficulty)
        if exercise_type is not None:
            query = query.filter(Exercise.exercise_type == exercise_type)
        if is_active is not None:
            query = query.filter(Exercise.is_active == is_active)
        if tags:
            # Assuming tags is a JSON array in the database
            query = query.filter(Exercise.tags.op("@>")(tags))
        
        return query.offset(skip).limit(limit).all()
        
    def evaluate_text_answer(self, user_answer: str, correct_answer: str) -> dict:
        """Evaluate a user's text answer against the correct answer."""
        is_correct = normalize_text(user_answer) == normalize_text(correct_answer)
        feedback = ""
        score = 1.0 if is_correct else 0.0

        if not is_correct:
            sim = semantic_similarity(user_answer, correct_answer)
            if sim > 0.8:
                feedback = f"Yaqin javob! To'g'ri javob: '{correct_answer}'"
            else:
                feedback = f"Noto'g'ri. To'g'ri javob: '{correct_answer}'"

        return {"is_correct": is_correct, "feedback": feedback, "score": score}
    
    def _evaluate_listening_answer(
        self,
        user_answer: str,
        correct_answer: Union[str, List[str]],
        audio_url: Optional[str] = None,
        language: str = 'uz'
    ) -> tuple[bool, Dict[str, Any]]:
        """Evaluate listening comprehension answers."""
        feedback = {
            "general": "",
            "specific": {},
            "suggestions": [],
            "audio_feedback": None,
            "score": 0.0
        }
        
        if not user_answer and not audio_url:
            feedback["general"] = "❌ Javob yoki audio fayl kiritilmagan."
            return False, feedback
        
        # If audio_url is provided but no user_answer, we'd normally transcribe it here
        # For now, we'll just use the user_answer if available
        if not user_answer and audio_url:
            feedback["general"] = "❌ Audio transkripsiya qilinmadi. Iltimos, yozma javob yuboring."
            return False, feedback
        
        # Convert single correct answer to list for uniform processing
        correct_answers = [correct_answer] if isinstance(correct_answer, str) else correct_answer
        
        # Check for exact or close match
        for ans in correct_answers:
            if semantic_similarity(user_answer, ans, threshold=0.9):
                feedback["general"] = "✅ Ajoyib! Siz to'g'ri eshitdingiz."
                feedback["score"] = 1.0
                return True, feedback
        
        # Calculate word overlap for partial matches
        user_words = set(normalize_text(user_answer, language).split())
        best_match_score = 0.0
        best_match = ""
        
        for ans in correct_answers:
            ans_words = set(normalize_text(str(ans), language).split())
            if not ans_words:
                continue
                
            common_words = user_words.intersection(ans_words)
            match_score = len(common_words) / max(len(ans_words), 1)
            
            if match_score > best_match_score:
                best_match_score = match_score
                best_match = ans
        
        is_correct = best_match_score >= 0.7  # 70% word overlap
        
        if is_correct:
            feedback["general"] = "✅ Yaxshi eshitdingiz! Biroz xatolar bo'lishi mumkin."
            feedback["suggestions"].append("Eshitish mahoratingizni yaxshilash uchun qayta eshiting.")
            feedback["score"] = min(0.9, best_match_score)  # Cap at 0.9 for listening
        else:
            feedback["general"] = "❌ Eshitganlaringizda xatolik bor."
            feedback["suggestions"].append(f"To'g'ri javob: {best_match}")
            feedback["score"] = best_match_score * 0.5  # Partial credit
            
            if audio_url:
                feedback["suggestions"].append("Audio yozuvini qayta eshiting.")
                feedback["audio_feedback"] = {
                    "audio_url": audio_url,
                    "message": "Audio yozuvini qayta eshiting."
                }
        
        return is_correct, feedback
    
    def _evaluate_speaking_answer(
        self,
        audio_url: str,
        expected_text: str,
        language: str = 'uz'
    ) -> tuple[bool, Dict[str, Any]]:
        """Evaluate speaking exercises (pronunciation, fluency, etc.)."""
        feedback = {
            "general": "",
            "pronunciation": {
                "score": 0.0,
                "feedback": "",
                "word_level": []
            },
            "fluency": {
                "score": 0.0,
                "feedback": ""
            },
            "suggestions": [],
            "score": 0.0
        }
        
        try:
            # In a real implementation, we would call a speech-to-text service
            # and pronunciation evaluation service here
            # For now, we'll simulate the response
            
            # Simulate speech recognition (in reality, this would call a service)
            recognized_text = expected_text  # This would come from STT
            
            # Check if the recognized text matches the expected text
            is_recognized = semantic_similarity(recognized_text, expected_text, threshold=0.9)
            
            # Simulate pronunciation scoring (0.7-1.0 range for recognized, 0.3-0.7 for partially recognized)
            import random
            if is_recognized:
                feedback["general"] = "✅ Ajoyib! Siz to'g'ri aytdingiz."
                feedback["pronunciation"]["score"] = round(0.85 + random.random() * 0.15, 2)  # 0.85-1.0
                feedback["pronunciation"]["feedback"] = "Yaxshi talaffuz qildingiz."
                feedback["fluency"]["score"] = round(0.8 + random.random() * 0.2, 2)  # 0.8-1.0
                feedback["fluency"]["feedback"] = "Sokin va aniq gapirdingiz."
                feedback["score"] = (feedback["pronunciation"]["score"] * 0.6 + 
                                   feedback["fluency"]["score"] * 0.4)
            else:
                feedback["general"] = "❌ Siz noto'g'ri aytdingiz."
                feedback["pronunciation"]["score"] = round(0.4 + random.random() * 0.3, 2)  # 0.4-0.7
                feedback["pronunciation"]["feedback"] = "Ba'zi so'zlarni talaffuz qilishda xatolik bor."
                feedback["fluency"]["score"] = round(0.5 + random.random() * 0.2, 2)  # 0.5-0.7
                feedback["fluency"]["feedback"] = "Bu borada yaxshiroq bo'lishi mumkin."
                feedback["suggestions"].append(f"Kutilgan matn: {expected_text}")
                feedback["suggestions"].append("Tovushlarni aniqroq aytishga harakat qiling.")
                
                # Calculate overall score (weighted average)
                feedback["score"] = (feedback["pronunciation"]["score"] * 0.6 + 
                                   feedback["fluency"]["score"] * 0.4)
            
            # Add word-level feedback (simulated)
            words = expected_text.split()
            for i, word in enumerate(words[:5]):  # Limit to first 5 words for brevity
                feedback["pronunciation"]["word_level"].append({
                    "word": word,
                    "score": round(0.7 + random.random() * 0.3, 2),  # 0.7-1.0
                    "feedback": "Yaxshi" if random.random() > 0.3 else "Yaxshiroq bo'lishi mumkin"
                })
            
            return is_recognized, feedback
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error evaluating speaking answer: {str(e)}")
            
            feedback["general"] = "❌ Nutqni baholashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
            feedback["score"] = 0.0
            return False, feedback
    
    def _evaluate_translation(
        self,
        user_translation: str,
        source_text: str,
        target_language: str,
        reference_translation: str
    ) -> tuple[bool, Dict[str, Any]]:
        """Evaluate translation exercises."""
        feedback = {
            "general": "",
            "accuracy": {
                "score": 0.0,
                "feedback": ""
            },
            "fluency": {
                "score": 0.0,
                "feedback": ""
            },
            "suggestions": [],
            "score": 0.0
        }
        
        if not user_translation or not isinstance(user_translation, str):
            feedback["general"] = "❌ Tarjima kutilgan formatda emas. Iltimos, matn kiriting."
            return False, feedback
        
        # Simple evaluation - can be enhanced with NLP and translation APIs
        user_words = set(normalize_text(user_translation, target_language).split())
        ref_words = set(normalize_text(reference_translation, target_language).split())
        
        # Calculate word overlap
        common_words = user_words.intersection(ref_words)
        word_overlap = len(common_words) / max(len(ref_words), 1)
        
        # Check for exact or close match
        if semantic_similarity(user_translation, reference_translation, threshold=0.9):
            feedback["general"] = "✅ Ajoyib! To'liq to'g'ri tarjima."
            feedback["accuracy"]["score"] = 1.0
            feedback["accuracy"]["feedback"] = "Tarjimangiz aniq va to'g'ri."
            feedback["fluency"]["score"] = 1.0
            feedback["fluency"]["feedback"] = "Tarjimangiz o'qish uchun qulay va tabiiy."
            feedback["score"] = 1.0
            return True, feedback
        
        # Evaluate based on word overlap
        if word_overlap >= 0.7:  # 70% word overlap
            is_correct = True
            feedback["general"] = "✅ Yaxshi ish! Asosiy mazmun to'g'ri."
            feedback["accuracy"]["score"] = min(0.9, word_overlap)  # Cap at 0.9 for partial matches
            feedback["accuracy"]["feedback"] = "Asosiy mazmun to'g'ri, lekin ba'zi jihatlarni yaxshilashingiz mumkin."
            feedback["fluency"]["score"] = 0.8
            feedback["fluency"]["feedback"] = "Tarjimangiz tushinarli, lekin biroz yaxshilash mumkin."
            feedback["suggestions"].append(f"To'g'ri tarjima: {reference_translation}")
        else:
            is_correct = False
            feedback["general"] = "❌ Tarjimangizda xatoliklar bor."
            feedback["accuracy"]["score"] = word_overlap * 0.7  # Scale down the score
            feedback["accuracy"]["feedback"] = "Tarjimangiz asl mazmunni to'liq aks ettirmayapti."
            feedback["fluency"]["score"] = 0.5
            feedback["fluency"]["feedback"] = "Matn tushunarsiz yoki noaniq bo'lib qolgan."
            feedback["suggestions"].append(f"To'g'ri tarjima: {reference_translation}")
        
        # Calculate overall score (weighted average)
        accuracy_weight = 0.6
        fluency_weight = 0.4
        feedback["score"] = round(
            (feedback["accuracy"]["score"] * accuracy_weight +
             feedback["fluency"]["score"] * fluency_weight),
            2
        )
        
        return is_correct, feedback
    
    def _evaluate_dictation(
        self,
        audio_url: Optional[str],
        user_text: Optional[str],
        expected_text: str,
        language: str = 'uz'
    ) -> tuple[bool, Dict[str, Any]]:
        """Evaluate dictation exercises."""
        feedback = {
            "general": "",
            "accuracy": {
                "score": 0.0,
                "feedback": ""
            },
            "suggestions": [],
            "score": 0.0
        }
        
        try:
            # If audio_url is provided but no user_text, we'd transcribe it here
            # For now, we'll just use the user_text if available
            if not user_text and audio_url:
                feedback["general"] = "❌ Audio transkripsiya qilinmadi. Iltimos, yozma javob yuboring."
                return False, feedback
            
            # Check if the user's text matches the expected text
            is_correct = semantic_similarity(user_text, expected_text, threshold=0.9)
            
            if is_correct:
                feedback["general"] = "✅ Ajoyib! Siz to'g'ri yozdingiz."
                feedback["accuracy"]["score"] = 1.0
                feedback["accuracy"]["feedback"] = "Barcha so'zlar to'g'ri yozilgan."
                feedback["score"] = 1.0
            else:
                # Calculate character-level accuracy
                distance = levenshtein_distance(normalize_text(user_text, language), normalize_text(expected_text, language))
                max_length = max(len(user_text or ""), len(expected_text))
                accuracy = 1 - (distance / max_length) if max_length > 0 else 0
                
                is_correct = accuracy >= 0.9  # 90% accuracy threshold
                
                if is_correct:
                    feedback["general"] = "✅ Yaxshi! Kichik xatolar bilan yozdingiz."
                    feedback["accuracy"]["score"] = round(0.9, 2)
                    feedback["accuracy"]["feedback"] = "Asosiy qismi to'g'ri, lekin kichik xatolar bor."
                else:
                    feedback["general"] = "❌ Yozuvingizda xatoliklar bor."
                    feedback["accuracy"]["score"] = round(accuracy * 0.8, 2)  # Scale down the score
                    feedback["accuracy"]["feedback"] = f"Yozuvingizda {int((1-accuracy)*100)}% xatolik bor."
                
                feedback["suggestions"].append(f"Kutilgan matn: {expected_text}")
                feedback["suggestions"].append(f"Siz yozgan matn: {user_text}")
                feedback["score"] = feedback["accuracy"]["score"]
            
            return is_correct, feedback
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error evaluating dictation: {str(e)}")
            
            feedback["general"] = "❌ Diktantni baholashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
            feedback["score"] = 0.0
            return False, feedback
    
    def check_answer(
        self, 
        db: Session, 
        *, 
        exercise_id: int, 
        user_answer: Union[str, List, Dict, None] = None,
        user_id: Optional[int] = None,
        audio_url: Optional[str] = None,
        language: str = "uz"
    ) -> Dict[str, Any]:
        """
        Check if the user's answer is correct and provide detailed feedback.
        
        Args:
            db: Database session
            exercise_id: ID of the exercise
            user_answer: User's answer (can be text, list, or dict depending on exercise type)
            user_id: Optional user ID to track progress
            audio_url: Optional URL for audio responses (used for speaking/dictation)
            language: Language code for feedback (default: 'uz')
            
        Returns:
            Dict containing is_correct, score, feedback, and explanation
        """
        # Get the exercise
        exercise = self.get(db, id=exercise_id)
        if not exercise or not exercise.is_active:
            raise ValueError(f"Exercise with ID {exercise_id} not found or inactive")
        
        # Initialize response
        is_correct = False
        score = 0.0
        feedback = {
            "general": "", 
            "specific": {},
            "suggestions": [],
            "audio_feedback": None
        }
        
        try:
            # Normalize user answer
            if isinstance(user_answer, str):
                user_answer = user_answer.strip()
            
            # Check answer based on exercise type
            if exercise.exercise_type == schemas.ExerciseType.MULTIPLE_CHOICE:
                # Validate that the answer is one of the provided options, if any
                if exercise.options:
                    valid_values = []
                    if isinstance(exercise.options, dict):
                        valid_values = [str(k) for k in exercise.options.keys()]
                    elif isinstance(exercise.options, list):
                        valid_values = [str(opt.get('value')) for opt in exercise.options if isinstance(opt, dict) and 'value' in opt]
                    # If we have a set of valid values and user_answer is not among them -> invalid
                    if valid_values:
                        if str(user_answer) not in valid_values:
                            raise ValueError("Invalid option selected")

                is_correct = str(user_answer).lower() == str(exercise.correct_answer).lower()
                score = 1.0 if is_correct else 0.0
                feedback["general"] = "✅ To'g'ri!" if is_correct else "❌ Noto'g'ri. Qaytadan urinib ko'ring."
                
                # Provide the correct answer if available in options
                if not is_correct and exercise.options:
                    # Options can be a dict like {"A":"3", "B":"4"} or a list of {value, text}
                    if isinstance(exercise.options, dict):
                        correct_text = None
                        # correct_answer may be like "B"; fetch its text
                        correct_text = exercise.options.get(str(exercise.correct_answer))
                        if correct_text is None:
                            correct_text = exercise.options.get(exercise.correct_answer)
                        if correct_text is not None:
                            feedback["To'g'ri javob"] = str(correct_text)
                            feedback["suggestions"].append(f"To'g'ri javob: {correct_text}")
                    elif isinstance(exercise.options, list):
                        try:
                            correct_option = next(
                                opt for opt in exercise.options
                                if isinstance(opt, dict) and str(opt.get('value', '')).lower() == str(exercise.correct_answer).lower()
                            )
                            if correct_option:
                                text = correct_option.get('text') or correct_option.get('label') or correct_option.get('value')
                                if text is not None:
                                    feedback["To'g'ri javob"] = str(text)
                                    feedback["suggestions"].append(f"To'g'ri javob: {text}")
                        except StopIteration:
                            pass
            
            elif exercise.exercise_type == schemas.ExerciseType.TRUE_FALSE:
                is_correct = bool(user_answer) == bool(exercise.correct_answer)
                score = 1.0 if is_correct else 0.0
                correct_text = "To'g'ri" if exercise.correct_answer else "Noto'g'ri"
                feedback["general"] = "✅ To'g'ri!" if is_correct else f"❌ Noto'g'ri. To'g'ri javob: {correct_text}"
            
            elif exercise.exercise_type == schemas.ExerciseType.FILL_IN_BLANK:
                if not user_answer:
                    feedback["general"] = "❌ Javob kiritilmagan. Iltimos, javobingizni yozing."
                    score = 0.0
                else:
                    if isinstance(exercise.correct_answer, list):
                        # Multiple possible correct answers
                        user_answer_str = str(user_answer).strip().lower()
                        is_correct = any(
                            normalize_text(str(correct), language) == normalize_text(user_answer_str, language)
                            for correct in exercise.correct_answer
                        )
                        score = 1.0 if is_correct else 0.0
                    else:
                        # Single correct answer with fuzzy matching
                        is_correct = semantic_similarity(str(user_answer).strip(), str(exercise.correct_answer).strip(), language=language)
                        score = 1.0 if is_correct else 0.0
                    
                    if is_correct:
                        feedback["general"] = "✅ To'g'ri!"
                    else:
                        correct_answers = (
                            exercise.correct_answer 
                            if isinstance(exercise.correct_answer, list)
                            else [exercise.correct_answer]
                        )
                        feedback["general"] = "❌ Noto'g'ri. "
                        feedback["suggestions"] = [f"To'g'ri javob(lar): {', '.join(str(a) for a in correct_answers)}"]
            
            elif exercise.exercise_type == schemas.ExerciseType.MATCHING:
                if not user_answer or not isinstance(user_answer, dict):
                    feedback["general"] = "❌ Noto'g'ri format. Moslashuvchi javoblar lug'at ko'rinishida bo'lishi kerak."
                    score = 0.0
                else:
                    correct_items = exercise.correct_answer
                    user_items = user_answer
                    
                    correct_count = 0
                    total = len(correct_items) if correct_items else 0
                    
                    for key, value in correct_items.items():
                        user_value = user_items.get(key, "")
                        if isinstance(user_value, str) and semantic_similarity(user_value, value, language=language):
                            correct_count += 1
                            feedback["specific"][key] = {"status": "correct", "user_answer": user_value}
                        else:
                            feedback["specific"][key] = {
                                "status": "incorrect", 
                                "user_answer": user_value,
                                "correct_answer": value
                            }
                    
                    is_correct = correct_count == total
                    score = correct_count / total if total > 0 else 0.0
                    
                    if is_correct:
                        feedback["general"] = "✅ Barcha javoblar to'g'ri!"
                    else:
                        feedback["general"] = f"✅ {correct_count} ta to'g'ri, ❌ {total - correct_count} ta xato"
            
            elif exercise.exercise_type in [schemas.ExerciseType.SHORT_ANSWER, schemas.ExerciseType.ESSAY]:
                if not user_answer:
                    feedback["general"] = "❌ Javob kiritilmagan. Iltimos, javobingizni yozing."
                    score = 0.0
                else:
                    # For short answers and essays, evaluate based on content
                    is_correct, detailed_feedback = self.evaluate_text_answer(
                        user_answer=user_answer,
                        correct_answer=exercise.correct_answer,
                    )
                    score = detailed_feedback.get("score", 0.0)
                    feedback.update(detailed_feedback)
            
            elif exercise.exercise_type == schemas.ExerciseType.LISTENING:
                if not user_answer and not audio_url:
                    feedback["general"] = "❌ Javob yoki audio fayl kiritilmagan."
                    score = 0.0
                else:
                    # For listening exercises, evaluate based on transcription
                    is_correct, detailed_feedback = self._evaluate_listening_answer(
                        user_answer=user_answer,
                        correct_answer=exercise.correct_answer,
                        audio_url=audio_url,
                        language=language
                    )
                    score = 1.0 if is_correct else 0.0
                    feedback.update(detailed_feedback)
            
            elif exercise.exercise_type == schemas.ExerciseType.SPEAKING:
                if not audio_url:
                    feedback["general"] = "❌ Audio fayl kiritilmagan. Iltimos, ovozli javob yuboring."
                    score = 0.0
                else:
                    # For speaking exercises, evaluate pronunciation and content
                    is_correct, detailed_feedback = self._evaluate_speaking_answer(
                        audio_url=audio_url,
                        expected_text=exercise.correct_answer,
                        language=language
                    )
                    score = detailed_feedback.get("score", 0.0)
                    feedback.update(detailed_feedback)
            
            elif exercise.exercise_type == schemas.ExerciseType.TRANSLATION:
                if not user_answer:
                    feedback["general"] = "❌ Tarjima kiritilmagan. Iltimos, tarjimangizni yozing."
                    score = 0.0
                else:
                    # For translation exercises, evaluate meaning
                    is_correct, detailed_feedback = self._evaluate_translation(
                        user_translation=user_answer,
                        source_text=exercise.metadata_.get("source_text", ""),
                        target_language=language,
                        reference_translation=exercise.correct_answer
                    )
                    score = detailed_feedback.get("score", 0.0)
                    feedback.update(detailed_feedback)
            
            elif exercise.exercise_type == schemas.ExerciseType.DICTATION:
                if not audio_url and not user_answer:
                    feedback["general"] = "❌ Audio fayl yoki yozma javob kiritilmagan."
                    score = 0.0
                else:
                    # For dictation, compare the transcribed text with the correct text
                    is_correct, detailed_feedback = self._evaluate_dictation(
                        audio_url=audio_url,
                        user_text=user_answer,
                        expected_text=exercise.correct_answer,
                        language=language
                    )
                    score = detailed_feedback.get("score", 0.0)
                    feedback.update(detailed_feedback)
            
            # Add explanation if available
            if exercise.explanation:
                feedback["explanation"] = exercise.explanation
            
            # Log the attempt if user_id is provided
            if user_id is not None:
                self.log_attempt(
                    db,
                    user_id=user_id,
                    exercise_id=exercise_id,
                    user_answer=user_answer,
                    is_correct=is_correct,
                    score=score,
                    feedback=feedback,
                    time_spent=None  # Can be added if tracked
                )
            
            return {
                "is_correct": is_correct,
                "score": score,
                "feedback": feedback,
                "explanation": exercise.explanation
            }
            
        except ValueError:
            # Let invalid input errors bubble up to the API layer
            raise
        except Exception as e:
            # Log the error and return a generic error message
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error checking answer: {str(e)}")
            
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": {
                    "general": "❌ Javobni tekshirishda xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.",
                    "error": str(e)
                },
                "explanation": None
            }
        
        # For other exercise types, we might need more complex evaluation
        else:
            # Default implementation for other types
            is_correct = str(user_answer).strip().lower() == str(exercise.correct_answer).strip().lower()
            score = 1.0 if is_correct else 0.0
            feedback["general"] = "Answer received. This exercise type requires manual review."
        
        # Log the attempt if user_id is provided
        if user_id is not None:
            self.log_attempt(
                db,
                user_id=user_id,
                exercise_id=exercise_id,
                user_answer=user_answer,
                is_correct=is_correct,
                score=score,
                feedback=feedback
            )
        
        return {
            "is_correct": is_correct,
            "score": score,
            "feedback": feedback,
            "explanation": exercise.explanation
        }
    
    def log_attempt(
        self,
        db: Session,
        *,
        user_id: int,
        exercise_id: int,
        user_answer: Union[str, List, Dict],
        is_correct: bool,
        score: float,
        feedback: Optional[Dict[str, Any]] = None,
        time_spent: Optional[int] = None
    ) -> ExerciseAttempt:
        """Log a user's attempt at an exercise."""
        db_attempt = ExerciseAttempt(
            user_id=user_id,
            exercise_id=exercise_id,
            user_answer=user_answer,
            is_correct=is_correct,
            score=score,
            feedback=feedback,
            time_spent=time_spent
        )
        db.add(db_attempt)
        db.commit()
        db.refresh(db_attempt)
        
        # Update user progress
        self.update_user_progress(
            db,
            user_id=user_id,
            exercise_id=exercise_id,
            score=score,
            completed=is_correct
        )
        
        return db_attempt
    
    def update_user_progress(
        self,
        db: Session,
        *,
        user_id: int,
        exercise_id: int,
        score: float,
        completed: bool = False
    ) -> UserProgress:
        """Update aggregate user progress.

        Note: Current UserProgress model tracks aggregate metrics per user and
        does not have per-exercise fields like exercise_id/attempts/score/completed.
        We therefore update totals by user_id only.
        """
        # Fetch progress for the user
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id
        ).first()

        if progress is None:
            # Create a new aggregate progress row
            progress = UserProgress(
                user_id=user_id,
                total_exercises_completed=1 if completed else 0,
            )
            db.add(progress)
        else:
            # Increment totals conservatively
            if completed:
                try:
                    progress.total_exercises_completed = (progress.total_exercises_completed or 0) + 1
                except Exception:
                    # Fallback in case of unexpected None
                    progress.total_exercises_completed = 1
            db.add(progress)

        db.commit()
        db.refresh(progress)
        return progress

class CRUDPronunciationAttempt(
    CRUDBase[PronunciationAttempt, PronunciationAttemptCreate, Dict[str, Any]]
):
    """CRUD operations for PronunciationAttempt model"""

    def get_user_stats(self, db: Session, *, user_id: int) -> Dict[str, Any]:
        """Get pronunciation statistics for a user"""
        stats = (
            db.query(
                func.avg(self.model.score).label("avg_score"),
                func.count(self.model.id).label("total_attempts"),
                func.max(self.model.timestamp).label("last_attempt"),
            )
            .filter(self.model.user_id == user_id)
            .first()
        )

        return {
            "average_score": float(stats.avg_score) if stats.avg_score else 0.0,
            "total_attempts": stats.total_attempts or 0,
            "last_attempt": stats.last_attempt,
        }

    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[PronunciationAttempt]:
        """Get all pronunciation attempts for a user"""
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(desc(self.model.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDExerciseAttempt(CRUDBase[ExerciseAttempt, ExerciseAttemptCreate, Dict[str, Any]]):
    """CRUD operations for ExerciseAttempt model."""

    def get_by_user_and_exercise(self, db: Session, *, user_id: int, exercise_id: int) -> List[ExerciseAttempt]:
        """Get all attempts for a specific user and exercise."""
        return db.query(self.model).filter(
            ExerciseAttempt.user_id == user_id, 
            ExerciseAttempt.exercise_id == exercise_id
        ).order_by(ExerciseAttempt.created_at.desc()).all()

    def get_last_attempt(self, db: Session, *, user_id: int, exercise_id: int) -> Optional[ExerciseAttempt]:
        """Get the last attempt for a specific user and exercise."""
        return db.query(self.model).filter(
            ExerciseAttempt.user_id == user_id, 
            ExerciseAttempt.exercise_id == exercise_id
        ).order_by(ExerciseAttempt.created_at.desc()).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        exercise_id: Optional[int] = None,
    ) -> List[ExerciseAttempt]:
        """List attempts with optional filters by user and exercise."""
        q = db.query(self.model)
        if user_id is not None:
            q = q.filter(ExerciseAttempt.user_id == user_id)
        if exercise_id is not None:
            q = q.filter(ExerciseAttempt.exercise_id == exercise_id)
        try:
            q = q.order_by(ExerciseAttempt.created_at.desc())
        except Exception:
            # created_at may not exist in some schemas; ignore ordering
            pass
        return q.offset(skip).limit(limit).all()


class CRUDExerciseSet(CRUDBase[ExerciseSet, ExerciseSetCreate, ExerciseSetUpdate]):
    """CRUD operations for ExerciseSet model."""
    
    def create_with_exercises(
        self, 
        db: Session, 
        *, 
        obj_in: ExerciseSetCreate,
        exercise_ids: List[int]
    ) -> ExerciseSet:
        """Create an exercise set with exercises."""
        db_obj = ExerciseSet(
            title=obj_in.title,
            description=obj_in.description,
            exercise_type=obj_in.exercise_type,
            difficulty=obj_in.difficulty,
            is_active=obj_in.is_active,
            metadata=obj_in.metadata
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Add exercises to the set
        for i, ex_id in enumerate(exercise_ids):
            item = ExerciseSetItem(
                exercise_set_id=db_obj.id,
                exercise_id=ex_id,
                order=i
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_exercises(
        self, 
        db: Session, 
        *, 
        set_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Exercise]:
        """Get exercises in a set."""
        return (
            db.query(Exercise)
            .join(ExerciseSetItem, Exercise.id == ExerciseSetItem.exercise_id)
            .filter(ExerciseSetItem.exercise_set_id == set_id)
            .order_by(ExerciseSetItem.order)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def add_exercises(
        self,
        db: Session,
        *,
        set_id: int,
        exercise_ids: List[int],
        start_order: Optional[int] = None
    ) -> List[ExerciseSetItem]:
        """Add exercises to a set."""
        # Get current max order if start_order not provided
        if start_order is None:
            last_item = (
                db.query(ExerciseSetItem)
                .filter(ExerciseSetItem.exercise_set_id == set_id)
                .order_by(ExerciseSetItem.order.desc())
                .first()
            )
            start_order = last_item.order + 1 if last_item else 0
        
        # Add new items
        items = []
        for i, ex_id in enumerate(exercise_ids):
            item = ExerciseSetItem(
                exercise_set_id=set_id,
                exercise_id=ex_id,
                order=start_order + i
            )
            db.add(item)
            items.append(item)
        
        db.commit()
        return items
    
    def remove_exercises(
        self,
        db: Session,
        *,
        set_id: int,
        exercise_ids: List[int]
    ) -> int:
        """Remove exercises from a set."""
        result = (
            db.query(ExerciseSetItem)
            .filter(
                ExerciseSetItem.exercise_set_id == set_id,
                ExerciseSetItem.exercise_id.in_(exercise_ids)
            )
            .delete(synchronize_session=False)
        )
        db.commit()
        return result

class CRUDTestSession(CRUDBase[TestSession, TestSessionCreate, TestSessionUpdate]):
    """CRUD operations for TestSession model."""
    
    def create_with_exercise_set(
        self,
        db: Session,
        *, 
        obj_in: TestSessionCreate,
        user_id: int
    ) -> TestSession:
        """Create a test session with an exercise set."""
        db_obj = TestSession(
            user_id=user_id,
            test_type=obj_in.test_type,
            time_limit=obj_in.time_limit,
            metadata=obj_in.metadata
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # If an exercise set is provided, add its exercises to the test
        if hasattr(obj_in, 'exercise_set_id') and obj_in.exercise_set_id:
            exercises = db.query(ExerciseSetItem).filter(
                ExerciseSetItem.exercise_set_id == obj_in.exercise_set_id
            ).all()
            
            for item in exercises:
                response = TestResponse(
                    test_session_id=db_obj.id,
                    exercise_id=item.exercise_id
                )
                db.add(response)
            
            db.commit()
            db.refresh(db_obj)
        
        return db_obj
    
    def submit_response(
        self,
        db: Session,
        *,
        test_session_id: int,
        response_in: TestResponseCreate,
        user_id: int
    ) -> TestResponse:
        """Submit a response for a test question."""
        # Verify the test session exists and belongs to the user
        test_session = db.query(TestSession).filter(
            TestSession.id == test_session_id,
            TestSession.user_id == user_id
        ).first()
        
        if not test_session:
            raise ValueError("Test session not found or access denied")
        
        # Check if the test is still in progress
        if test_session.status != "in_progress":
            raise ValueError("Cannot submit response to a completed or abandoned test")
        
        # Get or create the test response
        response = db.query(TestResponse).filter(
            TestResponse.test_session_id == test_session_id,
            TestResponse.exercise_id == response_in.exercise_id
        ).first()
        
        if response:
            # Update existing response
            response.user_answer = response_in.user_answer
            response.time_spent = response_in.time_spent
        else:
            # Create new response
            response = TestResponse(
                test_session_id=test_session_id,
                exercise_id=response_in.exercise_id,
                user_answer=response_in.user_answer,
                time_spent=response_in.time_spent
            )
        
        db.add(response)
        db.commit()
        db.refresh(response)
        return response
    
    def grade_test(self, db: Session, *, test_session_id: int) -> TestSession:
        """Grade a completed test session."""
        test_session = db.query(TestSession).get(test_session_id)
        if not test_session:
            raise ValueError("Test session not found")
        
        # Only grade if not already graded
        if test_session.status != "in_progress":
            return test_session
        
        # Get all responses for this test
        responses = db.query(TestResponse).filter(
            TestResponse.test_session_id == test_session_id
        ).all()
        
        if not responses:
            # No responses to grade
            test_session.status = "completed"
            test_session.total_score = 0.0
            db.add(test_session)
            db.commit()
            db.refresh(test_session)
            return test_session
        
        # Grade each response
        total_score = 0.0
        max_score = len(responses)
        
        for response in responses:
            # Get the exercise
            exercise = db.query(Exercise).get(response.exercise_id)
            if not exercise:
                continue
            
            # Check the answer
            result = CRUDExercise(Exercise).check_answer(
                db,
                exercise_id=exercise.id,
                user_answer=response.user_answer
            )
            
            # Update the response
            response.is_correct = result["is_correct"]
            response.score = result["score"]
            response.feedback = result["feedback"]
            
            # Add to total score
            total_score += response.score
            
            db.add(response)
        
        # Calculate final score (0-100)
        final_score = (total_score / max_score) * 100 if max_score > 0 else 0
        
        # Update test session
        test_session.status = "completed"
        test_session.total_score = final_score
        test_session.end_time = func.now()
        
        db.add(test_session)
        db.commit()
        db.refresh(test_session)
        
        return test_session

# Initialize CRUD objects
exercise = CRUDExercise(Exercise)
exercise_attempt = CRUDExerciseAttempt(ExerciseAttempt)
exercise_set = CRUDBase[ExerciseSet, ExerciseSetCreate, ExerciseSetUpdate](ExerciseSet)
exercise_set_item = CRUDBase[ExerciseSetItem, Any, Any](ExerciseSetItem)
test_session = CRUDBase[TestSession, TestSessionCreate, TestSessionUpdate](TestSession)
test_response = CRUDBase[TestResponse, TestResponseCreate, TestResponseUpdate](
    TestResponse
)
user_progress = CRUDBase[UserProgress, Any, UserProgressUpdate](UserProgress)
pronunciation_attempt = CRUDPronunciationAttempt(PronunciationAttempt)

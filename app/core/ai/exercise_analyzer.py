"""
Test va mashq javoblarini tahlil qilish va fikr-mulohaza berish uchun AI xizmati.
"""
from typing import Dict, Any, List, Optional
import json
from enum import Enum
from datetime import datetime

from app.core.ai.gemini_service import gemini_service
from app.models.exercise import Exercise, ExerciseAttempt, ExerciseType
from app.models.user import User

class FeedbackType(str, Enum):
    """Fikr-mulohaza turlari."""
    CORRECT = "correct"
    PARTIALLY_CORRECT = "partially_correct"
    INCORRECT = "incorrect"
    NEEDS_IMPROVEMENT = "needs_improvement"
    EXCELLENT = "excellent"

class ExerciseAnalyzer:
    """Mashq va test javoblarini tahlil qilish uchun asosiy xizmat."""
    
    def __init__(self):
        self.gemini = gemini_service
    
    async def analyze_exercise_attempt(
        self, 
        exercise: Exercise, 
        user_answer: Any, 
        user: User,
        attempt: Optional[ExerciseAttempt] = None
    ) -> Dict[str, Any]:
        """Mashq yoki test javobini tahlil qilish.
        
        Args:
            exercise: Mashq yoki test
            user_answer: Foydalanuvchi javobi
            user: Foydalanuvchi
            attempt: Oldingi urinishlar (agar mavjud bo'lsa)
            
        Returns:
            Dict: Tahlil natijalari
        """
        # Asosiy ma'lumotlarni yig'amiz
        context = self._prepare_analysis_context(exercise, user_answer, user, attempt)
        
        # AI yordamida tahlil qilish
        analysis = await self._get_ai_analysis(context)
        
        # Natijalarni qayta ishlash
        result = self._process_analysis_results(analysis, context)
        
        # Foydalanuvchi progressini yangilash
        await self._update_user_progress(user, exercise, result)
        
        return result
    
    def _prepare_analysis_context(
        self, 
        exercise: Exercise, 
        user_answer: Any,
        user: User,
        attempt: Optional[ExerciseAttempt]
    ) -> Dict[str, Any]:
        """Tahlil uchun kontekst tayyorlash."""
        return {
            "exercise": {
                "id": exercise.id,
                "question": exercise.question,
                "type": exercise.exercise_type,
                "difficulty": exercise.difficulty,
                "correct_answer": exercise.correct_answer,
                "explanation": exercise.explanation,
                "options": exercise.options,
                "tags": exercise.tags or []
            },
            "user_answer": user_answer,
            "user": {
                "id": user.id,
                "level": user.get_current_level().value,
                "previous_attempts": [
                    {
                        "is_correct": a.is_correct,
                        "score": a.score,
                        "created_at": a.created_at.isoformat()
                    }
                    for a in (attempt.exercise.attempts if attempt and attempt.exercise else [])[:5]
                ] if attempt and attempt.exercise else []
            }
        }
    
    async def _get_ai_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """AI yordamida tahlil qilish."""
        prompt = self._create_analysis_prompt(context)
        
        try:
            response = await self.gemini.generate_text(
                prompt=prompt,
                temperature=0.3,
                max_output_tokens=1024
            )
            
            # JSON javobini o'qish
            return json.loads(response)
        except Exception as e:
            # Xatolik yuz berganda standart javob qaytarish
            return self._get_default_analysis(context)
    
    def _create_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """AI uchun prompt yaratish."""
        exercise = context["exercise"]
        
        prompt = f"""
        Siz tajribali til o'qituvchisiz. Quyidagi mashq javobini tahlil qiling:
        
        SAVOL: {exercise['question']}
        TO'G'RI JAVOB: {exercise['correct_answer']}
        O'QUVCHI JAVOBI: {context['user_answer']}
        
        Quyidagi formatda JSON javob qaytaring:
        {{
            "is_correct": boolean,
            "score": 0-100 oraliqidagi ball,
            "feedback": "Tushunarli va qisqa fikr-mulohaza",
            "feedback_type": "correct" | "partially_correct" | "incorrect" | "needs_improvement" | "excellent",
            "suggestions": ["Tavsiyalar ro'yxati"],
            "grammar_analysis": [{"issue": "grammatik xato", "correction": "tuzatilgan varianti"}],
            "vocabulary_analysis": [{"word": "noto'g'ri so'z", "suggestion": "tavsiya"}],
            "pronunciation_tips": "Talaffuz bo'yicha maslahatlar"
        }}
        """
        
        return prompt
    
    def _process_analysis_results(
        self, 
        analysis: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """AI tahlil natijalarini qayta ishlash."""
        # Asosiy natijalarni qaytarish
        return {
            "exercise_id": context["exercise"]["id"],
            "user_id": context["user"]["id"],
            "is_correct": analysis.get("is_correct", False),
            "score": analysis.get("score", 0),
            "feedback": analysis.get("feedback", ""),
            "feedback_type": analysis.get("feedback_type", FeedbackType.INCORRECT),
            "suggestions": analysis.get("suggestions", []),
            "grammar_issues": analysis.get("grammar_analysis", []),
            "vocabulary_issues": analysis.get("vocabulary_analysis", []),
            "pronunciation_tips": analysis.get("pronunciation_tips", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _update_user_progress(
        self, 
        user: User, 
        exercise: Exercise, 
        result: Dict[str, Any]
    ) -> None:
        """Foydalanuvchi progressini yangilash."""
        # Progress yangilash uchun kerakli ma'lumotlarni olish
        score = result["score"]
        is_correct = result["is_correct"]
        
        # Progress yangilash uchun o'zgaruvchilar
        updates = {
            "total_exercises_completed": 1
        }
        
        # Ballarni yangilash
        if exercise.exercise_type in ["listening", "reading"]:
            updates["listening_score"] = score
        elif exercise.exercise_type in ["speaking", "pronunciation"]:
            updates["speaking_score"] = score
        elif exercise.exercise_type in ["grammar", "vocabulary"]:
            updates["grammar_score"] = score
            updates["vocabulary_score"] = score
        
        # Foydalanuvchi progressini yangilash
        user.update_progress(**updates)
    
    def _get_default_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Standart tahlil natijasini qaytarish."""
        is_correct = str(context["user_answer"]).lower().strip() == str(context["exercise"]["correct_answer"]).lower().strip()
        
        return {
            "is_correct": is_correct,
            "score": 100 if is_correct else 0,
            "feedback": "Javobingiz qabul qilindi." if is_correct else "Javobingiz noto'g'ri.",
            "feedback_type": FeedbackType.CORRECT if is_correct else FeedbackType.INCORRECT,
            "suggestions": [],
            "grammar_analysis": [],
            "vocabulary_analysis": [],
            "pronunciation_tips": ""
        }

# Standart foydalanish uchun instance
exercise_analyzer = ExerciseAnalyzer()

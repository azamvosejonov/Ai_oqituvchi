"""
Foydalanuvchilar uchun shaxsiylashtirilgan tavsiyalar tizimi.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

from sqlalchemy.orm import Session

from app import models
from app.models import User, Exercise, UserProgress, UserLessonProgress
from app.models.user_level import UserLevel
from app.models.lesson import LessonDifficulty
from app.core.ai.exercise_analyzer import exercise_analyzer


class RecommendationService:
    """Foydalanuvchilar uchun shaxsiylashtirilgan tavsiyalar tizimi."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_personalized_recommendations(
        self, 
        user: User,
        limit: int = 5,
        content_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Foydalanuvchi uchun shaxsiylashtirilgan tavsiyalar ro'yxatini olish.
        
        Args:
            user: Foydalanuvchi obyekti
            limit: Tavsiyalar soni
            content_types: Qaytariladigan kontent turlari (masalan, ['exercises', 'lessons'])
            
        Returns:
            Dict: Tavsiyalar ro'yxati
        """
        if content_types is None:
            content_types = ['exercises', 'lessons']
        
        recommendations = {}
        
        # Foydalanuvchi progressi va darajasini olish (fallback: BEGINNER)
        try:
            user_level: UserLevel = (
                user.progress.level if getattr(user, "progress", None) and user.progress.level else UserLevel.BEGINNER
            )
        except Exception:
            user_level = UserLevel.BEGINNER
        
        # Har bir kontent turi uchun tavsiyalar
        if 'exercises' in content_types:
            exercises = await self._recommend_exercises(user, limit, user_level)
            recommendations['exercises'] = exercises
        
        if 'lessons' in content_types:
            lessons = await self._recommend_lessons(user, limit, user_level)
            recommendations['lessons'] = lessons
        
        return recommendations
    
    async def _recommend_exercises(
        self, 
        user: User, 
        limit: int,
        user_level: UserLevel
    ) -> List[Dict[str, Any]]:
        """Foydalanuvchi uchun mos mashqlarni tavsiya qilish."""
        # 1. Foydalanuvchi progressini olish
        progress = getattr(user, "progress", None)
        
        # 2. Zaif tomonlarni aniqlash (unused for filtering to avoid JSON operators issues)
        weak_areas = self._identify_weak_areas(progress)
        
        # 3. Tavsiya qilinadigan mashqlarni topish
        exercises = []
        
        # Faqat darajaga mos mashqlarni olamiz (JSON tags bo'yicha filter qo'llamaymiz)
        if len(exercises) < limit:
            additional = self.db.query(Exercise).filter(
                Exercise.difficulty == user_level.value,
                Exercise.is_active == True
            ).limit(limit - len(exercises)).all()
            exercises.extend(additional)
        
        # Tasodifiy tartiblash
        random.shuffle(exercises)
        
        return exercises[:limit]
    
    async def _recommend_lessons(
        self, 
        user: User, 
        limit: int,
        user_level: UserLevel
    ) -> List[Dict[str, Any]]:
        """Foydalanuvchi uchun mos darslarni tavsiya qilish."""
        # 1. Foydalanuvchi progressini olish
        # O'tilgan darslar ro'yxatini olish
        completed_lesson_ids = self.db.query(models.UserLessonProgress.lesson_id).filter(
            models.UserLessonProgress.user_id == user.id,
            models.UserLessonProgress.is_completed == True
        ).all()
        completed_lesson_ids = [item[0] for item in completed_lesson_ids]

        # 2. Zaif tomonlarni aniqlash (unused for filtering to avoid JSON operators issues)
        progress = user.progress
        weak_areas = self._identify_weak_areas(progress)
        
        # 3. Tavsiya qilinadigan darslarni topish
        lessons = []
        
        # UserLevel -> LessonDifficulty mapping
        def map_level_to_lesson_difficulty(level: UserLevel) -> LessonDifficulty:
            mapping = {
                UserLevel.BEGINNER: LessonDifficulty.EASY,
                UserLevel.ELEMENTARY: LessonDifficulty.EASY,
                UserLevel.PRE_INTERMEDIATE: LessonDifficulty.MEDIUM,
                UserLevel.INTERMEDIATE: LessonDifficulty.MEDIUM,
                UserLevel.UPPER_INTERMEDIATE: LessonDifficulty.HARD,
                UserLevel.ADVANCED: LessonDifficulty.EXPERT,
                UserLevel.PROFICIENT: LessonDifficulty.EXPERT,
            }
            return mapping.get(level, LessonDifficulty.MEDIUM)

        target_diff = map_level_to_lesson_difficulty(user_level)

        # Faqat darajaga mos va hali tugallanmagan darslarni olish (tags bo'yicha filter yo'q)
        if len(lessons) < limit:
            additional = self.db.query(models.InteractiveLesson).filter(
                models.InteractiveLesson.difficulty == target_diff,
                models.InteractiveLesson.is_active == True,
                ~models.InteractiveLesson.id.in_(completed_lesson_ids)
            ).limit(limit - len(lessons)).all()
            lessons.extend(additional)
        
        # Tasodifiy tartiblash
        random.shuffle(lessons)
        
        return lessons[:limit]
    
    def _identify_weak_areas(self, progress: UserProgress) -> List[str]:
        """Foydalanuvchining zaif tomonlarini aniqlash."""
        if not progress:
            return ['vocabulary', 'grammar']  # Boshlang'ich qiymatlar
        
        # Ballarni solishtirish
        areas = [
            ('vocabulary', progress.vocabulary_score or 0),
            ('grammar', progress.grammar_score or 0),
            ('speaking', progress.speaking_score or 0),
            ('listening', progress.listening_score or 0)
        ]
        
        # Eng past balli sohalar bo'yicha tartiblash
        areas_sorted = sorted(areas, key=lambda x: x[1])
        
        # Faqat sohalar nomlarini qaytarish
        return [area[0] for area in areas_sorted]
    
    async def get_adaptive_lesson_plan(
        self, 
        user: User, 
        lesson_id: int
    ) -> Dict[str, Any]:
        """Foydalanuvchi uchun moslashtirilgan dars rejasini yaratish."""
        # Dars ma'lumotlarini olish
        lesson = self.db.query(models.InteractiveLesson).get(lesson_id)
        if not lesson:
            return {"error": "Dars topilmadi"}
        
        # Foydalanuvchi progressini olish
        progress = user.progress
        
        # Dars rejasini yaratish
        plan = {
            "lesson_id": lesson.id,
            "title": lesson.title,
            "description": lesson.description,
            "difficulty": getattr(lesson.difficulty, "value", str(lesson.difficulty)),
            "sections": [],  # Sections model mavjud emas, soddalashtiramiz
            "estimated_duration": lesson.estimated_duration or 0,
            "recommended_study_plan": [],
            # Response model (schemas.AdaptiveLessonPlan) talabiga muvofiq:
            # kamida bo'sh ro'yxat sifatida 'steps' ni qaytaramiz
            "steps": []
        }
        
        # O'quv rejasini yaratish
        plan["recommended_study_plan"] = self._create_study_plan(plan["sections"])  # hozircha bo'sh
        # Agar sections bo'sh bo'lsa, estimated_duration ni mavjud qiymatdan foydalanamiz
        
        return plan
    
    def _adapt_exercise(
        self, 
        exercise: Exercise, 
        user_level: UserLevel,
        progress: UserProgress
    ) -> Dict[str, Any]:
        """Mashqni foydalanuvchi darajasiga moslashtirish."""
        # Asosiy ma'lumotlar
        exercise_data = {
            "id": exercise.id,
            "question": exercise.question,
            "type": exercise.exercise_type,
            "difficulty": exercise.difficulty,
            "options": exercise.options,
            "hints": []
        }
        
        # Foydalanuvchi darajasi va progressiga qo'shimcha yordam qo'shish
        if progress and progress.vocabulary_score < 50:
            exercise_data["hints"].append("Murakkab so'zlar uchun lug'at yordami")
        
        if progress and progress.grammar_score < 50:
            exercise_data["hints"].append("Grammatik qoidalar yordami")
        
        # Agar mashq murakkab bo'lsa, qo'shimcha yordam
        if exercise.difficulty in ["intermediate", "upper_intermediate"]:
            exercise_data["hints"].append("Namuna javoblar")
        
        return exercise_data
    
    def _create_study_plan(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """O'quv rejasini yaratish."""
        plan = []
        day = 1
        
        for i, section in enumerate(sections, 1):
            plan.append({
                "day": day,
                "sections": [section["id"]],
                "activities": [
                    f"{section['title']} bo'limini o'rganish",
                    f"{len(section.get('exercises', []))} ta mashq bajarish"
                ],
                "estimated_time": 30  # daqiqa
            })
            
            # Har kuni 2 ta bo'limni taklif qilamiz
            if i % 2 == 0:
                day += 1
        
        return plan

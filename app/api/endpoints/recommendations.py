"""
Foydalanuvchilar uchun shaxsiylashtirilgan tavsiyalar endpointlari.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app import schemas, models, crud
from app.api import deps
from app.core.ai.recommendation_service import RecommendationService
from app.db.session import get_db
from app.models.user import User
from app.models.user_level import UserLevel
from app.schemas.recommendation import ForYouRecommendations
from app.models.lesson import LessonDifficulty

router = APIRouter()

@router.get("/next-lessons", response_model=List[schemas.Lesson])
async def get_next_lessons(
    limit: int = Query(5, description="Qaytariladigan darslar soni", ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user_with_free_window),
):
    """Foydalanuvchi uchun keyingi darslar (darajaga mos + premium gating)."""

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

    level = current_user.get_current_level() or UserLevel.BEGINNER
    target_diff = map_level_to_lesson_difficulty(level)

    # Asosiy ro'yxat: darajaga mos, active
    base_q = db.query(models.InteractiveLesson).filter(
        models.InteractiveLesson.difficulty == target_diff,
        models.InteractiveLesson.is_active == True,
    ).order_by(models.InteractiveLesson.id.asc())

    candidates = base_q.limit(max(limit * 3, limit)).all()

    # Premium gating: premium bo'lmasa premium darslarni chiqarma
    is_premium = crud.user.is_premium(current_user) or crud.user.is_superuser(current_user)
    filtered = [l for l in candidates if (not getattr(l, "is_premium", False)) or is_premium]

    # Agar yetarli bo'lmasa, boshqa active darslardan to'ldiramiz
    if len(filtered) < limit:
        extra_q = db.query(models.InteractiveLesson).filter(
            models.InteractiveLesson.is_active == True,
        ).order_by(models.InteractiveLesson.id.asc()).limit(limit * 3)
        extra = extra_q.all()
        extra = [l for l in extra if l.id not in {x.id for x in filtered}]
        extra = [l for l in extra if (not getattr(l, "is_premium", False)) or is_premium]
        filtered.extend(extra)

    return filtered[:limit]

@router.get("/personalized", response_model=schemas.PersonalizedRecommendations)
async def get_personalized_recommendations(
    content_types: Optional[List[str]] = Query(
        None, 
        description="Qaytariladigan kontent turlari (masalan, exercises, lessons)"
    ),
    limit: int = Query(5, description="Har bir turdagi tavsiyalar soni", ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Foydalanuvchi uchun shaxsiylashtirilgan tavsiyalar ro'yxatini olish."""
    try:
        service = RecommendationService(db)
        recommendations = await service.get_personalized_recommendations(
            user=current_user,
            limit=limit,
            content_types=content_types
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tavsiyalar yuklanmadi: {str(e)}"
        )

@router.get("/adaptive-lesson-plan/{lesson_id}", response_model=schemas.AdaptiveLessonPlan)
async def get_adaptive_lesson_plan(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Foydalanuvchi uchun moslashtirilgan dars rejasini olish."""
    try:
        service = RecommendationService(db)
        plan = await service.get_adaptive_lesson_plan(
            user=current_user,
            lesson_id=lesson_id
        )
        
        if "error" in plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=plan["error"]
            )
            
        return plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dars rejasi yuklanmadi: {str(e)}"
        )

@router.get("/for-you", response_model=ForYouRecommendations)
async def get_for_you_recommendations(
    limit: int = Query(5, description="Har bir turdagi tavsiyalar soni", ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Foydalanuvchi uchun "Siz uchun" bo'limidagi tavsiyalar."""
    try:
        service = RecommendationService(db)
        
        # Eng so'ngi dars progresslarini olish (UserLessonProgress)
        recent_lesson_progress = db.query(models.UserLessonProgress).filter(
            models.UserLessonProgress.user_id == current_user.id
        ).order_by(
            models.UserLessonProgress.last_accessed.desc()
        ).first()

        # Foydalanuvchi darajasini olish (fallback BEGINNER)
        user_level = current_user.get_current_level() or UserLevel.BEGINNER
        
        # Tavsiyalarni yig'ish
        recommendations = {
            "continue_learning": [],
            "based_on_level": [],
            "popular": [],
            "new": []
        }
        
        # Davom etish uchun darslar
        if recent_lesson_progress and recent_lesson_progress.lesson_id:
            lesson = db.query(models.InteractiveLesson).get(recent_lesson_progress.lesson_id)
            if lesson:
                recommendations["continue_learning"] = [lesson]
        
        # Darajaga mos darslar (UserLevel -> LessonDifficulty mapping)
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

        level_lessons = db.query(models.InteractiveLesson).filter(
            models.InteractiveLesson.difficulty == target_diff,
            models.InteractiveLesson.is_active == True
        ).limit(limit).all()
        
        recommendations["based_on_level"] = level_lessons
        
        # Mashhur darslar
        # Hozircha "popular" uchun faqat active bo'lgan darslar ichidan tanlaymiz
        popular_lessons = db.query(models.InteractiveLesson).filter(
            models.InteractiveLesson.is_active == True
        ).limit(limit).all()
        
        recommendations["popular"] = popular_lessons
        
        # Yangi darslar
        # created_at yo'qligi sababli order maydonidan yoki id bo'yicha qaytamiz
        new_lessons = db.query(models.InteractiveLesson).filter(
            models.InteractiveLesson.is_active == True
        ).order_by(
            models.InteractiveLesson.id.desc()
        ).limit(limit).all()
        
        recommendations["new"] = new_lessons
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tavsiyalar yuklanmadi: {str(e)}"
        )

from sqlalchemy.orm import Session

from app.models.lesson import InteractiveLesson
from app.models.ai_avatar import AIAvatar


def create_test_lesson(db: Session, course_id: int, **kwargs):
    """Create a test interactive lesson using ORM model."""
    # Ensure we have an avatar to satisfy NOT NULL avatar_id
    avatar = db.query(AIAvatar).first()
    if avatar is None:
        avatar = AIAvatar(
            name="Test Avatar",
            description="Avatar for tests",
            tts_voice="en"
        )
        db.add(avatar)
        db.commit()
        db.refresh(avatar)

    lesson_data = {
        "title": "Test Lesson",
        "content": {"text": "This is a test lesson content."},  # JSON field
        "course_id": course_id,
        "order": 1,
        "is_premium": False,
        "video_url": "https://example.com/video1",
        "avatar_id": avatar.id,
        **kwargs,
    }

    lesson = InteractiveLesson(**lesson_data)
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


def create_random_lesson(db: Session, course_id: int, **kwargs):
    """Backward-compatible alias expected by some tests."""
    return create_test_lesson(db, course_id=course_id, **kwargs)

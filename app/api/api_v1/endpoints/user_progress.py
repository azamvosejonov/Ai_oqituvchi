from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.models.user_lesson_progress import UserLessonProgress

router = APIRouter()


@router.get("/", response_model=List[schemas.UserLessonCompletion])
def read_user_progress(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all completed lessons for the current user.
    """
    completions = crud.user_lesson_completion.get_by_user(db, user_id=current_user.id)
    return completions


@router.post("/lessons/{lesson_id}/complete", response_model=schemas.UserLessonCompletion)
def mark_lesson_as_complete(
    *,
    db: Session = Depends(deps.get_db),
    lesson_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Mark a lesson as complete for the current user.
    If the lesson completes a course, a certificate is generated.
    """
    lesson = crud.lesson.get(db=db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Check if the completion record already exists
    completion = crud.user_lesson_completion.get_by_user_and_lesson(db, user_id=current_user.id, lesson_id=lesson_id)

    if completion:
        # If already complete, no need to do anything else
        return completion

    # Create a new completion record
    completion_in = schemas.UserLessonCompletionCreate(user_id=current_user.id, lesson_id=lesson_id)
    new_completion = crud.user_lesson_completion.create(db=db, obj_in=completion_in)

    # Check if this lesson completes a course
    if lesson.course_id:
        # We need to commit the new completion first so the is_course_completed check can see it
        db.commit()
        db.refresh(new_completion)

        if crud.course.is_course_completed(db, user_id=current_user.id, course_id=lesson.course_id):
            # Check if a certificate for this course already exists
            existing_certificate = crud.certificate.get_by_user_and_course(db, user_id=current_user.id, course_id=lesson.course_id)
            if not existing_certificate:
                # Generate certificate
                course = crud.course.get(db, id=lesson.course_id)
                if course:
                    new_cert = crud.certificate.create_with_pdf(
                        db,
                        user=current_user,
                        course_name=course.title,
                        level_completed=course.level, # Pass the course level
                        course_id=course.id # Pass the course_id
                    )
                    # Create a notification for the user
                    if new_cert:
                        notification_message = f"Tabriklaymiz! Siz '{course.title}' kursini muvaffaqiyatli tamomlab, yangi sertifikat qo'lga kiritdingiz."
                        crud.notification.create_for_user(
                            db,
                            obj_in=schemas.NotificationCreate(
                                user_id=current_user.id,
                                message=notification_message,
                                notification_type='certificate'
                            )
                        )

    return new_completion


@router.get("/last", response_model=schemas.Lesson)
def get_last_lesson(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
):
    """Return the user's last viewed lesson or a sensible fallback."""
    last_id = getattr(current_user, "last_viewed_lesson_id", None)
    if last_id:
        lesson = crud.lesson.get(db=db, id=last_id)
        if lesson:
            return lesson
    # Fallback: first available lesson
    lessons = crud.lesson.get_multi(db, skip=0, limit=1)
    if lessons:
        return lessons[0]
    raise HTTPException(status_code=404, detail="No lessons available")


@router.post("/lessons/{lesson_id}/start")
def start_lesson(
    *,
    db: Session = Depends(deps.get_db),
    lesson_id: int,
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
):
    """Mark a lesson as started (analytics) and set it as last viewed."""
    lesson = crud.lesson.get(db=db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Update last viewed lesson id
    crud.user.update(db, db_obj=current_user, obj_in={"last_viewed_lesson_id": lesson_id})

    # Upsert progress row
    progress = (
        db.query(UserLessonProgress)
        .filter(UserLessonProgress.user_id == current_user.id, UserLessonProgress.lesson_id == lesson_id)
        .first()
    )
    if not progress:
        progress = UserLessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            is_completed=False,
        )
        db.add(progress)
    # Touch last_accessed via SQLAlchemy default/onupdate by setting any field
    progress.time_spent = progress.time_spent or 0
    db.commit()
    db.refresh(progress)

    return {"status": "started", "lesson_id": lesson_id}

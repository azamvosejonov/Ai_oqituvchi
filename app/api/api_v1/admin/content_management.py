from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, crud
from app.api import deps
from app.services import file_uploader

router = APIRouter()

@router.post("/lessons/{lesson_id}/upload-video", response_model=schemas.InteractiveLesson)
def upload_lesson_video(
    *, 
    db: Session = Depends(deps.get_db),
    lesson_id: int,
    video_file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Upload a video for a specific interactive lesson.
    """
    lesson = crud.interactive_lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found.",
        )

    # Handle the file upload and get the relative path
    file_path = file_uploader.handle_file_upload(upload_file=video_file, sub_folder="videos")

    # Update the lesson with the new video URL
    lesson_update_data = schemas.InteractiveLessonUpdate(video_url=str(file_path))
    updated_lesson = crud.interactive_lesson.update(db, db_obj=lesson, obj_in=lesson_update_data)

    return updated_lesson

@router.post("/exercises/{exercise_id}/upload-audio", response_model=schemas.Exercise)
def upload_exercise_audio(
    *,
    db: Session = Depends(deps.get_db),
    exercise_id: int,
    audio_file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Upload an audio file for a specific exercise.
    """
    exercise = crud.exercise.get(db, id=exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found.",
        )

    # Handle the file upload and get the relative path
    file_path = file_uploader.handle_file_upload(upload_file=audio_file, sub_folder="audios")

    # Update the exercise with the new audio URL
    exercise_update_data = schemas.ExerciseUpdate(audio_url=str(file_path))
    updated_exercise = crud.exercise.update(db, db_obj=exercise, obj_in=exercise_update_data)

    return updated_exercise

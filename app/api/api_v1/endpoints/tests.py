from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()
admin_router = APIRouter()

# Placeholder endpoints for IELTS/TOEFL sections (premium features)
@router.get("/ielts")
def get_ielts_overview() -> Any:
    """Return a placeholder IELTS overview (200 OK)."""
    return {"sections": [], "message": "IELTS module coming soon"}

@router.get("/toefl")
def get_toefl_overview() -> Any:
    """Return a placeholder TOEFL overview (200 OK)."""
    return {"sections": [], "message": "TOEFL module coming soon"}

# ------------------ ADMIN ENDPOINTS ------------------

@admin_router.post("/", response_model=schemas.TestInDB)
def create_test(
    *, 
    db: Session = Depends(deps.get_db),
    test_in: schemas.TestCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Create new test. Superusers only."""
    test = crud.test.create(db, obj_in=test_in)
    return test

@admin_router.put("/{test_id}", response_model=schemas.TestInDB)
def update_test(
    *,
    db: Session = Depends(deps.get_db),
    test_id: int,
    test_in: schemas.TestUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Update a test. Superusers only."""
    test = crud.test.get(db, id=test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    test = crud.test.update(db, db_obj=test, obj_in=test_in)
    return test

@admin_router.post("/{test_id}/sections/", response_model=schemas.TestSectionInDB)
def create_test_section(
    *,
    db: Session = Depends(deps.get_db),
    test_id: int,
    section_in: schemas.TestSectionCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Create a new section for a test. Superusers only."""
    test = crud.test.get(db, id=test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    section = crud.test_section.create(db, obj_in=section_in)
    return section

@admin_router.put("/sections/{section_id}", response_model=schemas.TestSectionInDB)
def update_test_section(
    *,
    db: Session = Depends(deps.get_db),
    section_id: int,
    section_in: schemas.TestSectionUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Update a test section. Superusers only."""
    section = crud.test_section.get(db, id=section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    section = crud.test_section.update(db, db_obj=section, obj_in=section_in)
    return section

@admin_router.delete("/sections/{section_id}")
def delete_test_section(
    *,
    db: Session = Depends(deps.get_db),
    section_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Delete a test section. Superusers only."""
    section = crud.test_section.get(db, id=section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    crud.test_section.delete(db, id=section_id)
    return {"msg": "Section deleted successfully"}

@admin_router.post("/sections/{section_id}/questions/", response_model=schemas.TestQuestionInDB)
def create_test_question(
    *,
    db: Session = Depends(deps.get_db),
    section_id: int,
    question_in: schemas.TestQuestionCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Create a new question for a section. Superusers only."""
    section = crud.test_section.get(db, id=section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    question = crud.test_question.create(db, obj_in=question_in)
    return question

@admin_router.put("/questions/{question_id}", response_model=schemas.TestQuestionInDB)
def update_test_question(
    *,
    db: Session = Depends(deps.get_db),
    question_id: int,
    question_in: schemas.TestQuestionUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Update a test question. Superusers only."""
    question = crud.test_question.get(db, id=question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    question = crud.test_question.update(db, db_obj=question, obj_in=question_in)
    return question

@admin_router.delete("/questions/{question_id}")
def delete_test_question(
    *,
    db: Session = Depends(deps.get_db),
    question_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Delete a test question. Superusers only."""
    question = crud.test_question.get(db, id=question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    crud.test_question.delete(db, id=question_id)
    return {"msg": "Question deleted successfully"}

# ------------------ USER ENDPOINTS ------------------

@router.get("/", response_model=List[schemas.TestInDB])
def read_tests(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Retrieve all available tests."""
    tests = crud.test.get_multi(db, skip=skip, limit=limit)
    return tests

@router.get("/{test_id}", response_model=schemas.TestInDB)
def read_test(
    *,
    db: Session = Depends(deps.get_db),
    test_id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Get a specific test by ID, with all its sections and questions."""
    test = crud.test.get(db, id=test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

@router.post("/{test_id}/start", response_model=schemas.TestAttemptInDB)
def start_test_attempt(
    *,
    db: Session = Depends(deps.get_db),
    test_id: int,
    current_user: models.User = Depends(deps.get_current_active_premium_user)
) -> Any:
    """Start a new test attempt for the current user. Premium users only."""
    test = crud.test.get(db, id=test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    existing_attempt = crud.test_attempt.get_in_progress_by_user_and_test(db, user_id=current_user.id, test_id=test_id)
    if existing_attempt:
        raise HTTPException(status_code=400, detail="You already have an in-progress attempt for this test.")

    attempt_in = schemas.TestAttemptCreate(test_id=test_id, user_id=current_user.id)
    attempt = crud.test_attempt.create(db, obj_in=attempt_in)
    return attempt

@router.get("/attempts/me", response_model=List[schemas.TestAttemptInDB])
def read_my_attempts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Retrieve all test attempts for the current user."""
    attempts = crud.test_attempt.get_multi_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return attempts

@router.get("/attempts/{attempt_id}", response_model=schemas.TestAttemptInDB)
def read_my_attempt(
    *,
    db: Session = Depends(deps.get_db),
    attempt_id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Retrieve a specific test attempt for the current user."""
    attempt = crud.test_attempt.get(db, id=attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return attempt

@router.post("/attempts/{attempt_id}/submit", response_model=schemas.Message)
def submit_answers(
    *,
    db: Session = Depends(deps.get_db),
    attempt_id: int,
    answers_in: List[schemas.TestAnswerCreate],
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Submit answers for a test attempt."""
    attempt = crud.test_attempt.get(db, id=attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.is_completed:
        raise HTTPException(status_code=400, detail="This attempt has already been completed.")
    
    # Here we would normally validate that the questions belong to the test
    crud.test_answer.create_multi_for_attempt(db, answers=answers_in, attempt_id=attempt_id)
    
    return {"msg": "Answers submitted successfully"}

@router.post("/attempts/{attempt_id}/finish", response_model=schemas.TestResultResponse)
def finish_test_attempt(
    *,
    db: Session = Depends(deps.get_db),
    attempt_id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Finish a test attempt and get the final results."""
    attempt = crud.test_attempt.get(db, id=attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.is_completed:
        raise HTTPException(status_code=400, detail="This attempt has already been completed.")

    # Placeholder for a real grading service
    # from app.services.grading_service import grade_attempt
    # result = grade_attempt(db, attempt)
    # For now, we'll just mark it as complete with a dummy score
    result = {"total_score": 0.0, "max_score": 0.0, "percentage": 0.0, "is_passed": False, "sections": [], "feedback": "Grading not implemented yet."}

    crud.test_attempt.complete(db, db_obj=attempt, total_score=result['total_score'], max_score=result['max_score'])

    return {
        "attempt_id": attempt.id,
        "test_id": attempt.test_id,
        "test_title": attempt.test.title,
        **result
    }

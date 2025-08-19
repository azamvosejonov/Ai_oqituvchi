from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.schemas.test import (
    TestResponse, TestListResponse, TestSectionResponse, TestQuestionResponse,
    TestAttemptResponse, TestAnswerResponse, TestStartResponse, TestSubmitRequest,
    TestResultResponse
)

router = APIRouter()

# Test endpoints
@router.get("/", response_model=TestListResponse)
def read_tests(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    test_type: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Retrieve tests with optional filtering by test type.
    """
    tests = crud.test.get_multi(db, skip=skip, limit=limit, test_type=test_type)
    total = crud.test.count(db)
    return {
        "tests": tests,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }

@router.get("/{test_id}", response_model=TestResponse)
def read_test(
    test_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get a specific test by ID.
    """
    test = crud.test.get_with_sections(db, id=test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

@router.post("/{test_id}/start", response_model=TestStartResponse)
def start_test(
    test_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Start a new test attempt.
    """
    # Check if test exists
    test = crud.test.get(db, id=test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Check if user has an active attempt
    active_attempt = db.query(models.TestAttempt).filter(
        models.TestAttempt.user_id == current_user.id,
        models.TestAttempt.test_id == test_id,
        models.TestAttempt.is_completed == False
    ).first()
    
    if active_attempt:
        # Return existing active attempt
        return {
            "attempt_id": active_attempt.id,
            "test": test,
            "start_time": active_attempt.start_time
        }
    
    # Create new attempt
    attempt_in = schemas.TestAttemptCreate(test_id=test_id, user_id=current_user.id)
    attempt = crud.test_attempt.create_with_user(db, obj_in=attempt_in, user_id=current_user.id)
    
    return {
        "attempt_id": attempt.id,
        "test": test,
        "start_time": attempt.start_time
    }

@router.post("/attempts/{attempt_id}/submit", response_model=TestResultResponse)
def submit_test_attempt(
    attempt_id: int,
    submit_data: TestSubmitRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Submit answers for a test attempt and get results.
    """
    # Get the attempt
    attempt = crud.test_attempt.get(db, id=attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Test attempt not found")
    
    if attempt.is_completed:
        raise HTTPException(status_code=400, detail="Test already submitted")
    
    # Save answers
    answers = [
        schemas.TestAnswerCreate(
            question_id=answer["question_id"],
            answer_data=answer["answer_data"],
            attempt_id=attempt_id
        )
        for answer in submit_data.answers
    ]
    
    crud.test_answer.create_multi(db, answers=answers, attempt_id=attempt_id)
    
    # Grade the test
    crud.test_answer.grade_answers(db, attempt_id=attempt_id, answers=submit_data.answers)
    
    # Calculate total score
    attempt_answers = crud.test_answer.get_by_attempt(db, attempt_id=attempt_id)
    total_score = sum(answer.score for answer in attempt_answers)
    max_score = sum(answer.question.marks for answer in attempt_answers)
    
    # Complete the attempt
    attempt = crud.test_attempt.complete_attempt(
        db, db_obj=attempt, total_score=total_score, max_score=max_score
    )
    
    # Generate result
    percentage = (total_score / max_score) * 100 if max_score > 0 else 0
    is_passed = percentage >= 70  # 70% passing threshold
    
    # Get section-wise scores
    sections = []
    for section in attempt.test.sections:
        section_answers = [a for a in attempt_answers if a.question.section_id == section.id]
        section_score = sum(a.score for a in section_answers)
        section_max = sum(a.question.marks for a in section_answers)
        
        sections.append({
            "id": section.id,
            "title": section.title,
            "score": section_score,
            "max_score": section_max,
            "percentage": (section_score / section_max * 100) if section_max > 0 else 0
        })
    
    # TODO: Generate certificate if test is passed
    certificate_url = None
    if is_passed:
        # certificate_url = generate_certificate(attempt)
        pass
    
    return {
        "attempt_id": attempt.id,
        "test_id": attempt.test_id,
        "test_title": attempt.test.title,
        "total_score": total_score,
        "max_score": max_score,
        "percentage": round(percentage, 2),
        "is_passed": is_passed,
        "sections": sections,
        "feedback": "Congratulations! You passed the test!" if is_passed else "Try again to improve your score!",
        "certificate_url": certificate_url
    }

@router.get("/attempts/{attempt_id}", response_model=TestAttemptResponse)
def get_test_attempt(
    attempt_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get details of a specific test attempt.
    """
    attempt = crud.test_attempt.get(db, id=attempt_id)
    if not attempt or (attempt.user_id != current_user.id and not current_user.is_superuser):
        raise HTTPException(status_code=404, detail="Test attempt not found")
    return attempt

@router.get("/users/me/attempts", response_model=List[TestAttemptResponse])
def get_user_test_attempts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get test attempts for the current user.
    """
    return crud.test_attempt.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )

# Admin endpoints
@router.post("/", response_model=TestResponse, status_code=status.HTTP_201_CREATED)
def create_test(
    test_in: schemas.TestCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_admin_user),
):
    """
    Create a new test (Admin only).
    """
    return crud.test.create(db, obj_in=test_in)

@router.post("/sections/", response_model=TestSectionResponse, status_code=status.HTTP_201_CREATED)
def create_test_section(
    section_in: schemas.TestSectionCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_admin_user),
):
    """
    Create a new test section (Admin only).
    """
    return crud.test_section.create(db, obj_in=section_in)

@router.post("/questions/", response_model=TestQuestionResponse, status_code=status.HTTP_201_CREATED)
def create_test_question(
    question_in: schemas.TestQuestionCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_admin_user),
):
    """
    Create a new test question (Admin only).
    """
    return crud.test_question.create(db, obj_in=question_in)

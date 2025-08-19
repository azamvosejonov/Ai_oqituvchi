import random
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app import models, schemas
from app.core.config import settings
from tests.utils.utils import random_lower_string

def create_random_exercise(
    db: Session,
    exercise_in: Optional[Dict[str, Any]] = None,
    owner_id: Optional[int] = None,
) -> models.Exercise:
    """Create a random exercise for testing"""
    if exercise_in is None:
        exercise_in = {}
    
    # Default exercise data
    default_data = {
        "question": f"Test question {random_lower_string()}",
        "correct_answer": "Test answer",
        "explanation": "Test explanation",
        "exercise_type": schemas.ExerciseType.SHORT_ANSWER,
        "difficulty": "easy",
        "is_active": True,
        "tags": ["test"],
        "metadata": {}
    }
    
    # Update with any provided data
    exercise_data = {**default_data, **exercise_in}
    
    # Create the exercise
    exercise = models.Exercise(**exercise_data, owner_id=owner_id)
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise

def create_random_exercise_answer(
    db: Session,
    exercise_id: int,
    user_id: int,
    answer: Optional[Dict[str, Any]] = None
) -> models.ExerciseAttempt:
    """Create a random exercise answer for testing"""
    if answer is None:
        answer = {}
    
    default_answer = {
        "user_answer": {"choice": "A"},
        "is_correct": True,
        "score": 1.0,
        "feedback": {"message": "Good job!"}
    }
    
    final_answer = {**default_answer, **answer}
    
    exercise_answer = models.ExerciseAttempt(
        exercise_id=exercise_id,
        user_id=user_id,
        **final_answer
    )
    
    db.add(exercise_answer)
    db.commit()
    db.refresh(exercise_answer)
    return exercise_answer

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict, ValidationInfo
from enum import Enum
from .ai_chat import DifficultyLevel

class ExerciseType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_BLANK = "fill_in_blank"
    MATCHING = "matching"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    LISTENING = "listening"
    SPEAKING = "speaking"
    TRANSLATION = "translation"
    DICTATION = "dictation"

class ExerciseBase(BaseModel):
    """Base model for exercise creation and update."""
    question: str = Field(..., description="The exercise question/prompt")
    exercise_type: ExerciseType = Field(..., description="Type of the exercise")
    difficulty: DifficultyLevel = Field(DifficultyLevel.BEGINNER, description="Difficulty level")
    correct_answer: Union[str, List, Dict] = Field(..., description="Correct answer(s)")
    explanation: Optional[str] = Field(None, description="Explanation of the correct answer")
    options: Optional[Union[List, Dict]] = Field(None, description="Options for multiple choice, matching, etc.")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    lesson_id: Optional[int] = Field(None, description="Optional lesson ID this exercise belongs to")
    is_active: bool = Field(True, description="Whether the exercise is active")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    audio_url: Optional[str] = Field(None, description="Optional audio URL for listening exercises")

    @field_validator('correct_answer')
    def validate_correct_answer(cls, v, info: ValidationInfo):
        """Validate correct_answer based on exercise_type (Pydantic v2)."""
        ex_type = None
        try:
            if info and info.data:
                ex_type = info.data.get('exercise_type')
        except Exception:
            ex_type = None
        if not ex_type:
            return v
        
        if ex_type == ExerciseType.MULTIPLE_CHOICE:
            if not isinstance(v, (str, int)):
                raise ValueError("Multiple choice must have a single correct answer (index or value)")
        elif ex_type == ExerciseType.TRUE_FALSE:
            if not isinstance(v, bool):
                raise ValueError("True/False must have a boolean correct answer")
        elif ex_type == ExerciseType.FILL_IN_BLANK:
            if not isinstance(v, (str, list)):
                raise ValueError("Fill in blank must have string or list of strings as correct answer")
        elif ex_type == ExerciseType.MATCHING:
            if not isinstance(v, dict):
                raise ValueError("Matching must have a dictionary as correct answer")
                
        return v

    class Config:
        from_attributes = True

class ExerciseCreate(ExerciseBase):
    class Config:
        from_attributes = True

class ExerciseUpdate(BaseModel):
    """Model for updating exercises."""
    question: Optional[str] = None
    exercise_type: Optional[ExerciseType] = None
    difficulty: Optional[DifficultyLevel] = None
    correct_answer: Optional[Union[str, List, Dict]] = None
    explanation: Optional[str] = None
    options: Optional[Union[List, Dict]] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    audio_url: Optional[str] = None

    class Config:
        from_attributes = True

class ExerciseInDBBase(ExerciseBase):
    """Base model for Exercise in the database."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Exercise(ExerciseInDBBase):
    """Exercise model for API responses."""
    class Config:
        from_attributes = True

class ExerciseInDB(ExerciseInDBBase):
    """Exercise model for DB-backed responses (alias for compatibility)."""
    class Config:
        from_attributes = True

class ExerciseAttemptBase(BaseModel):
    """Base model for exercise attempts."""
    user_answer: Union[str, List, Dict] = Field(..., description="User's answer")
    time_spent: Optional[int] = Field(None, description="Time spent in seconds")

    class Config:
        from_attributes = True

class ExerciseAttemptCreate(ExerciseAttemptBase):
    """Model for creating exercise attempts."""
    exercise_id: int = Field(..., description="ID of the exercise being attempted")

    class Config:
        from_attributes = True

class ExerciseAttemptInDBBase(ExerciseAttemptBase):
    """Base model for ExerciseAttempt in the database."""
    id: int
    user_id: int
    exercise_id: int
    is_correct: bool
    score: float
    feedback: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ExerciseAttempt(ExerciseAttemptInDBBase):
    """Exercise attempt model for API responses."""
    class Config:
        from_attributes = True

class ExerciseAttemptInDB(ExerciseAttemptInDBBase):
    """Exercise attempt model alias for endpoints expecting ExerciseAttemptInDB."""
    class Config:
        from_attributes = True

class ExerciseAnalysisResult(BaseModel):
    """Response schema for AI analysis of an exercise attempt."""
    is_correct: bool
    score: float
    feedback: Dict[str, Any] | str | None = None
    feedback_type: Optional[str] = None
    suggestions: Optional[List[str]] = None
    grammar_analysis: Optional[List[Dict[str, Any]]] = None
    vocabulary_analysis: Optional[List[Dict[str, Any]]] = None
    pronunciation_tips: Optional[str] = None
    attempt_id: Optional[int] = None

    class Config:
        from_attributes = True

class ExerciseSetBase(BaseModel):
    """Base model for exercise sets."""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    exercise_type: Optional[ExerciseType] = None
    difficulty: Optional[DifficultyLevel] = None
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ExerciseSetCreate(ExerciseSetBase):
    """Model for creating exercise sets."""
    exercise_ids: List[int] = Field(..., description="List of exercise IDs to include in the set")

    class Config:
        from_attributes = True

class ExerciseSetUpdate(BaseModel):
    """Model for updating exercise sets."""
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ExerciseSetInDBBase(ExerciseSetBase):
    """Base model for ExerciseSet in the database."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ExerciseSet(ExerciseSetInDBBase):
    """Exercise set model for API responses."""
    exercises: List[Exercise] = []

    class Config:
        from_attributes = True

class ExerciseSetItemBase(BaseModel):
    """Base model for exercise set items."""
    exercise_id: int
    order: int = 0
    points: int = 1
    required: bool = True

    class Config:
        from_attributes = True

class ExerciseSetItemCreate(ExerciseSetItemBase):
    """Model for creating exercise set items."""
    class Config:
        from_attributes = True

class ExerciseSetItem(ExerciseSetItemBase):
    """Exercise set item model for API responses."""
    id: int
    exercise_set_id: int
    exercise: Exercise

    class Config:
        from_attributes = True

class UserProgressBase(BaseModel):
    """Base model for user progress."""
    user_id: int
    exercise_id: Optional[int] = None
    lesson_id: Optional[int] = None
    score: float = 0.0
    completed: bool = False
    attempts: int = 0

    class Config:
        from_attributes = True

class UserProgressCreate(UserProgressBase):
    """Model for creating user progress."""
    class Config:
        from_attributes = True

class UserProgressUpdate(BaseModel):
    """Model for updating user progress."""
    score: Optional[float] = None
    completed: Optional[bool] = None
    attempts: Optional[int] = None

    class Config:
        from_attributes = True

class UserProgress(UserProgressBase):
    """User progress model for API responses."""
    id: int
    last_attempted: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TestSessionBase(BaseModel):
    """Base model for test sessions."""
    test_type: str = Field(..., description="Type of test (e.g., 'ielts_listening')")
    time_limit: Optional[int] = Field(None, description="Time limit in seconds")
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class TestSessionCreate(TestSessionBase):
    """Model for creating test sessions."""
    exercise_set_id: Optional[int] = Field(None, description="Optional exercise set ID for the test")

    class Config:
        from_attributes = True

class TestSessionUpdate(BaseModel):
    """Model for updating test sessions."""
    status: Optional[str] = None
    total_score: Optional[float] = None
    end_time: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class TestSession(TestSessionBase):
    """Test session model for API responses."""
    id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    total_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    responses: List["TestResponse"] = []

    class Config:
        from_attributes = True

class TestResponseBase(BaseModel):
    """Base model for test responses."""
    exercise_id: int
    user_answer: Optional[Union[str, List, Dict]] = None
    time_spent: Optional[int] = None

    class Config:
        from_attributes = True

class TestResponseCreate(TestResponseBase):
    """Model for creating test responses."""
    test_session_id: int

    class Config:
        from_attributes = True

class TestResponseUpdate(BaseModel):
    """Model for updating test responses."""
    user_answer: Optional[Union[str, List, Dict]] = None
    is_correct: Optional[bool] = None
    score: Optional[float] = None
    feedback: Optional[Dict[str, Any]] = None
    time_spent: Optional[int] = None

    class Config:
        from_attributes = True

class TestResponse(TestResponseBase):
    """Test response model for API responses."""
    id: int
    test_session_id: int
    is_correct: Optional[bool] = None
    score: Optional[float] = None
    feedback: Optional[Dict[str, Any]] = None
    created_at: datetime
    exercise: Exercise

    class Config:
        from_attributes = True

# Update forward references for Pydantic models
TestSession.model_rebuild()

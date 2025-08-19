from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
from .user import User

# Enums
class TestType(str, Enum):
    IELTS = "ielts"
    TOEFL = "toefl"
    PRACTICE = "practice"

class TestSectionType(str, Enum):
    LISTENING = "listening"
    READING = "reading"
    WRITING = "writing"
    SPEAKING = "speaking"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_anwser"
    ESSAY = "essay"
    MATCHING = "matching"
    FILL_BLANKS = "fill_blanks"

# Base schemas
class TestBase(BaseModel):
    title: str
    description: Optional[str] = None
    test_type: TestType
    duration_minutes: int = Field(..., gt=0)
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

    @field_validator("test_type", mode="before")
    @classmethod
    def _normalize_test_type(cls, v):
        if v is None:
            return v
        # Accept incoming strings or enums; normalize to lowercase string so Enum coercion succeeds
        if isinstance(v, str):
            return v.lower()
        try:
            return str(v).lower()
        except Exception:
            return v

class TestSectionBase(BaseModel):
    section_type: TestSectionType
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    duration_minutes: int = Field(..., gt=0)
    order_index: int = 0

    model_config = ConfigDict(from_attributes=True)

    @field_validator("section_type", mode="before")
    @classmethod
    def _normalize_section_type(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            return v.lower()
        try:
            return str(v).lower()
        except Exception:
            return v

class TestQuestionBase(BaseModel):
    question_type: QuestionType
    question_text: str
    question_data: Dict[str, Any]  # For options, correct answers, etc.
    marks: float = 1.0
    order_index: int = 0

    model_config = ConfigDict(from_attributes=True)

class TestAttemptBase(BaseModel):
    test_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class TestAnswerBase(BaseModel):
    question_id: int
    answer_data: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

# Create schemas
class TestCreate(TestBase):
    pass

    model_config = ConfigDict(from_attributes=True)

class TestSectionCreate(TestSectionBase):
    test_id: int

    model_config = ConfigDict(from_attributes=True)

class TestQuestionCreate(TestQuestionBase):
    section_id: int

    model_config = ConfigDict(from_attributes=True)

class TestAttemptCreate(TestAttemptBase):
    pass

    model_config = ConfigDict(from_attributes=True)

class TestAnswerCreate(TestAnswerBase):
    attempt_id: int

    model_config = ConfigDict(from_attributes=True)

# Update schemas
class TestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    test_type: Optional[TestType] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("test_type", mode="before")
    @classmethod
    def _normalize_test_type_update(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            return v.lower()
        try:
            return str(v).lower()
        except Exception:
            return v

class TestSectionUpdate(BaseModel):
    section_type: Optional[TestSectionType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    order_index: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("section_type", mode="before")
    @classmethod
    def _normalize_section_type_update(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            return v.lower()
        try:
            return str(v).lower()
        except Exception:
            return v

class TestQuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_data: Optional[Dict[str, Any]] = None
    marks: Optional[float] = None
    order_index: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

# Response schemas
class TestAnswerInDB(TestAnswerBase):
    id: int
    is_correct: Optional[bool] = None
    score: float = 0.0
    feedback: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class TestQuestionInDB(TestQuestionBase):
    id: int
    section_id: int
    answers: List[TestAnswerInDB] = []

    model_config = ConfigDict(from_attributes=True)

class TestSectionInDB(TestSectionBase):
    id: int
    test_id: int
    questions: List[TestQuestionInDB] = []

    model_config = ConfigDict(from_attributes=True)

class TestInDB(TestBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    sections: List[TestSectionInDB] = []

    model_config = ConfigDict(from_attributes=True)

class TestAttemptInDB(TestAttemptBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    time_spent_seconds: int = 0
    is_completed: bool = False
    total_score: float = 0.0
    max_score: float = 0.0
    answers: List[TestAnswerInDB] = []
    user: User

    model_config = ConfigDict(from_attributes=True)

# Response models
class TestResponse(TestInDB):
    model_config = ConfigDict(from_attributes=True)

class TestSectionResponse(TestSectionInDB):
    model_config = ConfigDict(from_attributes=True)

class TestQuestionResponse(TestQuestionInDB):
    model_config = ConfigDict(from_attributes=True)

class TestAttemptResponse(TestAttemptInDB):
    test: TestInDB

    model_config = ConfigDict(from_attributes=True)

class TestAnswerResponse(TestAnswerInDB):
    question: TestQuestionInDB

    model_config = ConfigDict(from_attributes=True)

# Specialized schemas
class TestStartResponse(BaseModel):
    attempt_id: int
    test: TestInDB
    start_time: datetime

    model_config = ConfigDict(from_attributes=True)

class TestSubmitRequest(BaseModel):
    answers: List[TestAnswerCreate]

    model_config = ConfigDict(from_attributes=True)

class GradedAnswer(BaseModel):
    question_id: int
    user_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    is_correct: bool
    score: float

    model_config = ConfigDict(from_attributes=True)

class GradedSection(BaseModel):
    section_id: int
    section_title: str
    score: float
    max_score: float
    answers: List[GradedAnswer]

    model_config = ConfigDict(from_attributes=True)

class TestResultResponse(BaseModel):
    attempt_id: int
    test_id: int
    test_title: str
    total_score: float
    max_score: float
    percentage: float
    is_passed: bool
    sections: List[GradedSection]
    feedback: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class TestListResponse(BaseModel):
    tests: List[TestInDB]
    total: int
    page: int
    size: int

    model_config = ConfigDict(from_attributes=True)

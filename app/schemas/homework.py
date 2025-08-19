from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator, HttpUrl, ConfigDict

from .user import User
from .lesson import Lesson
from .course import Course


class HomeworkType(str, Enum):
    WRITTEN = "written"
    ORAL = "oral"
    QUIZ = "quiz"
    PROJECT = "project"

class HomeworkStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    LATE = "late"
    GRADED = "graded"
    RETURNED = "returned"

# Shared properties for Homework
class HomeworkBase(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    homework_type: HomeworkType = Field(HomeworkType.WRITTEN, description="Type of homework")
    due_date: Optional[datetime] = None
    max_score: int = Field(100, description="Maximum score for this assignment")
    is_published: bool = Field(False, description="Whether the homework is published to students")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata in JSON format")

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Oral Assignment specific properties
class OralAssignmentBase(BaseModel):
    topic: str
    time_limit: Optional[int] = Field(None, description="Time limit in seconds")
    questions: Optional[List[Dict[str, Any]]] = Field(None, description="List of questions or prompts")
    criteria: Optional[Dict[str, Any]] = Field(None, description="Grading criteria")

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Properties to receive on homework creation
class HomeworkCreate(HomeworkBase):
    course_id: int
    lesson_id: Optional[int] = None
    oral_assignment: Optional[OralAssignmentBase] = Field(
        None, 
        description="Required if homework_type is 'oral'"
    )
    
    @field_validator('oral_assignment', mode='before')
    def validate_oral_assignment(cls, v, values):
        if values.data.get('homework_type') == HomeworkType.ORAL and v is None:
            raise ValueError("oral_assignment is required for oral homework type")
        return v

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Properties to receive on homework update
class HomeworkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    due_date: Optional[datetime] = None
    max_score: Optional[int] = None
    is_published: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    oral_assignment: Optional[OralAssignmentBase] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Properties shared by models stored in DB
class HomeworkInDBBase(HomeworkBase):
    id: int
    lesson_id: Optional[int] = None
    # Map DB attribute `created_by` to API field `teacher_id`
    teacher_id: int = Field(
        default=..., validation_alias='created_by', serialization_alias='teacher_id',
        description="ID of the teacher who created the homework"
    )
    created_at: datetime
    updated_at: datetime

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Properties to return to client
class Homework(HomeworkInDBBase):
    lesson: Optional[Lesson] = None
    submissions: List["HomeworkSubmission"] = []

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Properties stored in DB
class HomeworkInDB(HomeworkInDBBase):
    pass

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Shared properties for UserHomework
class UserHomeworkBase(BaseModel):
    status: str = Field("assigned", description="Status: assigned, in_progress, submitted, graded")
    submission: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None
    score: Optional[int] = Field(None, ge=0, le=100, description="Score out of 100")

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Properties to receive on user homework creation
class UserHomeworkCreate(UserHomeworkBase):
    user_id: int
    homework_id: int

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Properties to receive on user homework update
class UserHomeworkUpdate(UserHomeworkBase):
    submission: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None
    score: Optional[int] = Field(None, ge=0, le=100)

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Properties shared by models stored in DB
class UserHomeworkInDBBase(UserHomeworkBase):
    id: int
    user_id: int
    homework_id: int
    submitted_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Properties to return to client
class UserHomework(UserHomeworkInDBBase):
    homework: Optional[Homework] = None
    user: Optional[User] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Properties stored in DB
class UserHomeworkInDB(UserHomeworkInDBBase):
    pass

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


# Schemas for HomeworkSubmission
class HomeworkSubmissionBase(BaseModel):
    content: Optional[str] = None
    file_url: Optional[HttpUrl] = None
    audio_url: Optional[HttpUrl] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


class HomeworkSubmissionCreate(HomeworkSubmissionBase):
    homework_id: int

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


class HomeworkSubmissionUpdate(BaseModel):
    status: Optional[HomeworkStatus] = None
    score: Optional[int] = Field(None, ge=0)
    feedback: Optional[str] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


class HomeworkSubmissionInDBBase(HomeworkSubmissionBase):
    id: int
    homework_id: int
    student_id: int
    status: HomeworkStatus
    score: Optional[int] = None
    feedback: Optional[str] = None
    submitted_at: datetime
    graded_at: Optional[datetime] = None
    graded_by: Optional[int] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )


class HomeworkSubmission(HomeworkSubmissionInDBBase):
    student: Optional[User] = None
    homework: Optional[Homework] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

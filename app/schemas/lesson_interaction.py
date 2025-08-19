from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from .user import User


# Shared properties
class LessonInteractionBase(BaseModel):
    user_input: str = Field(..., description="User's input text or transcription")
    ai_response: str = Field(..., description="AI's response to the user input")

    model_config = ConfigDict(
        from_attributes=True,
    )


# Properties to receive on interaction creation
class LessonInteractionCreate(LessonInteractionBase):
    session_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


# Properties to receive on interaction update
class LessonInteractionUpdate(BaseModel):
    user_input: Optional[str] = None
    ai_response: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


# Properties shared by models stored in DB
class LessonInteractionInDBBase(LessonInteractionBase):
    id: int
    session_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


# Properties to return to client
class LessonInteraction(LessonInteractionInDBBase):
    pass

    model_config = ConfigDict(
        from_attributes=True,
    )


# Properties properties stored in DB
class LessonInteractionInDB(LessonInteractionInDBBase):
    pass

    model_config = ConfigDict(
        from_attributes=True,
    )

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# Shared properties
class UserLessonCompletionBase(BaseModel):
    user_id: int
    lesson_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )

# Properties to receive on item creation
class UserLessonCompletionCreate(UserLessonCompletionBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

# Properties to receive on item update
class UserLessonCompletionUpdate(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )
    pass # Usually we don't update these records, but create new ones

# Properties shared by models stored in DB
class UserLessonCompletionInDBBase(UserLessonCompletionBase):
    id: int
    completed_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

# Properties to return to client
class UserLessonCompletion(UserLessonCompletionInDBBase):
    model_config = ConfigDict(
        from_attributes=True,
    )
    pass

# Properties stored in DB
class UserLessonCompletionInDB(UserLessonCompletionInDBBase):
    model_config = ConfigDict(
        from_attributes=True,
    )
    pass

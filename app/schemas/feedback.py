from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

# Shared properties
class FeedbackBase(BaseModel):
    content: str
    rating: int = Field(..., ge=1, le=5) # Rating from 1 to 5

    model_config = ConfigDict(
        from_attributes=True,
    )

# Properties to receive on item creation
class FeedbackCreate(FeedbackBase):
    pass

# Properties to receive on item update
class FeedbackUpdate(FeedbackBase):
    pass

# Properties shared by models stored in DB
class FeedbackInDBBase(FeedbackBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

# Properties to return to client
class Feedback(FeedbackInDBBase):
    pass

# Properties stored in DB
class FeedbackInDB(FeedbackInDBBase):
    pass

from pydantic import BaseModel, ConfigDict
from .ai_chat import DifficultyLevel

class UserLevel(BaseModel):
    level: str
    xp: int

    model_config = ConfigDict(
        from_attributes=True,
    )

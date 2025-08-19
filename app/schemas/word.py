from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class WordBase(BaseModel):
    word: str
    translation: str
    ipa_pronunciation: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class WordCreate(WordBase):
    lesson_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class WordUpdate(BaseModel):
    word: Optional[str] = None
    translation: Optional[str] = None
    ipa_pronunciation: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class WordInDBBase(WordBase):
    id: int
    lesson_id: Optional[int]

    model_config = ConfigDict(
        from_attributes=True,
    )


class Word(WordInDBBase):
    model_config = ConfigDict(
        from_attributes=True,
    )


class WordInDB(WordInDBBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

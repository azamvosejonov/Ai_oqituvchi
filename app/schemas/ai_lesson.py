from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any

class AILessonGenerateRequest(BaseModel):
    topic: str
    level: str = "B1"
    language: str = "English"
    num_words: int = 5
    num_questions: int = 3

    model_config = ConfigDict(
        from_attributes=True,
    )

class AIGeneratedWord(BaseModel):
    word: str
    translation: str
    definition: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class AIGeneratedQuestion(BaseModel):
    question_text: str
    options: List[str]
    correct_answer: str

    model_config = ConfigDict(
        from_attributes=True,
    )

class AILessonGenerateResponse(BaseModel):
    course_title: str
    lesson_title: str
    lesson_content: str
    vocabulary: List[Dict[str, str]]
    quiz: List[Dict[str, Any]]

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonSessionStartRequest(BaseModel):
    lesson_id: int
    ai_model: Optional[str] = "gemini-2.0-flash"

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonInteractionRequest(BaseModel):
    user_input: str
    interaction_type: str = "text"

    model_config = ConfigDict(
        from_attributes=True,
    )

class LessonInteractionResponse(BaseModel):
    ai_response: str
    progress: float

    model_config = ConfigDict(
        from_attributes=True,
    )

from pydantic import BaseModel, ConfigDict


class AIUsageStats(BaseModel):
    tts_chars_used: int
    stt_seconds_used: int
    chat_tokens_used: int

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

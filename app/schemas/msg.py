from pydantic import BaseModel, ConfigDict


class Message(BaseModel):
    msg: str

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

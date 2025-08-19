from sqlalchemy.orm import Session
from app.models.ai_avatar import AIAvatar
from app.schemas.ai_avatar import AIAvatarCreate
from app.crud import crud_ai_avatar

def create_random_avatar(db: Session) -> AIAvatar:
    avatar_in = AIAvatarCreate(name="Test Avatar", voice_id="test_voice")
    return crud_ai_avatar.create(db=db, obj_in=avatar_in)

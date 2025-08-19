from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from app import models, crud, schemas
from app.api import deps

# This is a mock database for avatars for now.
# In a real application, this would come from the database.
AVATAR_DATABASE = {
    "sara": {
        "id": "sara",
        "name": "Sara",
        "description": "A friendly and patient English teacher.",
        "language": "en-US",
        "voice_style": "friendly",
        "is_premium": False
    },
    "david": {
        "id": "david",
        "name": "David",
        "description": "An expert in business English.",
        "language": "en-US",
        "voice_style": "professional",
        "is_premium": True
    }
}

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def list_avatars(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_with_free_window)
):
    """
    Get available AI avatars with their configurations.
    Also ensures mock avatars are present in DB and returns int IDs.
    """
    results: List[Dict[str, Any]] = []
    for key, a in AVATAR_DATABASE.items():
        # Upsert by name into DB so we have a real integer ID
        db_avatar = crud.ai_avatar.get_by_name(db, name=a["name"])  # type: ignore[arg-type]
        if not db_avatar:
            # Provide sensible defaults for required fields
            create_in = schemas.AIAvatarCreate(
                name=a["name"],
                description=a.get("description"),
                avatar_url=f"https://example.com/avatars/{key}.png",
                voice_id=f"{key}-voice",
                language=a.get("language", "en-US"),
                is_active=True,
                metadata={
                    "legacy_id": a["id"],
                    "voice_style": a.get("voice_style"),
                    "is_premium": a.get("is_premium", False),
                },
            )
            db_avatar = crud.ai_avatar.create(db, obj_in=create_in)
        results.append({
            "id": db_avatar.id,  # int ID for FK usage
            "legacy_id": a["id"],
            "name": db_avatar.name,
            "description": db_avatar.description,
            "language": db_avatar.language,
            "voice_style": a.get("voice_style"),
            "is_premium": a.get("is_premium", False),
            "avatar_url": db_avatar.avatar_url,
            "voice_id": db_avatar.voice_id,
        })
    return results

@router.get("/{avatar_id}", response_model=Dict[str, Any])
async def get_avatar(
    avatar_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user_with_free_window)
):
    """
    Get configuration for a specific avatar.
    Accepts either legacy string id (e.g., "sara") or integer DB id.
    """
    avatar = AVATAR_DATABASE.get(avatar_id)
    if avatar:
        # Ensure it's in DB and return enriched record
        # Reuse list_avatars logic by filtering
        entries = await list_avatars(db=db, current_user=current_user)
        for e in entries:
            if str(e.get("legacy_id")) == avatar_id:
                return e
    # Try integer DB id path
    try:
        int_id = int(avatar_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Avatar not found")
    db_avatar = crud.ai_avatar.get(db, id=int_id)
    if not db_avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    return {
        "id": db_avatar.id,
        "legacy_id": None,
        "name": db_avatar.name,
        "description": db_avatar.description,
        "language": db_avatar.language,
        "voice_style": None,
        "is_premium": False,
        "avatar_url": db_avatar.avatar_url,
        "voice_id": db_avatar.voice_id,
    }

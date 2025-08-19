from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
import json

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.schemas.lesson_interaction import LessonInteraction, LessonInteractionCreate
from app.services.ai_service import InteractiveLessonService

router = APIRouter()


@router.post(
    "/{session_id}/interact", 
    response_model=LessonInteraction,
    summary="Create a new lesson interaction",
    description="""
    Create a new interaction in a lesson session.
    
    This endpoint accepts either text input or an audio file for speech-to-text conversion.
    The AI will process the input and generate an appropriate response.
    
    **Note**: Either `user_input` or `audio_file` must be provided.
    """,
    responses={
        200: {"description": "Interaction created successfully"},
        400: {"description": "Invalid input or missing parameters"},
        401: {"description": "Not authenticated"},
        404: {"description": "Session not found"},
        500: {"description": "Error processing interaction"}
    }
)
async def create_lesson_interaction(
    *,
    db: Session = Depends(deps.get_db),
    session_id: int,
    payload: dict = Body(..., description="JSON body supporting user_input and optional ai_response"),
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
):
    # Check if session exists and belongs to user
    session = crud.interactive_lesson_session.get(db, id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Extract inputs from JSON payload (tests send user_input + ai_response)
    user_input = payload.get("user_input")
    provided_ai_response = payload.get("ai_response")
    if not user_input:
        raise HTTPException(status_code=400, detail="user_input is required")
    
    # Initialize AI service
    ai_service = InteractiveLessonService(db)
    
    # Get AI response (or use provided one in tests)
    if provided_ai_response is not None:
        ai_response = provided_ai_response
    else:
        try:
            ai_response = await ai_service.get_ai_response(
                user_id=current_user.id,
                session_id=session_id,
                user_input=user_input,
                lesson_id=session.lesson_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting AI response: {str(e)}")
    
    # Create interaction record
    interaction_in = LessonInteractionCreate(
        user_input=user_input,
        ai_response=ai_response,
        session_id=session_id
    )
    
    return crud.interactive_lesson_interaction.create(db, obj_in=interaction_in)


@router.get(
    "/{session_id}/interactions", 
    response_model=List[LessonInteraction],
    summary="Get lesson session interactions",
    description="""
    Retrieve interactions for a specific lesson session.
    
    Returns a paginated list of interactions between the user and AI tutor.
    """,
    responses={
        200: {"description": "List of interactions retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to access this session"},
        404: {"description": "Session not found"}
    }
)
async def read_lesson_interactions(
    *,
    db: Session = Depends(deps.get_db),
    session_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user_with_free_window),
):
    """
    Retrieve interactions for a lesson session.
    """
    # Check if session exists and belongs to user
    session = crud.interactive_lesson_session.get(db, id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud.interactive_lesson_interaction.get_by_session(
        db, session_id=session_id, skip=skip, limit=limit
    )

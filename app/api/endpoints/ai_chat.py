import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import json

from app import models, schemas, crud
from app.api import deps
from app.core.config import settings
from app.schemas.ai_chat import AIChatResponse, AIChatInput, WritingFeedback, WritingFeedbackInput
from app.services.ai_service import (
    ask_llm, 
    get_audio_response_from_prompt,
    score_pronunciation,
    InteractiveLessonService,
    get_chat_completion
)
from app.services.stt_service import stt_service
from app.crud import crud_user_ai_usage
from app.models.ai_usage import AIFeatureType

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages active WebSocket connections for chat."""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)
    
    async def broadcast(self, message: str, exclude: str = None):
        for client_id, connection in self.active_connections.items():
            if client_id != exclude:
                await connection.send_text(message)

# Global connection manager
manager = ConnectionManager()

@router.post("/chat", response_model=AIChatResponse)
async def chat_with_ai(
    chat_input: AIChatInput,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Chat with the AI assistant.
    
    This endpoint allows users to have a text-based conversation with the AI assistant.
    It supports context from lessons and tracks conversation history.
    """
    try:
        # Check if user has chat quota
        if not current_user.is_superuser:
            usage = crud_user_ai_usage.user_ai_usage.get_usage(
                db, 
                user_id=current_user.id,
                feature_type=AIFeatureType.CHAT
            )
            
            if usage.remaining_quota <= 0:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="You have exceeded your chat quota. Please upgrade to premium for more."
                )
        
        # Get AI response
        response_text = ""
        
        # If this is a follow-up in a lesson, use the interactive lesson service
        if chat_input.lesson_id and chat_input.session_id:
            lesson_service = InteractiveLessonService(db)
            response_text = await lesson_service.generate_ai_response(
                user_input=chat_input.message,
                session_id=chat_input.session_id,
                user_id=current_user.id
            )
        else:
            # Regular chat mode
            response_text = ""
            async for chunk in ask_llm(
                prompt=chat_input.message,
                db=db,
                lesson_id=chat_input.lesson_id,
                user=current_user
            ):
                response_text += chunk
        
        # Log the usage if not admin
        if not current_user.is_superuser and chat_input.log_usage:
            # Estimate tokens (roughly 4 characters per token)
            tokens_used = max(1, len(chat_input.message) // 4 + len(response_text) // 4)
            
            crud_user_ai_usage.user_ai_usage.increment_usage(
                db,
                user_id=current_user.id,
                feature_type=AIFeatureType.CHAT,
                characters_used=tokens_used
            )
            
            # Refresh usage
            usage = crud_user_ai_usage.user_ai_usage.get_usage(
                db, 
                user_id=current_user.id,
                feature_type=AIFeatureType.CHAT
            )
            remaining_quota = usage.remaining_quota
        else:
            remaining_quota = None
        
        return {
            "response": response_text,
            "remaining_quota": remaining_quota,
            "message_type": "text"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat_with_ai: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )

@router.post("/chat/audio", response_model=AIChatResponse)
async def chat_with_ai_audio(
    audio_file: UploadFile = File(...),
    lesson_id: Optional[int] = Form(None),
    session_id: Optional[int] = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Chat with the AI assistant using voice input.
    
    This endpoint allows users to speak to the AI assistant and get a voice response.
    The audio is first transcribed to text, then processed by the AI, and finally
    converted back to speech.
    """
    try:
        # Check if STT service is available
        if not stt_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Speech-to-text service is currently unavailable"
            )
        
        # Check user's AI usage quota
        if not current_user.is_superuser:
            usage = crud_user_ai_usage.user_ai_usage.get_usage(
                db, 
                user_id=current_user.id,
                feature_type=AIFeatureType.VOICE_CHAT
            )
            
            if usage.remaining_quota <= 0:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="You have exceeded your voice chat quota. Please upgrade to premium for more."
                )
        
        # Transcribe the audio to text
        transcription = await stt_service.transcribe_audio(
            audio_file,
            language_code=current_user.language or "uz-UZ"
        )
        
        if not transcription.get('transcript'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not transcribe the audio. Please try again."
            )
        
        user_message = transcription['transcript']
        
        # Get AI response
        if lesson_id and session_id:
            # Lesson context
            lesson_service = InteractiveLessonService(db)
            response_text = await lesson_service.generate_ai_response(
                user_input=user_message,
                session_id=session_id,
                user_id=current_user.id,
                interaction_type="voice"
            )
        else:
            # Regular chat
            response_text = ""
            async for chunk in ask_llm(
                prompt=user_message,
                db=db,
                lesson_id=lesson_id,
                user=current_user
            ):
                response_text += chunk
        
        # Convert response to speech
        audio_response = await get_audio_response_from_prompt(
            prompt=response_text,
            db=db,
            user=current_user,
            language_code=current_user.language or "uz-UZ"
        )
        
        # Log the usage if not admin
        if not current_user.is_superuser:
            # Estimate tokens (roughly 4 characters per token)
            input_tokens = max(1, len(user_message) // 4)
            output_tokens = max(1, len(response_text) // 4)
            
            # Log STT usage
            crud_user_ai_usage.user_ai_usage.increment_usage(
                db,
                user_id=current_user.id,
                feature_type=AIFeatureType.STT,
                characters_used=len(user_message)
            )
            
            # Log chat usage
            crud_user_ai_usage.user_ai_usage.increment_usage(
                db,
                user_id=current_user.id,
                feature_type=AIFeatureType.VOICE_CHAT,
                characters_used=input_tokens + output_tokens
            )
            
            # Log TTS usage
            crud_user_ai_usage.user_ai_usage.increment_usage(
                db,
                user_id=current_user.id,
                feature_type=AIFeatureType.TTS,
                characters_used=len(response_text)
            )
            
            # Get updated usage
            usage = crud_user_ai_usage.user_ai_usage.get_usage(
                db, 
                user_id=current_user.id,
                feature_type=AIFeatureType.VOICE_CHAT
            )
            remaining_quota = usage.remaining_quota
        else:
            remaining_quota = None
        
        return {
            "response": response_text,
            "audio_response": audio_response,
            "remaining_quota": remaining_quota,
            "message_type": "audio"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat_with_ai_audio: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your audio request"
        )

@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(deps.get_db)
):
    """
    WebSocket endpoint for real-time chat with the AI.
    """
    try:
        # Authenticate user
        user = deps.get_current_user_ws(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Generate a unique client ID
        client_id = f"user_{user.id}_{id(websocket)}"
        
        # Add connection to manager
        await manager.connect(websocket, client_id)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Process message based on type
                if message.get("type") == "chat":
                    # Regular chat message
                    chat_input = message.get("data", {})
                    
                    # Get AI response
                    response_text = ""
                    if chat_input.get("lesson_id") and chat_input.get("session_id"):
                        # Lesson context
                        lesson_service = InteractiveLessonService(db)
                        response_text = await lesson_service.generate_ai_response(
                            user_input=chat_input.get("message", ""),
                            session_id=chat_input["session_id"],
                            user_id=user.id
                        )
                    else:
                        # Regular chat
                        async for chunk in ask_llm(
                            prompt=chat_input.get("message", ""),
                            db=db,
                            lesson_id=chat_input.get("lesson_id"),
                            user=user
                        ):
                            response_text += chunk
                    
                    # Send response back to client
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "chat_response",
                            "data": {
                                "message": response_text,
                                "message_type": "text"
                            }
                        }),
                        client_id
                    )
                
                elif message.get("type") == "audio":
                    # Audio message (STT -> AI -> TTS)
                    audio_data = message.get("data", {})
                    
                    # Here you would process the audio data, but for now we'll just echo back
                    # In a real implementation, you would:
                    # 1. Decode the audio data
                    # 2. Transcribe it using STT
                    # 3. Get AI response
                    # 4. Convert response to speech
                    # 5. Send back the audio data
                    
                    # For now, just send a placeholder response
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "audio_response",
                            "data": {
                                "message": "Audio processing would happen here",
                                "audio_data": None,
                                "message_type": "audio"
                            }
                        }),
                        client_id
                    )
                
                elif message.get("type") == "typing":
                    # User is typing indicator
                    await manager.broadcast(
                        json.dumps({
                            "type": "user_typing",
                            "data": {
                                "user_id": user.id,
                                "is_typing": message.get("data", {}).get("is_typing", False)
                            }
                        }),
                        exclude=client_id
                    )
        
        except WebSocketDisconnect:
            manager.disconnect(client_id)
            await manager.broadcast(
                json.dumps({
                    "type": "user_disconnected",
                    "data": {"user_id": user.id}
                }),
                exclude=client_id
            )
        
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}", exc_info=True)
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}", exc_info=True)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

@router.post("/feedback/pronunciation", response_model=schemas.PronunciationFeedback)
async def get_pronunciation_feedback(
    audio_file: UploadFile = File(...),
    reference_text: str = Form(...),
    language_code: str = Form("uz-UZ"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Get detailed pronunciation feedback for spoken audio.
    
    This endpoint analyzes the user's pronunciation against a reference text
    and provides detailed feedback on accuracy, fluency, and completeness.
    """
    try:
        # Check user's quota if not admin
        if not current_user.is_superuser:
            usage = crud_user_ai_usage.user_ai_usage.get_usage(
                db, 
                user_id=current_user.id,
                feature_type=AIFeatureType.PRONUNCIATION_ASSESSMENT
            )
            
            if usage.remaining_quota <= 0:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="You have exceeded your pronunciation assessment quota. Please upgrade to premium for more."
                )
        
        # Get pronunciation assessment
        assessment = await score_pronunciation(
            file=audio_file,
            target_text=reference_text,
            db=db
        )
        
        # Log the usage if not admin
        if not current_user.is_superuser:
            # Estimate characters processed (approximate)
            characters_used = len(reference_text)
            crud_user_ai_usage.user_ai_usage.increment_usage(
                db,
                user_id=current_user.id,
                feature_type=AIFeatureType.PRONUNCIATION_ASSESSMENT,
                characters_used=characters_used
            )
            
            # Get updated usage
            usage = crud_user_ai_usage.user_ai_usage.get_usage(
                db, 
                user_id=current_user.id,
                feature_type=AIFeatureType.PRONUNCIATION_ASSESSMENT
            )
            assessment["remaining_quota"] = usage.remaining_quota - characters_used
        
        return assessment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_pronunciation_feedback: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while assessing pronunciation"
        )

@router.post("/feedback/writing", response_model=WritingFeedback)
async def get_writing_feedback(
    writing_input: WritingFeedbackInput,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Get feedback on writing.
    
    This endpoint analyzes the user's writing and provides feedback on
    grammar, vocabulary, and style.
    """
    try:
        # Check user's quota if not admin
        if not current_user.is_superuser:
            usage = crud_user_ai_usage.user_ai_usage.get_usage(
                db, 
                user_id=current_user.id,
                feature_type=AIFeatureType.WRITING_FEEDBACK
            )
            
            if usage.remaining_quota <= 0:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="You have exceeded your writing feedback quota. Please upgrade to premium for more."
                )
        
        # Prepare the prompt for the AI
        prompt = f"""
        Please provide detailed feedback on the following writing sample.
        
        Language: {writing_input.language}
        Writing Level: {writing_input.skill_level or 'Not specified'}
        
        Writing Prompt:
        {writing_input.prompt or 'No specific prompt provided'}
        
        User's Writing:
        {writing_input.text}
        
        Please provide feedback on the following aspects:
        1. Grammar and spelling
        2. Vocabulary usage
        3. Sentence structure
        4. Coherence and cohesion
        5. Task achievement (if there was a specific prompt)
        6. Suggestions for improvement
        
        Format your response as a JSON object with the following structure:
        {
            "grammar_feedback": "...",
            "vocabulary_feedback": "...",
            "structure_feedback": "...",
            "coherence_feedback": "...",
            "task_achievement": "...",
            "suggestions": ["...", "..."],
            "overall_score": 0-100,
            "corrected_text": "..."
        }
        """
        
        # Get AI response
        response_text = ""
        async for chunk in ask_llm(
            prompt=prompt,
            db=db,
            user=current_user,
            model="gemini-1.5-pro"  # Use a more advanced model for better feedback
        ):
            response_text += chunk
        
        # Parse the JSON response
        try:
            feedback = json.loads(response_text)
        except json.JSONDecodeError:
            # If the response isn't valid JSON, return it as a raw response
            feedback = {
                "raw_feedback": response_text,
                "error": "Could not parse AI response as JSON"
            }
        
        # Log the usage if not admin
        if not current_user.is_superuser:
            # Estimate tokens (input + output)
            input_tokens = max(1, len(prompt) // 4)
            output_tokens = max(1, len(response_text) // 4)
            
            crud_user_ai_usage.user_ai_usage.increment_usage(
                db,
                user_id=current_user.id,
                feature_type=AIFeatureType.WRITING_FEEDBACK,
                characters_used=input_tokens + output_tokens
            )
            
            # Get updated usage
            usage = crud_user_ai_usage.user_ai_usage.get_usage(
                db, 
                user_id=current_user.id,
                feature_type=AIFeatureType.WRITING_FEEDBACK
            )
            feedback["remaining_quota"] = usage.remaining_quota - (input_tokens + output_tokens)
        
        return feedback
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_writing_feedback: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating writing feedback"
        )

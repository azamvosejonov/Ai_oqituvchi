from typing import Dict, List, Optional, Tuple
import json
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from pydantic import BaseModel

from app.core.config import settings
from app.services.ai.stt import STTService
from app.services.ai.tts import TTSService
from app.services.ai.pronunciation import PronunciationAnalyzer
from app.core.cache import cache_result

logger = logging.getLogger(__name__)

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

@dataclass
class ConversationMessage:
    role: MessageRole
    content: str
    timestamp: datetime = None
    pronunciation_score: Optional[float] = None
    feedback: Optional[Dict] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "pronunciation_score": self.pronunciation_score,
            "feedback": self.feedback
        }

class ConversationContext(BaseModel):
    user_id: str
    conversation_id: str
    messages: List[Dict] = []
    current_topic: Optional[str] = None
    user_level: str = "beginner"
    learning_goals: List[str] = []
    last_interaction: datetime = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_message(self, message: ConversationMessage):
        self.messages.append(message.to_dict())
        self.last_interaction = datetime.utcnow()
    
    def get_conversation_history(self, max_messages: int = 10) -> List[Dict]:
        """Get the most recent messages, limited by max_messages"""
        return self.messages[-max_messages:]

class AIConversationService:
    """
    Handles the complete conversation flow with AI, including:
    - Speech-to-Text (STT)
    - Text-to-Speech (TTS)
    - Pronunciation analysis
    - Context management
    - Adaptive learning
    """
    
    def __init__(self):
        self.stt_service = STTService()
        self.tts_service = TTSService()
        self.pronunciation_analyzer = PronunciationAnalyzer()
        self.conversation_contexts: Dict[str, ConversationContext] = {}
    
    async def process_audio_input(
        self, 
        user_id: str, 
        audio_data: bytes, 
        conversation_id: Optional[str] = None
    ) -> Dict:
        """
        Process audio input from user and return AI response with pronunciation feedback
        """
        # Convert speech to text
        text, stt_confidence = await self.stt_service.transcribe(audio_data)
        
        # Get or create conversation context
        context = await self._get_or_create_context(user_id, conversation_id)
        
        # Analyze pronunciation
        pronunciation_result = await self.pronunciation_analyzer.analyze(
            audio_data=audio_data,
            text=text,
            language=context.user_level
        )
        
        # Create user message with pronunciation feedback
        user_message = ConversationMessage(
            role=MessageRole.USER,
            content=text,
            pronunciation_score=pronunciation_result.score,
            feedback=pronunciation_result.feedback
        )
        
        # Add to conversation history
        context.add_message(user_message)
        
        # Generate AI response based on conversation context
        ai_response = await self._generate_ai_response(context)
        
        # Convert AI response to speech
        audio_response = await self.tts_service.synthesize(
            text=ai_response.content,
            voice_id=self._get_voice_for_level(context.user_level)
        )
        
        # Add AI response to context
        context.add_message(ai_response)
        
        # Update conversation context in storage
        await self._save_context(context)
        
        return {
            "text_response": ai_response.content,
            "audio_response": audio_response,
            "pronunciation_feedback": pronunciation_result.feedback,
            "conversation_id": context.conversation_id,
            "user_level": context.user_level,
            "suggested_topics": self._suggest_topics(context)
        }
    
    async def _get_or_create_context(
        self, 
        user_id: str, 
        conversation_id: Optional[str] = None
    ) -> ConversationContext:
        """Get existing or create new conversation context"""
        if conversation_id and conversation_id in self.conversation_contexts:
            return self.conversation_contexts[conversation_id]
            
        # In a real app, load from database
        new_context = ConversationContext(
            user_id=user_id,
            conversation_id=conversation_id or f"conv_{datetime.utcnow().timestamp()}",
            last_interaction=datetime.utcnow()
        )
        
        self.conversation_contexts[new_context.conversation_id] = new_context
        return new_context
    
    async def _generate_ai_response(
        self, 
        context: ConversationContext
    ) -> ConversationMessage:
        """Generate AI response based on conversation context"""
        # In a real implementation, this would call GPT-4o or similar
        # For now, return a simple response
        response_text = "I understand you said: " + context.messages[-1]["content"]
        
        return ConversationMessage(
            role=MessageRole.ASSISTANT,
            content=response_text,
            feedback={"type": "response", "suggestions": ["Try to use more complex sentences"]}
        )
    
    def _get_voice_for_level(self, level: str) -> str:
        """Select appropriate voice based on user level"""
        voices = {
            "beginner": "en-US-GuyNeural",
            "intermediate": "en-US-JennyNeural",
            "advanced": "en-US-AriaNeural"
        }
        return voices.get(level, "en-US-GuyNeural")
    
    def _suggest_topics(self, context: ConversationContext) -> List[str]:
        """Suggest topics based on user level and interests"""
        # Simple implementation - in reality would use ML model
        topics = {
            "beginner": ["Introductions", "Daily routines", "Hobbies"],
            "intermediate": ["Travel", "Technology", "Culture"],
            "advanced": ["Politics", "Science", "Philosophy"]
        }
        return topics.get(context.user_level, topics["beginner"])
    
    async def _save_context(self, context: ConversationContext):
        """Save conversation context to database"""
        # In a real app, save to database
        self.conversation_contexts[context.conversation_id] = context

# Singleton instance
conversation_service = AIConversationService()

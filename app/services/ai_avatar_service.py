import os
import json
import uuid
import random
import logging
import json
from typing import Dict, List, Optional, Any, Union
import google.generativeai as genai
from fastapi import HTTPException
import tempfile

from app.core.config import settings
from app.services.ai.tts import tts_service
from app.services.ai.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class AIAvatarService:
    def __init__(self):
        self.gemini_service = None
        self.default_responses = [
            "Kechirasiz, hozirda AI xizmati mavjud emas. Iltimos, keyinroq urinib ko'ring.",
            "Uzr, men hozir javob bera olmayman. Iltimos, keyinroq qayta urinib ko'ring.",
            "Hozircha sizga yordam bera olmayman. Iltimos, keyinroq harakat qiling."
        ]
        
        # Define available avatars
        self.avatars = {
            "default": {
                "name": "Aisha",
                "style": "friendly_teacher",
                "voice": "uz-UZ-MadinaNeural",
                "greeting": "Salom! Men sizga yordam berishdan xursandman.",
                "language": "uz-UZ",
                "gender": "female"
            },
            "professional": {
                "name": "Dilshod",
                "style": "professional_teacher",
                "voice": "uz-UZ-SardorNeural",
                "greeting": "Assalomu alaykum! Bugun nimalar o'rganamiz?",
                "language": "uz-UZ",
                "gender": "male"
            },
            "english_teacher": {
                "name": "Emma",
                "style": "friendly_teacher",
                "voice": "en-US-JennyNeural",
                "greeting": "Hello! I'm Emma, your English teacher. How can I help you today?",
                "language": "en-US",
                "gender": "female"
            }
        }
        
        # Initialize Gemini service if API key is available
        try:
            if not hasattr(settings, 'GOOGLE_API_KEY') or not settings.GOOGLE_API_KEY:
                raise ValueError("Google API key is not configured")
                
            self.gemini_service = GeminiService()
            logger.info("Gemini service initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini service: {e}")
            logger.warning("AI avatar service will run in limited mode without AI capabilities")

    async def get_response(
        self, 
        message: str, 
        user_id: int, 
        session_id: int, 
        history: List[Dict] = None,
        lesson_context: Dict[str, Any] = None,
        avatar_type: str = "default"
    ) -> Dict[str, Any]:
        """
        Get a response from the AI avatar using Google Gemini
        
        Args:
            message: User's message
            user_id: ID of the user
            session_id: ID of the current session
            history: List of previous interactions in the session
            lesson_context: Context about the current lesson
            avatar_type: Type of avatar to use for the response
            
        Returns:
            Dictionary containing the AI's response text, audio, and metadata
        """
        # If Gemini service is not available, return a default response
        if not self.gemini_service:
            return {
                "text": random.choice(self.default_responses),
                "avatar_type": avatar_type,
                "avatar_name": self.avatars.get(avatar_type, self.avatars["default"])["name"],
                "suggestions": ["Tushundim", "Tushunmadim", "Keyinroq"]
            }
            
        try:
            # Get avatar configuration
            avatar = self.avatars.get(avatar_type, self.avatars["default"])
            
            # Prepare conversation history
            messages = []
            
            # Add system prompt with avatar personality and lesson context
            system_prompt = (
                f"You are {avatar['name']}, a {avatar['style']} AI language teacher. "
                f"You are helping a student learn {avatar['language']} through interactive lessons.\n\n"
            )
            
            if lesson_context:
                system_prompt += f"Current lesson: {lesson_context.get('title', 'General Practice')}\n"
                if 'objectives' in lesson_context:
                    system_prompt += f"Lesson objectives: {', '.join(lesson_context['objectives'])}\n"
                if 'vocabulary' in lesson_context:
                    system_prompt += f"Vocabulary: {', '.join(lesson_context['vocabulary'])}\n"
            
            system_prompt += "\nKeep your responses concise, friendly, and educational. "
            system_prompt += "Correct any mistakes in the student's input and provide explanations when helpful.\n"
            system_prompt += "If the student makes a mistake, gently correct them and provide the right form.\n"
            
            messages.append({"role": "user", "parts": [system_prompt]})
            messages.append({"role": "model", "parts": ["Understood! I'll be a helpful and patient language teacher."]})
            
            # Add history if available
            if history:
                for item in history:
                    if item.get("user_message"):
                        messages.append({"role": "user", "parts": [item["user_message"]]})
                    if item.get("ai_response"):
                        messages.append({"role": "model", "parts": [item["ai_response"]]})
            
            # Add current message
            messages.append({"role": "user", "parts": [message]})
            
            # Get response from Gemini
            response_text = await self.gemini_service.generate_chat_response(messages)
            
            # Generate speech from response
            audio_data = await tts_service.synthesize(
                text=response_text,
                voice_id=avatar["voice"],
                language=avatar["language"],
                gender=avatar.get("gender", "female")
            )
            
            # Save audio to a temporary file and get URL (in a real app, this would be stored in object storage)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                temp_audio.write(audio_data)
                audio_url = f"/api/audio/temp/{os.path.basename(temp_audio.name)}"
            
            # Generate suggestions for the user's next input
            suggestions = await self._generate_suggestions(response_text, avatar["language"])
            
            return {
                "text": response_text,
                "audio_url": audio_url,
                "audio_data": audio_data,  # Include raw audio data for real-time streaming
                "avatar_type": avatar_type,
                "avatar_name": avatar["name"],
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}", exc_info=True)
            return {
                "text": "Uzr, xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.",
                "avatar_type": avatar_type,
                "avatar_name": "Xatolik",
                "suggestions": ["Qayta urinib ko'rish", "Keyinroq", "Yopish"]
            }
    
    async def _generate_suggestions(self, response_text: str, language: str) -> List[str]:
        """Generate suggested responses based on the AI's last message"""
        try:
            prompt = (
                f"Based on this message in {language}, suggest 2-3 short possible responses a student might give. "
                f"Return as a JSON array of strings.\n\n"
                f"Message: {response_text}\n\n"
                "Suggestions:"
            )
            
            # Use the centralized Gemini service
            suggestions_text = await self.gemini_service.generate_chat_response([
                {"role": "user", "parts": [prompt]}
            ])
            
            # Extract JSON array from response
            try:
                # Find JSON array in the response
                import re
                json_match = re.search(r'\[.*\]', suggestions_text, re.DOTALL)
                if json_match:
                    suggestions = json.loads(json_match.group(0))
                    return suggestions[:3]  # Return max 3 suggestions
            except (json.JSONDecodeError, AttributeError):
                pass
                
            # Fallback to default suggestions if JSON parsing fails
            if language.startswith('uz'):
                return ["Tushundim", "Tushunmadim", "Boshqa savol bormi?"]
            else:
                return ["I understand", "I don't understand", "What else?"]
                
        except Exception as e:
            logger.warning(f"Error generating suggestions: {e}")
            if language.startswith('uz'):
                return ["Tushundim", "Tushunmadim", "Boshqa savol bormi?"]
            else:
                return ["I understand", "I don't understand", "What else?"]
    
    def get_avatar_options(self) -> Dict[str, Dict]:
        """
        Return available avatar options with complete details
        
        Returns:
            Dictionary mapping avatar types to their configurations
        """
        return {
            key: {
                "name": value["name"],
                "style": value["style"],
                "voice": value["voice"],
                "language": value["language"],
                "gender": value.get("gender", "neutral"),
                "greeting": value["greeting"],
                "sample_audio_url": f"/api/tts/preview?text={value['greeting']}&voice_id={value['voice']}"
            }
            for key, value in self.avatars.items()
        }
    
    def get_avatar(self, avatar_type: str) -> Dict[str, Any]:
        """
        Get configuration for a specific avatar
        
        Args:
            avatar_type: Type of the avatar to retrieve
            
        Returns:
            Avatar configuration dictionary
        """
        return self.avatars.get(avatar_type, self.avatars["default"])

# Initialize the service
ai_avatar_service = AIAvatarService()

# Export the service instance
__all__ = ["ai_avatar_service"]

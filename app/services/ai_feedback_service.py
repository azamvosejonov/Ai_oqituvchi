import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.services.ai_clients import gemini_model
from app.schemas.ai_feedback import (
    AIFeedbackRequest,
    AIFeedbackResponse,
    FeedbackType,
    GrammarFeedback,
    VocabularyFeedback,
    PronunciationFeedback,
    FluencyFeedback,
    OverallFeedback
)

logger = logging.getLogger(__name__)

class AIFeedbackService:
    """Service for generating AI-powered feedback on user responses"""
    
    async def generate_feedback(
        self, 
        request: AIFeedbackRequest
    ) -> AIFeedbackResponse:
        """
        Generate comprehensive feedback on user's response
        
        Args:
            request: Contains user response, reference text, and context
            
        Returns:
            AIFeedbackResponse with detailed feedback
        """
        if not gemini_model:
            logger.error("Gemini client is not initialized. Cannot generate AI feedback.")
            return AIFeedbackResponse(
                feedback_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                **self._get_default_feedback()
            )

        try:
            # Generate feedback using Gemini
            feedback_prompt = self._create_feedback_prompt(
                user_response=request.user_response,
                reference_text=request.reference_text,
                context=request.context,
                feedback_types=request.feedback_types
            )
            
            # Get feedback from Gemini
            response = await gemini_model.generate_content_async(feedback_prompt)
            feedback_text = response.text
            
            # Parse the structured feedback
            structured_feedback = self._parse_feedback(feedback_text)
            
            return AIFeedbackResponse(
                feedback_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                **structured_feedback
            )
            
        except Exception as e:
            logger.error(f"Error generating AI feedback: {e}", exc_info=True)
            raise
    
    def _create_feedback_prompt(
        self,
        user_response: str,
        reference_text: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        feedback_types: Optional[List[FeedbackType]] = None
    ) -> str:
        """Create a prompt for generating feedback"""
        if feedback_types is None:
            feedback_types = list(FeedbackType)
            
        prompt = """You are an expert language teacher providing feedback on a student's response.
        Please provide detailed, constructive feedback in the following JSON format:
        
        {
            "grammar": {
                "score": 0-100,
                "feedback": "Detailed feedback on grammar",
                "corrections": ["list of corrections"]
            },
            "vocabulary": {
                "score": 0-100,
                "feedback": "Feedback on word choice and vocabulary",
                "suggestions": ["suggested improvements"]
            },
            "pronunciation": {
                "score": 0-100,
                "feedback": "Feedback on pronunciation (if applicable)",
                "tips": ["pronunciation tips"]
            },
            "fluency": {
                "score": 0-100,
                "feedback": "Feedback on fluency and naturalness",
                "suggestions": ["suggestions for improvement"]
            },
            "overall": {
                "score": 0-100,
                "feedback": "Overall feedback and suggestions",
                "next_steps": ["recommended next steps"]
            }
        }
        """
        
        prompt += f"\n\nStudent's response: {user_response}"
        
        if reference_text:
            prompt += f"\nReference/Expected response: {reference_text}"
            
        if context:
            prompt += "\n\nContext: "
            for key, value in context.items():
                prompt += f"\n- {key}: {value}"
                
        prompt += "\n\nPlease provide your feedback in a supportive and encouraging manner."
        
        return prompt
    
    def _parse_feedback(self, feedback_text: str) -> Dict[str, Any]:
        """Parse the feedback text into structured format"""
        # This is a simplified version - in practice, you'd want to parse the JSON
        # and handle potential parsing errors
        try:
            import json
            feedback_data = json.loads(feedback_text)
            
            return {
                "grammar": GrammarFeedback(**feedback_data.get("grammar", {})),
                "vocabulary": VocabularyFeedback(**feedback_data.get("vocabulary", {})),
                "pronunciation": PronunciationFeedback(**feedback_data.get("pronunciation", {})),
                "fluency": FluencyFeedback(**feedback_data.get("fluency", {})),
                "overall": OverallFeedback(**feedback_data.get("overall", {}))
            }
        except Exception as e:
            logger.warning(f"Failed to parse feedback: {e}")
            # Return default feedback if parsing fails
            return self._get_default_feedback()
    
    def _get_default_feedback(self) -> Dict[str, Any]:
        """Return default feedback in case of parsing errors"""
        return {
            "grammar": GrammarFeedback(
                score=0,
                feedback="Unable to analyze grammar at this time.",
                corrections=[]
            ),
            "vocabulary": VocabularyFeedback(
                score=0,
                feedback="Unable to analyze vocabulary at this time.",
                suggestions=[]
            ),
            "pronunciation": PronunciationFeedback(
                score=0,
                feedback="Unable to analyze pronunciation at this time.",
                tips=[]
            ),
            "fluency": FluencyFeedback(
                score=0,
                feedback="Unable to analyze fluency at this time.",
                suggestions=[]
            ),
            "overall": OverallFeedback(
                score=0,
                feedback="We encountered an issue analyzing your response. Please try again.",
                next_steps=["Try rephrasing your response"]
            )
        }

# Initialize the service
ai_feedback_service = AIFeedbackService()

__all__ = ["ai_feedback_service"]

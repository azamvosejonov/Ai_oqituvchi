import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables
load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_AI_API_KEY not found in environment variables")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def generate_response(self, prompt: str, context: str = None) -> str:
        """
        Generate a response using Google's Gemini model
        
        Args:
            prompt: User's input prompt
            context: Optional context for the conversation
            
        Returns:
            str: Generated response from Gemini
        """
        try:
            # Combine context and prompt if context is provided
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating AI response: {str(e)}"
            )

# Create a singleton instance
gemini_service = GeminiService()

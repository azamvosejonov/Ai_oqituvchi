"""
Google Gemini AI servisi uchun asosiy modul.
"""
import os
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

# .env faylidan o'qib olish
load_dotenv()

class GeminiService:
    """Google Gemini API bilan ishlash uchun asosiy servis."""
    
    def __init__(self):
        """Google Gemini API bilan ulanishni o'rnatish."""
        self.api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_AI_API_KEY muhit o'zgaruvchisi topilmadi. .env faylini tekshiring.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Matn generatsiya qilish uchun asosiy metod.
        
        Args:
            prompt: AI ga beriladigan so'rov matni
            **kwargs: Qo'shimcha parametrlar (temperature, max_tokens, va h.k.)
            
        Returns:
            str: AI tomonidan generatsiya qilingan javob
        """
        try:
            response = await self.model.generate_content_async(
                prompt,
                **kwargs
            )
            return response.text
        except Exception as e:
            raise Exception(f"AI xizmatida xatolik: {str(e)}")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Chat rejimida suhbat qilish uchun metod.
        
        Args:
            messages: Suhbat tarixi [{"role": "user"|"model", "content": "..."}]
            **kwargs: Qo'shimcha parametrlar
            
        Returns:
            str: AI javobi
        """
        try:
            chat = self.model.start_chat(history=[])
            
            # Chat tarixini yuklash
            for msg in messages[:-1]:  # Oxirgi xabarni alohida yuboramiz
                if msg["role"].lower() == "user":
                    chat.send_message(msg["content"], stream=False)
                else:
                    chat.history.append(
                        genai.types.content.Part(
                            text=msg["content"],
                            role="model"
                        )
                    )
            
            # Yangi xabarni yuborish
            response = await chat.send_message_async(
                messages[-1]["content"],
                **kwargs
            )
            return response.text
            
        except Exception as e:
            raise Exception(f"Chat xizmatida xatolik: {str(e)}")

# Singleton pattern orqali bitta instansiyani yaratish
gemini_service = GeminiService()

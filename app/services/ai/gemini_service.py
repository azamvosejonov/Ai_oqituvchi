import os
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    """Google Gemini API orqali video tahlili va savol generatsiyasi"""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.model_name = getattr(settings, "GEMINI_MODEL", "gemini-1.5-pro")
        self._configure()
    
    def _configure(self):
        """API konfiguratsiyasi"""
        if not self.api_key:
            logger.warning("Google API kaliti topilmadi. .env faylida GOOGLE_API_KEY ni tekshiring.")
            return
        genai.configure(api_key=self.api_key)
    
    async def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """Videoni tahlil qilish"""
        if not self.api_key:
            raise ValueError("Google API kaliti topilmadi")
        
        try:
            model = genai.GenerativeModel(self.model_name)
            
            # Videoni yuklash va tahlil qilish
            response = model.generate_content([
                "Videoni tahlil qiling va quyidagi ma'lumotlarni JSON formatida qaytaring:"
                "1. Video mavzusi"
                "2. Asosiy mavzular royxati"
                "3. Muhim nuqtalar"
                "4. Tavsiya qilingan savollar",
                genai.upload_file(video_path)
            ])
            
            return {
                "status": "completed",
                "analysis": response.text,
                "model": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Video tahlilida xatolik: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def generate_questions(self, content: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        """Kontent asosida savollar generatsiya qilish"""
        if not self.api_key:
            raise ValueError("Google API kaliti topilmadi")
        
        try:
            model = genai.GenerativeModel(self.model_name)
            
            prompt = f"""
            Quyidagi kontent asosida {num_questions} ta test savig'ini generatsiya qiling:
            
            {content}
            
            Har bir savol uchun quyidagi formatda javob bering:
            {{
                "question": "Savol matni",
                "type": "multiple_choice | true_false | short_answer",
                "options": ["Variant 1", "Variant 2", ...],  // Faqat multiple_choice uchun
                "correct_answer": "To'g'ri javob",
                "explanation": "Tushuntirish",
                "difficulty": "easy | medium | hard"
            }}
            """
            
            response = model.generate_content(prompt)
            return self._parse_questions(response.text)
            
        except Exception as e:
            logger.error(f"Savol generatsiyasida xatolik: {str(e)}")
            raise
    
    def _parse_questions(self, text: str) -> List[Dict[str, Any]]:
        """Javobni JSON formatiga o'tkazish"""
        # Oddiy JSON pars qilish
        import json
        try:
            # JSON qismini topish
            start = text.find('[')
            end = text.rfind(']') + 1
            json_str = text[start:end]
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("Javob JSON formatida emas, qo'lda tahlil qilinmoqda")
            return [{"question": "Javob tahlil qilinmoqda...", "type": "short_answer"}]

    async def generate_chat_response(self, messages: List[Dict[str, Any]]) -> str:
        """Suhbat uchun javob generatsiya qilish"""
        if not self.api_key:
            raise ValueError("Google API kaliti topilmadi")

        try:
            model = genai.GenerativeModel(self.model_name)
            response = await model.generate_content_async(
                contents=messages,
                generation_config={
                    "max_output_tokens": 1024,
                    "temperature": 0.7,
                }
            )
            return response.text
        except Exception as e:
            logger.error(f"Suhbat javobini generatsiya qilishda xatolik: {str(e)}")
            raise

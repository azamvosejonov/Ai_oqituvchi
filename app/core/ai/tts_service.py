"""
Text-to-Speech (TTS) xizmati.
"""
import os
import tempfile
from pathlib import Path
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import io

class TTSService:
    """Matnni ovozga aylantirish uchun servis."""
    
    def __init__(self, lang: str = 'uz'):
        """TTS servisini ishga tushirish.
        
        Args:
            lang: Til kodi (masalan, 'uz', 'en', 'ru')
        """
        self.lang = lang
    
    async def text_to_speech(self, text: str, slow: bool = False) -> bytes:
        """Matnni ovozga aylantirish.
        
        Args:
            text: Ovozga aylantiriladigan matn
            slow: Sekinroq talaffuz qilish uchun
            
        Returns:
            bytes: Audio fayl ma'lumotlari (MP3 formatida)
        """
        try:
            # gTTS orqali audio generatsiya qilish
            tts = gTTS(text=text, lang=self.lang, slow=slow)
            
            # Audio ma'lumotlarini bytelarga yozish
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.read()
            
        except Exception as e:
            raise Exception(f"TTS xatolik: {str(e)}")
    
    async def save_speech(self, text: str, output_path: str, slow: bool = False) -> str:
        """Ovozni faylga saqlash.
        
        Args:
            text: Ovozga aylantiriladigan matn
            output_path: Saqlanadigan fayl yo'li
            slow: Sekinroq talaffuz qilish uchun
            
        Returns:
            str: Saqlangan fayl yo'li
        """
        try:
            audio_data = await self.text_to_speech(text, slow)
            
            # Faylga yozish
            with open(output_path, 'wb') as f:
                f.write(audio_data)
                
            return output_path
            
        except Exception as e:
            raise Exception(f"Ovoz faylini saqlashda xatolik: {str(e)}")

# Standart foydalanish uchun instance
tts_service = TTSService(lang='uz')

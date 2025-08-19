"""
Speech-to-Text (STT) xizmati.
"""
import os
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
import io

class STTService:
    """Ovozni matnga aylantirish uchun servis."""
    
    def __init__(self, language: str = 'uz-UZ'):
        """STT servisini ishga tushirish.
        
        Args:
            language: Til kodi (masalan, 'uz-UZ', 'en-US', 'ru-RU')
        """
        self.language = language
        self.recognizer = sr.Recognizer()
    
    async def speech_to_text(self, audio_data: bytes, audio_format: str = 'wav') -> str:
        """Ovoz ma'lumotlarini matnga aylantirish.
        
        Args:
            audio_data: Ovoz ma'lumotlari (baytlar ko'rinishida)
            audio_format: Audio format ('wav', 'mp3', va h.k.)
            
        Returns:
            str: Tan olingan matn
        """
        try:
            # Audio ma'lumotlarini AudioData ga o'tkazish
            audio_file = io.BytesIO(audio_data)
            
            # Agar mp3 bo'lsa, wav ga o'tkazish kerak
            if audio_format.lower() == 'mp3':
                audio = AudioSegment.from_mp3(audio_file)
                audio_file = io.BytesIO()
                audio.export(audio_file, format='wav')
                audio_file.seek(0)
            
            # Audio faylni o'qish
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            
            # Google Web Speech API orqali matnni olish
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text
            
        except sr.UnknownValueError:
            raise Exception("Audio tushunarsiz yoki bo'sh")
        except sr.RequestError as e:
            raise Exception(f"Google Web Speech API xatosi; {e}")
        except Exception as e:
            raise Exception(f"STT xatolik: {str(e)}")
    
    async def transcribe_audio_file(self, file_path: str) -> str:
        """Audio faylidan matn olish.
        
        Args:
            file_path: Audio fayl yo'li
            
        Returns:
            str: Tan olingan matn
        """
        try:
            # Fayl kengaytmasini olish
            file_ext = os.path.splitext(file_path)[1].lower().replace('.', '')
            
            # Faylni o'qib olish
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            
            # Transkripsiya qilish
            return await self.speech_to_text(audio_data, file_ext)
            
        except Exception as e:
            raise Exception(f"Audio faylni o'qishda xatolik: {str(e)}")

# Standart foydalanish uchun instancestt_service = STTService(language='uz-UZ')

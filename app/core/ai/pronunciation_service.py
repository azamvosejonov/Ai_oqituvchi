"""
Talaffuzni baholash xizmati.
"""
import difflib
import numpy as np
from typing import Tuple, Dict, Any

class PronunciationService:
    """Talaffuzni baholash uchun servis."""
    
    def __init__(self, similarity_threshold: float = 0.7):
        """Talaffuz baholash servisini ishga tushirish.
        
        Args:
            similarity_threshold: Talaffuzning to'g'ri deb hisoblanishi uchun minimal o'xshashlik darajasi (0.0 dan 1.0 gacha)
        """
        self.similarity_threshold = similarity_threshold
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Ikki matn orasidagi o'xshashlik darajasini hisoblash.
        
        Args:
            text1: Birinchi matn
            text2: Ikkinchi matn
            
        Returns:
            float: 0.0 (umumiy o'xshamaydi) dan 1.0 gacha (aynan bir xil)
        """
        # Kichik harflarga o'tkazish va bosh-ohanglarni olib tashlash
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        # Matnlar bo'sh bo'lsa
        if not text1 or not text2:
            return 0.0
            
        # Aniq mos kelish holati
        if text1 == text2:
            return 1.0
            
        # Levenshtein masosiga asoslangan o'xshashlik
        return difflib.SequenceMatcher(None, text1, text2).ratio()
    
    def evaluate_pronunciation(self, reference_text: str, recognized_text: str) -> Dict[str, Any]:
        """Talaffuzni baholash.
        
        Args:
            reference_text: To'g'ri variant (dastur tomonidan kutilayotgan matn)
            recognized_text: Foydalanuvchi tomonidan aytilgan va tan olingan matn
            
        Returns:
            Dict: Baholash natijalari
        """
        # O'xshashlik darajasini hisoblash
        similarity = self.calculate_similarity(reference_text, recognized_text)
        
        # Asosiy so'zlar bo'yicha tekshirish
        ref_words = set(reference_text.lower().split())
        rec_words = set(recognized_text.lower().split())
        
        # Umumiy va to'g'ri topilgan so'zlar
        common_words = ref_words.intersection(rec_words)
        
        # Baholash natijalari
        result = {
            'similarity_score': float(similarity),
            'is_correct': similarity >= self.similarity_threshold,
            'reference_text': reference_text,
            'recognized_text': recognized_text,
            'word_accuracy': {
                'total_words': len(ref_words),
                'correct_words': len(common_words),
                'accuracy_percentage': (len(common_words) / len(ref_words)) * 100 if ref_words else 0.0,
                'missing_words': list(ref_words - rec_words),
                'extra_words': list(rec_words - ref_words)
            },
            'feedback': self._generate_feedback(reference_text, recognized_text, similarity)
        }
        
        return result
    
    def _generate_feedback(self, reference: str, recognized: str, similarity: float) -> str:
        """Talaffuz bo'yicha fikr-mulohaza generatsiya qilish.
        
        Args:
            reference: To'g'ri variant
            recognized: Tan olingan variant
            similarity: O'xshashlik darajasi
            
        Returns:
            str: Fikr-mulohaza matni
        """
        if similarity >= 0.9:
            return "Ajoyib! Siz bu jumlani juda yaxshi talaffuz qildingiz."
        elif similarity >= 0.7:
            return "Yaxshi! Ammo ba'zi so'zlarni yanada aniqroq talaffuz qilishga harakat qiling."
        elif similarity >= 0.5:
            return "Yordam berishim mumkinmi? Keling, qaytadan urinib ko'ramiz."
        else:
            return "Iltimos, qaytadan urinib ko'ring. Men sizni tushunolmadim."

# Standart foydalanish uchun instance
pronunciation_service = PronunciationService()

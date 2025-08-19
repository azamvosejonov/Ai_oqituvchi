from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, ConfigDict

# Video tahlili uchun asosiy schema'lar

class VideoAnalysisBase(BaseModel):
    title: str = Field(..., max_length=255, description="Video sarlavhasi")
    description: Optional[str] = Field(None, description="Video haqida qisqacha")
    video_url: str = Field(..., description="Video fayl manzili")
    language: str = Field("uz", description="Video tili")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Qo'shimcha ma'lumotlar")

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

class VideoAnalysisCreate(VideoAnalysisBase):
    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

class VideoAnalysisUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255, description="Yangilangan sarlavha")
    description: Optional[str] = Field(None, description="Yangilangan tavsif")
    is_processed: Optional[bool] = Field(None, description="Tahlil qilinganligi")
    processing_status: Optional[str] = Field(None, description="Tahlil holati")

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

class VideoSegmentBase(BaseModel):
    start_time: int = Field(..., ge=0, description="Segment boshlanish vaqti (sekundda)")
    end_time: int = Field(..., ge=0, description="Segment tugash vaqti (sekundda)")
    text: Optional[str] = Field(None, description="Transkripsiya matni")
    summary: Optional[str] = Field(None, description="Qisqacha mazmuni")

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

class VideoQuestionBase(BaseModel):
    question_type: str = Field(..., description="Savol turi (multiple_choice, true_false, short_answer)")
    question_text: str = Field(..., description="Savol matni")
    options: Optional[List[str]] = Field(None, description="Javob variantlari")
    correct_answer: Any = Field(..., description="To'g'ri javob")
    explanation: Optional[str] = Field(None, description="Tushuntirish")
    difficulty: str = Field("medium", description="Savel qiyinlik darajasi (easy, medium, hard)")

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

# Javob uchun schema'lar
class VideoQuestion(VideoQuestionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

class VideoSegment(VideoSegmentBase):
    id: int
    questions: List[VideoQuestion] = []

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

class VideoAnalysis(VideoAnalysisBase):
    id: int
    owner_id: int
    is_processed: bool
    processing_status: str
    duration: Optional[int]
    thumbnail_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    segments: List[VideoSegment] = []

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

# Video yuklash uchun schema
class VideoUploadResponse(BaseModel):
    id: int
    upload_url: Optional[HttpUrl] = None
    status: str
    message: Optional[str] = None

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

# Video tahlili natijalari
class AnalysisResult(BaseModel):
    status: str
    progress: int = Field(0, ge=0, le=100, description="Tahlil jarayoni % da")
    segments_processed: int = 0
    total_segments: int = 0
    questions_generated: int = 0

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

# Video asosida test generatsiya so'rovi
class GenerateTestRequest(BaseModel):
    difficulty: str = Field("medium", description="Test qiyinlik darajasi")
    num_questions: int = Field(10, ge=1, le=50, description="Generatsiya qilinadigan savollar soni")
    question_types: List[str] = Field(
        ["multiple_choice", "true_false", "short_answer"],
        description="Qanday turdagi savollar generatsiya qilinsin"
    )

    class Config:
        model_config = ConfigDict(
            from_attributes=True,
        )

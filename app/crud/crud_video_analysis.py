from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import and_

from app import models
from app.schemas import video_analysis as schemas
from app.crud.base import CRUDBase

class CRUDVideoAnalysis(CRUDBase[models.VideoAnalysis, schemas.VideoAnalysisCreate, schemas.VideoAnalysisUpdate]):
    """Video tahlili uchun CRUD operatsiyalari"""
    
    def create_with_owner(
        self, db: Session, *, obj_in: schemas.VideoAnalysisCreate, owner_id: int
    ) -> models.VideoAnalysis:
        """Yangi video tahlili yaratish"""
        db_obj = models.VideoAnalysis(
            **obj_in.dict(),
            owner_id=owner_id,
            is_processed=False,
            processing_status="pending"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.VideoAnalysis]:
        """Foydalanuvchining barcha video tahlillarini olish"""
        return (
            db.query(self.model)
            .filter(models.VideoAnalysis.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_processing_status(
        self, db: Session, *, db_obj: models.VideoAnalysis, status: str, message: str = None
    ) -> models.VideoAnalysis:
        """Video tahlil holatini yangilash"""
        db_obj.processing_status = status
        if message:
            db_obj.metadata = db_obj.metadata or {}
            db_obj.metadata["last_message"] = message
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def mark_as_processed(
        self, db: Session, *, db_obj: models.VideoAnalysis, duration: int = None
    ) -> models.VideoAnalysis:
        """Video tahlil qilingan deb belgilash"""
        db_obj.is_processed = True
        db_obj.processing_status = "completed"
        if duration is not None:
            db_obj.duration = duration
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

class CRUDVideoSegment(CRUDBase[models.VideoSegment, schemas.VideoSegmentBase, schemas.VideoSegmentBase]):
    """Video segmentlari uchun CRUD operatsiyalari"""
    
    def create_with_analysis(
        self, db: Session, *, obj_in: schemas.VideoSegmentBase, video_analysis_id: int
    ) -> models.VideoSegment:
        """Yangi video segmenti qo'shish"""
        db_obj = models.VideoSegment(
            **obj_in.dict(),
            video_analysis_id=video_analysis_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_analysis(
        self, db: Session, *, video_analysis_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.VideoSegment]:
        """Video tahliliga tegishli segmentlarni olish"""
        return (
            db.query(self.model)
            .filter(models.VideoSegment.video_analysis_id == video_analysis_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

class CRUDVideoQuestion(CRUDBase[models.VideoQuestion, schemas.VideoQuestionBase, schemas.VideoQuestionBase]):
    """Video savollari uchun CRUD operatsiyalari"""
    
    def create_with_segment(
        self, db: Session, *, obj_in: schemas.VideoQuestionBase, segment_id: int
    ) -> models.VideoQuestion:
        """Yangi savol qo'shish"""
        db_obj = models.VideoQuestion(
            **obj_in.dict(),
            segment_id=segment_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_segment(
        self, db: Session, *, segment_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.VideoQuestion]:
        """Segmentga tegishli savollarni olish"""
        return (
            db.query(self.model)
            .filter(models.VideoQuestion.segment_id == segment_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

# CRUD ob'ektlarini yaratamiz
class CRUDVideoQuestion(CRUDBase[models.VideoQuestion, schemas.VideoQuestionBase, schemas.VideoQuestionBase]):
    def get_by_video(
        self, db: Session, *, video_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.VideoQuestion]:
        return (
            db.query(self.model)
            .join(models.VideoSegment)
            .filter(models.VideoSegment.video_analysis_id == video_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_video(
        self, db: Session, *, obj_in: schemas.VideoQuestionCreate, video_id: int
    ) -> models.VideoQuestion:
        db_obj = models.VideoQuestion(
            **obj_in.dict(),
            video_id=video_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

video_analysis = CRUDVideoAnalysis(models.VideoAnalysis)
video_segment = CRUDVideoSegment(models.VideoSegment)
video_question = CRUDVideoQuestion(models.VideoQuestion)

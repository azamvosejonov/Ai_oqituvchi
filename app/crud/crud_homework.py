from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models import Homework
from app.models.homework import HomeworkSubmission as HomeworkSubmissionModel, HomeworkStatus
from app.schemas.homework import (
    HomeworkCreate,
    HomeworkUpdate,
    HomeworkSubmission,
    HomeworkSubmissionCreate,
    HomeworkSubmissionUpdate,
)


class CRUDHomework(CRUDBase[Homework, HomeworkCreate, HomeworkUpdate]):
    def create(self, db: Session, *, obj_in: HomeworkCreate, created_by: int) -> Homework:
        # Use model_dump() which is the Pydantic v2 replacement for dict()
        # It preserves datetime objects by default.
        obj_in_data = obj_in.model_dump()
        # The 'oral_assignment' is part of the schema but not the model itself.
        # It's handled separately in the service layer, so we pop it here.
        obj_in_data.pop("oral_assignment", None)
        db_obj = self.model(**obj_in_data, created_by=created_by)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_lesson(
        self, db: Session, *, lesson_id: int, skip: int = 0, limit: int = 100
    ) -> List[Homework]:
        return (
            db.query(self.model)
            .filter(Homework.lesson_id == lesson_id)
            .order_by(Homework.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_multi_by_due_date(
        self, db: Session, *, due_date: datetime, skip: int = 0, limit: int = 100
    ) -> List[Homework]:
        return (
            db.query(self.model)
            .filter(Homework.due_date <= due_date)
            .order_by(Homework.due_date.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDHomeworkSubmission(CRUDBase[HomeworkSubmissionModel, HomeworkSubmissionCreate, HomeworkSubmissionUpdate]):
    def get_by_student_and_homework(
        self, db: Session, *, student_id: int, homework_id: int
    ) -> Optional[HomeworkSubmissionModel]:
        return (
            db.query(self.model)
            .filter(
                self.model.student_id == student_id,
                self.model.homework_id == homework_id,
            )
            .order_by(self.model.submitted_at.desc())
            .first()
        )

    def create_with_student(
        self, db: Session, *, obj_in: HomeworkSubmissionCreate, student_id: int
    ) -> HomeworkSubmissionModel:
        db_obj = HomeworkSubmissionModel(
            **obj_in.model_dump(),
            student_id=student_id,
            status=HomeworkStatus.SUBMITTED
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_pending_with_student(
        self, db: Session, *, homework_id: int, student_id: int
    ) -> HomeworkSubmissionModel:
        db_obj = HomeworkSubmissionModel(
            homework_id=homework_id,
            student_id=student_id,
            status=HomeworkStatus.PENDING,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def grade_submission(
        self,
        db: Session,
        *,
        db_obj: HomeworkSubmissionModel,
        feedback: str,
        score: int,
        graded_by: int | None = None,
    ) -> HomeworkSubmissionModel:
        db_obj.status = HomeworkStatus.GRADED
        db_obj.feedback = feedback
        db_obj.score = score
        db_obj.graded_at = datetime.utcnow()
        if graded_by is not None:
            db_obj.graded_by = graded_by
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def submit(
        self,
        db: Session,
        *,
        db_obj: HomeworkSubmissionModel,
        content: str | None = None,
        file_url: str | None = None,
        audio_url: str | None = None,
        metadata: dict | None = None,
    ) -> HomeworkSubmissionModel:
        if content is not None:
            db_obj.content = content
        if file_url is not None:
            db_obj.file_url = file_url
        if audio_url is not None:
            db_obj.audio_url = audio_url
        if metadata is not None:
            db_obj.metadata_ = metadata
        db_obj.status = HomeworkStatus.SUBMITTED
        db_obj.submitted_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_student(
        self, db: Session, *, student_id: int, skip: int = 0, limit: int = 100
    ) -> list[HomeworkSubmissionModel]:
        return (
            db.query(self.model)
            .filter(self.model.student_id == student_id)
            .order_by(self.model.submitted_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


homework = CRUDHomework(Homework)
homework_submission = CRUDHomeworkSubmission(HomeworkSubmissionModel)

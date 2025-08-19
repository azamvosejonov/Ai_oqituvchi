from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from app.models import Test,  TestQuestion, User
from app.models.test import TestSection, TestAttempt, TestAnswer
from app.schemas.test import (
    TestCreate, TestUpdate, TestSectionCreate, TestSectionUpdate,
    TestQuestionCreate, TestQuestionUpdate, TestAttemptCreate, TestAnswerCreate
)
from app.crud.base import CRUDBase
from fastapi.encoders import jsonable_encoder

class CRUDTest(CRUDBase[Test, TestCreate, TestUpdate]):
    def create(self, db: Session, *, obj_in: TestCreate) -> Test:
        obj_in_data = jsonable_encoder(obj_in)
        if 'test_type' in obj_in_data:
            # Ensure stored value matches schema enum values (lowercase)
            if isinstance(obj_in_data['test_type'], str):
                obj_in_data['test_type'] = obj_in_data['test_type'].lower()
            else:
                # In case an Enum or other type sneaks in, cast to str then lower
                obj_in_data['test_type'] = str(obj_in_data['test_type']).lower()
        
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, test_type: str = None
    ) -> List[Test]:
        query = db.query(self.model)
        if test_type:
            query = query.filter(Test.test_type == test_type)
        return query.offset(skip).limit(limit).all()

    def get_with_sections(self, db: Session, id: int) -> Optional[Test]:
        return db.query(Test).filter(Test.id == id).first()

class CRUDTestSection(CRUDBase[TestSection, TestSectionCreate, TestSectionUpdate]):
    def create(self, db: Session, *, obj_in: TestSectionCreate) -> TestSection:
        obj_in_data = jsonable_encoder(obj_in)
        if 'section_type' in obj_in_data:
            # Ensure stored value matches schema enum values (lowercase)
            if isinstance(obj_in_data['section_type'], str):
                obj_in_data['section_type'] = obj_in_data['section_type'].lower()
            else:
                obj_in_data['section_type'] = str(obj_in_data['section_type']).lower()
        
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_test(
        self, db: Session, *, test_id: int, skip: int = 0, limit: int = 100
    ) -> List[TestSection]:
        return (
            db.query(self.model)
            .filter(TestSection.test_id == test_id)
            .order_by(TestSection.order_index)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete(self, db: Session, *, id: int) -> Optional[TestSection]:
        """Delete a test section by ID and return the deleted object or None if not found."""
        return self.remove(db, id=id)

class CRUDTestQuestion(CRUDBase[TestQuestion, TestQuestionCreate, TestQuestionUpdate]):
    def get_multi_by_section(
        self, db: Session, *, section_id: int, skip: int = 0, limit: int = 100
    ) -> List[TestQuestion]:
        return (
            db.query(self.model)
            .filter(TestQuestion.section_id == section_id)
            .order_by(TestQuestion.order_index)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete(self, db: Session, *, id: int) -> Optional[TestQuestion]:
        """Delete a test question by ID and return the deleted object or None if not found."""
        return self.remove(db, id=id)

class CRUDTestAttempt(CRUDBase[TestAttempt, TestAttemptCreate, dict]):
    def get_in_progress_by_user_and_test(self, db: Session, *, user_id: int, test_id: int) -> Optional[TestAttempt]:
        return db.query(self.model).filter(
            TestAttempt.user_id == user_id, 
            TestAttempt.test_id == test_id, 
            TestAttempt.is_completed == False
        ).first()

    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[TestAttempt]:
        return (
            db.query(self.model)
            .filter(TestAttempt.user_id == user_id)
            .order_by(TestAttempt.start_time.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def complete(
        self, db: Session, *, db_obj: TestAttempt, total_score: float, max_score: float
    ) -> TestAttempt:
        db_obj.is_completed = True
        db_obj.end_time = datetime.utcnow()
        db_obj.time_spent_seconds = int((db_obj.end_time - db_obj.start_time).total_seconds())
        db_obj.total_score = total_score
        db_obj.max_score = max_score
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

class CRUDTestAnswer(CRUDBase[TestAnswer, TestAnswerCreate, dict]):
    def create_multi_for_attempt(
        self, db: Session, *, answers: List[TestAnswerCreate], attempt_id: int
    ) -> List[TestAnswer]:
        db_answers = [
            TestAnswer(**answer.dict(), attempt_id=attempt_id)
            for answer in answers
        ]
        db.bulk_save_objects(db_answers)
        db.commit()
        # We don't have the created objects with IDs here, so we return the input
        # A more complex implementation might query them back.
        return answers

    def get_by_attempt(
        self, db: Session, *, attempt_id: int, skip: int = 0, limit: int = 100
    ) -> List[TestAnswer]:
        return (
            db.query(self.model)
            .filter(TestAnswer.attempt_id == attempt_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def grade_answers(
        self, db: Session, *, attempt_id: int, answers: List[Dict[str, Any]]
    ) -> None:
        # This is a simplified grading logic
        # You might want to implement more complex grading based on question types
        for answer_data in answers:
            answer = db.query(TestAnswer).filter(
                TestAnswer.id == answer_data["id"],
                TestAnswer.attempt_id == attempt_id
            ).first()
            
            if answer:
                question = answer.question
                correct_answers = question.question_data.get("correct_answers", [])
                user_answers = answer.answer_data.get("answers", [])
                
                # Simple exact match grading
                is_correct = set(user_answers) == set(correct_answers)
                score = question.marks if is_correct else 0
                
                answer.is_correct = is_correct
                answer.score = score
                answer.feedback = "Correct!" if is_correct else "Incorrect answer."
                
                db.add(answer)
        
        db.commit()

# Initialize CRUD instances
test = CRUDTest(Test)
test_section = CRUDTestSection(TestSection)
test_question = CRUDTestQuestion(TestQuestion)
test_attempt = CRUDTestAttempt(TestAttempt)
test_answer = CRUDTestAnswer(TestAnswer)

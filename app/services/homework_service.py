import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app import models, schemas
from app.crud import crud_homework, crud_user
# from app.core.ai.assessment import assess_written_response
from app.core.config import settings
from app.models.homework import (
    OralAssignment,
    HomeworkSubmission as HomeworkSubmissionModel,
    HomeworkStatus,
)
from app.schemas.homework import OralAssignmentBase

logger = logging.getLogger(__name__)

class HomeworkService:
    """Service for handling homework-related business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_homework(
        self, 
        homework_in: schemas.HomeworkCreate,
        teacher_id: int
    ) -> models.Homework:
        """Create a new homework assignment"""
        try:
            # Pass the schema object directly to the CRUD layer
            homework = crud_homework.homework.create(
                self.db, 
                obj_in=homework_in, # Pass the schema directly
                created_by=teacher_id
            )
            
            # Handle oral assignment if needed
            if homework_in.homework_type == "oral" and homework_in.oral_assignment:
                self._create_oral_assignment(
                    homework_id=homework.id,
                    oral_assignment=homework_in.oral_assignment
                )
            
            # Assign to students if published
            if homework.is_published:
                self._assign_to_students(homework)
            
            return homework
            
        except Exception as e:
            logger.error(f"Error creating homework: {e}", exc_info=True)
            raise
    
    def _create_oral_assignment(
        self, 
        homework_id: int, 
        oral_assignment: OralAssignmentBase
    ) -> OralAssignment:
        """Create an oral assignment record"""
        oral_assignment_data = oral_assignment.dict()
        oral_assignment_data["homework_id"] = homework_id
        return OralAssignment(**oral_assignment_data)
    
    def _assign_to_students(self, homework: models.Homework) -> None:
        """Assign homework to all students in the course"""
        # Get all students in the course
        students = crud_user.user.get_students_in_course(
            self.db, 
            course_id=homework.course_id
        )
        
        # Create pending submission records for each student
        for student in students:
            crud_homework.homework_submission.create_pending_with_student(
                self.db,
                homework_id=homework.id,
                student_id=student.id,
            )
    
    async def submit_homework(
        self,
        homework_id: int,
        student_id: int,
        submission: Dict[str, Any]
    ) -> HomeworkSubmissionModel:
        """Submit homework using HomeworkSubmission model"""
        # Find or create a submission for the student/homework
        sub = crud_homework.homework_submission.get_by_student_and_homework(
            self.db,
            student_id=student_id,
            homework_id=homework_id,
        )
        if not sub:
            sub = crud_homework.homework_submission.create_pending_with_student(
                self.db,
                homework_id=homework_id,
                student_id=student_id,
            )

        # Map generic submission payload to model fields
        content = None
        file_url = None
        audio_url = None
        metadata = None
        if isinstance(submission, dict):
            content = submission.get("text") or submission.get("content")
            file_url = submission.get("file_url")
            audio_url = submission.get("audio_url")
            metadata = submission.get("metadata")

        sub = crud_homework.homework_submission.submit(
            self.db,
            db_obj=sub,
            content=content,
            file_url=file_url,
            audio_url=audio_url,
            metadata=metadata,
        )

        # Auto-grade if possible
        if sub.homework and str(sub.homework.homework_type) == "written":
            pass
        
        return sub
    
    async def _auto_grade_written_homework(
        self, 
        submission: HomeworkSubmissionModel
    ) -> None:
        """Automatically grade written homework using AI"""
        try:
            # Get the homework
            homework = submission.homework
            
            # Generate assessment using AI
            # assessment = await assess_written_response(
            #     response=submission.content or "",
            #     prompt=homework.instructions or "",
            #     criteria=(homework.metadata_ or {}).get("grading_criteria", {})
            # )
            # crud_homework.homework_submission.grade_submission(
            #     self.db,
            #     db_obj=submission,
            #     feedback=assessment.get("feedback", ""),
            #     score=assessment.get("score", 0)
            # )
            
        except Exception as e:
            logger.error(f"Error auto-grading homework: {e}", exc_info=True)
    
    def get_student_homework(
        self,
        student_id: int,
        status: Optional[str] = None,
        course_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get homework assignments for a student"""
        query = self.db.query(HomeworkSubmissionModel).filter(
            HomeworkSubmissionModel.student_id == student_id
        )
        
        if status:
            try:
                enum_status = HomeworkStatus(status)
                query = query.filter(HomeworkSubmissionModel.status == enum_status)
            except Exception:
                pass
            
        if course_id:
            query = query.join(
                models.Homework
            ).filter(
                models.Homework.course_id == course_id
            )
        
        assignments = query.offset(skip).limit(limit).all()
        
        # Format the response
        result = []
        for submission in assignments:
            hw = submission.homework
            result.append({
                "id": submission.id,
                "homework_id": hw.id,
                "title": hw.title,
                "type": hw.homework_type,
                "status": submission.status,
                "due_date": hw.due_date,
                "submitted_at": submission.submitted_at,
                "score": submission.score,
                "max_score": hw.max_score,
                "course": {
                    "id": hw.course.id,
                    "title": hw.course.title
                } if hw.course else None
            })
        
        return result
    
    def get_homework_submissions(
        self,
        homework_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all submissions for a homework assignment"""
        query = self.db.query(HomeworkSubmissionModel).filter(
            HomeworkSubmissionModel.homework_id == homework_id
        )
        
        if status:
            try:
                enum_status = HomeworkStatus(status)
                query = query.filter(HomeworkSubmissionModel.status == enum_status)
            except Exception:
                pass
        
        submissions = query.offset(skip).limit(limit).all()
        
        # Format the response
        result = []
        for submission in submissions:
            result.append({
                "id": submission.id,
                "student_id": submission.student_id,
                "student_name": f"{getattr(submission.student, 'first_name', '')} {getattr(submission.student, 'last_name', '')}".strip(),
                "status": submission.status,
                "submitted_at": submission.submitted_at,
                "score": submission.score,
                "feedback": submission.feedback
            })
        
        return result
    
    async def provide_feedback(
        self,
        submission_id: int,
        feedback: str,
        score: int,
        grader_id: int
    ) -> HomeworkSubmissionModel:
        """Provide feedback on a homework submission"""
        # Get the submission
        submission = crud_homework.homework_submission.get(self.db, id=submission_id)
        if not submission:
            raise ValueError("Submission not found")
        
        # Update with feedback
        submission = crud_homework.homework_submission.grade_submission(
            self.db,
            db_obj=submission,
            feedback=feedback,
            score=score,
            graded_by=grader_id,
        )
        
        # Log the grading action
        self._log_grading(submission_id, grader_id, score)
        
        return submission
    
    def _log_grading(
        self,
        submission_id: int,
        grader_id: int,
        score: int
    ) -> None:
        """Log the grading action"""
        logger.info(
            f"Grading submission_id={submission_id} by grader_id={grader_id} with score={score} at {datetime.utcnow().isoformat()}"
        )
    
    def get_upcoming_deadlines(
        self,
        user_id: int,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get upcoming homework deadlines for a student"""
        now = datetime.utcnow()
        end_date = now + timedelta(days=days)
        
        assignments = self.db.query(
            HomeworkSubmissionModel
        ).join(
            models.Homework
        ).filter(
            HomeworkSubmissionModel.student_id == user_id,
            HomeworkSubmissionModel.status.in_([HomeworkStatus.PENDING, HomeworkStatus.SUBMITTED]),
            models.Homework.due_date.between(now, end_date)
        ).order_by(
            models.Homework.due_date.asc()
        ).all()
        
        return [{
            "id": a.homework.id,
            "title": a.homework.title,
            "due_date": a.homework.due_date,
            "days_remaining": (a.homework.due_date.date() - now.date()).days,
            "course": {
                "id": a.homework.course.id,
                "title": a.homework.course.title
            } if a.homework.course else None
        } for a in assignments]

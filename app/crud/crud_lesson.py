from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.lesson import InteractiveLesson as LessonModel
from app.models.user import User, Role as UserRole
from app.models.course import Course
from app.schemas.lesson import LessonCreate, LessonUpdate, Lesson as LessonSchema


class CRUDLesson(CRUDBase[LessonModel, LessonCreate, LessonUpdate]):
    def get_with_course(self, db: Session, id: int) -> Optional[LessonModel]:
        """Get a lesson with its course relationship loaded."""
        return db.query(self.model).options(joinedload(self.model.course)).filter(self.model.id == id).first()

    def get_next_lesson_for_user(self, db: Session, *, user_id: int) -> Optional[LessonModel]:
        """
        Get the next lesson for a user based on their progress.
        
        Args:
            db: Database session
            user_id: ID of the user
            
        Returns:
            Optional[LessonModel]: The next lesson or None if no more lessons
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # Some deployments may not have this column; fall back gracefully
        last_lesson_id = getattr(user, 'last_viewed_lesson_id', None)

        # Determine privilege once using roles relationship (robust to deployments)
        try:
            user_roles = {role.name for role in getattr(user, 'roles', [])}
        except Exception:
            user_roles = set()
        is_privileged_user = any(role in user_roles for role in ["premium", "admin", "superadmin"])

        if last_lesson_id:
            last_lesson = self.get(db, id=last_lesson_id)
            if last_lesson:
                # Find the next lesson in the same course
                query = (
                    db.query(self.model)
                    .filter(
                        self.model.course_id == last_lesson.course_id,
                        self.model.order > last_lesson.order,
                    )
                )
                # For non-privileged users, filter out premium lessons
                if not is_privileged_user:
                    query = query.filter(self.model.is_premium == False)

                next_lesson = query.order_by(self.model.order.asc()).first()
                if next_lesson:
                    return next_lesson

        # If no last lesson or no next lesson in the current course, find the first available lesson
        query = db.query(self.model).join(Course, self.model.course_id == Course.id)
        
        # For free users, only show non-premium lessons
        if not is_privileged_user:
            query = query.filter(self.model.is_premium == False)
            
        first_lesson = query.order_by(Course.id.asc(), self.model.order.asc()).first()
        return first_lesson
        
    def get_accessible_lessons(
        self, 
        db: Session, 
        *, 
        user: Optional[User] = None,
        user_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100,
        course_id: Optional[int] = None
    ) -> List[LessonModel]:
        """
        Get a list of lessons that the user has access to.
        
        Args:
            db: Database session
            user: The user to check access for
            skip: Number of records to skip
            limit: Maximum number of records to return
            course_id: Optional course ID to filter by
            
        Returns:
            List[LessonModel]: List of accessible lessons
        """
        # Resolve user if only user_id provided
        if user is None and user_id is not None:
            user = db.query(User).filter(User.id == user_id).first()

        query = db.query(self.model)
        
        # Filter by course if specified
        if course_id is not None:
            query = query.filter(self.model.course_id == course_id)
            
        # For free users, only show non-premium lessons
        role_names = set()
        if user is not None:
            # Many-to-many roles
            try:
                role_names |= {r.name for r in getattr(user, "roles", []) if getattr(r, "name", None)}
            except Exception:
                pass
            # Single role relationship
            role_obj = getattr(user, "role", None)
            if role_obj and getattr(role_obj, "name", None):
                role_names.add(role_obj.name)
            # Fallback via role_id
            if not role_names:
                rid = getattr(user, "role_id", None)
                if rid:
                    role = db.query(UserRole).filter(UserRole.id == rid).first()
                    if role and role.name:
                        role_names.add(role.name)

        is_privileged_user = any(r in role_names for r in ["premium", "admin", "superadmin"])

        if not is_privileged_user:
            query = query.filter(self.model.is_premium == False)
            
        return query.offset(skip).limit(limit).all()
        
    def can_access_lesson(self, db: Session, *, user: Optional[User] = None, user_id: Optional[int] = None, lesson_id: int) -> bool:
        """
        Check if a user can access a specific lesson.
        
        Args:
            db: Database session
            user: The user to check access for
            user_id: Optional user id (for backward compatibility)
            lesson_id: ID of the lesson to check
            
        Returns:
            bool: True if the user can access the lesson, False otherwise
        """
        # Resolve user if only user_id provided
        if user is None and user_id is not None:
            user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return False

        # Admins and superadmins have full access
        role_names = set()
        try:
            role_names |= {r.name for r in getattr(user, "roles", []) if getattr(r, "name", None)}
        except Exception:
            pass
        role_obj = getattr(user, "role", None)
        if role_obj and getattr(role_obj, "name", None):
            role_names.add(role_obj.name)
        if not role_names:
            rid = getattr(user, "role_id", None)
            if rid:
                role = db.query(UserRole).filter(UserRole.id == rid).first()
                if role and role.name:
                    role_names.add(role.name)

        is_privileged_user = any(r in role_names for r in ["premium", "admin", "superadmin"])

        if is_privileged_user:
            return True
            
        # Get the lesson with course relationship
        lesson = self.get_with_course(db, id=lesson_id)
        if not lesson:
            return False
            
        # Course creators have access to their own lessons
        if lesson.course and lesson.course.instructor_id == user.id:
            return True
            
        # Check premium access
        if lesson.is_premium and not is_privileged_user:
            return False
            
        return True

    def get_count(self, db: Session) -> int:
        return db.query(self.model).count()

    def get_by_title(self, db: Session, *, title: str) -> Optional[LessonModel]:
        return db.query(self.model).filter(self.model.title == title).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[LessonModel]:
        return (
            db.query(self.model)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_course(
        self, db: Session, *, course_id: int, skip: int = 0, limit: int = 100
    ) -> List[LessonModel]:
        """
        Get a list of lessons for a specific course.
        
        Args:
            db: Database session
            course_id: ID of the course
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[LessonModel]: List of lessons for the course
        """
        return (
            db.query(self.model)
            .filter(self.model.course_id == course_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


# Create a singleton instance
lesson = CRUDLesson(LessonModel)

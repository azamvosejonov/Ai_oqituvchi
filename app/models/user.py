from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, JSON, Text, Table, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base_class import Base

# Association table for user roles (many-to-many)
user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    hashed_refresh_token = Column(String(255), nullable=True)
    refresh_token_expires_at = Column(DateTime, nullable=True)
    phone_number = Column(String(50), nullable=True, unique=True, index=True)
    full_name = Column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_teacher: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # AI Usage Counters
    gpt4o_requests_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False, server_default='0')
    stt_requests_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False, server_default='0')
    tts_chars_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False, server_default='0')
    pronunciation_analysis_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False, server_default='0')
    
    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary="user_role", back_populates="users"
    )
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    homework_submissions = relationship("HomeworkSubmission", back_populates="student", foreign_keys='HomeworkSubmission.student_id', cascade="all, delete-orphan")
    oral_assignments = relationship("OralAssignment", back_populates="user", foreign_keys='OralAssignment.user_id', cascade="all, delete-orphan")
    exercise_attempts = relationship("ExerciseAttempt", back_populates="user", cascade="all, delete-orphan")
    forum_posts = relationship("ForumPost", back_populates="author", foreign_keys='ForumPost.author_id', cascade="all, delete-orphan")
    forum_topics = relationship("ForumTopic", back_populates="author", foreign_keys='ForumTopic.author_id', cascade="all, delete-orphan")
    ai_usage = relationship("UserAIUsage", back_populates="user", foreign_keys='UserAIUsage.user_id', cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", uselist=False, foreign_keys='UserProgress.user_id', cascade="all, delete-orphan")
    pronunciation_practice_sessions = relationship("PronunciationSession", back_populates="user", foreign_keys='PronunciationSession.user_id', cascade="all, delete-orphan")
    pronunciation_practice_attempts = relationship("PronunciationAttempt", back_populates="user", foreign_keys='PronunciationAttempt.user_id', cascade="all, delete-orphan")
    pronunciation_profile = relationship("UserPronunciationProfile", back_populates="user", uselist=False, foreign_keys='UserPronunciationProfile.user_id', cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="user", cascade="all, delete-orphan") 
    courses_taught = relationship("Course", back_populates="instructor", cascade="all, delete-orphan") 
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan") 
    feedbacks = relationship("Feedback", foreign_keys='Feedback.user_id', back_populates="user", cascade="all, delete-orphan") 
    lesson_sessions = relationship("LessonSession", back_populates="user", cascade="all, delete-orphan") 
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan") 
    payment_verifications = relationship("PaymentVerification", back_populates="user", cascade="all, delete-orphan") 
    lesson_progress = relationship("UserLessonProgress", back_populates="user", cascade="all, delete-orphan") 
    lesson_completions = relationship("UserLessonCompletion", back_populates="user", cascade="all, delete-orphan") 
    video_analyses = relationship("VideoAnalysis", back_populates="owner", cascade="all, delete-orphan")
    test_attempts = relationship("TestAttempt", back_populates="user", cascade="all, delete-orphan")
    test_sessions = relationship("TestSession", back_populates="user", cascade="all, delete-orphan")

    def get_current_level(self) -> Optional['UserLevel']:
        """Foydalanuvchi hozirgi darajasini qaytaradi."""
        if self.progress and self.progress.level:
            return self.progress.level.level_name
        return None

    def update_progress(self, **kwargs) -> None:
        """Foydalanuvchi progressini yangilash.
        
        Args:
            **kwargs: Yangilanishlarni o'z ichiga olgan lug'at.
                    vocabulary_score, grammar_score, speaking_score, listening_score,
                    completed_lessons, completed_exercises, time_spent
        """
        from app.models.user_level import UserProgress
        if not self.progress:
            self.progress = UserProgress(user_id=self.id)
        
        for key, value in kwargs.items():
            if hasattr(self.progress, key):
                setattr(self.progress, key, value)
        
        # Darajani yangilash
        self.progress.level = self.progress.determine_level()
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    @property
    def is_admin(self):
        return any(role.name == "admin" for role in self.roles)

    @property
    def is_premium(self) -> bool:
        """Checks if the user has premium access (superuser, active subscription, or in trial)."""
        if self.is_superuser:
            return True
        
        now = datetime.utcnow()

        # Check for active trial period
        if self.trial_ends_at and self.trial_ends_at.replace(tzinfo=None) > now:
            return True

        # Check for an active subscription
        for sub in self.subscriptions:
            if sub.is_active and sub.end_date > now:
                return True

        return False


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(JSON, nullable=True, default=dict)
    
    # Default AI Quota Limits for this role
    gpt4o_requests_limit = Column(Integer, nullable=False, default=0, server_default='0')
    stt_requests_limit = Column(Integer, nullable=False, default=0, server_default='0')
    tts_chars_limit = Column(Integer, nullable=False, default=0, server_default='0')
    pronunciation_analysis_limit = Column(Integer, nullable=False, default=0, server_default='0')

    # Relationships
    users = relationship("User", secondary=user_role, back_populates="roles")
    
    def __repr__(self):
        return f"<Role {self.name}>"

# This file centralizes all SQLAlchemy model imports to prevent circular dependencies.
# It is generated based on the actual model files in this directory.

from app.db.base_class import Base

# --- Model Imports (Alphabetical Order) ---
from .admin_log import AdminLog
from .ai_avatar import AIAvatar
from .certificate import Certificate
from .course import Course, Enrollment
from .exercise import Exercise, ExerciseAttempt, ExerciseType
from .feedback import Feedback
from .forum import ForumTopic, ForumPost
from .homework import Homework, HomeworkSubmission
from .lesson import InteractiveLesson, LessonInteraction, LessonSession
from .notification import Notification
from .payment_verification import PaymentVerification
from .pronunciation import PronunciationAttempt, PronunciationAnalysisResult, PronunciationPhrase, PronunciationSession, \
    UserPronunciationProfile
from .subscription import Subscription, SubscriptionPlan
from .test import Test, TestQuestion
from .user import User, Role
from .user_ai_usage import UserAIUsage
from .user_lesson_progress import UserLessonProgress, UserLessonCompletion
from .user_level import UserLevel, UserProgress
from .video_analysis import VideoAnalysis, VideoSegment, VideoQuestion
from .word import Word, WordDefinition, WordExample

# --- __all__ list (Alphabetical Order) ---
__all__ = [
    'AdminLog',
    'AIAvatar',
    'AIChat',
    'AIConversation',
    'AIFeedback',
    'AILesson',
    'Base',
    'Certificate',
    'Course',
    'Enrollment',
    'Exercise',
    'ExerciseAttempt',
    'ExerciseType',
    'Feedback',
    'ForumPost',
    'ForumTopic',
    'Homework',
    'HomeworkSubmission',
    'InteractiveLesson',
    'Lesson',
    'LessonInteraction',
    'LessonSession',
    'Notification',
    'Payment',
    'PaymentVerification',
    'PronunciationAnalysisResult',
    'PronunciationAttempt',
    'PronunciationPhrase',
    'PronunciationSession',
    'Role',
    'Subscription',
    'SubscriptionPlan',
    'Test',
    'TestQuestion',
    'User',
    'UserAIUsage',
    'UserLessonCompletion',
    'UserLessonProgress',
    'UserLevel',
    'UserProgress',
    'UserPronunciationProfile',
    'UserSubscription',
    'VideoAnalysis',
    'VideoQuestion',
    'VideoSegment',
    'Word',
    'WordDefinition',
    'WordExample'
]

# Schemas for basic models
from enum import Enum

from ..models.test import TestSection, TestQuestion, TestAttempt, TestAnswer, Test


class UserRole(str, Enum):
    superadmin = "superadmin"
    admin = "admin"
    creator = "creator"
    premium = "premium"
    free = "free"

from .msg import Message
from .token import Token, TokenPayload, LoginRequest, UserInResponse, TokenResponse, LocationInfo
from .user import User, UserCreate, UserUpdate, UserInDB, UserBase, PasswordChange
from .user_level import UserLevel

# Schemas for features
from .ai import AIQuestion, STTResponse, TTSRequest, AIPronunciationAssessment
from .ai_avatar import AIAvatar, AIAvatarCreate, AIAvatarInDB, AIAvatarUpdate
from .ai_chat import DifficultyLevel, PronunciationFeedback, AIChatInput, AIChatResponse
from .ai_feedback import AIFeedbackRequest, AIFeedbackResponse
from .voice_loop import VoiceLoopResponse
from .ai_lesson import AILessonGenerateRequest, AILessonGenerateResponse
from .certificate import Certificate, CertificateCreate, CertificateUpdate
from .course import Course, CourseCreate, CourseUpdate
from .exercise import (
    ExerciseType, Exercise, ExerciseCreate, ExerciseUpdate, ExerciseInDBBase,
    ExerciseAttempt, ExerciseAttemptCreate, ExerciseAttemptInDBBase,
    ExerciseSet, ExerciseSetCreate, ExerciseSetUpdate, ExerciseSetInDBBase,
    ExerciseSetItem, ExerciseSetItemCreate,
    TestSession, TestSessionCreate, TestSessionUpdate, TestSessionBase,
    TestResponse, TestResponseCreate, TestResponseUpdate, TestResponseBase,
    UserProgress, UserProgressCreate, UserProgressUpdate, UserProgressBase
)
from .feedback import Feedback, FeedbackCreate, FeedbackUpdate
from .forum import ForumTopic, ForumTopicCreate, ForumTopicUpdate, ForumPost, ForumPostCreate, ForumPostUpdate, ForumCategory, ForumCategoryCreate, ForumCategoryUpdate
from .homework import Homework, HomeworkCreate, HomeworkUpdate, HomeworkInDB, UserHomework, UserHomeworkCreate, UserHomeworkUpdate, UserHomeworkInDB, HomeworkSubmission, HomeworkSubmissionCreate, HomeworkSubmissionUpdate
from .interactive_lesson import (
    InteractiveLesson, InteractiveLessonCreate, InteractiveLessonUpdate, 
    InteractiveLessonSessionCreate, InteractiveLessonSessionInDB, LessonStart,
    LessonStartResponse, UserMessage, AIResponse, PronunciationAssessment
)
from .lesson_session import LessonSession, LessonSessionCreate, LessonSessionUpdate, LessonSessionInDB, LessonSessionStatus, LessonSessionWithInteractions
from .lesson import Lesson, LessonCreate, LessonUpdate, LessonBase
from .lesson_interaction import LessonInteraction, LessonInteractionCreate
from .notification import Notification, NotificationCreate, NotificationUpdate, UnreadCount
from .payment_verification import PaymentVerificationBase, PaymentVerificationCreate, PaymentVerificationUpdate, PaymentVerificationInDB, PaymentVerificationApprove, PaymentVerificationReject
from .pronunciation import PronunciationWordAssessment, PronunciationAssessmentRequest, PronunciationAssessmentResponse, PronunciationExercise
from .recommendation import PersonalizedRecommendations, AdaptiveLessonPlan, ForYouRecommendations
from .statistics import UserStats, PaymentStats, DashboardStats, GeneralStats
from .stripe import SubscriptionPlanId, StripeCheckoutSession
from .subscription import Subscription, SubscriptionCreate, SubscriptionUpdate, SubscriptionPlan, SubscriptionPlanCreate, SubscriptionPlanUpdate
from .test import (
     TestCreate, TestUpdate, TestInDB,
     TestSectionCreate, TestSectionUpdate, TestSectionInDB,
     TestQuestionCreate, TestQuestionUpdate, TestQuestionInDB,
     TestAttemptCreate,  TestAttemptInDB,
 TestAnswerCreate,
    TestResultResponse, GradedSection, GradedAnswer,
    TestType, QuestionType
)
from .user_ai_usage import UserAIUsage, UserAIUsageCreate, UserAIUsageUpdate
from .user_lesson_completion import UserLessonCompletion, UserLessonCompletionCreate, UserLessonCompletionUpdate
from .word import Word, WordCreate, WordUpdate
from .role import Role, RoleCreate, RoleUpdate
from .admin_stats import UserStats, ContentStats, AIUsageStats, PlatformStats
from .admin import UserUpdateAdmin

from .user import User, UserCreate, UserUpdate, UserInDB
from .course import Course, CourseCreate, CourseUpdate, CourseInDB
from .lesson import Lesson, LessonCreate, LessonUpdate, LessonInDB
from .token import Token, TokenPayload, LoginRequest, TokenWithUser
from .role import Role, RoleCreate, RoleUpdate
from .subscription import Subscription, SubscriptionCreate, SubscriptionUpdate, SubscriptionPlan, SubscriptionPlanCreate, SubscriptionPlanUpdate
from .feedback import Feedback, FeedbackCreate, FeedbackUpdate
from .certificate import Certificate, CertificateCreate, CertificateUpdate
from .forum import ForumTopic, ForumTopicCreate, ForumTopicUpdate, ForumPost, ForumPostCreate, ForumPostUpdate
from .homework import Homework, HomeworkCreate, HomeworkUpdate, HomeworkSubmission, HomeworkSubmissionCreate, HomeworkSubmissionUpdate
from .user_ai_usage import UserAIUsage, UserAIUsageCreate, UserAIUsageUpdate
from .interactive_lesson import InteractiveLesson, InteractiveLessonCreate, InteractiveLessonUpdate
from .notification import Notification, NotificationCreate, NotificationUpdate
from .payment_verification import PaymentVerification, PaymentVerificationCreate, PaymentVerificationUpdate

# Resolve forward references
User.model_rebuild()
Course.model_rebuild()
Lesson.model_rebuild()

# __all__ list to control what `from app.schemas import *` imports
__all__ = [
    # User and Auth
    'User', 'UserCreate', 'UserUpdate', 'UserInDB', 'UserBase', 'PasswordChange',
    'Token', 'TokenPayload', 'LoginRequest', 'UserInResponse', 'TokenResponse', 'LocationInfo',
    'Message',
    'UserRole',

    # Admin
    'UserUpdateAdmin',
    'DashboardStats',
    'UserStats',
    'ContentStats',
    'AIUsageStats',
    'PlatformStats',
    'GeneralStats',

    # AI
    'AIQuestion', 'STTResponse', 'TTSRequest', 'AIPronunciationAssessment',
    'AIAvatar', 'AIAvatarCreate', 'AIAvatarInDB', 'AIAvatarUpdate',
    'DifficultyLevel', 'PronunciationFeedback', 'AIChatInput', 'AIChatResponse',
    'AIFeedbackRequest', 'AIFeedbackResponse',
    'VoiceLoopResponse',
    'AILessonGenerateRequest', 'AILessonGenerateResponse',
    'InteractiveLesson', 'InteractiveLessonCreate', 'InteractiveLessonUpdate',
    'InteractiveLessonSessionCreate', 'InteractiveLessonSessionInDB',
    'LessonInteraction', 'LessonInteractionCreate',
    'LessonSession', 'LessonSessionCreate', 'LessonSessionUpdate', 'LessonSessionInDB', 'LessonSessionStatus', 'LessonSessionWithInteractions',
    'PronunciationWordAssessment', 'PronunciationAssessmentRequest', 'PronunciationAssessmentResponse', 'PronunciationExercise',
    'UserAIUsage', 'UserAIUsageCreate', 'UserAIUsageUpdate',
    'AnswerEvaluationResponse',
    'LessonStart', 'LessonStartResponse', 'UserMessage', 'AIResponse', 'PronunciationAssessment',

    # Content
    'Course', 'CourseCreate', 'CourseUpdate',
    'Lesson', 'LessonCreate', 'LessonUpdate', 'LessonBase',
    'Word', 'WordCreate', 'WordUpdate',
    'Certificate', 'CertificateCreate', 'CertificateUpdate',
    'Homework', 'HomeworkCreate', 'HomeworkUpdate', 'HomeworkInDB',
    'UserHomework', 'UserHomeworkCreate', 'UserHomeworkUpdate', 'UserHomeworkInDB',
    'HomeworkSubmission', 'HomeworkSubmissionCreate', 'HomeworkSubmissionUpdate',

    # Exercises and Tests
    'ExerciseType', 'Exercise', 'ExerciseCreate', 'ExerciseUpdate', 'ExerciseInDBBase',
    'ExerciseAttempt', 'ExerciseAttemptCreate', 'ExerciseAttemptInDBBase',
    'ExerciseSet', 'ExerciseSetCreate', 'ExerciseSetUpdate', 'ExerciseSetInDBBase',
    'ExerciseSetItem', 'ExerciseSetItemCreate',
    'TestType', 'QuestionType',
    'Test', 'TestCreate', 'TestUpdate', 'TestInDB',
    'TestSection', 'TestSectionCreate', 'TestSectionUpdate', 'TestSectionInDB',
    'TestQuestion', 'TestQuestionCreate', 'TestQuestionUpdate', 'TestQuestionInDB',
    'TestAttempt', 'TestAttemptCreate', 'TestAttemptInDB',
    'TestAnswer', 'TestAnswerCreate',
    'TestResultResponse', 'GradedSection', 'GradedAnswer',
    'TestSession', 'TestSessionCreate', 'TestSessionUpdate', 'TestSessionBase',
    'TestResponse', 'TestResponseCreate', 'TestResponseUpdate', 'TestResponseBase',

    # User Progress
    'UserProgress', 'UserProgressCreate', 'UserProgressUpdate', 'UserProgressBase',
    'UserLessonCompletion', 'UserLessonCompletionCreate', 'UserLessonCompletionUpdate',
    'UserLevel',

    # Community and Feedback
    'Feedback', 'FeedbackCreate', 'FeedbackUpdate',
    'ForumTopic', 'ForumTopicCreate', 'ForumTopicUpdate',
    'ForumPost', 'ForumPostCreate', 'ForumPostUpdate',
    'ForumCategory', 'ForumCategoryCreate', 'ForumCategoryUpdate',

    # Payments and Subscriptions
    'Subscription', 'SubscriptionCreate', 'SubscriptionUpdate',
    'SubscriptionPlan', 'SubscriptionPlanCreate', 'SubscriptionPlanUpdate',
    'PaymentVerificationBase', 'PaymentVerificationCreate', 'PaymentVerificationUpdate', 'PaymentVerificationInDB',
    'PaymentVerificationApprove', 'PaymentVerificationReject',
    'SubscriptionPlanId', 'StripeCheckoutSession',

    # Other
    'Notification', 'NotificationCreate', 'NotificationUpdate',
    'PersonalizedRecommendations', 'AdaptiveLessonPlan', 'ForYouRecommendations',
    'Role', 'RoleCreate', 'RoleUpdate',
    'UnreadCount',
]

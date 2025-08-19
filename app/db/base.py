# This file is the single source of truth for the SQLAlchemy Base and all models.
# By importing all models here, we ensure that Base.metadata is populated correctly
# before being used by Alembic or for table creation in tests.

# Import the Base from its definition
from app.db.base_class import Base  # noqa

# Import all the models, so they register themselves with the Base
from app.models.user import User, Role  # noqa
from app.models.course import Course, Enrollment  # noqa
from app.models.lesson import InteractiveLesson, LessonSession  # noqa
from app.models.user_lesson_progress import UserLessonProgress  # noqa
from app.models.word import Word, WordDefinition  # noqa
from app.models.exercise import Exercise, ExerciseAttempt, ExerciseSet, ExerciseSetItem  # noqa
from app.models.test import Test, TestSection, TestQuestion, TestAttempt, TestAnswer  # noqa
from app.models.subscription import Subscription, SubscriptionPlan  # noqa
from app.models.payment_verification import PaymentVerification  # noqa
from app.models.certificate import Certificate  # noqa
from app.models.feedback import Feedback  # noqa
from app.models.forum import ForumTopic, ForumPost  # noqa
from app.models.homework import Homework, HomeworkSubmission, OralAssignment  # noqa
from app.models.notification import Notification  # noqa
from app.models.pronunciation import PronunciationPhrase, PronunciationSession, PronunciationAttempt  # noqa
from app.models.ai_avatar import AIAvatar  # noqa
from app.models.admin_log import AdminLog  # noqa
from app.models.user_ai_usage import UserAIUsage  # noqa
from app.models.user_level import UserLevel  # noqa
from app.models.video_analysis import VideoAnalysis, VideoSegment, VideoQuestion  # noqa

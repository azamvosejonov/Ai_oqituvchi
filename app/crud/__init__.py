from .crud_user import user
from .crud_course import course
from .crud_lesson import lesson
from .crud_ai_avatar import ai_avatar
from .crud_lesson_session import lesson_session
from .crud_homework import homework, homework_submission
from .crud_word import word
from .crud_user_lesson_completion import user_lesson_completion
from .crud_certificate import certificate
from .crud_feedback import feedback
from .crud_forum import forum_topic, forum_post
from .crud_forum_category import forum_category
from . import crud_subscription as subscription

from .crud_word import word
from .crud_notification import notification
from . import crud_statistics as statistics
from .crud_user_ai_usage import user_ai_usage
from .crud_payment_verification import payment_verification
from .crud_role import CRUDRole
from ..models import Role

role = CRUDRole(Role)

# Interactive lessons CRUD (tozalandi)
from .crud_interactive_lesson import (
    interactive_lesson,
    interactive_lesson_session,
    interactive_lesson_interaction,
)

# Exercise and Pronunciation CRUD (yangilandi)
from .crud_exercise import (
    exercise,
    exercise_attempt,
    exercise_set,
    pronunciation_attempt,
    user_progress,
)

# Pronunciation CRUD (explicit exports for tests expecting these names)
from .crud_pronunciation import (
    crud_pronunciation_phrase,
    crud_pronunciation_session,
    crud_pronunciation_attempt,
    crud_user_pronunciation_profile,
)

# Test CRUD
from .crud_test import test, test_section, test_question, test_attempt, test_answer

# The following imports are for backwards compatibility and can be phased out.
# Direct function imports for subscription:
from .crud_subscription import (
    get_subscription_plan,
    get_subscription_plans,
    create_subscription_plan,
    update_subscription_plan,
    delete_subscription_plan,
    get_subscription,
    get_user_subscriptions,
    get_all as get_all_subscriptions,
    update_subscription,
    create_with_plan_details,
)

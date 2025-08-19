import os
from typing import List, Tuple

import httpx
import pytest

from main import app
from app.core.config import settings


# Minimal set of endpoints to actually hit (safe, minimal payload)
# format: (method, path, requires_auth)
SMOKE_ENDPOINTS: List[Tuple[str, str, bool]] = [
    # login/auth
    ("POST", f"{settings.API_V1_STR}/login/access-token", False),
    ("GET", f"{settings.API_V1_STR}/login/test-token", True),
    ("POST", f"{settings.API_V1_STR}/logout", True),

    # users
    ("GET", f"{settings.API_V1_STR}/users/", True),
    ("POST", f"{settings.API_V1_STR}/users/", False),
    ("GET", f"{settings.API_V1_STR}/users/me", True),
    ("PATCH", f"{settings.API_V1_STR}/users/me", True),
    ("GET", f"{settings.API_V1_STR}/users/me/premium-data", True),
    ("GET", f"{settings.API_V1_STR}/users/me/next-lesson", True),
    ("GET", f"{settings.API_V1_STR}/users/test-superuser", True),
    ("GET", f"{settings.API_V1_STR}/users/999999", True),  # id path -> may 404
    ("PUT", f"{settings.API_V1_STR}/users/999999", True),
    ("DELETE", f"{settings.API_V1_STR}/users/999999", True),
    ("POST", f"{settings.API_V1_STR}/users/courses/999999/complete", True),
    ("GET", f"{settings.API_V1_STR}/users/certificates/", True),
    ("GET", f"{settings.API_V1_STR}/users/certificates/999999", True),

    # subscription-plans (admin-style)
    ("POST", f"{settings.API_V1_STR}/subscription-plans/", True),
    ("GET", f"{settings.API_V1_STR}/subscription-plans/", True),
    ("GET", f"{settings.API_V1_STR}/subscription-plans/999999", True),
    ("PUT", f"{settings.API_V1_STR}/subscription-plans/999999", True),
    ("DELETE", f"{settings.API_V1_STR}/subscription-plans/999999", True),

    # courses
    ("GET", f"{settings.API_V1_STR}/courses/", True),
    ("POST", f"{settings.API_V1_STR}/courses/", True),
    ("PUT", f"{settings.API_V1_STR}/courses/999999", True),
    ("GET", f"{settings.API_V1_STR}/courses/999999", True),
    ("DELETE", f"{settings.API_V1_STR}/courses/999999", True),

    # subscriptions
    ("GET", f"{settings.API_V1_STR}/subscriptions/plans", True),
    ("POST", f"{settings.API_V1_STR}/subscriptions/stripe-webhook", False),
    ("POST", f"{settings.API_V1_STR}/subscriptions/create-checkout-session", True),
    ("GET", f"{settings.API_V1_STR}/subscriptions/", True),
    ("POST", f"{settings.API_V1_STR}/subscriptions/users/999999/subscriptions", True),
    ("GET", f"{settings.API_V1_STR}/subscriptions/users/999999/subscriptions", True),
    ("GET", f"{settings.API_V1_STR}/subscriptions/me", True),
    ("DELETE", f"{settings.API_V1_STR}/subscriptions/999999", True),

    # lessons
    ("GET", f"{settings.API_V1_STR}/lessons/", False),
    ("POST", f"{settings.API_V1_STR}/lessons/", True),
    ("GET", f"{settings.API_V1_STR}/lessons/categories", False),
    ("GET", f"{settings.API_V1_STR}/lessons/videos", True),
    ("GET", f"{settings.API_V1_STR}/lessons/continue", True),
    ("PUT", f"{settings.API_V1_STR}/lessons/999999", True),
    ("GET", f"{settings.API_V1_STR}/lessons/999999", True),
    ("DELETE", f"{settings.API_V1_STR}/lessons/999999", True),

    # words
    ("GET", f"{settings.API_V1_STR}/words/", True),
    ("POST", f"{settings.API_V1_STR}/words/", True),
    ("PUT", f"{settings.API_V1_STR}/words/999999", True),
    ("PATCH", f"{settings.API_V1_STR}/words/999999", True),
    ("GET", f"{settings.API_V1_STR}/words/999999", True),
    ("DELETE", f"{settings.API_V1_STR}/words/999999", True),

    # statistics
    ("GET", f"{settings.API_V1_STR}/statistics/", True),
    ("GET", f"{settings.API_V1_STR}/statistics/top-users", True),
    ("GET", f"{settings.API_V1_STR}/statistics/payment-stats", True),

    # user-progress
    ("GET", f"{settings.API_V1_STR}/user-progress/", True),
    ("POST", f"{settings.API_V1_STR}/user-progress/lessons/999999/complete", True),

    # certificates
    ("POST", f"{settings.API_V1_STR}/certificates/", True),
    ("GET", f"{settings.API_V1_STR}/certificates/user/999999", True),
    ("GET", f"{settings.API_V1_STR}/certificates/my-certificates", True),
    ("GET", f"{settings.API_V1_STR}/certificates/999999/download", True),
    ("GET", f"{settings.API_V1_STR}/certificates/999999/verify/unknown", True),

    # feedback
    ("GET", f"{settings.API_V1_STR}/feedback/", True),
    ("POST", f"{settings.API_V1_STR}/feedback/", True),
    ("DELETE", f"{settings.API_V1_STR}/feedback/999999", True),

    # forum
    ("POST", f"{settings.API_V1_STR}/forum/categories/", True),
    ("GET", f"{settings.API_V1_STR}/forum/categories/", False),
    ("PUT", f"{settings.API_V1_STR}/forum/categories/999999", True),
    ("DELETE", f"{settings.API_V1_STR}/forum/categories/999999", True),
    ("GET", f"{settings.API_V1_STR}/forum/topics/", False),
    ("POST", f"{settings.API_V1_STR}/forum/topics/", True),
    ("GET", f"{settings.API_V1_STR}/forum/categories/999999/topics", False),
    ("GET", f"{settings.API_V1_STR}/forum/topics/999999", False),
    ("PUT", f"{settings.API_V1_STR}/forum/topics/999999", True),
    ("DELETE", f"{settings.API_V1_STR}/forum/topics/999999", True),
    ("POST", f"{settings.API_V1_STR}/forum/posts/", True),
    ("PUT", f"{settings.API_V1_STR}/forum/posts/999999", True),
    ("DELETE", f"{settings.API_V1_STR}/forum/posts/999999", True),

    # ai
    ("GET", f"{settings.API_V1_STR}/ai/tts/voices", False),
    ("GET", f"{settings.API_V1_STR}/ai/stt/languages", False),
    ("POST", f"{settings.API_V1_STR}/ai/ask", True),
    ("POST", f"{settings.API_V1_STR}/ai/tts", True),
    ("POST", f"{settings.API_V1_STR}/ai/stt", True),
    ("POST", f"{settings.API_V1_STR}/ai/pronunciation", True),
    ("POST", f"{settings.API_V1_STR}/ai/suggest-lesson", True),

    # notifications
    ("GET", f"{settings.API_V1_STR}/notifications/", True),
    ("GET", f"{settings.API_V1_STR}/notifications/unread-count", True),
    ("POST", f"{settings.API_V1_STR}/notifications/999999/read", True),
    ("POST", f"{settings.API_V1_STR}/notifications/read-all", True),
    ("POST", f"{settings.API_V1_STR}/notifications/admin/send", True),

    # tests
    ("GET", f"{settings.API_V1_STR}/tests/ielts", False),
    ("GET", f"{settings.API_V1_STR}/tests/toefl", False),
    ("GET", f"{settings.API_V1_STR}/tests/", True),
    ("GET", f"{settings.API_V1_STR}/tests/999999", True),
    ("POST", f"{settings.API_V1_STR}/tests/999999/start", True),
    ("GET", f"{settings.API_V1_STR}/tests/attempts/me", True),
    ("GET", f"{settings.API_V1_STR}/tests/attempts/999999", True),
    ("POST", f"{settings.API_V1_STR}/tests/attempts/999999/submit", True),
    ("POST", f"{settings.API_V1_STR}/tests/attempts/999999/finish", True),

    # admin-tests
    ("POST", f"{settings.API_V1_STR}/admin/tests/", True),
    ("PUT", f"{settings.API_V1_STR}/admin/tests/999999", True),
    ("POST", f"{settings.API_V1_STR}/admin/tests/999999/sections/", True),
    ("PUT", f"{settings.API_V1_STR}/admin/tests/sections/999999", True),
    ("DELETE", f"{settings.API_V1_STR}/admin/tests/sections/999999", True),
    ("POST", f"{settings.API_V1_STR}/admin/tests/sections/999999/questions/", True),
    ("PUT", f"{settings.API_V1_STR}/admin/tests/questions/999999", True),
    ("DELETE", f"{settings.API_V1_STR}/admin/tests/questions/999999", True),

    # admin
    ("GET", f"{settings.API_V1_STR}/admin/statistics", True),
    ("GET", f"{settings.API_V1_STR}/admin/users", True),
    ("POST", f"{settings.API_V1_STR}/admin/users", True),
    ("GET", f"{settings.API_V1_STR}/admin/users/999999", True),
    ("PATCH", f"{settings.API_V1_STR}/admin/users/999999", True),
    ("DELETE", f"{settings.API_V1_STR}/admin/users/999999", True),
    ("PATCH", f"{settings.API_V1_STR}/admin/users/999999/profile", True),
    ("PATCH", f"{settings.API_V1_STR}/admin/users/999999/role", True),
    ("GET", f"{settings.API_V1_STR}/admin/subscription-plans/", True),
    ("POST", f"{settings.API_V1_STR}/admin/subscription-plans/", True),
    ("PUT", f"{settings.API_V1_STR}/admin/subscription-plans/999999", True),
    ("DELETE", f"{settings.API_V1_STR}/admin/subscription-plans/999999", True),
    ("GET", f"{settings.API_V1_STR}/admin/courses/", True),
    ("POST", f"{settings.API_V1_STR}/admin/courses/", True),
    ("PUT", f"{settings.API_V1_STR}/admin/courses/999999", True),
    ("DELETE", f"{settings.API_V1_STR}/admin/courses/999999", True),
    ("GET", f"{settings.API_V1_STR}/admin/interactive-lessons/", True),
    ("POST", f"{settings.API_V1_STR}/admin/interactive-lessons/", True),
    ("PUT", f"{settings.API_V1_STR}/admin/interactive-lessons/999999", True),
    ("DELETE", f"{settings.API_V1_STR}/admin/interactive-lessons/999999", True),

    # content
    ("GET", f"{settings.API_V1_STR}/content/lessons-json", True),
    ("PUT", f"{settings.API_V1_STR}/content/lessons-json", True),
    ("GET", f"{settings.API_V1_STR}/content/media", True),
    ("POST", f"{settings.API_V1_STR}/content/media/upload", True),
    ("DELETE", f"{settings.API_V1_STR}/content/media/ghost.png", True),

    # profile
    ("GET", f"{settings.API_V1_STR}/profile/me", True),
    ("PATCH", f"{settings.API_V1_STR}/profile/me", True),
    ("GET", f"{settings.API_V1_STR}/profile/stats", True),
    ("POST", f"{settings.API_V1_STR}/profile/change-password", True),
    ("POST", f"{settings.API_V1_STR}/profile/avatar", True),

    # interactive-lessons
    ("GET", f"{settings.API_V1_STR}/interactive-lessons/", True),
    ("GET", f"{settings.API_V1_STR}/interactive-lessons/999999", True),
    ("POST", f"{settings.API_V1_STR}/interactive-lessons/start-lesson", True),
    ("POST", f"{settings.API_V1_STR}/interactive-lessons/send-message", True),
    ("POST", f"{settings.API_V1_STR}/interactive-lessons/send-audio-message", True),
    ("POST", f"{settings.API_V1_STR}/interactive-lessons/assess-pronunciation", True),

    # lesson-interactions
    ("POST", f"{settings.API_V1_STR}/lesson-interactions/999999/interact", True),
    ("GET", f"{settings.API_V1_STR}/lesson-interactions/999999/interactions", True),

    # homework
    ("GET", f"{settings.API_V1_STR}/homework/", True),
    ("POST", f"{settings.API_V1_STR}/homework/", True),
    ("GET", f"{settings.API_V1_STR}/homework/999999", True),
    ("GET", f"{settings.API_V1_STR}/homework/lesson/999999", True),
    ("GET", f"{settings.API_V1_STR}/homework/files/999999/download", True),
    ("POST", f"{settings.API_V1_STR}/homework/999999/assign", True),
    ("GET", f"{settings.API_V1_STR}/homework/user/me", True),
    ("POST", f"{settings.API_V1_STR}/homework/999999/submit", True),
    ("POST", f"{settings.API_V1_STR}/homework/submissions/999999/grade", True),
    ("GET", f"{settings.API_V1_STR}/homework/submissions/me", True),
    ("POST", f"{settings.API_V1_STR}/homework/999999/submit-oral", True),
    ("POST", f"{settings.API_V1_STR}/homework/grade/999999", True),

    # payments
    ("GET", f"{settings.API_V1_STR}/payments/", True),
    ("POST", f"{settings.API_V1_STR}/payments/webhook/stripe", False),
    ("POST", f"{settings.API_V1_STR}/payments/create-checkout-session", True),

    # webrtc
    ("POST", f"{settings.API_V1_STR}/webrtc/rooms/create", True),
    ("GET", f"{settings.API_V1_STR}/webrtc/rooms/ghost-room/users", True),
    ("POST", f"{settings.API_V1_STR}/webrtc/rooms/ghost-room/end", True),

    # avatars
    ("GET", f"{settings.API_V1_STR}/avatars/", True),
    ("GET", f"{settings.API_V1_STR}/avatars/999999", True),

    # metrics & health
    ("GET", f"{settings.API_V1_STR}/metrics", True),
    ("GET", f"{settings.API_V1_STR}/metrics/health", False),
    ("GET", f"{settings.API_V1_STR}/metrics/status", True),
    ("GET", "/health", False),

    # recommendations
    ("GET", f"{settings.API_V1_STR}/recommendations/personalized", True),
    ("GET", f"{settings.API_V1_STR}/recommendations/adaptive-lesson-plan/999999", True),
    ("GET", f"{settings.API_V1_STR}/recommendations/for-you", True),
]

# Full inventory to check existence only (no requests)
ROUTE_INVENTORY = [
    ("POST", f"{settings.API_V1_STR}/login/access-token"),
    ("GET", f"{settings.API_V1_STR}/login/test-token"),
    ("POST", f"{settings.API_V1_STR}/logout"),

    ("GET", f"{settings.API_V1_STR}/users/"),
    ("POST", f"{settings.API_V1_STR}/users/"),
    ("GET", f"{settings.API_V1_STR}/users/me"),
    ("PATCH", f"{settings.API_V1_STR}/users/me"),
    ("GET", f"{settings.API_V1_STR}/users/me/premium-data"),
    ("GET", f"{settings.API_V1_STR}/users/me/next-lesson"),
    ("GET", f"{settings.API_V1_STR}/users/test-superuser"),
    ("GET", f"{settings.API_V1_STR}/users/{{user_id}}"),
    ("PUT", f"{settings.API_V1_STR}/users/{{user_id}}"),
    ("DELETE", f"{settings.API_V1_STR}/users/{{user_id}}"),
    ("POST", f"{settings.API_V1_STR}/users/courses/{{course_id}}/complete"),
    ("GET", f"{settings.API_V1_STR}/users/certificates/"),
    ("GET", f"{settings.API_V1_STR}/users/certificates/{{certificate_id}}"),

    ("POST", f"{settings.API_V1_STR}/subscription-plans/"),
    ("GET", f"{settings.API_V1_STR}/subscription-plans/"),
    ("GET", f"{settings.API_V1_STR}/subscription-plans/{{plan_id}}"),
    ("PUT", f"{settings.API_V1_STR}/subscription-plans/{{plan_id}}"),
    ("DELETE", f"{settings.API_V1_STR}/subscription-plans/{{plan_id}}"),

    ("GET", f"{settings.API_V1_STR}/courses/"),
    ("POST", f"{settings.API_V1_STR}/courses/"),
    ("PUT", f"{settings.API_V1_STR}/courses/{{id}}"),
    ("GET", f"{settings.API_V1_STR}/courses/{{id}}"),
    ("DELETE", f"{settings.API_V1_STR}/courses/{{id}}"),

    ("GET", f"{settings.API_V1_STR}/subscriptions/plans"),
    ("POST", f"{settings.API_V1_STR}/subscriptions/stripe-webhook"),
    ("POST", f"{settings.API_V1_STR}/subscriptions/create-checkout-session"),
    ("GET", f"{settings.API_V1_STR}/subscriptions/"),
    ("POST", f"{settings.API_V1_STR}/subscriptions/users/{{user_id}}/subscriptions"),
    ("GET", f"{settings.API_V1_STR}/subscriptions/users/{{user_id}}/subscriptions"),
    ("GET", f"{settings.API_V1_STR}/subscriptions/me"),
    ("DELETE", f"{settings.API_V1_STR}/subscriptions/{{subscription_id}}"),

    ("GET", f"{settings.API_V1_STR}/lessons/"),
    ("POST", f"{settings.API_V1_STR}/lessons/"),
    ("GET", f"{settings.API_V1_STR}/lessons/categories"),
    ("GET", f"{settings.API_V1_STR}/lessons/videos"),
    ("GET", f"{settings.API_V1_STR}/lessons/continue"),
    ("PUT", f"{settings.API_V1_STR}/lessons/{{id}}"),
    ("GET", f"{settings.API_V1_STR}/lessons/{{id}}"),
    ("DELETE", f"{settings.API_V1_STR}/lessons/{{id}}"),

    ("GET", f"{settings.API_V1_STR}/words/"),
    ("POST", f"{settings.API_V1_STR}/words/"),
    ("PUT", f"{settings.API_V1_STR}/words/{{id}}"),
    ("PATCH", f"{settings.API_V1_STR}/words/{{id}}"),
    ("GET", f"{settings.API_V1_STR}/words/{{id}}"),
    ("DELETE", f"{settings.API_V1_STR}/words/{{id}}"),

    ("GET", f"{settings.API_V1_STR}/statistics/"),
    ("GET", f"{settings.API_V1_STR}/statistics/top-users"),
    ("GET", f"{settings.API_V1_STR}/statistics/payment-stats"),

    ("GET", f"{settings.API_V1_STR}/user-progress/"),
    ("POST", f"{settings.API_V1_STR}/user-progress/lessons/{{lesson_id}}/complete"),

    ("POST", f"{settings.API_V1_STR}/certificates/"),
    ("GET", f"{settings.API_V1_STR}/certificates/user/{{user_id}}"),
    ("GET", f"{settings.API_V1_STR}/certificates/my-certificates"),
    ("GET", f"{settings.API_V1_STR}/certificates/{{certificate_id}}/download"),
    ("GET", f"{settings.API_V1_STR}/certificates/{{certificate_id}}/verify/{{verification_code}}"),

    ("GET", f"{settings.API_V1_STR}/feedback/"),
    ("POST", f"{settings.API_V1_STR}/feedback/"),
    ("DELETE", f"{settings.API_V1_STR}/feedback/{{id}}"),

    ("POST", f"{settings.API_V1_STR}/forum/categories/"),
    ("GET", f"{settings.API_V1_STR}/forum/categories/"),
    ("PUT", f"{settings.API_V1_STR}/forum/categories/{{category_id}}"),
    ("DELETE", f"{settings.API_V1_STR}/forum/categories/{{category_id}}"),
    ("GET", f"{settings.API_V1_STR}/forum/topics/"),
    ("POST", f"{settings.API_V1_STR}/forum/topics/"),
    ("GET", f"{settings.API_V1_STR}/forum/categories/{{category_id}}/topics"),
    ("GET", f"{settings.API_V1_STR}/forum/topics/{{topic_id}}"),
    ("PUT", f"{settings.API_V1_STR}/forum/topics/{{topic_id}}"),
    ("DELETE", f"{settings.API_V1_STR}/forum/topics/{{topic_id}}"),
    ("POST", f"{settings.API_V1_STR}/forum/posts/"),
    ("PUT", f"{settings.API_V1_STR}/forum/posts/{{post_id}}"),
    ("DELETE", f"{settings.API_V1_STR}/forum/posts/{{post_id}}"),

    ("GET", f"{settings.API_V1_STR}/ai/tts/voices"),
    ("GET", f"{settings.API_V1_STR}/ai/stt/languages"),
    ("POST", f"{settings.API_V1_STR}/ai/ask"),
    ("POST", f"{settings.API_V1_STR}/ai/tts"),
    ("POST", f"{settings.API_V1_STR}/ai/stt"),
    ("POST", f"{settings.API_V1_STR}/ai/pronunciation"),
    ("POST", f"{settings.API_V1_STR}/ai/suggest-lesson"),

    ("GET", f"{settings.API_V1_STR}/notifications/"),
    ("GET", f"{settings.API_V1_STR}/notifications/unread-count"),
    ("POST", f"{settings.API_V1_STR}/notifications/{{notification_id}}/read"),
    ("POST", f"{settings.API_V1_STR}/notifications/read-all"),
    ("POST", f"{settings.API_V1_STR}/notifications/admin/send"),

    ("GET", f"{settings.API_V1_STR}/tests/ielts"),
    ("GET", f"{settings.API_V1_STR}/tests/toefl"),
    ("GET", f"{settings.API_V1_STR}/tests/"),
    ("GET", f"{settings.API_V1_STR}/tests/{{test_id}}"),
    ("POST", f"{settings.API_V1_STR}/tests/{{test_id}}/start"),
    ("GET", f"{settings.API_V1_STR}/tests/attempts/me"),
    ("GET", f"{settings.API_V1_STR}/tests/attempts/{{attempt_id}}"),
    ("POST", f"{settings.API_V1_STR}/tests/attempts/{{attempt_id}}/submit"),
    ("POST", f"{settings.API_V1_STR}/tests/attempts/{{attempt_id}}/finish"),

    ("POST", f"{settings.API_V1_STR}/admin/tests/"),
    ("PUT", f"{settings.API_V1_STR}/admin/tests/{{test_id}}"),
    ("POST", f"{settings.API_V1_STR}/admin/tests/{{test_id}}/sections/"),
    ("PUT", f"{settings.API_V1_STR}/admin/tests/sections/{{section_id}}"),
    ("DELETE", f"{settings.API_V1_STR}/admin/tests/sections/{{section_id}}"),
    ("POST", f"{settings.API_V1_STR}/admin/tests/sections/{{section_id}}/questions/"),
    ("PUT", f"{settings.API_V1_STR}/admin/tests/questions/{{question_id}}"),
    ("DELETE", f"{settings.API_V1_STR}/admin/tests/questions/{{question_id}}"),

    ("GET", f"{settings.API_V1_STR}/admin/statistics"),
    ("GET", f"{settings.API_V1_STR}/admin/users"),
    ("POST", f"{settings.API_V1_STR}/admin/users"),
    ("GET", f"{settings.API_V1_STR}/admin/users/{{user_id}}"),
    ("PATCH", f"{settings.API_V1_STR}/admin/users/{{user_id}}"),
    ("DELETE", f"{settings.API_V1_STR}/admin/users/{{user_id}}"),
    ("PATCH", f"{settings.API_V1_STR}/admin/users/{{user_id}}/profile"),
    ("PATCH", f"{settings.API_V1_STR}/admin/users/{{user_id}}/role"),
    ("GET", f"{settings.API_V1_STR}/admin/subscription-plans/"),
    ("POST", f"{settings.API_V1_STR}/admin/subscription-plans/"),
    ("PUT", f"{settings.API_V1_STR}/admin/subscription-plans/{{plan_id}}"),
    ("DELETE", f"{settings.API_V1_STR}/admin/subscription-plans/{{plan_id}}"),
    ("GET", f"{settings.API_V1_STR}/admin/courses/"),
    ("POST", f"{settings.API_V1_STR}/admin/courses/"),
    ("PUT", f"{settings.API_V1_STR}/admin/courses/{{course_id}}"),
    ("DELETE", f"{settings.API_V1_STR}/admin/courses/{{course_id}}"),
    ("GET", f"{settings.API_V1_STR}/admin/interactive-lessons/"),
    ("POST", f"{settings.API_V1_STR}/admin/interactive-lessons/"),
    ("PUT", f"{settings.API_V1_STR}/admin/interactive-lessons/{{lesson_id}}"),
    ("DELETE", f"{settings.API_V1_STR}/admin/interactive-lessons/{{lesson_id}}"),

    ("GET", f"{settings.API_V1_STR}/content/lessons-json"),
    ("PUT", f"{settings.API_V1_STR}/content/lessons-json"),
    ("GET", f"{settings.API_V1_STR}/content/media"),
    ("POST", f"{settings.API_V1_STR}/content/media/upload"),
    ("DELETE", f"{settings.API_V1_STR}/content/media/{{filename}}"),

    ("GET", f"{settings.API_V1_STR}/profile/me"),
    ("PATCH", f"{settings.API_V1_STR}/profile/me"),
    ("GET", f"{settings.API_V1_STR}/profile/stats"),
    ("POST", f"{settings.API_V1_STR}/profile/change-password"),
    ("POST", f"{settings.API_V1_STR}/profile/avatar"),

    ("GET", f"{settings.API_V1_STR}/interactive-lessons/"),
    ("GET", f"{settings.API_V1_STR}/interactive-lessons/{{lesson_id}}"),
    ("POST", f"{settings.API_V1_STR}/interactive-lessons/start-lesson"),
    ("POST", f"{settings.API_V1_STR}/interactive-lessons/send-message"),
    ("POST", f"{settings.API_V1_STR}/interactive-lessons/send-audio-message"),
    ("POST", f"{settings.API_V1_STR}/interactive-lessons/assess-pronunciation"),

    ("POST", f"{settings.API_V1_STR}/lesson-interactions/{{session_id}}/interact"),
    ("GET", f"{settings.API_V1_STR}/lesson-interactions/{{session_id}}/interactions"),

    ("GET", f"{settings.API_V1_STR}/homework/"),
    ("POST", f"{settings.API_V1_STR}/homework/"),
    ("GET", f"{settings.API_V1_STR}/homework/{{homework_id}}"),
    ("GET", f"{settings.API_V1_STR}/homework/lesson/{{lesson_id}}"),
    ("GET", f"{settings.API_V1_STR}/homework/files/{{file_id}}/download"),
    ("POST", f"{settings.API_V1_STR}/homework/{{homework_id}}/assign"),
    ("GET", f"{settings.API_V1_STR}/homework/user/me"),
    ("POST", f"{settings.API_V1_STR}/homework/{{homework_id}}/submit"),
    ("POST", f"{settings.API_V1_STR}/homework/submissions/{{submission_id}}/grade"),
    ("GET", f"{settings.API_V1_STR}/homework/submissions/me"),
    ("POST", f"{settings.API_V1_STR}/homework/{{homework_id}}/submit-oral"),
    ("POST", f"{settings.API_V1_STR}/homework/grade/{{user_homework_id}}"),

    ("GET", f"{settings.API_V1_STR}/payments/"),
    ("POST", f"{settings.API_V1_STR}/payments/webhook/stripe"),
    ("POST", f"{settings.API_V1_STR}/payments/create-checkout-session"),

    ("POST", f"{settings.API_V1_STR}/webrtc/rooms/create"),
    ("GET", f"{settings.API_V1_STR}/webrtc/rooms/{{room_id}}/users"),
    ("POST", f"{settings.API_V1_STR}/webrtc/rooms/{{room_id}}/end"),

    ("GET", f"{settings.API_V1_STR}/avatars/"),
    ("GET", f"{settings.API_V1_STR}/avatars/{{avatar_id}}"),

    ("GET", f"{settings.API_V1_STR}/metrics"),
    ("GET", f"{settings.API_V1_STR}/metrics/health"),
    ("GET", f"{settings.API_V1_STR}/metrics/status"),

    ("GET", f"{settings.API_V1_STR}/recommendations/personalized"),
    ("GET", f"{settings.API_V1_STR}/recommendations/adaptive-lesson-plan/{{lesson_id}}"),
    ("GET", f"{settings.API_V1_STR}/recommendations/for-you"),
]


def _normalize(path: str) -> str:
    # Remove path parameters to allow pattern existence checks
    return path.replace("{", "{")


def get_registered_routes():
    registered = []
    for r in app.router.routes:
        try:
            path = r.path
            methods = getattr(r, "methods", set()) or set()
            registered.append((path, methods))
        except Exception:
            continue
    return registered


def route_exists(method: str, path_pattern: str) -> bool:
    registered = get_registered_routes()
    # simple match: either exact path or same structure ignoring parameter names
    for path, methods in registered:
        if method.upper() in methods:
            if path == path_pattern:
                return True
            # match parameterized paths by replacing {var}
            if "{" in path_pattern and "/".join([
                ("{}" if seg.startswith("{") and seg.endswith("}") else seg)
                for seg in path.strip("/").split("/")
            ]) == "/".join([
                ("{}" if seg.startswith("{") and seg.endswith("}") else seg)
                for seg in path_pattern.strip("/").split("/")
            ]):
                return True
    return False


LIVE_BASE_URL = os.getenv("LIVE_BASE_URL")  # e.g. http://0.0.0.0:8002


@pytest.mark.skipif(LIVE_BASE_URL is not None, reason="Route introspection only in INPROC mode")
@pytest.mark.parametrize("method,path", ROUTE_INVENTORY)
def test_route_exists_inproc(method, path):
    assert route_exists(method, path), f"Missing route: {method} {path}"


@pytest.mark.skipif(LIVE_BASE_URL is None, reason="LIVE mode only")
@pytest.mark.parametrize("method,path,requires_auth", SMOKE_ENDPOINTS)
def test_smoke_endpoints_live(method, path, requires_auth):
    headers = {}
    # obtain token via live login if needed
    if requires_auth:
        live_user = os.getenv("LIVE_USER_EMAIL")
        live_pass = os.getenv("LIVE_USER_PASSWORD")
        if live_user and live_pass:
            # login form-encoded
            login_url = f"{LIVE_BASE_URL}{settings.API_V1_STR}/login/access-token"
            with httpx.Client(timeout=10.0) as hc:
                lr = hc.post(login_url, data={"username": live_user, "password": live_pass})
                if lr.status_code == 200:
                    token = lr.json().get("access_token")
                    if token:
                        headers["Authorization"] = f"Bearer {token}"

    url = f"{LIVE_BASE_URL}{path}"
    with httpx.Client(timeout=10.0) as hc:
        method_u = method.upper()
        if method_u == "GET":
            r = hc.get(url, headers=headers)
        elif method_u == "POST":
            # Special case: try to login with provided creds
            if path == f"{settings.API_V1_STR}/login/access-token":
                live_user = os.getenv("LIVE_USER_EMAIL")
                live_pass = os.getenv("LIVE_USER_PASSWORD")
                data = {"username": live_user, "password": live_pass} if (live_user and live_pass) else {}
                r = hc.post(url, data=data, headers=headers)
            else:
                # generic minimal body; many endpoints will 401/403/422 which is acceptable
                r = hc.post(url, json={}, headers=headers)
        elif method_u == "PATCH":
            r = hc.patch(url, json={}, headers=headers)
        elif method_u == "PUT":
            r = hc.put(url, json={}, headers=headers)
        elif method_u == "DELETE":
            r = hc.delete(url, headers=headers)
        else:
            pytest.skip(f"Unsupported method {method}")

    acceptable = {200, 201, 202, 204}
    # Protected endpoints may return 401/403 depending on permissions or missing token
    if requires_auth:
        acceptable |= {401, 403}
    # Endpoints with unknown IDs or not-found resources
    acceptable |= {404}
    # Write methods often need payload/permissions/content-type
    if method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
        acceptable |= {400, 405, 415, 422}
    # Login endpoint may return 400/401/422 for invalid credentials or formats
    if path == f"{settings.API_V1_STR}/login/access-token":
        acceptable |= {400, 401, 422}
    assert r.status_code in acceptable, (
        f"LIVE {method} {url} -> {r.status_code}: {getattr(r, 'text', '')}"
    )


@pytest.mark.skipif(LIVE_BASE_URL is not None, reason="INPROC mode only")
@pytest.mark.parametrize("method,path,requires_auth", SMOKE_ENDPOINTS)
def test_smoke_endpoints_inproc(client, power_user_token_headers, method, path, requires_auth):
    headers = power_user_token_headers if requires_auth else {}
    # Make request with minimal payloads similar to LIVE test
    if method.upper() == "GET":
        r = client.get(path, headers=headers)
    elif method.upper() == "POST":
        if path == f"{settings.API_V1_STR}/login/access-token":
            # No creds in INPROC; allow 400/401/422 later
            r = client.post(path, data={}, headers=headers)
        else:
            r = client.post(path, json={}, headers=headers)
    elif method.upper() == "PATCH":
        r = client.patch(path, json={}, headers=headers)
    elif method.upper() == "PUT":
        r = client.put(path, json={}, headers=headers)
    elif method.upper() == "DELETE":
        r = client.delete(path, headers=headers)
    else:
        pytest.skip(f"Unsupported method {method}")

    acceptable = {200, 201, 202, 204}
    if requires_auth:
        acceptable |= {401, 403}
    acceptable |= {404}
    if method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
        acceptable |= {400, 405, 415, 422}
    if path == f"{settings.API_V1_STR}/login/access-token":
        acceptable |= {400, 401, 422}
    assert r.status_code in acceptable, (
        f"{method} {path} -> {r.status_code}: {r.text}"
    )

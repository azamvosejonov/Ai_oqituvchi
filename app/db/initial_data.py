import logging
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.db import base  # noqa: F401
from app.schemas import UserRole

logger = logging.getLogger(__name__)


ROLES = [
    {
        "name": UserRole.superadmin.value, 
        "description": "Superadmin Role",
        "gpt4o_requests_limit": -1,  # Unlimited
        "stt_requests_limit": -1,
        "tts_chars_limit": -1,
        "pronunciation_analysis_limit": -1,
    },
    {
        "name": UserRole.admin.value, 
        "description": "Admin Role",
        "gpt4o_requests_limit": -1,  # Unlimited
        "stt_requests_limit": -1,
        "tts_chars_limit": -1,
        "pronunciation_analysis_limit": -1,
    },
    {
        "name": UserRole.premium.value, 
        "description": "Premium User Role",
        "gpt4o_requests_limit": 1000,
        "stt_requests_limit": 2500,
        "tts_chars_limit": 125000,
        "pronunciation_analysis_limit": 500,
    },
    {
        "name": UserRole.free.value, 
        "description": "Free User Role",
        "gpt4o_requests_limit": 50,
        "stt_requests_limit": 100,
        "tts_chars_limit": 5000,
        "pronunciation_analysis_limit": 20,
    },
]

SUBSCRIPTION_PLANS = [
    {
        "name": "Free Trial",
        "description": "1-day free trial for all new users.",
        "price": 0.00,
        "duration_days": 1,
        "is_active": True,
        "features": '["Limited access to video lessons", "Basic AI chat"]',
        "stripe_price_id": "price_free_trial",
        "gpt4o_requests_quota": 50,
        "stt_requests_quota": 100,
        "tts_chars_quota": 5000,
        "pronunciation_analysis_quota": 20
    },
    {
        "name": "Weekly",
        "description": "Full access for one week.",
        "price": 4.99,
        "duration_days": 7,
        "is_active": True,
        "features": '["Full access to all content", "Premium AI features"]',
        "stripe_price_id": "price_weekly",
        "gpt4o_requests_quota": 200,
        "stt_requests_quota": 500,
        "tts_chars_quota": 25000,
        "pronunciation_analysis_quota": 100
    },
    {
        "name": "Monthly",
        "description": "Full access for one month.",
        "price": 14.99,
        "duration_days": 30,
        "is_active": True,
        "features": '["Full access to all content", "Premium AI features"]',
        "stripe_price_id": "price_monthly",
        "gpt4o_requests_quota": 1000,
        "stt_requests_quota": 2500,
        "tts_chars_quota": 125000,
        "pronunciation_analysis_quota": 500
    },
    {
        "name": "Quarterly",
        "description": "Full access for three months.",
        "price": 39.99,
        "duration_days": 90,
        "is_active": True,
        "features": '["Full access to all content", "Premium AI features"]',
        "stripe_price_id": "price_quarterly",
        "gpt4o_requests_quota": 3500,
        "stt_requests_quota": 8000,
        "tts_chars_quota": 400000,
        "pronunciation_analysis_quota": 1750
    },
    {
        "name": "Semi-Annual",
        "description": "Full access for six months.",
        "price": 69.99,
        "duration_days": 180,
        "is_active": True,
        "features": '["Full access to all content", "Premium AI features"]',
        "stripe_price_id": "price_semi_annual",
        "gpt4o_requests_quota": 8000,
        "stt_requests_quota": 20000,
        "tts_chars_quota": 1000000,
        "pronunciation_analysis_quota": 4000
    },
    {
        "name": "Annual",
        "description": "Full access for one year.",
        "price": 99.99,
        "duration_days": 365,
        "is_active": True,
        "features": '["Full access to all content", "Premium AI features"]',
        "stripe_price_id": "price_annual",
        "gpt4o_requests_quota": 20000,
        "stt_requests_quota": 50000,
        "tts_chars_quota": 2500000,
        "pronunciation_analysis_quota": 10000
    },
]

def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=db.get_bind())

    roles = ["superadmin", "admin", "teacher", "premium", "free"]
    for role_name in roles:
        role = crud.role.get_by_name(db, name=role_name)
        if not role:
            role_in = schemas.RoleCreate(name=role_name, description=f"{role_name.capitalize()} role")
            crud.role.create(db, obj_in=role_in)
            logger.info(f"Created role: {role_name}")

    # Create subscription plans
    plans = [
        {
            "name": "Free Trial",
            "description": "1-day free trial for all new users.",
            "price": 0.00,
            "duration_days": 1,
            "is_active": True,
            "features": '["Limited access to video lessons", "Basic AI chat"]',
            "stripe_price_id": "price_free_trial",
            "gpt4o_requests_quota": 50,
            "stt_requests_quota": 100,
            "tts_chars_quota": 5000,
            "pronunciation_analysis_quota": 20
        },
        {
            "name": "Weekly",
            "description": "Full access for one week.",
            "price": 4.99,
            "duration_days": 7,
            "is_active": True,
            "features": '["Full access to all content", "Premium AI features"]',
            "stripe_price_id": "price_weekly",
            "gpt4o_requests_quota": 200,
            "stt_requests_quota": 500,
            "tts_chars_quota": 25000,
            "pronunciation_analysis_quota": 100
        },
        {
            "name": "Monthly",
            "description": "Full access for one month.",
            "price": 14.99,
            "duration_days": 30,
            "is_active": True,
            "features": '["Full access to all content", "Premium AI features"]',
            "stripe_price_id": "price_monthly",
            "gpt4o_requests_quota": 1000,
            "stt_requests_quota": 2500,
            "tts_chars_quota": 125000,
            "pronunciation_analysis_quota": 500
        },
        {
            "name": "Quarterly",
            "description": "Full access for three months.",
            "price": 39.99,
            "duration_days": 90,
            "is_active": True,
            "features": '["Full access to all content", "Premium AI features"]',
            "stripe_price_id": "price_quarterly",
            "gpt4o_requests_quota": 3500,
            "stt_requests_quota": 8000,
            "tts_chars_quota": 400000,
            "pronunciation_analysis_quota": 1750
        },
        {
            "name": "Semi-Annual",
            "description": "Full access for six months.",
            "price": 69.99,
            "duration_days": 180,
            "is_active": True,
            "features": '["Full access to all content", "Premium AI features"]',
            "stripe_price_id": "price_semi_annual",
            "gpt4o_requests_quota": 8000,
            "stt_requests_quota": 20000,
            "tts_chars_quota": 1000000,
            "pronunciation_analysis_quota": 4000
        },
        {
            "name": "Annual",
            "description": "Full access for one year.",
            "price": 99.99,
            "duration_days": 365,
            "is_active": True,
            "features": '["Full access to all content", "Premium AI features"]',
            "stripe_price_id": "price_annual",
            "gpt4o_requests_quota": 20000,
            "stt_requests_quota": 50000,
            "tts_chars_quota": 2500000,
            "pronunciation_analysis_quota": 10000
        },
    ]

    for plan_data in plans:
        plan = crud.subscription.get_subscription_plan_by_name(db, name=plan_data["name"])
        if not plan:
            plan_in = schemas.SubscriptionPlanCreate(**plan_data)
            crud.subscription.create_subscription_plan(db, obj_in=plan_in)
            logger.info(f"Created subscription plan: {plan_data['name']}")

    # Create first superuser
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            username=settings.FIRST_SUPERUSER,
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            full_name="Initial Super User"
        )
        user = crud.user.create(db, obj_in=user_in)

        # Assign superuser role
        superuser_role = crud.role.get_by_name(db, name="superadmin")
        if superuser_role:
            user.roles.append(superuser_role)
            db.add(user)
            db.commit()

    # Create test user
    test_user = crud.user.get_by_email(db, email=settings.EMAIL_TEST_USER)
    if not test_user:
        user_in = schemas.UserCreate(
            username=settings.EMAIL_TEST_USER,
            email=settings.EMAIL_TEST_USER,
            password=settings.EMAIL_TEST_USER_PASSWORD,
            is_superuser=False,
            full_name="Test User"
        )
        test_user = crud.user.create(db, obj_in=user_in)

    # Create a default AI Avatar
    avatar = crud.ai_avatar.get_by_name(db, name="Orzu")
    if not avatar:
        avatar_in = schemas.AIAvatarCreate(
            name="Orzu",
            description="A friendly and helpful AI assistant for learning languages.",
            avatar_url="https://example.com/orzu.png",
            voice_id="default_voice",
            language="uz-UZ",
            is_public=True,
        )
        avatar = crud.ai_avatar.create(db, obj_in=avatar_in)
        logger.info("Created default AI Avatar: Orzu")

    # Create a default Course
    course = crud.course.get_by_title(db, title="English for Beginners")
    if not course:
        # Assuming the first superuser is the default instructor
        superuser = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
        if superuser:
            course_in = schemas.CourseCreate(
                title="English for Beginners",
                description="A comprehensive course for starting your English learning journey.",
                difficulty_level="Beginner",
                instructor_id=superuser.id  # Assign superuser's ID
            )
            course = crud.course.create_with_instructor(
                db, obj_in=course_in
            )
            logger.info("Created default course: English for Beginners")

    # Create some lessons if none exist for the course
    if course and avatar and not course.lessons:
        lessons_to_create = [
            {
                "title": "Lesson 1: Greetings",
                "description": "Learn common English greetings.",
                "content": {"text": "Hello! How are you? - Bu eng keng tarqalgan salomlashish usuli..."},
                "order": 1,
                "is_premium": False,
                "course_id": course.id,
                "avatar_id": avatar.id,
                "difficulty": "easy",
            },
            {
                "title": "Lesson 2: The Alphabet",
                "description": "Learn the English alphabet.",
                "content": {"text": "The English alphabet consists of 26 letters..."},
                "order": 2,
                "is_premium": False,
                "course_id": course.id,
                "avatar_id": avatar.id,
                "difficulty": "easy",
            },
            {
                "title": "Lesson 3: Basic Verbs (Premium)",
                "description": "Learn essential verbs like to be, to have, to do.",
                "content": {"text": "Verbs are action words. Let's start with the most important ones..."},
                "order": 3,
                "is_premium": True,
                "course_id": course.id,
                "avatar_id": avatar.id,
                "difficulty": "medium",
            },
        ]

        for lesson_data in lessons_to_create:
            # Ensure avatar_id is correctly passed from the dictionary
            lesson_in = schemas.InteractiveLessonCreate(**lesson_data)
            crud.interactive_lesson.create(db, obj_in=lesson_in)
            logger.info(f"Created lesson: {lesson_data['title']}")
    elif not avatar:
        logger.error("Default AI Avatar not found, cannot create lessons.")

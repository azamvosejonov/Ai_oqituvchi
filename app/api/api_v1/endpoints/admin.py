from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.models.lesson import LessonDifficulty as ModelLessonDifficulty
from app.api import deps
from app.core.role_checker import RoleChecker
from app.schemas import UserRole
from app.schemas.user import UserRoleUpdate, UserUpdateProfile, UserInDBBase

import logging
logging.basicConfig(level=logging.INFO)

router = APIRouter()

# Role checkers for admin endpoints
admin_role_checker = RoleChecker([UserRole.admin.value, UserRole.superadmin.value])
superadmin_role_checker = RoleChecker([UserRole.superadmin.value])

def get_current_admin_user(
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_check_result: None = Depends(deps.ip_check),
) -> models.User:
    """Dependency to check if the user is an admin or superadmin."""
    user_roles = {role.name for role in current_user.roles}
    if not {UserRole.admin.value, UserRole.superadmin.value}.intersection(user_roles):
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges"
        )
    return current_user

@router.get("/statistics", response_model=schemas.DashboardStats)
def get_admin_dashboard_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ip_check_result: None = Depends(deps.ip_check),
) -> Any:
    """
    Retrieve admin dashboard statistics.
    - Total users
    - Premium users
    - Active subscriptions
    - Total revenue
    - etc.
    Superusers only.
    """
    stats = crud.statistics.get_dashboard_stats(db)
    return stats

@router.get("/users", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    current_admin: models.User = Depends(get_current_admin_user),
) -> Any:
    """Retrieve all users. Only for admins. Can be filtered by role."""
    users = crud.user.get_multi(db, skip=skip, limit=limit, role=role)
    return users

@router.post("/users", response_model=UserInDBBase)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ip_check_result: None = Depends(deps.ip_check),
) -> Any:
    """Create new user. Superusers only."""
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud.user.create(db, obj_in=user_in)
    return user

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(get_current_admin_user),
) -> Any:
    """Get a specific user by id. Only for admins."""
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/users/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdateAdmin,
    current_admin: models.User = Depends(get_current_admin_user),
) -> Any:
    """Update a user's details. Only for admins."""
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system.",
        )

    if crud.user.is_superuser(user) and not crud.user.is_superuser(current_admin):
        raise HTTPException(status_code=403, detail="Admins cannot modify a Superadmin.")

    update_data = user_in.model_dump(exclude_unset=True)

    # Uniqueness checks
    new_email = update_data.get("email")
    if new_email and new_email != user.email:
        existing = crud.user.get_by_email(db, email=new_email)
        if existing and existing.id != user.id:
            raise HTTPException(status_code=400, detail="The user with this email already exists in the system.")

    new_username = update_data.get("username")
    if new_username and new_username != user.username:
        existing_u = crud.user.get_by_username(db, username=new_username)
        if existing_u and existing_u.id != user.id:
            raise HTTPException(status_code=400, detail="The user with this username already exists in the system.")

    if "roles" in update_data:
        role_names = update_data.pop("roles")
        user.roles = [crud.role.get_or_create(db, name=name) for name in role_names]

    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.patch("/users/{user_id}/profile", response_model=schemas.User)
def update_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdateProfile,
    current_admin: models.User = Depends(get_current_admin_user),
) -> Any:
    """Update a user's profile information (full_name, email)."""
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Uniqueness check for email if provided
    upd = user_in.model_dump(exclude_unset=True)
    new_email = upd.get("email")
    if new_email and new_email != user.email:
        existing = crud.user.get_by_email(db, email=new_email)
        if existing and existing.id != user.id:
            raise HTTPException(status_code=400, detail="The user with this email already exists in the system.")

    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user

@router.patch("/users/{user_id}/role", response_model=schemas.User)
def update_user_role(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserRoleUpdate,
    current_admin: models.User = Depends(deps.get_current_active_superuser), 
    ip_check_result: None = Depends(deps.ip_check),
) -> Any:
    """Update a user's role. Only for superadmins."""
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system.",
        )

    if user.id == current_admin.id:
        raise HTTPException(status_code=403, detail="You cannot change your own role.")

    user = crud.user.update_role(db, user=user, role_name=user_in.role)
    return user

@router.delete("/users/{user_id}", response_model=schemas.Message)
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_active_superuser),
    ip_check_result: None = Depends(deps.ip_check),
) -> Any:
    """Delete a user. Only for superadmins."""
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_admin.id:
        raise HTTPException(status_code=403, detail="You cannot delete your own account.")

    if crud.user.is_superuser(user):
        raise HTTPException(status_code=403, detail="Superusers cannot be deleted.")

    crud.user.remove(db, id=user_id)
    return {"msg": f"User {user_id} successfully deleted."}

# Subscription Plan Management

@router.get("/subscription-plans/", response_model=List[schemas.SubscriptionPlan])
def read_subscription_plans(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ip_check_result: None = Depends(deps.ip_check),
) -> Any:
    """Retrieve all subscription plans. Superusers only."""
    plans = crud.subscription.get_subscription_plans(db, skip=skip, limit=limit)
    return plans

@router.post("/subscription-plans/", response_model=schemas.SubscriptionPlan)
def create_subscription_plan(
    *,
    db: Session = Depends(deps.get_db),
    plan_in: schemas.SubscriptionPlanCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ip_check_result: None = Depends(deps.ip_check),
) -> Any:
    """Create a new subscription plan. Superusers only."""
    plan = crud.subscription.create_subscription_plan(db, obj_in=plan_in)
    return plan

@router.put("/subscription-plans/{plan_id}", response_model=schemas.SubscriptionPlan)
def update_subscription_plan(
    *,
    db: Session = Depends(deps.get_db),
    plan_id: int,
    plan_in: schemas.SubscriptionPlanUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ip_check_result: None = Depends(deps.ip_check),
) -> Any:
    """Update a subscription plan. Superusers only."""
    plan = crud.subscription.get_subscription_plan(db, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    plan = crud.subscription.update_subscription_plan(db, db_plan=plan, plan_in=plan_in)
    return plan

@router.delete("/subscription-plans/{plan_id}", response_model=schemas.SubscriptionPlan)
def delete_subscription_plan(
    *,
    db: Session = Depends(deps.get_db),
    plan_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ip_check_result: None = Depends(deps.ip_check),
) -> Any:
    """Delete a subscription plan. Superusers only."""
    plan = crud.subscription.delete_subscription_plan(db, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    return plan

# Content Management: Courses

@router.get("/courses/", response_model=List[schemas.Course])
def read_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_admin_user),
) -> Any:
    """Retrieve all courses. Only for admins."""
    courses = crud.course.get_multi(db, skip=skip, limit=limit)
    return courses

@router.post("/courses/", response_model=schemas.Course)
def create_course(
    course_in: schemas.CourseCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ip_check_result: None = Depends(deps.ip_check),
) -> schemas.Course:
    """Create a new course. Superusers only."""
    course_in.instructor_id = current_user.id
    course = crud.course.create_with_instructor(
        db, obj_in=course_in
    )
    return course

@router.put("/courses/{course_id}", response_model=schemas.Course)
def update_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    course_in: schemas.CourseUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ip_check_result: None = Depends(deps.ip_check),
) -> Any:
    """Update a course. Superusers only."""
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    course = crud.course.update(db, db_obj=course, obj_in=course_in)
    return course

@router.delete("/courses/{course_id}", response_model=schemas.Course)
def delete_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ip_check_result: None = Depends(deps.ip_check),
) -> Any:
    """Delete a course. Superusers only."""
    course = crud.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Prepare sanitized response before deletion to avoid lazy-load on detached instance
    resp = {
        "id": course.id,
        "title": getattr(course, "title", None),
        "description": getattr(course, "description", None),
        "short_description": getattr(course, "short_description", None),
        "thumbnail_url": getattr(course, "thumbnail_url", None),
        "is_published": getattr(course, "is_published", False),
        "is_featured": getattr(course, "is_featured", False),
        "difficulty_level": getattr(course, "difficulty_level", None),
        "estimated_duration": getattr(course, "estimated_duration", None),
        "language": getattr(course, "language", None),
        "price": getattr(course, "price", None),
        "discount_price": getattr(course, "discount_price", None),
        "instructor_id": getattr(course, "instructor_id", None),
        "category": getattr(course, "category", None),
        "tags": getattr(course, "tags", None),
        "requirements": getattr(course, "requirements", None),
        "learning_outcomes": getattr(course, "learning_outcomes", None),
        "created_at": getattr(course, "created_at", None),
        "updated_at": getattr(course, "updated_at", None),
        "instructor": None,
        "lessons": [],
    }

    # Proceed with deletion
    db.delete(course)
    db.commit()
    return resp

# Content Management: Interactive Lessons

@router.get("/interactive-lessons/", response_model=List[schemas.InteractiveLesson])
def read_lessons_admin(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ip_check_result: None = Depends(deps.ip_check),
) -> Any:
    """
    Retrieve all interactive lessons. Superusers only.
    """
    lessons = crud.interactive_lesson.get_multi(db, skip=skip, limit=limit)
    return lessons

@router.post("/interactive-lessons/", response_model=schemas.InteractiveLesson)
def create_lesson(
    *,
    db: Session = Depends(deps.get_db),
    lesson_in: schemas.InteractiveLessonCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ip_check_result: None = Depends(deps.ip_check),
) -> Any:
    """Create a new interactive lesson. Superusers only."""
    # Ensure course_id exists; create or reuse a default course if missing
    if not getattr(lesson_in, "course_id", None):
        # Try to find an existing default course
        existing = db.query(models.Course).filter(models.Course.title == "General").first()
        if not existing:
            default_course = schemas.CourseCreate(
                title="General",
                description="Default course for interactive lessons",
                difficulty_level="beginner",
                instructor_id=current_user.id,
                is_published=False,
            )
            existing = crud.course.create_with_instructor(db, obj_in=default_course)
        lesson_in.course_id = existing.id

    # Normalize difficulty to model enum values
    valid_difficulties = {e.value for e in ModelLessonDifficulty}
    diff = getattr(lesson_in, "difficulty", None)
    if not diff or diff not in valid_difficulties:
        lesson_in.difficulty = ModelLessonDifficulty.MEDIUM.value

    lesson = crud.interactive_lesson.create(db, obj_in=lesson_in)
    return lesson

@router.put("/interactive-lessons/{lesson_id}", response_model=schemas.InteractiveLesson)
def update_lesson(
    *,
    db: Session = Depends(deps.get_db),
    lesson_id: int,
    lesson_in: schemas.InteractiveLessonUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ip_check_result: None = Depends(deps.ip_check),
) -> Any:
    """Update an interactive lesson. Superusers only."""
    lesson = crud.interactive_lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    # Normalize difficulty if provided
    if getattr(lesson_in, "difficulty", None):
        valid_difficulties = {e.value for e in ModelLessonDifficulty}
        if lesson_in.difficulty not in valid_difficulties:
            lesson_in.difficulty = ModelLessonDifficulty.MEDIUM.value
    lesson = crud.interactive_lesson.update(db, db_obj=lesson, obj_in=lesson_in)
    return lesson

@router.delete("/interactive-lessons/{lesson_id}", response_model=schemas.InteractiveLesson)
def delete_lesson(
    *,
    db: Session = Depends(deps.get_db),
    lesson_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ip_check_result: None = Depends(deps.ip_check),
) -> Any:
    """Delete an interactive lesson. Superusers only."""
    lesson = crud.interactive_lesson.remove(db, id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson

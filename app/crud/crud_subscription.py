from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from sqlalchemy import func
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.models.subscription import SubscriptionPlan, Subscription
from app.models.user_ai_usage import UserAIUsage
from app.schemas.subscription import SubscriptionPlanCreate, SubscriptionPlanUpdate
from app.crud.crud_user_ai_usage import user_ai_usage
from app.models.user import User  # Import the User model

# SubscriptionPlan CRUD

def get_subscription_plan(db: Session, plan_id: int) -> Optional[SubscriptionPlan]:
    return db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()

def get_subscription_plan_by_name(db: Session, name: str) -> Optional[SubscriptionPlan]:
    return db.query(SubscriptionPlan).filter(SubscriptionPlan.name == name).first()

def get_subscription_plans(db: Session, skip: int = 0, limit: int = 100) -> List[SubscriptionPlan]:
    return db.query(SubscriptionPlan).offset(skip).limit(limit).all()

def create_subscription_plan(db: Session, *, obj_in: SubscriptionPlanCreate) -> SubscriptionPlan:
    # Prevent duplicate stripe_price_id if provided
    if obj_in.stripe_price_id:
        existing = (
            db.query(SubscriptionPlan)
            .filter(SubscriptionPlan.stripe_price_id == obj_in.stripe_price_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription plan with this stripe_price_id already exists",
            )
    db_obj = SubscriptionPlan(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_subscription_plan(db: Session, db_plan: SubscriptionPlan, plan_in: SubscriptionPlanUpdate) -> SubscriptionPlan:
    update_data = plan_in.model_dump(exclude_unset=True)
    # Prevent duplicate stripe_price_id if it is being updated
    new_price_id = update_data.get("stripe_price_id")
    if new_price_id and new_price_id != getattr(db_plan, "stripe_price_id", None):
        conflict = (
            db.query(SubscriptionPlan)
            .filter(SubscriptionPlan.stripe_price_id == new_price_id, SubscriptionPlan.id != db_plan.id)
            .first()
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another subscription plan already uses this stripe_price_id",
            )
    for field, value in update_data.items():
        setattr(db_plan, field, value)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def delete_subscription_plan(db: Session, plan_id: int) -> Optional[SubscriptionPlan]:
    db_plan = db.query(SubscriptionPlan).get(plan_id)
    if db_plan:
        db.delete(db_plan)
        db.commit()
    return db_plan


# User Subscription CRUD

def get_multi(db: Session, *, skip: int = 0, limit: int = 100) -> List[Subscription]:
    """Get multiple subscriptions for admin management."""
    return db.query(Subscription).offset(skip).limit(limit).all()

def get_subscription(db: Session, subscription_id: int) -> Optional[Subscription]:
    return db.query(Subscription).filter(Subscription.id == subscription_id).first()

def get_user_subscriptions(db: Session, user_id: int) -> List[Subscription]:
    """Get all subscriptions for a specific user."""
    return db.query(Subscription).filter(Subscription.user_id == user_id).all()

def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Subscription]:
    return db.query(Subscription).offset(skip).limit(limit).all()

def update_subscription(db: Session, db_sub: Subscription, sub_in: Dict) -> Subscription:
    update_data = sub_in
    for field, value in update_data.items():
        setattr(db_sub, field, value)
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

def create_with_plan_details(db: Session, user_id: int, plan_id: int) -> Optional[Subscription]:
    """
    Create a new subscription for a user based on a plan, 
    deactivate old ones, and update AI quota.
    """
    plan = get_subscription_plan(db, plan_id)
    if not plan:
        return None

    # Deactivate any existing active subscriptions for the user
    existing_subscriptions = db.query(Subscription).filter(Subscription.user_id == user_id, Subscription.is_active == True).all()
    for sub in existing_subscriptions:
        sub.is_active = False
        db.add(sub)

    # Create new subscription
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=plan.duration_days)
    
    db_subscription = Subscription(
        user_id=user_id,
        plan_id=plan_id,
        start_date=start_date,
        end_date=end_date,
        is_active=True
    )
    db.add(db_subscription)

    # Update or create user's AI quota
    ai_usage_obj = user_ai_usage.get_or_create(db=db, user_id=user_id)
    ai_usage_obj.quota_limit = plan.ai_quota
    ai_usage_obj.usage_count = 0  # Reset usage on new subscription
    db.add(ai_usage_obj)

    db.commit()
    db.refresh(db_subscription)
    return db_subscription

def create_user_subscription(db: Session, user_id: int, plan_id: int) -> Subscription:
    plan = get_subscription_plan(db, plan_id)
    if not plan:
        return None # Or raise an exception

    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=plan.duration_days)

    db_subscription = Subscription(
        user_id=user_id,
        plan_id=plan_id,
        start_date=start_date,
        end_date=end_date,
        is_active=True
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

def create_trial_subscription(db: Session, user_id: int) -> Optional[Subscription]:
    """
    Creates a 1-day trial subscription for a new user.
    This deactivates any previous subscriptions and sets a default AI quota.
    """
    # 1. Find the trial plan (prefer the seeded name 'Free Trial', fallback to legacy 'Trial Plan')
    trial_plan = (
        db.query(SubscriptionPlan)
        .filter(SubscriptionPlan.name.in_(["Free Trial", "Trial Plan"]))
        .order_by(SubscriptionPlan.name.desc())  # ensures 'Free Trial' preferred if both exist
        .first()
    )
    if not trial_plan:
        # If trial plan doesn't exist, we can't create a trial subscription.
        # This should be seeded into the database.
        return None

    # 2. Deactivate any existing active subscriptions for the user
    db.query(Subscription).filter(Subscription.user_id == user_id, Subscription.is_active == True).update({Subscription.is_active: False})

    # 3. Create a new 1-day trial subscription
    end_date = datetime.utcnow() + timedelta(days=trial_plan.duration_days)
    new_subscription = Subscription(
        user_id=user_id,
        plan_id=trial_plan.id,
        start_date=datetime.utcnow(),
        end_date=end_date,
        is_active=True
    )
    db.add(new_subscription)

    # 4. Update the user's trial_ends_at field directly
    user_obj = db.query(User).filter(User.id == user_id).first()
    if user_obj:
        user_obj.trial_ends_at = end_date
        db.add(user_obj)

    # 5. Create or update UserAIUsage with the trial quota
    user_ai_usage_obj = user_ai_usage.get_or_create(db, user_id=user_id)
    user_ai_usage_obj.quota_limit = trial_plan.ai_quota
    user_ai_usage_obj.usage_count = 0  # Reset usage
    db.add(user_ai_usage_obj)

    # 6. Commit all changes to the database
    db.commit()
    db.refresh(new_subscription)
    
    return new_subscription

def get_user_active_subscription(db: Session, user_id: int) -> Optional[Subscription]:
    """
    Retrieves the active subscription for a specific user.
    """
    return db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.is_active == True
    ).first()

def get_user_subscriptions(db: Session, user_id: int) -> List[Subscription]:
    return db.query(Subscription).filter(Subscription.user_id == user_id).all()

def delete_user_subscription(db: Session, subscription_id: int) -> Optional[Subscription]:
    db_subscription = db.query(Subscription).get(subscription_id)
    if db_subscription:
        db.delete(db_subscription)
        db.commit()
    return db_subscription

def get_all_subscriptions(db: Session, skip: int = 0, limit: int = 100) -> List[Subscription]:
    return db.query(Subscription).order_by(Subscription.created_at.desc()).offset(skip).limit(limit).all()

def get_payment_statistics(db: Session) -> dict:
    """
    Calculate payment statistics.
    - Total revenue from all subscriptions.
    - Count of currently active subscriptions.
    """
    total_revenue = (
        db.query(func.sum(SubscriptionPlan.price))
        .join(Subscription, Subscription.plan_id == SubscriptionPlan.id)
        .scalar()
    )

    active_subscriptions_count = (
        db.query(func.count(Subscription.id))
        .filter(Subscription.is_active == True, Subscription.end_date >= datetime.utcnow())
        .scalar()
    )

    return {
        "total_revenue": total_revenue or 0.0,
        "active_subscriptions_count": active_subscriptions_count or 0,
    }

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings

router = APIRouter()

@router.get("/plans", response_model=List[schemas.SubscriptionPlan])
def get_subscription_plans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get all subscription plans.
    """
    subscription_plans = crud.subscription_plan.get_multi(db, skip=skip, limit=limit)
    return subscription_plans

@router.get("/plans/{plan_id}", response_model=schemas.SubscriptionPlan)
def get_subscription_plan(
    plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get a specific subscription plan by ID.
    """
    subscription_plan = crud.subscription_plan.get(db, id=plan_id)
    if not subscription_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    return subscription_plan

@router.get("/my-subscription", response_model=Optional[schemas.Subscription])
def get_my_subscription(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get the current user's active subscription.
    """
    subscription = crud.subscription.get_active_subscription(db, user_id=current_user.id)
    return subscription

@router.post("/upgrade", response_model=schemas.Subscription)
async def upgrade_subscription(
    subscription_update: schemas.SubscriptionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Update the current user's subscription status.
    """
    # Get the user's active subscription
    subscription = crud.subscription.get_active_subscription(db, user_id=current_user.id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    # Update the subscription status
    if subscription_update.is_active is not None:
        subscription.is_active = subscription_update.is_active
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
    
    return subscription

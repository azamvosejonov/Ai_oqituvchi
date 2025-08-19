from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Subscription])
def read_subscriptions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve subscriptions. (Superuser only)
    """
    subscriptions = crud.subscription.get_multi(db, skip=skip, limit=limit)
    return subscriptions


@router.get("/{subscription_id}", response_model=schemas.Subscription)
def read_subscription(
    *,
    db: Session = Depends(deps.get_db),
    subscription_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get subscription by ID. (Superuser only)
    """
    subscription = crud.subscription.get(db, id=subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.put("/{subscription_id}", response_model=schemas.Subscription)
def update_subscription(
    *,
    db: Session = Depends(deps.get_db),
    subscription_id: int,
    subscription_in: schemas.SubscriptionUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a subscription. (Superuser only)
    """
    subscription = crud.subscription.get(db, id=subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    subscription = crud.subscription.update(db, db_obj=subscription, obj_in=subscription_in)
    return subscription


@router.delete("/{subscription_id}", response_model=schemas.Subscription)
def delete_subscription(
    *,
    db: Session = Depends(deps.get_db),
    subscription_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a subscription. (Superuser only)
    """
    subscription = crud.subscription.get(db, id=subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    subscription = crud.subscription.remove(db, id=subscription_id)
    return subscription

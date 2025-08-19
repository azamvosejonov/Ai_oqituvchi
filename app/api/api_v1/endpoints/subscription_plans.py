from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app import models, schemas
from app.api import deps
from app.crud import crud_subscription as crud

router = APIRouter()

@router.post("/", response_model=schemas.SubscriptionPlan, status_code=status.HTTP_201_CREATED)
def create_subscription_plan(
    *, 
    db: Session = Depends(deps.get_db),
    plan_in: schemas.SubscriptionPlanCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    """
    Create a new subscription plan. Only for admins.
    """
    plan = crud.get_subscription_plan_by_name(db, name=plan_in.name)
    if plan:
        raise HTTPException(
            status_code=400,
            detail="The subscription plan with this name already exists in the system.",
        )
    new_plan = crud.create_subscription_plan(db=db, obj_in=plan_in)
    return new_plan

@router.get("/", response_model=List[schemas.SubscriptionPlan])
def read_subscription_plans(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user) # All users can see plans
):
    """
    Retrieve all subscription plans.
    """
    plans = crud.get_subscription_plans(db, skip=skip, limit=limit) if hasattr(crud, 'get_subscription_plans') else []
    return plans

@router.get("/{plan_id}", response_model=schemas.SubscriptionPlan)
def read_subscription_plan(
    plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Get a specific subscription plan by ID.
    """
    plan = crud.get_subscription_plan(db, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    return plan

@router.put("/{plan_id}", response_model=schemas.SubscriptionPlan)
def update_subscription_plan(
    plan_id: int,
    *, 
    db: Session = Depends(deps.get_db),
    plan_in: schemas.SubscriptionPlanUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    """
    Update a subscription plan. Only for admins.
    """
    plan = crud.get_subscription_plan(db, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    updated_plan = crud.update_subscription_plan(db=db, db_plan=plan, plan_in=plan_in)
    return updated_plan

@router.delete("/{plan_id}", response_model=schemas.SubscriptionPlan)
def delete_subscription_plan(
    plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    """
    Delete a subscription plan. Only for admins.
    """
    plan = crud.get_subscription_plan(db, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    deleted_plan = crud.delete_subscription_plan(db=db, plan_id=plan_id)
    return deleted_plan

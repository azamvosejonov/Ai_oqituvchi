from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import List, Any

from app import crud, models, schemas
from app.api import deps
from app.services import stripe_service
from app.core.config import settings
import stripe

router = APIRouter()

@router.get(
    "/plans",
    response_model=List[schemas.SubscriptionPlan],
    summary="List subscription plans",
    description="Return available subscription plans for authenticated users.",
    responses={
        200: {
            "description": "List of plans",
            "content": {
                "application/json": {
                    "example": [
                        {"id": 1, "name": "Monthly", "price": 9.99, "duration_days": 30},
                        {"id": 2, "name": "Annual", "price": 79.0, "duration_days": 365}
                    ]
                }
            }
        }
    }
)
def read_available_subscription_plans(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get available subscription plans for authenticated users.
    """
    try:
        # Use direct query or dedicated functions if available
        plans = db.query(models.SubscriptionPlan).offset(skip).limit(limit).all()
        return plans
    except Exception:
        return []

@router.post(
    "/stripe-webhook",
    summary="Stripe webhook",
    description="Receives Stripe events and updates subscriptions/roles accordingly."
)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: Session = Depends(deps.get_db)
):
    """
    Stripe webhook endpoint to handle payment events.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload=await request.body(),
            sig_header=stripe_signature,
            secret=settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:  # Invalid payload
        raise HTTPException(status_code=400, detail=str(e))
    except stripe.error.SignatureVerificationError as e:  # Invalid signature
        raise HTTPException(status_code=400, detail=str(e))

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get("metadata", {}).get("user_id")
        plan_id = session.get("metadata", {}).get("plan_id")

        if user_id and plan_id:
            user = crud.user.get(db, id=int(user_id))
            plan = crud.get_subscription_plan(db, plan_id=int(plan_id))
            if user and plan:
                # Create subscription record and update AI quotas
                crud.create_with_plan_details(db, user_id=user.id, plan_id=plan.id)

                # Assign premium role automatically after successful payment
                try:
                    premium_role = crud.role.get_by_name(db, name="premium")
                    if premium_role and premium_role not in user.roles:
                        user.roles.append(premium_role)
                        db.add(user)
                        db.commit()
                except Exception:
                    pass

                # Mark a payment verification entry as paid_pending_approval (optional)
                try:
                    crud.payment_verification.create_or_update(
                        db,
                        user_id=user.id,
                        provider="stripe",
                        provider_reference=session.get("id"),
                        status="paid_pending_approval",
                        amount=plan.price,
                        currency="usd",
                        raw_event=event
                    )
                except Exception:
                    pass
        else:
            # Log an error if metadata is missing
            print(f"Error: Missing user_id or plan_id in Stripe checkout session metadata. Session ID: {session.id}")

    return {"status": "success"}

@router.get(
    "/status",
    summary="Get my subscription status",
    responses={
        200: {
            "description": "Current subscription status",
            "content": {
                "application/json": {
                    "example": {
                        "active": True,
                        "plan": "Monthly",
                        "plan_id": 1,
                        "ends_at": "2025-12-31T23:59:59Z",
                        "has_premium_role": True
                    }
                }
            }
        }
    }
)
def get_subscription_status(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Joriy foydalanuvchining obuna holatini qaytaradi.
    """
    try:
        active = crud.subscription.get_user_active_subscription(db, user_id=current_user.id)
        has_premium = any(r.name == "premium" for r in getattr(current_user, "roles", []))
        if active:
            return {
                "active": True,
                "plan": getattr(active.plan, "name", None),
                "plan_id": getattr(active.plan, "id", None),
                "ends_at": active.end_date,
                "has_premium_role": has_premium,
            }
        return {
            "active": False,
            "plan": None,
            "plan_id": None,
            "ends_at": None,
            "has_premium_role": has_premium,
        }
    except Exception:
        return {
            "active": False,
            "plan": None,
            "plan_id": None,
            "ends_at": None,
            "has_premium_role": False,
        }

@router.post(
    "/create-checkout-session",
    response_model=schemas.StripeCheckoutSession,
    summary="Create Stripe checkout session",
    description="Create a Stripe Checkout session for the selected plan.",
    responses={
        200: {
            "description": "Checkout session created",
            "content": {
                "application/json": {
                    "example": {
                        "id": "cs_test_123",
                        "url": "https://checkout.stripe.com/c/pay/cs_test_123",
                        "mode": "subscription"
                    }
                }
            }
        },
        404: {"description": "Subscription plan not found"}
    }
)
def create_checkout_session(
    *, 
    db: Session = Depends(deps.get_db),
    plan_id_in: schemas.SubscriptionPlanId, 
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Create a Stripe checkout session for a subscription plan.
    """
    plan = crud.get_subscription_plan(db, plan_id=plan_id_in.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")

    session_data = stripe_service.create_stripe_checkout_session(plan=plan, user=current_user)
    if "error" in session_data:
        raise HTTPException(status_code=500, detail=session_data["error"])

    return session_data

@router.get(
    "/",
    response_model=List[schemas.Subscription],
    summary="List all user subscriptions (admin)"
)
def read_all_subscriptions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> List[schemas.Subscription]:
    """
    Retrieve all subscriptions (admin only).
    """
    subscriptions = crud.get_all_subscriptions(db, skip=skip, limit=limit)
    return subscriptions

@router.post(
    "/users/{user_id}/subscriptions",
    response_model=schemas.Subscription,
    status_code=status.HTTP_201_CREATED,
    summary="Create subscription for user (admin)"
)
def create_subscription_for_user(
    user_id: int,
    plan_id: int, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    """
    Create a new subscription for a specific user. (Admin only)
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    plan = crud.get_subscription_plan(db, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")

    subscription = crud.create_user_subscription(db=db, user_id=user_id, plan_id=plan_id)
    return subscription

@router.get(
    "/me",
    response_model=List[schemas.Subscription],
    summary="List my subscriptions"
)
def read_my_subscriptions(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Get the current user's subscriptions.
    """
    subscriptions = crud.get_user_subscriptions(db=db, user_id=current_user.id)
    return subscriptions

@router.get(
    "/users/{user_id}/subscriptions",
    response_model=List[schemas.Subscription],
    summary="List user's subscriptions (admin)"
)
def read_user_subscriptions(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    """
    Get a specific user's subscriptions. (Admin only)
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    subscriptions = crud.get_user_subscriptions(db=db, user_id=user_id)
    return subscriptions

@router.delete(
    "/{subscription_id}",
    response_model=schemas.Subscription,
    summary="Delete subscription (superuser)",
    responses={
        200: {
            "description": "Deleted subscription",
            "content": {
                "application/json": {
                    "example": {
                        "id": 10,
                        "user_id": 5,
                        "plan_id": 1,
                        "is_active": False
                    }
                }
            }
        },
        404: {"description": "Subscription not found"}
    }
)
def delete_user_subscription(
    subscription_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    """
    Delete a user subscription. (Superuser only)
    """
    deleted_subscription = crud.subscription.delete_user_subscription(db=db, subscription_id=subscription_id)
    if not deleted_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return deleted_subscription


@router.get(
    "/admin/config-check",
    summary="Stripe config and plans check (admin)",
    description="Returns whether Stripe keys are set and which plans miss stripe_price_id.",
)
def stripe_config_check(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    """Admin diagnostic for Stripe config and plans."""
    stripe_key_set = bool(getattr(settings, "STRIPE_API_KEY", None))
    webhook_secret_set = bool(getattr(settings, "STRIPE_WEBHOOK_SECRET", None))
    domain_set = bool(getattr(settings, "DOMAIN", None))

    plans = db.query(models.SubscriptionPlan).all()
    missing_price_ids = [
        {"id": p.id, "name": p.name}
        for p in plans
        if not getattr(p, "stripe_price_id", None)
    ]

    return {
        "stripe_api_key": stripe_key_set,
        "stripe_webhook_secret": webhook_secret_set,
        "domain": domain_set,
        "plans_total": len(plans),
        "plans_missing_stripe_price_id": missing_price_ids,
    }

@router.post(
    "/admin/approve/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Approve premium (admin)",
    description="Admin approves premium after payment verification and assigns role.",
    responses={
        200: {
            "description": "Approved",
            "content": {
                "application/json": {
                    "example": {"status": "approved", "user_id": 123}
                }
            }
        }
    }
)
def approve_user_premium(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    """
    Admin approves premium after payment verification.
    - Assigns 'premium' role if missing
    - Ensures the latest subscription is active
    - Notifies the user
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Ensure user has an active subscription
    active_sub = crud.subscription.get_user_active_subscription(db=db, user_id=user.id) if hasattr(crud, 'subscription') else None
    if not active_sub:
        # As a fallback, mark the most recent as active if exists
        subs = crud.get_user_subscriptions(db=db, user_id=user.id)
        if not subs:
            raise HTTPException(status_code=400, detail="No subscriptions found for user")
        latest = sorted(subs, key=lambda s: s.start_date or 0, reverse=True)[0]
        latest.is_active = True
        db.add(latest)
        db.commit()

    # Assign premium role
    premium_role = crud.role.get_by_name(db, name="premium")
    if premium_role and premium_role not in user.roles:
        user.roles.append(premium_role)
        db.add(user)
        db.commit()

    # Notify user
    try:
        crud.notification.create_for_user(
            db,
            obj_in=schemas.NotificationCreate(
                user_id=user.id,
                message="Obunangiz admin tomonidan tasdiqlandi. Premium faollashtirildi.",
                notification_type='subscription'
            )
        )
    except Exception:
        pass

    return {"status": "approved", "user_id": user.id}

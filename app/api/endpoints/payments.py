import json
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import stripe

from app import models, schemas, crud
from app.api import deps
from app.core.config import settings
from app.models.notification import PaymentStatus
from app.schemas.notification import PaymentNotificationCreate

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Stripe
stripe.api_key = settings.STRIPE_API_KEY

@router.get("/", response_model=list)
def read_user_payments(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Get user's payment history and subscription information.
    """
    # For now, return basic payment info - can be expanded later
    try:
        # Get user's subscriptions as payment history
        user_subscriptions = crud.subscription.get_multi_by_owner(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        ) if hasattr(crud.subscription, 'get_multi_by_owner') else []
        
        return [
            {
                "id": sub.id if hasattr(sub, 'id') else 0,
                "type": "subscription",
                "status": "active" if getattr(sub, 'is_active', False) else "inactive",
                "amount": 0,  # Will be populated when payment model is available
                "created_at": getattr(sub, 'created_at', None)
            } for sub in user_subscriptions
        ]
    except Exception as e:
        # Return empty list if no payment history available
        return []

@router.post("/webhook/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: Session = Depends(deps.get_db)
):
    """
    Handle Stripe webhook events for payment processing.
    """
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe-Signature header"
        )
    
    payload = await request.body()
    
    try:
        # Verify the webhook signature
        event = stripe.Webhook.construct_event(
            payload, 
            stripe_signature, 
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    # Handle the event
    event_type = event['type']
    event_data = event['data']['object']
    
    logger.info(f"Received Stripe event: {event_type}")
    
    try:
        if event_type == 'checkout.session.completed':
            await handle_checkout_session_completed(event_data, db)
        elif event_type == 'payment_intent.succeeded':
            await handle_payment_intent_succeeded(event_data, db)
        elif event_type == 'payment_intent.payment_failed':
            await handle_payment_intent_failed(event_data, db)
        elif event_type == 'charge.refunded':
            await handle_charge_refunded(event_data, db)
            
        return JSONResponse(status_code=200, content={"status": "success"})
    except Exception as e:
        logger.error(f"Error processing webhook {event_type}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )

async def handle_checkout_session_completed(session, db: Session):
    """Handle successful checkout session completion."""
    # Get the user ID from the client reference ID
    user_id = session.get('client_reference_id')
    if not user_id:
        logger.warning("No client_reference_id in session")
        return
    
    # Get the subscription plan ID from the metadata
    metadata = session.get('metadata', {})
    subscription_plan_id = metadata.get('subscription_plan_id')
    subscription_duration_days = int(metadata.get('subscription_duration_days', 30))
    
    # Get the payment intent ID
    payment_intent_id = session.get('payment_intent')
    
    # Get the customer email
    customer_email = session.get('customer_email', '')
    
    # Get the user from the database
    user = crud.user.get(db, id=user_id)
    if not user:
        logger.warning(f"User not found: {user_id}")
        return
    
    # Create a payment notification
    payment_notification = PaymentNotificationCreate(
        user_id=user_id,
        amount=session.get('amount_total', 0) / 100,  # Convert from cents
        currency=session.get('currency', 'usd').upper(),
        payment_method=session.get('payment_method_types', ['card'])[0],
        status=PaymentStatus.PENDING,
        subscription_plan_id=subscription_plan_id,
        subscription_duration_days=subscription_duration_days,
        user_full_name=user.full_name or "",
        user_email=customer_email or user.email,
        payment_id=payment_intent_id or session.id,
        payment_provider='stripe',
        metadata={
            'session_id': session.id,
            'customer_id': session.get('customer'),
            'payment_status': session.get('payment_status'),
            'subscription': session.get('subscription')
        }
    )
    
    # Save the notification
    crud.notification.create_payment_notification(
        db=db,
        obj_in=payment_notification,
        user_id=user_id
    )

async def handle_payment_intent_succeeded(payment_intent, db: Session):
    """Handle successful payment intent."""
    payment_id = payment_intent.get('id')
    amount = payment_intent.get('amount', 0) / 100  # Convert from cents
    currency = payment_intent.get('currency', 'usd').upper()
    
    # Update the payment notification status
    notification = crud.notification.update_payment_status(
        db=db,
        payment_id=payment_id,
        status=PaymentStatus.COMPLETED.value,
        receipt_url=payment_intent.get('charges', {}).get('data', [{}])[0].get('receipt_url')
    )
    
    if notification and notification.user_id:
        # Get the subscription details from the notification data
        subscription_plan_id = notification.data.get('subscription_plan_id')
        subscription_duration_days = notification.data.get('subscription_duration_days', 30)
        
        if subscription_plan_id:
            # Update the user's subscription
            await update_user_subscription(
                db=db,
                user_id=notification.user_id,
                subscription_plan_id=subscription_plan_id,
                duration_days=subscription_duration_days
            )

async def handle_payment_intent_failed(payment_intent, db: Session):
    """Handle failed payment intent."""
    payment_id = payment_intent.get('id')
    
    # Update the payment notification status
    crud.notification.update_payment_status(
        db=db,
        payment_id=payment_id,
        status=PaymentStatus.FAILED.value,
    )

async def handle_charge_refunded(charge, db: Session):
    """Handle charge refunded event."""
    payment_intent = charge.get('payment_intent')
    
    # Update the payment notification status
    crud.notification.update_payment_status(
        db=db,
        payment_id=payment_intent,
        status=PaymentStatus.REFUNDED.value,
    )

async def update_user_subscription(
    db: Session,
    user_id: int,
    subscription_plan_id: int,
    duration_days: int = 30
):
    """Update user's subscription in the database."""
    from datetime import datetime, timedelta
    
    # Get the subscription plan
    subscription_plan = crud.subscription_plan.get(db, id=subscription_plan_id)
    if not subscription_plan:
        logger.warning(f"Subscription plan not found: {subscription_plan_id}")
        return
    
    # Calculate subscription end date
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=duration_days)
    
    # Check if user already has an active subscription
    existing_subscription = crud.subscription.get_active_subscription(db, user_id=user_id)
    
    if existing_subscription:
        # Extend the existing subscription
        existing_subscription.plan_id = subscription_plan_id
        existing_subscription.end_date = max(
            existing_subscription.end_date,
            end_date
        )
    else:
        # Create a new subscription
        subscription_data = {
            "user_id": user_id,
            "plan_id": subscription_plan_id,
            "start_date": start_date,
            "end_date": end_date,
            "is_active": True
        }
        crud.subscription.create(db, obj_in=subscription_data)
    
    # Update user's role to premium
    user = crud.user.get(db, id=user_id)
    if user:
        user.role = "premium"
        db.add(user)
        db.commit()
        db.refresh(user)
    
    logger.info(f"Updated subscription for user {user_id} to plan {subscription_plan_id} until {end_date}")

@router.post("/create-checkout-session", response_model=dict)
async def create_checkout_session(
    subscription_plan_id: int,
    success_url: str,
    cancel_url: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Create a Stripe Checkout Session for subscription.
    """
    # Get the subscription plan
    subscription_plan = crud.subscription_plan.get(db, id=subscription_plan_id)
    if not subscription_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    # Define subscription duration (in days)
    duration_days = 30  # Default to 1 month
    
    # Create a checkout session
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',  # Adjust based on your needs
                    'product_data': {
                        'name': subscription_plan.name,
                        'description': subscription_plan.description,
                    },
                    'unit_amount': int(subscription_plan.price * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=str(current_user.id),
            metadata={
                'subscription_plan_id': str(subscription_plan_id),
                'subscription_duration_days': str(duration_days)
            }
        )
        
        return {"sessionId": session.id, "url": session.url}
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating checkout session"
        )

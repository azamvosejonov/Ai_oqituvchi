import stripe
from typing import Dict, Any

from app.core.config import settings
from app import models, schemas

# Stripe API kalitini sozlash
stripe.api_key = settings.STRIPE_API_KEY

def create_stripe_checkout_session(plan: models.SubscriptionPlan, user: models.User) -> Dict[str, Any]:
    """
    Foydalanuvchi uchun Stripe to'lov sessiyasini yaratadi.
    """
    try:
        if not settings.STRIPE_API_KEY:
            return {"error": "Stripe is not configured: missing STRIPE_API_KEY"}
        if not plan.stripe_price_id:
            return {"error": "Plan is missing stripe_price_id"}

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': plan.stripe_price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=f"{settings.DOMAIN}/profile?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.DOMAIN}/pricing",
            customer_email=user.email,
            metadata={
                'user_id': user.id,
                'plan_id': plan.id
            }
        )
        return {"id": checkout_session.id, "url": checkout_session.url}
    except Exception as e:
        # Xatolikni loglash yoki qayta ishlash
        print(f"Stripe checkout session yaratishda xatolik: {e}")
        return {"error": str(e)}

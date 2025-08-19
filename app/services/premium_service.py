import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate

logger = logging.getLogger(__name__)

class PremiumService:
    """Service for handling premium user functionality."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def grant_premium_access(
        self,
        user_id: int,
        days: int,
        plan_name: str = "Premium",
        payment_verification_id: Optional[int] = None
    ) -> models.Subscription:
        """
        Grant premium access to a user for the specified number of days.
        
        Args:
            user_id: ID of the user to grant premium access to
            days: Number of days to grant premium access for
            plan_name: Name of the premium plan (default: "Premium")
            payment_verification_id: Optional ID of the payment verification record
            
        Returns:
            The created or updated subscription
        """
        # Check if user already has an active subscription
        current_subscription = crud.subscription.get_active_subscription(
            self.db, user_id=user_id
        )
        
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days)
        
        if current_subscription:
            # Extend existing subscription
            if current_subscription.end_date > start_date:
                # If subscription is still active, extend from the end date
                new_end_date = current_subscription.end_date + timedelta(days=days)
            else:
                # If subscription has expired, start from now
                new_end_date = end_date
                
            subscription_in = SubscriptionUpdate(
                end_date=new_end_date,
                status=SubscriptionStatus.ACTIVE,
                payment_verification_id=payment_verification_id
            )
            
            subscription = crud.subscription.update(
                self.db, db_obj=current_subscription, obj_in=subscription_in
            )
        else:
            # Create new subscription
            subscription_in = SubscriptionCreate(
                user_id=user_id,
                plan_name=plan_name,
                start_date=start_date,
                end_date=end_date,
                status=SubscriptionStatus.ACTIVE,
                payment_verification_id=payment_verification_id
            )
            
            subscription = crud.subscription.create(
                self.db, obj_in=subscription_in
            )
        
        # Update user's premium status
        user = crud.user.get(self.db, id=user_id)
        if user:
            user.is_premium = True
            user.premium_until = subscription.end_date
            self.db.add(user)
            self.db.commit()
        
        logger.info(f"Granted {days} days of premium access to user {user_id}")
        return subscription
    
    def revoke_premium_access(
        self,
        user_id: int,
        reason: str = "Payment verification rejected"
    ) -> Optional[models.Subscription]:
        """
        Revoke premium access from a user.
        
        Args:
            user_id: ID of the user to revoke premium access from
            reason: Reason for revoking premium access
            
        Returns:
            The updated subscription if one was found, None otherwise
        """
        # Get active subscription if it exists
        subscription = crud.subscription.get_active_subscription(
            self.db, user_id=user_id
        )
        
        if subscription:
            # Update subscription status
            subscription_in = SubscriptionUpdate(
                status=SubscriptionStatus.CANCELLED,
                cancellation_reason=reason,
                cancelled_at=datetime.utcnow()
            )
            
            subscription = crud.subscription.update(
                self.db, db_obj=subscription, obj_in=subscription_in
            )
            
            # Check if user has any other active subscriptions
            has_other_active = crud.subscription.has_active_subscription(
                self.db, user_id=user_id, exclude_id=subscription.id
            )
            
            # Update user's premium status
            user = crud.user.get(self.db, id=user_id)
            if user:
                if has_other_active:
                    # User has another active subscription, keep premium status
                    user.premium_until = subscription.end_date
                else:
                    # No other active subscriptions, revoke premium status
                    user.is_premium = False
                    user.premium_until = None
                
                self.db.add(user)
                self.db.commit()
            
            logger.info(f"Revoked premium access from user {user_id}. Reason: {reason}")
            return subscription
        
        return None
    
    def check_premium_access(self, user_id: int) -> bool:
        """
        Check if a user currently has premium access.
        
        Args:
            user_id: ID of the user to check
            
        Returns:
            bool: True if the user has active premium access, False otherwise
        """
        # Check user's premium status first (quick check)
        user = crud.user.get(self.db, id=user_id)
        if not user:
            return False
            
        if not user.is_premium or not user.premium_until:
            return False
            
        if user.premium_until < datetime.utcnow():
            # Premium has expired, update user status
            user.is_premium = False
            self.db.add(user)
            self.db.commit()
            return False
            
        return True

# Create a singleton instance
premium_service = PremiumService(None)

def get_premium_service(db: Session) -> PremiumService:
    """Get a premium service instance with the current database session."""
    premium_service.db = db
    return premium_service

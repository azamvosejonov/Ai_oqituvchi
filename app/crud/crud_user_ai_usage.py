import logging
from sqlalchemy.orm import Session

from app import models
from app.crud import crud_subscription
from app.models import UserAIUsage
from app.schemas import UserRole
from app.schemas.user_ai_usage import UserAIUsageUpdate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDUserAIUsage:
    def get_or_create(self, db: Session, *, user_id: int) -> UserAIUsage:
        """
        Retrieves the AI usage record for a user, creating one if it doesn't exist.
        """
        db_obj = db.query(UserAIUsage).filter(UserAIUsage.user_id == user_id).first()
        if not db_obj:
            # Create a record and then auto-initialize quotas based on role/subscription
            db_obj = UserAIUsage(user_id=user_id)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            # Attempt to populate initial quotas so users don't start with zeros
            try:
                db_obj = self.reset(db, user_id=user_id)
            except Exception:
                # If reset fails (e.g., subscription lookup), keep the zeroed record
                pass
        return db_obj

    def update(self, db: Session, *, db_obj: UserAIUsage, obj_in: UserAIUsageUpdate) -> UserAIUsage:
        """
        Updates a user's AI usage record from a schema object.
        """
        try:
            update_data = obj_in.model_dump(exclude_unset=True)
        except AttributeError:
            update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def increment(self, db: Session, *, user_id: int, field: str, amount: int = 1) -> UserAIUsage:
        db_obj = self.get_or_create(db=db, user_id=user_id)
        current_value = getattr(db_obj, field, 0)
        if current_value is None:  # Handle case where the DB value is NULL
            current_value = 0
        setattr(db_obj, field, current_value + amount)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def decrement(self, db: Session, *, user_id: int, field: str, amount: int = 1) -> UserAIUsage:
        db_obj = self.get_or_create(db=db, user_id=user_id)
        current_value = getattr(db_obj, field, 0)
        if current_value >= amount:
            setattr(db_obj, field, current_value - amount)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def reset(self, db: Session, *, user_id: int) -> UserAIUsage:
        logger.info(f"Starting AI usage reset for user_id: {user_id}")
        try:
            db_obj = self.get_or_create(db=db, user_id=user_id)
            from app.core.config import settings
            from app.models.user import User
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User with id {user_id} not found during reset.")
                # Return the object without changes if user not found
                return db_obj

            is_premium = UserRole.premium.value in {role.name for role in user.roles}
            logger.info(f"User {user_id} is_premium status: {is_premium}")

            if is_premium:
                logger.info(f"Attempting to get active subscription for premium user {user_id}")
                active_subscription = crud_subscription.get_user_active_subscription(db, user_id=user_id)
                
                if active_subscription and hasattr(active_subscription, 'plan') and active_subscription.plan:
                    logger.info(f"Active subscription with plan found for user {user_id}. Applying plan quotas.")
                    db_obj.gpt4o_requests_left = active_subscription.plan.gpt4o_requests_quota
                    db_obj.tts_chars_left = active_subscription.plan.tts_chars_quota
                    db_obj.stt_requests_left = active_subscription.plan.stt_requests_quota
                    db_obj.pronunciation_analysis_left = active_subscription.plan.pronunciation_analysis_quota
                else:
                    logger.info(f"No active subscription plan found for premium user {user_id}. Applying fallback quotas.")
                    db_obj.gpt4o_requests_left = 500
                    db_obj.tts_chars_left = 100000
                    db_obj.stt_requests_left = 2000
                    db_obj.pronunciation_analysis_left = 400
            else:
                logger.info(f"User {user_id} is a free user. Applying free quotas.")
                db_obj.gpt4o_requests_left = 50
                db_obj.tts_chars_left = 5000
                db_obj.stt_requests_left = 100
                db_obj.pronunciation_analysis_left = 20
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Successfully reset AI usage for user_id: {user_id}")
            return db_obj
        except Exception as e:
            logger.error(f"Error during AI usage reset for user_id {user_id}: {e}", exc_info=True)
            db.rollback()
            raise
        
    def has_enough_quota(self, db: Session, user_id: int, field: str, amount: int = 1) -> bool:
        """
        Check if user has enough quota for a specific action.
        Returns True if they have enough, False otherwise.
        Superadmins always have enough quota.
        """
        from app.crud import crud_user  # Local import to avoid circular dependency

        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user and crud_user.user.is_superuser(user):
            return True

        db_obj = self.get_or_create(db=db, user_id=user_id)
        current_value = getattr(db_obj, field, 0)
        if current_value is None:  # Handle case where the DB value is NULL
            current_value = 0
        return current_value >= amount


user_ai_usage = CRUDUserAIUsage()
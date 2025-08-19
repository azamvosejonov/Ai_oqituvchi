from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.payment_verification import PaymentVerification
from app.schemas.payment_verification import PaymentVerificationCreate, PaymentVerificationUpdate, \
    PaymentVerificationStatus
from app.crud.base import CRUDBase
from app.models.subscription import SubscriptionPlan
from app import crud

class CRUDPaymentVerification(CRUDBase[PaymentVerification, PaymentVerificationCreate, PaymentVerificationUpdate]):
    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[PaymentVerification]:
        return (
            db.query(self.model)
            .filter(PaymentVerification.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_pending_verifications(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[PaymentVerification]:
        return (
            db.query(self.model)
            .filter(PaymentVerification.status == PaymentVerificationStatus.PENDING)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def approve_verification(
        self,
        db: Session,
        *,
        db_obj: PaymentVerification,
        plan_id: Optional[int] = None,
        admin_notes: Optional[str] = None,
        premium_days: Optional[int] = None,
    ) -> PaymentVerification:
        from datetime import datetime, timedelta

        # Helper: find or create a manual plan if plan_id is not provided
        def _get_or_create_manual_plan(days: int) -> SubscriptionPlan:
            name = f"Manual Premium {days}d"
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == name).first()
            if plan:
                return plan
            # Create a minimal plan with sensible default quotas
            plan = SubscriptionPlan(
                name=name,
                description=f"Manual premium granted by admin for {days} days",
                price=0.0,
                duration_days=days,
                is_active=True,
                gpt4o_requests_quota=500,
                stt_requests_quota=200,
                tts_chars_quota=100000,
                pronunciation_analysis_quota=200,
            )
            db.add(plan)
            db.commit()
            db.refresh(plan)
            return plan

        # Resolve plan
        plan: Optional[SubscriptionPlan] = None
        if plan_id:
            plan = db.query(SubscriptionPlan).get(plan_id)
            if not plan:
                raise ValueError(f"Subscription plan with id {plan_id} not found.")
        elif premium_days and premium_days > 0:
            plan = _get_or_create_manual_plan(premium_days)
        else:
            raise ValueError("Either plan_id or premium_days must be provided for approval.")

        # Mark verification as approved
        db_obj.status = PaymentVerificationStatus.APPROVED
        db_obj.admin_notes = admin_notes
        db_obj.processed_at = datetime.utcnow()
        db_obj.is_processed = True
        db.add(db_obj)

        # Deactivate existing active subscriptions for the user
        try:
            from app.models.subscription import Subscription
            active_subs = (
                db.query(Subscription)
                .filter(Subscription.user_id == db_obj.user_id, Subscription.is_active == True)
                .all()
            )
            for s in active_subs:
                s.is_active = False
                db.add(s)

            # Create new subscription with end_date determined by premium_days or plan.duration_days
            start_date = datetime.utcnow()
            days = premium_days if premium_days and premium_days > 0 else plan.duration_days
            end_date = start_date + timedelta(days=days)

            new_sub = Subscription(
                user_id=db_obj.user_id,
                plan_id=plan.id,
                start_date=start_date,
                end_date=end_date,
                is_active=True,
            )
            db.add(new_sub)
            db.commit()
            db.refresh(new_sub)

            # Reset AI quotas according to active subscription plan
            try:
                from app.crud.crud_user_ai_usage import user_ai_usage
                user_ai_usage.reset(db, user_id=db_obj.user_id)
            except Exception:
                # Non-fatal; continue
                pass

        except Exception:
            db.rollback()
            raise

        # Ensure 'premium' role is assigned to the user
        try:
            user = crud.user.get(db, id=db_obj.user_id)
            premium_role = crud.role.get_by_name(db, name="premium")
            if user and premium_role and premium_role not in getattr(user, 'roles', []):
                user.roles.append(premium_role)
                db.add(user)
        except Exception:
            # Don't fail the whole operation due to role assignment
            pass

        # Commit all changes
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def reject_verification(
        self, db: Session, *, db_obj: PaymentVerification, admin_notes: str
    ) -> PaymentVerification:
        from datetime import datetime
        
        db_obj.status = PaymentVerificationStatus.REJECTED
        db_obj.admin_notes = admin_notes
        db_obj.processed_at = datetime.utcnow()
        db_obj.is_processed = True
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

payment_verification = CRUDPaymentVerification(PaymentVerification)

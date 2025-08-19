from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc

from app.crud.base import CRUDBase
from app.models.notification import Notification, NotificationType, PaymentStatus
from app.schemas.notification import (
    NotificationCreate, 
    NotificationUpdate,
    PaymentNotificationCreate,
)


class CRUDNotification(CRUDBase[Notification, NotificationCreate, NotificationUpdate]):
    def create_for_user(
        self, 
        db: Session, 
        *, 
        obj_in: Union[NotificationCreate, Dict[str, Any]],
        user_id: int
    ) -> Notification:
        """Create a new notification for a user."""
        if isinstance(obj_in, dict):
            create_data = dict(obj_in)
        else:
            create_data = obj_in.model_dump(exclude_unset=True)

        # Avoid passing user_id twice if present in payload
        # Prefer the explicit function parameter
        create_data.pop("user_id", None)

        db_obj = self.model(**create_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def create_payment_notification(
        self,
        db: Session,
        *,
        obj_in: PaymentNotificationCreate,
        user_id: int
    ) -> Notification:
        """Create a payment notification with payment details."""
        notification_data = {
            "title": f"Payment {obj_in.status.value.upper()}: {obj_in.amount} {obj_in.currency}",
            "message": (
                f"Your payment of {obj_in.amount} {obj_in.currency} "
                f"via {obj_in.payment_method} is {obj_in.status.value}."
            ),
            "notification_type": NotificationType.PAYMENT,
            "payment_status": obj_in.status.value,
            "payment_id": obj_in.payment_id,
            "payment_provider": obj_in.payment_provider,
            "amount": int(obj_in.amount * 100),  # Store in cents
            "currency": obj_in.currency,
            "receipt_url": str(obj_in.receipt_url) if obj_in.receipt_url else None,
            "data": {
                "subscription_plan_id": obj_in.subscription_plan_id,
                "subscription_duration_days": obj_in.subscription_duration_days,
                "user_full_name": obj_in.user_full_name,
                "user_email": obj_in.user_email,
                "user_phone": obj_in.user_phone,
                "metadata": obj_in.metadata or {}
            },
            "user_id": user_id
        }
        return self.create_for_user(db, obj_in=notification_data, user_id=user_id)

    def create_forum_reply_notification(
        self, 
        db: Session, 
        *, 
        recipient_user_id: int,
        topic_id: int,
        topic_title: str,
        reply_author_name: str
    ) -> Notification:
        """Create a notification for a new forum reply."""
        notification_data = {
            "title": f"New reply in: {topic_title}",
            "message": f"'{reply_author_name}' has replied to your topic.",
            "notification_type": NotificationType.FORUM_NEW_REPLY,
            "data": {
                "topic_id": topic_id,
                "topic_title": topic_title,
                "reply_author_name": reply_author_name
            }
        }
        return self.create_for_user(db, obj_in=notification_data, user_id=recipient_user_id)

    def create_certificate_issued_notification(
        self, 
        db: Session, 
        *, 
        user_id: int,
        course_name: str,
        certificate_id: int
    ) -> Notification:
        """Create a notification for an issued certificate."""
        notification_data = {
            "title": "Certificate Issued!",
            "message": f"Congratulations! You have been issued a certificate for completing the course: {course_name}.",
            "notification_type": NotificationType.CERTIFICATE_ISSUED,
            "data": {
                "course_name": course_name,
                "certificate_id": certificate_id
            }
        }
        return self.create_for_user(db, obj_in=notification_data, user_id=user_id)

    def get_multi_by_user(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        is_read: Optional[bool] = None,
        notification_type: Optional[NotificationType] = None,
        payment_status: Optional[str] = None,
    ) -> List[Notification]:
        """Get notifications for a user with optional filters."""
        query = db.query(self.model).filter(Notification.user_id == user_id)
        
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
            
        if notification_type:
            query = query.filter(Notification.notification_type == notification_type.value)
            
        if payment_status:
            query = query.filter(Notification.payment_status == payment_status)
        
        return (
            query
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_payment_notifications(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        payment_status: Optional[str] = None,
        user_id: Optional[int] = None,
        days: Optional[int] = None,
    ) -> List[Notification]:
        """Get payment notifications with optional filters."""
        query = db.query(self.model).filter(
            Notification.notification_type == NotificationType.PAYMENT.value
        )
        
        if payment_status:
            query = query.filter(Notification.payment_status == payment_status)
            
        if user_id:
            query = query.filter(Notification.user_id == user_id)
            
        if days:
            date_threshold = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Notification.created_at >= date_threshold)
            
        return (
            query
            .options(joinedload(Notification.user))
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_unread_count(self, db: Session, *, user_id: int) -> int:
        """Get the count of unread notifications for a user."""
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.is_read == False).count()

    def mark_all_as_read(self, db: Session, *, user_id: int) -> int:
        """Mark all unread notifications for a user as read."""
        updated_count = db.query(self.model).filter(
            self.model.user_id == user_id, 
            self.model.is_read == False
        ).update({self.model.is_read: True}, synchronize_session=False)
        db.commit()
        return updated_count
    
    def mark_as_read(
        self, 
        db: Session, 
        *, 
        notification_id: Optional[int] = None,
        user_id: Optional[int] = None,
        mark_all: bool = False
    ) -> Union[Notification, int]:
        """
        Mark notification(s) as read.
        
        Args:
            notification_id: Mark a specific notification as read
            user_id: If provided with mark_all=True, mark all user's notifications as read
            mark_all: If True, mark all user's notifications as read
            
        Returns:
            The updated notification if notification_id is provided, 
            or count of updated notifications if mark_all is True
        """
        if notification_id:
            db_notification = db.query(self.model).filter(Notification.id == notification_id).first()
            if db_notification:
                db_notification.is_read = True
                db.commit()
                db.refresh(db_notification)
            return db_notification
            
        elif user_id and mark_all:
            result = db.query(self.model).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            ).update({"is_read": True}, synchronize_session=False)
            db.commit()
            return result
            
        return None
    
    def update_payment_status(
        self,
        db: Session,
        *,
        payment_id: str,
        status: str,
        receipt_url: Optional[str] = None
    ) -> Optional[Notification]:
        """Update payment status and related fields for a payment notification."""
        db_notification = (
            db.query(self.model)
            .filter(
                Notification.payment_id == payment_id,
                Notification.notification_type == NotificationType.PAYMENT.value
            )
            .first()
        )
        
        if db_notification:
            update_data = {"payment_status": status}
            if receipt_url:
                update_data["receipt_url"] = receipt_url
                
            # Update notification data with new status
            if db_notification.data:
                db_notification.data["status_updated_at"] = datetime.utcnow().isoformat()
                
            db_notification.is_read = (status == PaymentStatus.COMPLETED.value)
            
            for field, value in update_data.items():
                setattr(db_notification, field, value)
                
            db.commit()
            db.refresh(db_notification)
            
        return db_notification


notification = CRUDNotification(Notification)

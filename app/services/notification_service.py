import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.models.notification import NotificationType
from app.schemas.notification import NotificationCreate, PaymentStatus

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling application notifications."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: NotificationType,
        status: PaymentStatus = PaymentStatus.PENDING,
        data: Optional[Dict[str, Any]] = None,
        related_id: Optional[int] = None
    ) -> models.Notification:
        """
        Create a new notification for a user.
        
        Args:
            user_id: ID of the user to notify
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            status: Notification status (default: UNREAD)
            data: Additional data to store with the notification
            related_id: ID of related entity (e.g., payment_verification_id)
            
        Returns:
            The created notification
        """
        notification_in = NotificationCreate(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            status=status,
            data=data or {},
            related_id=related_id
        )
        
        return crud.notification.create(db=self.db, obj_in=notification_in)
    
    def notify_payment_verification_submitted(
        self,
        user: models.User,
        payment_verification: models.PaymentVerification
    ) -> models.Notification:
        """
        Create a notification for a submitted payment verification.
        
        Args:
            user: The user who submitted the payment verification
            payment_verification: The payment verification that was submitted
            
        Returns:
            The created notification
        """
        title = "Payment Verification Submitted"
        message = (
            f"Your payment verification for ${payment_verification.amount:.2f} "
            f"has been submitted and is pending review."
        )
        
        return self.create_notification(
            user_id=user.id,
            title=title,
            message=message,
            notification_type=NotificationType.PAYMENT_VERIFICATION_SUBMITTED,
            related_id=payment_verification.id,
            data={
                "amount": float(payment_verification.amount),
                "payment_method": payment_verification.payment_method,
                "status": payment_verification.status
            }
        )
    
    def notify_payment_verification_approved(
        self,
        user: models.User,
        payment_verification: models.PaymentVerification
    ) -> models.Notification:
        """
        Create a notification for an approved payment verification.
        
        Args:
            user: The user whose payment was approved
            payment_verification: The payment verification that was approved
            
        Returns:
            The created notification
        """
        title = "Payment Approved"
        message = (
            f"Your payment of ${payment_verification.amount:.2f} has been approved. "
            f"Your premium access has been activated for {payment_verification.premium_days} days."
        )
        
        return self.create_notification(
            user_id=user.id,
            title=title,
            message=message,
            notification_type=NotificationType.PAYMENT_VERIFICATION_APPROVED,
            related_id=payment_verification.id,
            data={
                "amount": float(payment_verification.amount),
                "premium_days": payment_verification.premium_days,
                "approved_by": payment_verification.approved_by
            }
        )
    
    def notify_payment_verification_rejected(
        self,
        user: models.User,
        payment_verification: models.PaymentVerification
    ) -> models.Notification:
        """
        Create a notification for a rejected payment verification.
        
        Args:
            user: The user whose payment was rejected
            payment_verification: The payment verification that was rejected
            
        Returns:
            The created notification
        """
        title = "Payment Verification Rejected"
        message = (
            f"Your payment verification for ${payment_verification.amount:.2f} "
            f"has been rejected. Reason: {payment_verification.rejection_reason}"
        )
        
        return self.create_notification(
            user_id=user.id,
            title=title,
            message=message,
            notification_type=NotificationType.PAYMENT_VERIFICATION_REJECTED,
            related_id=payment_verification.id,
            data={
                "amount": float(payment_verification.amount),
                "rejection_reason": payment_verification.rejection_reason,
                "rejection_notes": payment_verification.rejection_notes,
                "rejected_by": payment_verification.rejected_by
            }
        )
    
    def notify_admin_payment_verification_submitted(
        self,
        payment_verification: models.PaymentVerification,
        admin_emails: List[str]
    ) -> List[models.Notification]:
        """
        Create notifications for admins about a new payment verification.
        
        Args:
            payment_verification: The payment verification that was submitted
            admin_emails: List of admin email addresses to notify
            
        Returns:
            List of created notifications
        """
        if not admin_emails:
            return []
            
        # Get admin users by email
        admins = crud.user.get_multi_by_emails(
            db=self.db, emails=admin_emails, is_superuser=True
        )
        
        notifications = []
        title = "New Payment Verification Submitted"
        message = (
            f"User {payment_verification.user.email} has submitted a payment verification "
            f"for ${payment_verification.amount:.2f} via {payment_verification.payment_method}."
        )
        
        for admin in admins:
            notification = self.create_notification(
                user_id=admin.id,
                title=title,
                message=message,
                notification_type=NotificationType.ADMIN_PAYMENT_VERIFICATION_SUBMITTED,
                related_id=payment_verification.id,
                data={
                    "user_id": payment_verification.user_id,
                    "user_email": payment_verification.user.email,
                    "amount": float(payment_verification.amount),
                    "payment_method": payment_verification.payment_method
                }
            )
            notifications.append(notification)
        
        return notifications

# Create a singleton instance
notification_service = NotificationService(None)

def get_notification_service(db: Session) -> NotificationService:
    """Get a notification service instance with the current database session."""
    notification_service.db = db
    return notification_service

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.crud import crud_notification
from app.models.notification import NotificationType, PaymentStatus
from app.schemas.notification import PaymentNotificationCreate

router = APIRouter()

@router.get("/", response_model=List[schemas.Notification])
async def get_notifications(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    is_read: Optional[bool] = None,
    notification_type: Optional[NotificationType] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get notifications for the current user with optional filters.
    """
    notifications = crud_notification.notification.get_multi_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        is_read=is_read,
        notification_type=notification_type
    )
    return notifications

@router.get("/unread-count", response_model=int)
async def get_unread_notifications_count(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get count of unread notifications for the current user.
    """
    notifications = crud_notification.notification.get_multi_by_user(
        db=db,
        user_id=current_user.id,
        is_read=False,
    )
    return len(notifications)

@router.post("/mark-read/{notification_id}", response_model=schemas.Notification)
async def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Mark a specific notification as read.
    """
    notification = crud_notification.notification.mark_as_read(
        db=db, 
        notification_id=notification_id,
    )
    
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or access denied",
        )
        
    return notification

@router.post("/mark-all-read", response_model=int)
async def mark_all_notifications_as_read(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Mark all notifications as read for the current user.
    Returns the count of updated notifications.
    """
    updated_count = crud_notification.notification.mark_as_read(
        db=db, 
        user_id=current_user.id,
        mark_all=True
    )
    return updated_count or 0

# Admin only endpoints
@router.get("/admin/payments", response_model=List[schemas.Notification])
async def get_payment_notifications(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    payment_status: Optional[str] = None,
    user_id: Optional[int] = None,
    days: Optional[int] = Query(None, description="Filter by last N days"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Get payment notifications (Admin only).
    """
    notifications = crud_notification.notification.get_payment_notifications(
        db=db,
        skip=skip,
        limit=limit,
        payment_status=payment_status,
        user_id=user_id,
        days=days
    )
    return notifications

@router.post("/admin/update-payment-status", response_model=schemas.Notification)
async def update_payment_status(
    payment_id: str,
    status: str,
    receipt_url: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Update payment status (Admin only).
    """
    if status not in [s.value for s in PaymentStatus]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join([s.value for s in PaymentStatus])}",
        )
        
    notification = crud_notification.notification.update_payment_status(
        db=db,
        payment_id=payment_id,
        status=status,
        receipt_url=receipt_url
    )
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found",
        )
        
    return notification

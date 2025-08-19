from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Notification])
def read_notifications(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    is_read: Optional[bool] = None,
) -> Any:
    """Retrieve notifications for the current user."""
    notifications = crud.notification.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit, is_read=is_read
    )
    return notifications


@router.get("/unread-count", response_model=schemas.UnreadCount)
def get_unread_notification_count(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Get the count of unread notifications for the current user."""
    count = crud.notification.get_unread_count(db, user_id=current_user.id)
    return {"unread_count": count}


@router.post("/{notification_id}/read", response_model=schemas.Notification)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Mark a specific notification as read."""
    notification = crud.notification.get(db, id=notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    updated_notification = crud.notification.mark_as_read(db, notification_id=notification_id)
    return updated_notification


@router.post("/read-all", response_model=schemas.Message)
def mark_all_notifications_as_read(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Mark all of the user's notifications as read."""
    updated_count = crud.notification.mark_all_as_read(db, user_id=current_user.id)
    return {"msg": f"{updated_count} notifications marked as read."}


@router.post("/admin/send", response_model=schemas.Notification)
def admin_send_notification(
    *,
    db: Session = Depends(deps.get_db),
    payload: schemas.NotificationCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Admin: send a notification to a specific user."""
    # Ensure target user exists
    user = crud.user.get(db, id=payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Target user not found")
    created = crud.notification.create_for_user(db, obj_in=payload, user_id=payload.user_id)
    return created

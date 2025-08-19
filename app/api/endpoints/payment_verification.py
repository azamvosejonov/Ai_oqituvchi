import os
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
import uuid

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.models.notification import NotificationType
from app.schemas.payment_verification import (
    PaymentVerificationCreate,
    PaymentVerificationUpdate,
    PaymentVerificationApprove,
    PaymentVerificationReject,
    PaymentVerificationInDB, PaymentVerificationStatus
)
from app.services.notification_service import get_notification_service
from app.services.premium_service import get_premium_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads/payment_proofs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_upload_file(file: UploadFile) -> str:
    """Save uploaded file and return the file path."""
    try:
        # Generate a unique filename
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else ''
        filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
            
        return file_path
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file"
        )

@router.post("/submit-proof", response_model=PaymentVerificationInDB)
async def submit_payment_proof(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    file: UploadFile = File(...),
    amount: float = Form(...),
    payment_method: str = Form(...),
    transaction_id: str = Form(None),
    notes: str = Form(None),
):
    """
    Submit payment proof for verification.
    
    This endpoint allows users to upload payment proof (screenshot/receipt) for premium subscription.
    """
    try:
        # Save the uploaded file
        file_path = save_upload_file(file)
        
        # Create payment verification record
        payment_data = PaymentVerificationCreate(
            user_id=current_user.id,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            proof_image_path=file_path,
            status=PaymentVerificationStatus.PENDING,
            notes=notes
        )
        
        # Create the payment verification record
        payment_verification = crud.payment_verification.create(db, obj_in=payment_data)
        
        # Send notification to user
        notification_service = get_notification_service(db)
        notification_service.notify_payment_verification_submitted(
            user=current_user,
            payment_verification=payment_verification
        )
        
        # Send notification to admins
        admin_emails = ["admin@example.com"]  # TODO: Get admin emails from config or database
        notification_service.notify_admin_payment_verification_submitted(
            payment_verification=payment_verification,
            admin_emails=admin_emails
        )
        
        return payment_verification
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting payment proof: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit payment proof"
        )

@router.get("/my-verifications", response_model=PaymentVerificationInDB)
def get_my_verifications(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get current user's payment verification history.
    """
    return crud.payment_verification.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )

@router.get("/admin/pending", response_model=PaymentVerificationInDB)
def get_pending_verifications(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all pending payment verifications (Admin only).
    """
    return crud.payment_verification.get_multi_by_status(
        db, status=PaymentVerificationStatus.PENDING, skip=skip, limit=limit
    )

@router.post("/admin/approve/{verification_id}", response_model=schemas.PaymentVerificationInDB)
def approve_payment_verification(
    verification_id: int,
    approval_data: schemas.PaymentVerificationApprove,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Approve a payment verification and grant premium access (Admin only).
    """
    # Get the payment verification
    verification = crud.payment_verification.get(db, id=verification_id)
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment verification not found"
        )
        
    if verification.status != PaymentVerificationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment verification is not in pending status"
        )
    
    # Approve the payment verification
    verification_update = {
        "status": PaymentVerificationStatus.APPROVED,
        "approved_by": current_user.id,
        "approval_notes": approval_data.notes,
        "premium_days": approval_data.premium_days
    }
    
    # Update the verification status
    verification = crud.payment_verification.update(
        db, db_obj=verification, obj_in=verification_update
    )
    
    # Grant premium access to the user
    if approval_data.premium_days > 0:
        premium_service = get_premium_service(db)
        premium_service.grant_premium_access(
            user_id=verification.user_id,
            days=approval_data.premium_days,
            plan_name=f"Premium ({approval_data.premium_days} days)",
            payment_verification_id=verification.id
        )
    
    # Send notification to user
    notification_service = get_notification_service(db)
    notification_service.notify_payment_verification_approved(
        user=verification.user,
        payment_verification=verification
    )
    
    return verification

@router.post("/admin/reject/{verification_id}", response_model=schemas.PaymentVerificationInDB)
def reject_payment_verification(
    verification_id: int,
    rejection_data: schemas.PaymentVerificationReject,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Reject a payment verification (Admin only).
    """
    # Get the payment verification
    verification = crud.payment_verification.get(db, id=verification_id)
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment verification not found"
        )
        
    if verification.status != PaymentVerificationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment verification is not in pending status"
        )
    
    # Reject the payment verification
    verification_update = {
        "status": PaymentVerificationStatus.REJECTED,
        "rejected_by": current_user.id,
        "rejection_reason": rejection_data.reason,
        "rejection_notes": rejection_data.notes
    }
    
    # Update the verification status
    verification = crud.payment_verification.update(
        db, db_obj=verification, obj_in=verification_update
    )
    
    # Send notification to user
    notification_service = get_notification_service(db)
    notification_service.notify_payment_verification_rejected(
        user=verification.user,
        payment_verification=verification
    )
    
    return verification

@router.get("/proof-image/{file_name}")
async def get_proof_image(
    file_name: str,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Get a payment proof image (restricted to admins and the user who submitted it).
    """
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    # Check if file exists
    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check permissions
    # TODO: Add logic to verify if the current user has permission to view this file
    # For now, only admins can view proof images
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return FileResponse(file_path)

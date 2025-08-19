import os
import stripe
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Any
import uuid

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.schemas.payment_verification import (
    PaymentVerificationCreate,
    PaymentVerification,
    PaymentVerificationApprove,
    PaymentVerificationReject, 
    PaymentVerificationStatus, 
    StripeCheckoutSession
)

router = APIRouter()

# --- Stripe Automated Payments ---
stripe.api_key = settings.STRIPE_API_KEY

@router.post("/create-checkout-session", response_model=StripeCheckoutSession)
def create_checkout_session(
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    DEPRECATED: Use /api/v1/subscriptions/create-checkout-session with plan_id instead.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Deprecated. Use /api/v1/subscriptions/create-checkout-session with plan_id."
    )


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: Session = Depends(deps.get_db)):
    """
    DEPRECATED: Use /api/v1/subscriptions/stripe-webhook.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Deprecated. Use /api/v1/subscriptions/stripe-webhook."
    )


# --- Manual Payment Verification ---

# Ensure upload directory exists
UPLOAD_DIR = "static/payment_proofs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_upload_file(file: UploadFile, user_id: int) -> str:
    """Save uploaded file and return the file path"""
    file_ext = os.path.splitext(file.filename)[1]  # Get file extension
    filename = f"{user_id}_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    return file_path

@router.post("/submit-payment", response_model=PaymentVerification)
async def submit_payment(
    *,
    username: str,
    payment_proof: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Submit payment proof for premium subscription
    """
    # Check file type
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if payment_proof.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Save the uploaded file
    try:
        file_path = save_upload_file(payment_proof, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
    
    # Create payment verification record
    payment_in = PaymentVerificationCreate(
        user_id=current_user.id,
        username=username,
        payment_proof_path=file_path
    )
    
    return crud.payment_verification.create(db, obj_in=payment_in)

@router.get("/", response_model=List[PaymentVerification])
def get_payments(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Get payment verification history.
    - Regular users can see their own history.
    - Superusers can see all history.
    """
    if crud.user.is_superuser(current_user):
        return crud.payment_verification.get_multi(db, skip=skip, limit=limit)
    else:
        return crud.payment_verification.get_multi_by_user(
            db, user_id=current_user.id, skip=skip, limit=limit
        )

@router.get("/my-payments", response_model=List[PaymentVerification])
def get_my_payments(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get payment verification history for current user
    """
    return crud.payment_verification.get_multi_by_user(
        db, user_id=current_user.id
    )

@router.get("/payment-proof/{payment_id}")
async def get_payment_proof(
    payment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get payment proof file (only for the payment owner or admin)
    """
    payment = crud.payment_verification.get(db, id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment verification not found"
        )
    
    # Check permission
    if payment.user_id != current_user.id and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if not os.path.exists(payment.payment_proof_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment proof file not found"
        )
    
    return FileResponse(payment.payment_proof_path)

# Admin endpoints
@router.get("/admin/pending", response_model=List[PaymentVerification])
def get_pending_verifications(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all pending payment verifications (admin only)
    """
    return crud.payment_verification.get_pending_verifications(
        db, skip=skip, limit=limit
    )

@router.post("/admin/approve/{payment_id}", response_model=PaymentVerification)
def approve_payment(
    payment_id: int,
    approval: PaymentVerificationApprove,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Approve a payment verification and grant premium access (admin only)
    """
    payment = crud.payment_verification.get(db, id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment verification not found"
        )
    
    if payment.status != PaymentVerificationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment is already {payment.status}"
        )
    
    try:
        return crud.payment_verification.approve_verification(
            db, 
            db_obj=payment, 
            plan_id=approval.plan_id,
            admin_notes=approval.admin_notes,
            premium_days=approval.premium_days,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/admin/reject/{payment_id}", response_model=PaymentVerification)
def reject_payment(
    payment_id: int,
    rejection: PaymentVerificationReject,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Reject a payment verification (admin only)
    """
    payment = crud.payment_verification.get(db, id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment verification not found"
        )
    
    if payment.status != PaymentVerificationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment is already {payment.status}"
        )
    
    return crud.payment_verification.reject_verification(
        db, db_obj=payment, admin_notes=rejection.admin_notes
    )

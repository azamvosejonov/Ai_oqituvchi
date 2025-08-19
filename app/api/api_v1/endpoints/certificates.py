import os
import uuid
from typing import Any, List
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from app import crud, models, schemas
from app.api import deps
from app.utils.pdf_generator import create_certificate_pdf

router = APIRouter()


@router.post("/", response_model=schemas.Certificate, status_code=201)
def create_certificate(
    *,
    db: Session = Depends(deps.get_db),
    certificate_in: schemas.CertificateCreate,
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create a new certificate for a user. (Admin only)
    """
    user = crud.user.get(db, id=certificate_in.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate a unique verification code
    certificate_in.verification_code = str(uuid.uuid4())

    # Create the certificate record first to get an ID
    db_cert = crud.certificate.create(db, obj_in=certificate_in)

    # Generate PDF
    pdf_path = create_certificate_pdf(
        user_name=user.full_name or user.username,
        level_completed=db_cert.level_completed,
        course_name=certificate_in.course_name,
        certificate_id=db_cert.id
    )

    # Update the certificate record with the PDF path
    update_data = schemas.CertificateUpdate(file_path=pdf_path)
    crud.certificate.update(db=db, db_obj=db_cert, obj_in=update_data)
    db.refresh(db_cert)

    return db_cert


@router.get("/user/{user_id}", response_model=List[schemas.Certificate])
def read_user_certificates(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Retrieve certificates for a specific user. (Admin only)
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    certificates = crud.certificate.get_multi_by_user(db, user_id=user_id)
    return certificates


@router.get("/my-certificates", response_model=List[schemas.Certificate])
def read_my_certificates(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve certificates for the current logged-in user.
    """
    certificates = crud.certificate.get_multi_by_user(db, user_id=current_user.id)
    return certificates


@router.get("/{certificate_id}/download", response_class=FileResponse)
async def download_certificate(
    *, 
    db: Session = Depends(deps.get_db),
    certificate_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Download a certificate as a PDF file.
    Only the owner or an admin can download it.
    """
    certificate = crud.certificate.get(db, id=certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")

    # Check for authorization
    if not crud.user.is_admin(current_user) and certificate.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to download this certificate")

    if not certificate.file_path:
        raise HTTPException(status_code=404, detail="Certificate file path not recorded in the database.")

    # Construct a robust absolute path from the project root
    try:
        # Assuming this file is at /app/api/api_v1/endpoints/certificates.py, we go up 4 levels
        PROJECT_ROOT = Path(__file__).resolve().parents[4]
        absolute_file_path = PROJECT_ROOT / certificate.file_path
    except IndexError:
        # Fallback in case the file structure changes
        raise HTTPException(status_code=500, detail="Could not determine project root directory.")

    if not absolute_file_path.exists():
        raise HTTPException(status_code=404, detail=f"Certificate file not found at path: {absolute_file_path}")

    try:
        return FileResponse(path=str(absolute_file_path), media_type='application/pdf', filename=os.path.basename(certificate.file_path))
    except Exception as e:
        # Log the error for debugging
        print(f"Error creating FileResponse: {e}")
        raise HTTPException(status_code=500, detail=f"Could not process the certificate file. Error: {str(e)}")


@router.get("/{certificate_id}/verify/{verification_code}", response_model=schemas.Certificate)
def verify_certificate(
    *,
    db: Session = Depends(deps.get_db),
    certificate_id: int,
    verification_code: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Verify a certificate by its verification code.
    """
    certificate = crud.certificate.get(db, id=certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")

    if certificate.verification_code != verification_code:
        raise HTTPException(status_code=403, detail="Invalid verification code")

    return certificate

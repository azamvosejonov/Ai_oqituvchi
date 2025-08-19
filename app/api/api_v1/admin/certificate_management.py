from typing import Any, List
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.post("/", response_model=schemas.Certificate, status_code=201)
def create_certificate(
    *, 
    db: Session = Depends(deps.get_db),
    certificate_in: schemas.CertificateCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Create new certificate for a user. (Superuser only)
    """
    # Check if user exists
    user = crud.user.get(db, id=certificate_in.user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {certificate_in.user_id} not found")
    
    # Generate verification code if not provided
    if not certificate_in.verification_code:
        certificate_in.verification_code = str(uuid.uuid4())

    certificate = crud.certificate.create(db=db, obj_in=certificate_in)
    return certificate


@router.get("/", response_model=List[schemas.Certificate])
def read_certificates(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve certificates. (Superuser only)
    """
    certificates = crud.certificate.get_multi(db, skip=skip, limit=limit)
    return certificates


@router.get("/{certificate_id}", response_model=schemas.Certificate)
def read_certificate(
    *,
    db: Session = Depends(deps.get_db),
    certificate_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get certificate by ID. (Superuser only)
    """
    certificate = crud.certificate.get(db, id=certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return certificate


@router.put("/{certificate_id}", response_model=schemas.Certificate)
def update_certificate(
    *,
    db: Session = Depends(deps.get_db),
    certificate_id: int,
    certificate_in: schemas.CertificateUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a certificate. (Superuser only)
    """
    certificate = crud.certificate.get(db, id=certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    certificate = crud.certificate.update(db, db_obj=certificate, obj_in=certificate_in)
    return certificate


@router.delete("/{certificate_id}", response_model=schemas.Certificate)
def delete_certificate(
    *,
    db: Session = Depends(deps.get_db),
    certificate_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a certificate. (Superuser only)
    """
    certificate = crud.certificate.get(db, id=certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    certificate = crud.certificate.remove(db, id=certificate_id)
    return certificate

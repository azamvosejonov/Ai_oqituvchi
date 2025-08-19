from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, crud
from app.api import deps

router = APIRouter()


@router.get("/statistics/payments", response_model=dict)
def get_payment_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve payment statistics (total revenue, active subscriptions). (Superuser only)
    """
    stats = crud.subscription.get_payment_statistics(db)
    return stats

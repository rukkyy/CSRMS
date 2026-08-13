from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from app.database import get_db
from app.models.user import User
from app.models.request import ServiceRequest
from app.dependencies import RequireRole

router = APIRouter(prefix="/api/maintenance", tags=["Maintenance Operations"])

@router.get("/dashboard/stats", response_model=Dict[str, Any])
def get_maintenance_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole(["MAINTENANCE"]))
):
    """Retrieve statistical counters for the maintenance staff dashboard."""
    # Count requests assigned to this user by status
    status_counts = db.query(
        ServiceRequest.status, func.count(ServiceRequest.id)
    ).filter(ServiceRequest.assigned_to == current_user.id)\
     .group_by(ServiceRequest.status).all()
    
    status_dict = {status: count for status, count in status_counts}

    total_assigned = db.query(func.count(ServiceRequest.id))\
        .filter(ServiceRequest.assigned_to == current_user.id).scalar() or 0

    return {
        "total_assigned": total_assigned,
        "status_counts": {
            "ASSIGNED": status_dict.get("ASSIGNED", 0),
            "IN_PROGRESS": status_dict.get("IN_PROGRESS", 0),
            "RESOLVED": status_dict.get("RESOLVED", 0),
            "CLOSED": status_dict.get("CLOSED", 0)
        }
    }

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from app.database import get_db
from app.models.user import User
from app.models.request import ServiceRequest
from app.models.category import Category
from app.schemas.user import UserResponse
from app.dependencies import RequireRole
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/api/admin", tags=["Admin Operations"])

@router.get("/dashboard/stats", response_model=Dict[str, Any])
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole(["ADMIN"]))
):
    """Retrieve statistical counters for the admin dashboard."""
    # Count requests by status
    status_counts = db.query(
        ServiceRequest.status, func.count(ServiceRequest.id)
    ).group_by(ServiceRequest.status).all()
    status_dict = {status: count for status, count in status_counts}

    # Count requests by priority
    priority_counts = db.query(
        ServiceRequest.priority, func.count(ServiceRequest.id)
    ).group_by(ServiceRequest.priority).all()
    priority_dict = {priority: count for priority, count in priority_counts}

    # Count requests by category
    category_counts = db.query(
        Category.name, func.count(ServiceRequest.id)
    ).join(ServiceRequest, ServiceRequest.category_id == Category.id, isouter=True)\
     .group_by(Category.name).all()
    category_dict = {cat_name: count for cat_name, count in category_counts}

    total_requests = db.query(func.count(ServiceRequest.id)).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0

    return {
        "total_requests": total_requests,
        "total_users": total_users,
        "status_counts": {
            "SUBMITTED": status_dict.get("SUBMITTED", 0),
            "ASSIGNED": status_dict.get("ASSIGNED", 0),
            "IN_PROGRESS": status_dict.get("IN_PROGRESS", 0),
            "RESOLVED": status_dict.get("RESOLVED", 0),
            "CLOSED": status_dict.get("CLOSED", 0)
        },
        "priority_counts": {
            "LOW": priority_dict.get("LOW", 0),
            "MEDIUM": priority_dict.get("MEDIUM", 0),
            "HIGH": priority_dict.get("HIGH", 0),
            "URGENT": priority_dict.get("URGENT", 0)
        },
        "category_counts": category_dict
    }

@router.get("/users", response_model=List[UserResponse])
def get_users(
    role: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole(["ADMIN"]))
):
    """Retrieve a list of users, filterable by role (e.g. MAINTENANCE)."""
    return UserRepository.get_all(db, role=role)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole(["ADMIN"]))
):
    """Delete a user account. Incorporates safety controls (cannot delete self or last admin)."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own administrator account"
        )
    UserService.delete_user(db, user_id)
    return None

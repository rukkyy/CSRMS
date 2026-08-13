from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.schemas.request import ServiceRequestCreate, ServiceRequestUpdate, ServiceRequestResponse, CategoryResponse
from app.dependencies import get_current_user, RequireRole
from app.services.request_service import RequestService
from app.repositories.category_repository import CategoryRepository

router = APIRouter(prefix="/api/requests", tags=["Service Requests"])

@router.post("/", response_model=ServiceRequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(
    request_data: ServiceRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole(["REQUESTER"]))
):
    """Submit a new service request. Allowed for Requesters only."""
    return RequestService.create_request(db, request_data, current_user.id)

@router.get("/", response_model=List[ServiceRequestResponse])
def get_requests(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List service requests. Returns requests filterable by status, priority, and category.
    - Requesters only see their own requests.
    - Maintenance staff only see requests assigned to them.
    - Administrators see all requests.
    """
    return RequestService.get_requests_for_user(
        db=db,
        user_id=current_user.id,
        role=current_user.role,
        status_filter=status,
        priority_filter=priority,
        category_filter=category_id
    )

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve all categories. Accessible by any authenticated user."""
    return CategoryRepository.get_all(db)

@router.get("/{request_id}", response_model=ServiceRequestResponse)
def get_request_details(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve details of a specific request.
    - Requesters can only view their own requests.
    - Maintenance staff can only view requests assigned to them.
    - Admins can view any request.
    """
    db_request = RequestService.get_request(db, request_id)
    
    # Authorize based on role
    if current_user.role == "REQUESTER" and db_request.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this request"
        )
    elif current_user.role == "MAINTENANCE" and db_request.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this request"
        )
        
    return db_request

@router.put("/{request_id}", response_model=ServiceRequestResponse)
def update_request(
    request_id: int,
    update_data: ServiceRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update request fields or transition request status.
    Rules:
    - Requesters can edit details only if status is SUBMITTED, and close request if status is RESOLVED.
    - Maintenance staff can mark request as IN_PROGRESS or RESOLVED (requires resolution notes).
    - Admins can update all fields, prioritize, and assign staff.
    """
    return RequestService.update_request(db, request_id, update_data, current_user)

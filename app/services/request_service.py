from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from app.models.request import ServiceRequest
from app.models.user import User
from app.schemas.request import ServiceRequestCreate, ServiceRequestUpdate
from app.repositories.request_repository import RequestRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.user_repository import UserRepository

class RequestService:
    @staticmethod
    def create_request(db: Session, request_data: ServiceRequestCreate, requester_id: int) -> ServiceRequest:
        # Validate category exists
        category = CategoryRepository.get_by_id(db, request_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with ID {request_data.category_id} does not exist"
            )
        return RequestRepository.create(db, request_data, requester_id)

    @staticmethod
    def get_request(db: Session, request_id: int) -> ServiceRequest:
        db_request = RequestRepository.get_by_id(db, request_id)
        if not db_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service request with ID {request_id} not found"
            )
        return db_request

    @staticmethod
    def get_requests_for_user(
        db: Session,
        user_id: int,
        role: str,
        status_filter: Optional[str] = None,
        priority_filter: Optional[str] = None,
        category_filter: Optional[int] = None
    ) -> List[ServiceRequest]:
        """Fetch filtered requests depending on user role."""
        if role == "ADMIN":
            return RequestRepository.get_all(
                db, status=status_filter, priority=priority_filter, category_id=category_filter
            )
        elif role == "MAINTENANCE":
            return RequestRepository.get_all(
                db, assigned_to=user_id, status=status_filter, priority=priority_filter, category_id=category_filter
            )
        else: # REQUESTER
            return RequestRepository.get_all(
                db, requester_id=user_id, status=status_filter, priority=priority_filter, category_id=category_filter
            )

    @staticmethod
    def update_request(
        db: Session,
        request_id: int,
        update_data: ServiceRequestUpdate,
        current_user: User
    ) -> ServiceRequest:
        db_request = RequestService.get_request(db, request_id)
        
        # Build update dictionary
        updates: Dict[str, Any] = {}

        # 1. Authorization & Role checks for fields
        if current_user.role == "REQUESTER":
            # Requesters can only edit their own requests
            if db_request.requester_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only manage your own service requests"
                )
            
            # Requesters can only update request details if it's still SUBMITTED
            if update_data.title or update_data.description or update_data.location or update_data.category_id:
                if db_request.status != "SUBMITTED":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot modify request details once it has been processed"
                    )
                if update_data.title: updates["title"] = update_data.title
                if update_data.description: updates["description"] = update_data.description
                if update_data.location: updates["location"] = update_data.location
                if update_data.category_id:
                    # Validate category
                    category = CategoryRepository.get_by_id(db, update_data.category_id)
                    if not category:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid category ID"
                        )
                    updates["category_id"] = update_data.category_id
            
            # Requesters can transition RESOLVED -> CLOSED
            if update_data.status:
                if update_data.status != "CLOSED":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Requesters are only allowed to transition requests to CLOSED"
                    )
                if db_request.status != "RESOLVED":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="You can only close requests that are currently RESOLVED"
                    )
                updates["status"] = "CLOSED"

        elif current_user.role == "MAINTENANCE":
            # Maintenance staff can only edit requests assigned to them
            if db_request.assigned_to != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_430_UNAUTHORIZED if hasattr(status, 'HTTP_430_UNAUTHORIZED') else 403,
                    detail="You can only update requests assigned to you"
                )
            
            # Maintenance staff cannot change fields other than status and resolution notes
            if update_data.title or update_data.description or update_data.location or update_data.category_id or update_data.priority or update_data.assigned_to:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Maintenance staff are not permitted to change request fields or assignments"
                )

            if update_data.status:
                # Enforce state machine for Maintenance
                # ASSIGNED -> IN_PROGRESS
                # IN_PROGRESS -> RESOLVED (requires notes)
                if update_data.status not in ["IN_PROGRESS", "RESOLVED"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Maintenance staff cannot set status to {update_data.status}"
                    )
                
                if update_data.status == "IN_PROGRESS":
                    if db_request.status != "ASSIGNED":
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Can only progress requests that are currently ASSIGNED"
                        )
                
                if update_data.status == "RESOLVED":
                    if db_request.status != "IN_PROGRESS":
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Can only resolve requests that are currently IN_PROGRESS"
                        )
                    # Require resolution notes
                    notes = update_data.resolution_notes or db_request.resolution_notes
                    if not notes or len(notes.strip()) < 5:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Resolution notes (minimum 5 characters) are required to resolve a request"
                        )
                    updates["resolution_notes"] = notes
                
                updates["status"] = update_data.status

            if update_data.resolution_notes and not update_data.status:
                updates["resolution_notes"] = update_data.resolution_notes

        elif current_user.role == "ADMIN":
            # Admins have full access to change details
            if update_data.title: updates["title"] = update_data.title
            if update_data.description: updates["description"] = update_data.description
            if update_data.location: updates["location"] = update_data.location
            if update_data.category_id:
                category = CategoryRepository.get_by_id(db, update_data.category_id)
                if not category:
                    raise HTTPException(status_code=400, detail="Invalid category ID")
                updates["category_id"] = update_data.category_id
            
            if update_data.priority:
                updates["priority"] = update_data.priority

            # Assignment Logic
            if update_data.assigned_to is not None:
                # If changing assignment
                if update_data.assigned_to == 0 or update_data.assigned_to == -1: # Represent unassign
                    updates["assigned_to"] = None
                    # If status was ASSIGNED/IN_PROGRESS, roll back to SUBMITTED
                    if db_request.status in ["ASSIGNED", "IN_PROGRESS"]:
                        updates["status"] = "SUBMITTED"
                else:
                    # Validate assignee exists and is MAINTENANCE
                    assignee = UserRepository.get_by_id(db, update_data.assigned_to)
                    if not assignee or assignee.role != "MAINTENANCE":
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Assignee must be a registered user with the MAINTENANCE role"
                        )
                    updates["assigned_to"] = update_data.assigned_to
                    # Automatically transition status to ASSIGNED if currently SUBMITTED
                    if db_request.status == "SUBMITTED":
                        updates["status"] = "ASSIGNED"

            # Admin status changes
            if update_data.status:
                # Verify transition safety
                if update_data.status == "ASSIGNED":
                    # Require assignment
                    assignee_id = updates.get("assigned_to", db_request.assigned_to)
                    if not assignee_id:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot transition to ASSIGNED without an assigned staff member"
                        )
                elif update_data.status == "RESOLVED":
                    notes = update_data.resolution_notes or db_request.resolution_notes
                    if not notes or len(notes.strip()) < 5:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Resolution notes (minimum 5 characters) are required to resolve a request"
                        )
                    updates["resolution_notes"] = notes
                
                updates["status"] = update_data.status
            
            if update_data.resolution_notes:
                updates["resolution_notes"] = update_data.resolution_notes

        return RequestRepository.update(db, db_request, updates)

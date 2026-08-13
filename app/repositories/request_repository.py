from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.request import ServiceRequest
from app.schemas.request import ServiceRequestCreate, ServiceRequestUpdate
import datetime

class RequestRepository:
    @staticmethod
    def get_by_id(db: Session, request_id: int) -> Optional[ServiceRequest]:
        return db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()

    @staticmethod
    def get_all(
        db: Session,
        requester_id: Optional[int] = None,
        assigned_to: Optional[int] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category_id: Optional[int] = None
    ) -> List[ServiceRequest]:
        query = db.query(ServiceRequest)
        if requester_id is not None:
            query = query.filter(ServiceRequest.requester_id == requester_id)
        if assigned_to is not None:
            query = query.filter(ServiceRequest.assigned_to == assigned_to)
        if status:
            query = query.filter(ServiceRequest.status == status)
        if priority:
            query = query.filter(ServiceRequest.priority == priority)
        if category_id is not None:
            query = query.filter(ServiceRequest.category_id == category_id)
        return query.order_by(ServiceRequest.created_at.desc()).all()

    @staticmethod
    def create(db: Session, request_data: ServiceRequestCreate, requester_id: int) -> ServiceRequest:
        db_request = ServiceRequest(
            title=request_data.title,
            description=request_data.description,
            location=request_data.location,
            category_id=request_data.category_id,
            priority=request_data.priority,
            status="SUBMITTED",
            requester_id=requester_id
        )
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        return db_request

    @staticmethod
    def update(
        db: Session,
        db_request: ServiceRequest,
        update_data: Dict[str, Any]
    ) -> ServiceRequest:
        for key, value in update_data.items():
            if value is not None or key in ["assigned_to", "resolution_notes"]:
                setattr(db_request, key, value)
        db_request.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(db_request)
        return db_request

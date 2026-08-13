from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="REQUESTER") # "REQUESTER", "ADMIN", "MAINTENANCE"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    submitted_requests = relationship(
        "ServiceRequest",
        back_populates="requester",
        foreign_keys="ServiceRequest.requester_id"
    )
    assigned_requests = relationship(
        "ServiceRequest",
        back_populates="assignee",
        foreign_keys="ServiceRequest.assigned_to"
    )

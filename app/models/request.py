from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from app.database import Base

class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String, nullable=False)
    priority = Column(String, nullable=False, default="MEDIUM") # "LOW", "MEDIUM", "HIGH", "URGENT"
    status = Column(String, nullable=False, default="SUBMITTED") # "SUBMITTED", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Foreign Keys
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Additional info
    resolution_notes = Column(Text, nullable=True)

    # Relationships
    requester = relationship(
        "User",
        back_populates="submitted_requests",
        foreign_keys=[requester_id]
    )
    assignee = relationship(
        "User",
        back_populates="assigned_requests",
        foreign_keys=[assigned_to]
    )
    category = relationship("Category", back_populates="service_requests")

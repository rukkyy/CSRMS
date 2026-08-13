from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponse

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=200)

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

class ServiceRequestBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10, max_length=2000)
    location: str = Field(..., min_length=2, max_length=100)
    category_id: int

class ServiceRequestCreate(ServiceRequestBase):
    priority: str = Field("MEDIUM", pattern="^(LOW|MEDIUM|HIGH|URGENT)$")

class ServiceRequestUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    location: Optional[str] = Field(None, min_length=2, max_length=100)
    category_id: Optional[int] = None
    priority: Optional[str] = Field(None, pattern="^(LOW|MEDIUM|HIGH|URGENT)$")
    status: Optional[str] = Field(None, pattern="^(SUBMITTED|ASSIGNED|IN_PROGRESS|RESOLVED|CLOSED)$")
    assigned_to: Optional[int] = None
    resolution_notes: Optional[str] = Field(None, max_length=2000)

class ServiceRequestResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime
    requester_id: int
    category_id: int
    assigned_to: Optional[int] = None
    resolution_notes: Optional[str] = None
    
    # Nested relations
    requester: UserResponse
    category: CategoryResponse
    assignee: Optional[UserResponse] = None

    class Config:
        from_attributes = True

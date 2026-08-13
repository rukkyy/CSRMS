from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50)
    role: str = Field("REQUESTER", pattern="^(REQUESTER|ADMIN|MAINTENANCE)$")

class UserUpdate(BaseModel):
    name: str = None
    email: EmailStr = None
    role: str = Field(None, pattern="^(REQUESTER|ADMIN|MAINTENANCE)$")

class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str
    email: str

class TokenData(BaseModel):
    email: str
    role: str

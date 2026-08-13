from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

class UserService:
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """Register a new user, verifying email uniqueness and hashing the password."""
        existing = UserRepository.get_by_email(db, user_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered"
            )
        
        # Hash password
        hashed_password = AuthService.hash_password(user_data.password)
        return UserRepository.create(db, user_data, hashed_password)

    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    @staticmethod
    def get_all_users(db: Session, role: Optional[str] = None) -> List[User]:
        return UserRepository.get_all(db, role)

    @staticmethod
    def delete_user(db: Session, user_id: int) -> None:
        user = UserService.get_user(db, user_id)
        if user.role == "ADMIN":
            # Protect against deleting the last admin
            admins = UserRepository.get_all(db, role="ADMIN")
            if len(admins) <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete the last administrator"
                )
        UserRepository.delete(db, user)

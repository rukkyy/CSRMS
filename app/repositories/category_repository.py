from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.category import Category

class CategoryRepository:
    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Category]:
        return db.query(Category).filter(Category.name == name).first()

    @staticmethod
    def get_all(db: Session) -> List[Category]:
        return db.query(Category).all()

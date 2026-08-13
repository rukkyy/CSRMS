from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Create database engine with SQLite configuration
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_database():
    """Create tables and seed initial categories and demo accounts if they don't exist."""
    # Import models here to avoid circular dependencies
    from app.models import Base as ModelBase
    from app.models.user import User
    from app.models.category import Category
    from app.services.auth_service import AuthService

    # Create tables
    ModelBase.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Seed categories
        default_categories = [
            {"name": "Plumbing", "description": "Leaking pipes, clogged drains, water issues"},
            {"name": "Electrical", "description": "Flickering lights, broken sockets, power cuts"},
            {"name": "Carpentry", "description": "Broken furniture, doors, windows"},
            {"name": "HVAC", "description": "Air conditioning, heating, ventilation repairs"},
            {"name": "Janitorial", "description": "Spills, cleaning requests, waste disposal"}
        ]

        for cat_data in default_categories:
            existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not existing:
                category = Category(name=cat_data["name"], description=cat_data["description"])
                db.add(category)
        
        # Seed demo users
        demo_users = [
            {
                "name": "Campus Administrator",
                "email": "admin@campus.edu",
                "password": "AdminPass123!",
                "role": "ADMIN"
            },
            {
                "name": "John Maintenance",
                "email": "staff@campus.edu",
                "password": "StaffPass123!",
                "role": "MAINTENANCE"
            },
            {
                "name": "Jane Student",
                "email": "requester@campus.edu",
                "password": "RequesterPass123!",
                "role": "REQUESTER"
            }
        ]

        for user_data in demo_users:
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing:
                hashed_pw = AuthService.hash_password(user_data["password"])
                user = User(
                    name=user_data["name"],
                    email=user_data["email"],
                    password_hash=hashed_pw,
                    role=user_data["role"]
                )
                db.add(user)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

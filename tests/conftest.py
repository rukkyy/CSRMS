import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Category, ServiceRequest
from app.database import get_db
from app.main import app
from app.services.auth_service import AuthService

# Use a local file-based database for reliable multi-connection testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Create a fresh database structure for each test function using a file-based SQLite test DB."""
    # Build schema
    Base.metadata.create_all(bind=engine)
    
    db_session = TestingSessionLocal()
    
    # Pre-seed categories
    categories = [
        Category(name="Plumbing", description="Plumbing issues"),
        Category(name="Electrical", description="Electrical issues"),
        Category(name="HVAC", description="HVAC issues")
    ]
    db_session.add_all(categories)

    # Pre-seed role-based test users
    admin_pw = AuthService.hash_password("AdminPass123!")
    staff_pw = AuthService.hash_password("StaffPass123!")
    req_pw = AuthService.hash_password("RequesterPass123!")
    
    users = [
        User(name="Test Admin", email="admin@test.com", password_hash=admin_pw, role="ADMIN"),
        User(name="Test Staff", email="staff@test.com", password_hash=staff_pw, role="MAINTENANCE"),
        User(name="Test Requester", email="requester@test.com", password_hash=req_pw, role="REQUESTER"),
        User(name="Other Requester", email="other@test.com", password_hash=req_pw, role="REQUESTER")
    ]
    db_session.add_all(users)
    db_session.commit()

    try:
        yield db_session
    finally:
        db_session.close()
        # Drop all tables to clean up schema
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Override get_db dependency with testing db session."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

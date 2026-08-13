import pytest
from app.services.auth_service import AuthService
from app.models.user import User

def test_password_hashing():
    """Unit test for secure password hashing and verification."""
    password = "MySecurePassword123!"
    hashed = AuthService.hash_password(password)
    assert hashed != password
    assert AuthService.verify_password(password, hashed) is True
    assert AuthService.verify_password("wrong_password", hashed) is False

def test_user_registration(client, db):
    """Integration test: Registering a new requester account."""
    payload = {
        "name": "Alice Smith",
        "email": "alice@test.com",
        "password": "Password123!",
        "role": "ADMIN" # Will be forced to REQUESTER by auth endpoint for security
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 211 or response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@test.com"
    assert data["role"] == "REQUESTER" # Verify role escalation prevention works
    assert "password_hash" not in data # Verify password hash is not leaked

    # Attempt to register again with same email
    response_dup = client.post("/api/auth/register", json=payload)
    assert response_dup.status_code == 400
    assert "already registered" in response_dup.json()["detail"]

def test_user_login(client):
    """Integration test: Logging in with valid and invalid credentials."""
    # Valid login
    login_payload = {
        "email": "requester@test.com",
        "password": "RequesterPass123!"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "REQUESTER"
    assert data["email"] == "requester@test.com"

    # Invalid password login
    bad_pw_payload = {
        "email": "requester@test.com",
        "password": "WrongPassword!"
    }
    response_bad_pw = client.post("/api/auth/login", json=bad_pw_payload)
    assert response_bad_pw.status_code == 401

    # Invalid email login
    bad_email_payload = {
        "email": "nonexistent@test.com",
        "password": "Password123!"
    }
    response_bad_email = client.post("/api/auth/login", json=bad_email_payload)
    assert response_bad_email.status_code == 401

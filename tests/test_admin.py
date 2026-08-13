import pytest
from app.services.auth_service import AuthService
from app.models.category import Category
from app.models.user import User

def get_auth_headers(email: str, role: str) -> dict:
    token = AuthService.create_access_token({"sub": email, "role": role})
    return {"Authorization": f"Bearer {token}"}

def test_admin_assignment_and_prioritization(client, db):
    """Test that Administrators can view all requests, prioritize them, and assign staff."""
    plumbing = db.query(Category).filter(Category.name == "Plumbing").first()
    staff = db.query(User).filter(User.role == "MAINTENANCE").first()

    headers_req = get_auth_headers("requester@test.com", "REQUESTER")
    headers_admin = get_auth_headers("admin@test.com", "ADMIN")

    # Requester submits request
    payload = {
        "title": "Clogged toilet drain",
        "description": "Third floor ladies room toilet is clogged.",
        "location": "Science Block, 3rd Floor",
        "category_id": plumbing.id,
        "priority": "MEDIUM"
    }
    req_id = client.post("/api/requests/", json=payload, headers=headers_req).json()["id"]

    # Admin lists all requests
    response_list = client.get("/api/requests/", headers=headers_admin)
    assert response_list.status_code == 200
    assert len(response_list.json()) == 1

    # Admin prioritizes and assigns request to staff
    update_payload = {
        "priority": "HIGH",
        "assigned_to": staff.id
    }
    response_update = client.put(f"/api/requests/{req_id}", json=update_payload, headers=headers_admin)
    assert response_update.status_code == 200
    data = response_update.json()
    assert data["priority"] == "HIGH"
    assert data["assigned_to"] == staff.id
    assert data["status"] == "ASSIGNED" # State should automatically transition to ASSIGNED

def test_admin_dashboard_stats(client, db):
    """Test retrieving statistics for the administrative dashboard."""
    headers_admin = get_auth_headers("admin@test.com", "ADMIN")
    response = client.get("/api/admin/dashboard/stats", headers=headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "total_users" in data
    assert "status_counts" in data
    assert "priority_counts" in data

def test_admin_user_deletion(client, db):
    """Test that administrators can delete users but are blocked from deleting the last admin."""
    headers_admin = get_auth_headers("admin@test.com", "ADMIN")
    
    # List all users
    response_users = client.get("/api/admin/users", headers=headers_admin)
    assert response_users.status_code == 200
    users_list = response_users.json()
    assert len(users_list) == 4

    # Deleting other requester
    other_req = db.query(User).filter(User.email == "other@test.com").first()
    response_del = client.delete(f"/api/admin/users/{other_req.id}", headers=headers_admin)
    assert response_del.status_code == 204

    # Attempt to delete own admin account (should fail)
    admin_user = db.query(User).filter(User.email == "admin@test.com").first()
    response_del_self = client.delete(f"/api/admin/users/{admin_user.id}", headers=headers_admin)
    assert response_del_self.status_code == 400
    assert "cannot delete your own" in response_del_self.json()["detail"]

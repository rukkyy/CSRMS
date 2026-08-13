import pytest
from app.services.auth_service import AuthService
from app.models.category import Category
from app.models.user import User

def get_auth_headers(email: str, role: str) -> dict:
    token = AuthService.create_access_token({"sub": email, "role": role})
    return {"Authorization": f"Bearer {token}"}

def test_role_escalation_admin_endpoints(client):
    """Test that non-admin users cannot access administrative endpoints."""
    headers_req = get_auth_headers("requester@test.com", "REQUESTER")
    headers_staff = get_auth_headers("staff@test.com", "MAINTENANCE")

    # Requester access admin stats
    response_req = client.get("/api/admin/dashboard/stats", headers=headers_req)
    assert response_req.status_code == 403

    # Requester access users list
    response_users_req = client.get("/api/admin/users", headers=headers_req)
    assert response_users_req.status_code == 403

    # Maintenance access admin stats
    response_staff = client.get("/api/admin/dashboard/stats", headers=headers_staff)
    assert response_staff.status_code == 403

def test_role_escalation_request_updates(client, db):
    """Test that unauthorized users are prevented from modifying request priority or assignment details."""
    plumbing = db.query(Category).filter(Category.name == "Plumbing").first()

    headers_req = get_auth_headers("requester@test.com", "REQUESTER")
    headers_other_req = get_auth_headers("other@test.com", "REQUESTER")
    headers_staff = get_auth_headers("staff@test.com", "MAINTENANCE")

    # 1. Requester submits a request
    payload = {
        "title": "Broken lock",
        "description": "The lock on room 101 is broken.",
        "location": "Science Block, Room 101",
        "category_id": plumbing.id,
        "priority": "MEDIUM"
    }
    req_id = client.post("/api/requests/", json=payload, headers=headers_req).json()["id"]

    # 2. Requester tries to escalate priority to URGENT directly (Should be ignored/forbidden)
    # The RequestService should ignore priority fields for Requesters or block it
    # Let's check our service: the update fields for Requester only processes title, location, description, category. Other fields are ignored, so priority won't change.
    response_req_update = client.put(
        f"/api/requests/{req_id}",
        json={"priority": "URGENT"},
        headers=headers_req
    )
    assert response_req_update.status_code == 200
    assert response_req_update.json()["priority"] == "MEDIUM" # Ignored priority update

    # 3. Staff user tries to escalate priority (Should return 403 because they aren't assigned yet, or because staff cannot change priorities)
    response_staff_escalate = client.put(
        f"/api/requests/{req_id}",
        json={"priority": "HIGH"},
        headers=headers_staff
    )
    assert response_staff_escalate.status_code == 403 or response_staff_escalate.status_code == 430

    # 4. Another requester tries to edit this request
    response_other_edit = client.put(
        f"/api/requests/{req_id}",
        json={"title": "Hacked title"},
        headers=headers_other_req
    )
    assert response_other_edit.status_code == 403

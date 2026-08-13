import pytest
from app.services.auth_service import AuthService
from app.models.category import Category
from app.models.user import User


def get_auth_headers(email: str, role: str) -> dict:
    """Generate headers with simulated JWT Bearer token."""
    token = AuthService.create_access_token({"sub": email, "role": role})
    return {"Authorization": f"Bearer {token}"}

def test_request_creation_and_visibility(client, db):
    """Test submitting tickets and verifying that visibility boundaries are respected."""
    # Find Plumbing category ID
    plumbing = db.query(Category).filter(Category.name == "Plumbing").first()
    assert plumbing is not None

    headers_req = get_auth_headers("requester@test.com", "REQUESTER")
    headers_other = get_auth_headers("other@test.com", "REQUESTER")

    # 1. Requester submits a request
    payload = {
        "title": "Leaking faucet in bathroom",
        "description": "The faucet in the third floor bathroom has been leaking for two days.",
        "location": "Science Block, 3rd Floor Bathroom",
        "category_id": plumbing.id,
        "priority": "MEDIUM"
    }
    
    response = client.post("/api/requests/", json=payload, headers=headers_req)
    assert response.status_code == 201
    req_data = response.json()
    assert req_data["title"] == "Leaking faucet in bathroom"
    assert req_data["status"] == "SUBMITTED"
    assert req_data["requester_id"] is not None

    # 2. Requester views their own requests
    response_list = client.get("/api/requests/", headers=headers_req)
    assert response_list.status_code == 200
    assert len(response_list.json()) == 1
    assert response_list.json()[0]["id"] == req_data["id"]

    # 3. Another requester should NOT see this request
    response_list_other = client.get("/api/requests/", headers=headers_other)
    assert response_list_other.status_code == 200
    assert len(response_list_other.json()) == 0

    # 4. Another requester tries to read details of this specific request
    response_details_other = client.get(f"/api/requests/{req_data['id']}", headers=headers_other)
    assert response_details_other.status_code == 403

def test_requester_updates(client, db):
    """Test that requesters can update details on SUBMITTED tickets but not after processing."""
    plumbing = db.query(Category).filter(Category.name == "Plumbing").first()
    headers_req = get_auth_headers("requester@test.com", "REQUESTER")

    # Submit ticket
    payload = {
        "title": "Broken light socket",
        "description": "Flickering lights in room 204.",
        "location": "Main Hall, Room 204",
        "category_id": plumbing.id,
        "priority": "LOW"
    }
    req_id = client.post("/api/requests/", json=payload, headers=headers_req).json()["id"]

    # Update ticket (Allowed since status is SUBMITTED)
    update_payload = {
        "title": "Completely Broken Socket",
        "description": "The socket is sparking. Extremely dangerous.",
        "location": "Main Hall, Room 204"
    }
    response_update = client.put(f"/api/requests/{req_id}", json=update_payload, headers=headers_req)
    assert response_update.status_code == 200
    assert response_update.json()["title"] == "Completely Broken Socket"

    # Simulate Admin progressing the request to ASSIGNED
    from app.models.request import ServiceRequest
    req_obj = db.query(ServiceRequest).filter(ServiceRequest.id == req_id).first()
    staff_user = db.query(User).filter(User.role == "MAINTENANCE").first()
    req_obj.status = "ASSIGNED"
    req_obj.assigned_to = staff_user.id
    db.commit()

    # Requester tries to update request details now (Should fail because status is ASSIGNED)
    response_blocked = client.put(f"/api/requests/{req_id}", json={"title": "Trying to edit again"}, headers=headers_req)
    assert response_blocked.status_code == 400
    assert "Cannot modify request details" in response_blocked.json()["detail"]

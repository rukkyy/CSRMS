import pytest
from app.services.auth_service import AuthService
from app.models.category import Category
from app.models.user import User
from app.models.request import ServiceRequest

def get_auth_headers(email: str, role: str) -> dict:
    token = AuthService.create_access_token({"sub": email, "role": role})
    return {"Authorization": f"Bearer {token}"}

def test_maintenance_workflow(client, db):
    """Test the complete progress lifecycle for maintenance workers."""
    plumbing = db.query(Category).filter(Category.name == "Plumbing").first()
    staff = db.query(User).filter(User.role == "MAINTENANCE").first()

    headers_req = get_auth_headers("requester@test.com", "REQUESTER")
    headers_staff = get_auth_headers("staff@test.com", "MAINTENANCE")

    # 1. Requester submits a request
    payload = {
        "title": "Water heater broken",
        "description": "No hot water in the campus locker rooms.",
        "location": "Gymnasium Locker Rooms",
        "category_id": plumbing.id,
        "priority": "HIGH"
    }
    req_id = client.post("/api/requests/", json=payload, headers=headers_req).json()["id"]

    # 2. Staff views assigned requests (should be empty initially)
    response_assigned = client.get("/api/requests/", headers=headers_staff)
    assert len(response_assigned.json()) == 0

    # 3. Simulate Admin assigning the request to Staff
    from app.models.request import ServiceRequest
    req_obj = db.query(ServiceRequest).filter(ServiceRequest.id == req_id).first()
    req_obj.status = "ASSIGNED"
    req_obj.assigned_to = staff.id
    db.commit()

    # 4. Staff views assigned requests again (should contain 1 ticket)
    response_assigned = client.get("/api/requests/", headers=headers_staff)
    assert len(response_assigned.json()) == 1
    assert response_assigned.json()[0]["id"] == req_id

    # 5. Staff starts work (transitions ASSIGNED -> IN_PROGRESS)
    response_start = client.put(
        f"/api/requests/{req_id}",
        json={"status": "IN_PROGRESS"},
        headers=headers_staff
    )
    assert response_start.status_code == 200
    assert response_start.json()["status"] == "IN_PROGRESS"

    # 6. Staff attempts to resolve request WITHOUT resolution notes (should fail)
    response_resolve_fail = client.put(
        f"/api/requests/{req_id}",
        json={"status": "RESOLVED"},
        headers=headers_staff
    )
    assert response_resolve_fail.status_code == 400
    assert "Resolution notes" in response_resolve_fail.json()["detail"]

    # 7. Staff attempts to resolve request with too short notes (should fail)
    response_resolve_fail_short = client.put(
        f"/api/requests/{req_id}",
        json={"status": "RESOLVED", "resolution_notes": "ok"},
        headers=headers_staff
    )
    assert response_resolve_fail_short.status_code == 400

    # 8. Staff resolves request WITH valid resolution notes (should succeed)
    response_resolve = client.put(
        f"/api/requests/{req_id}",
        json={
            "status": "RESOLVED",
            "resolution_notes": "Replaced the heating element and thermostat. Tested, works."
        },
        headers=headers_staff
    )
    assert response_resolve.status_code == 200
    assert response_resolve.json()["status"] == "RESOLVED"
    assert response_resolve.json()["resolution_notes"] == "Replaced the heating element and thermostat. Tested, works."

    # 9. Requester closes the resolved request (should succeed)
    response_close = client.put(
        f"/api/requests/{req_id}",
        json={"status": "CLOSED"},
        headers=headers_req
    )
    assert response_close.status_code == 200
    assert response_close.json()["status"] == "CLOSED"

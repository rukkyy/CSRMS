# Quality Assurance Test Plan & Results
## Campus Service Request Management System (CSRMS)

---

### 1. Quality Assurance Strategy
Our QA strategy employs multi-tiered testing to ensure the correctness, reliability, security, and usability of the CSRMS application:
1. **Unit Testing:** Validates independent functional components (e.g. password hashing and verification in `AuthService`).
2. **Integration Testing:** Tests interactions between components (e.g., endpoints interacting with SQLite databases and verifying session generation).
3. **Security Testing:** Verifies authorization boundaries by attempting role escalation actions (e.g. a requester attempting to delete accounts or modify assignments) and ensuring `403 Forbidden` is returned.
4. **Usability / E2E Manual Testing:** Evaluates page layout structure, form inputs validation, alert banners, and responsive scaling.

---

### 2. Comprehensive Test Cases Table

Below is the verification register mapping functional requirements to specific tests:

| Test ID | Req Mapping | Description | Precondition | Test Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|---|
| **TC-AUT-001** | FR-01 | User Registration | Email not already registered. | POST `/api/auth/register` with new email and role `ADMIN`. | User registered; role is forced to `REQUESTER`. | User created; role forced to `REQUESTER` successfully. | **PASSED** |
| **TC-AUT-002** | FR-01 | Duplicate Registration | Email `alice@test.com` exists. | POST `/api/auth/register` with same email. | Returns `400 Bad Request` with "Email is already registered". | Returned `400 Bad Request` with correct warning message. | **PASSED** |
| **TC-AUT-003** | FR-02 | Secure User Login | Pre-seeded requester account. | POST `/api/auth/login` with correct password. | Returns JWT token, name, email, and role. | Token and user metadata returned successfully. | **PASSED** |
| **TC-AUT-004** | FR-02 | Invalid Password Login | Pre-seeded requester account. | POST `/api/auth/login` with wrong password. | Returns `401 Unauthorized`. | Returned `401 Unauthorized` with WWW-Authenticate header. | **PASSED** |
| **TC-REQ-001** | FR-04, FR-05 | Submit Request & Visibility | Authenticated requester session. | 1. POST `/api/requests/` to submit. <br>2. GET `/api/requests/` as author. <br>3. GET `/api/requests/` as other user. | 1. Ticket created (`SUBMITTED`).<br>2. Ticket listed for author.<br>3. Ticket hidden from other requester. | 1. Ticket created successfully.<br>2. Listed for author.<br>3. Other requester list is empty. | **PASSED** |
| **TC-REQ-002** | FR-06 | Requester Modify Request | Request in state `SUBMITTED`. | PUT `/api/requests/{id}` modifying title. | Title updated successfully. | Title updated in DB. | **PASSED** |
| **TC-REQ-003** | FR-06 | Block Requester Edits | Request is assigned / processed. | PUT `/api/requests/{id}` after status is progressed. | Returns `400 Bad Request` block. | Returned `400 Bad Request` blocking edits. | **PASSED** |
| **TC-ADM-001** | FR-07, FR-08, FR-09 | Admin Assign & Prioritize | Submitted request exists. Admin is logged in. | PUT `/api/requests/{id}` with `priority='HIGH'` and `assigned_to={staff_id}`. | Request is updated to `HIGH` priority, assigned to staff, status changes to `ASSIGNED`. | Priority set to `HIGH`, staff assigned, status updated to `ASSIGNED` automatically. | **PASSED** |
| **TC-ADM-002** | FR-14 | Admin Dashboard Stats | Sample requests in database. | GET `/api/admin/dashboard/stats` as admin. | Returns counters grouped by status and priority. | Detailed statistics counters returned correctly. | **PASSED** |
| **TC-ADM-003** | FR-13 | Admin Delete User Check | Admin is logged in. | DELETE `/api/admin/users/{own_id}`. | Returns `400 Bad Request` blocking self-deletion. | Blocked self-deletion with appropriate detail message. | **PASSED** |
| **TC-MNT-001** | FR-10, FR-11 | Maintenance Progression | Assigned request exists. Staff is logged in. | 1. PUT `/api/requests/{id}` set `IN_PROGRESS`. <br>2. PUT `/api/requests/{id}` set `RESOLVED` (no notes). | 1. Status updated.<br>2. Blocks with `400 Bad Request`. | 1. Status set to `IN_PROGRESS`.<br>2. blocked resolution without notes. | **PASSED** |
| **TC-MNT-002** | FR-12 | Maintenance Resolve Work | Request in state `IN_PROGRESS`. | PUT `/api/requests/{id}` set `RESOLVED` with 20-character notes. | Status updated to `RESOLVED` and notes persisted. | Request resolved and notes saved. | **PASSED** |
| **TC-SEC-001** | FR-03 | Role Escalation Check | Authenticated requester session. | GET `/api/admin/dashboard/stats`. | Returns `403 Forbidden`. | Request blocked with `403 Forbidden`. | **PASSED** |
| **TC-USA-001** | FR-15 | User Secure Logout | Logged in browser session. | Click 'Logout' button on dashboard navbar. | local tokens cleared; redirects to `/login`. | Clear local credentials, redirects to login view. | **PASSED** |

---

### 3. Automated Test Execution Results

We executed the automated test suite using `pytest -v`. Here is the run summary showing all 11 tests passed:

```bash
============================= test session starts ==============================
platform darwin -- Python 3.9.13, pytest-8.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /Users/nurudeenmuniru/Desktop/CSRMS
plugins: anyio-4.10.0
collected 11 items

tests/test_admin.py::test_admin_assignment_and_prioritization PASSED     [  9%]
tests/test_admin.py::test_admin_dashboard_stats PASSED                   [ 18%]
tests/test_admin.py::test_admin_user_deletion PASSED                     [ 27%]
tests/test_auth.py::test_password_hashing PASSED                         [ 36%]
tests/test_auth.py::test_user_registration PASSED                        [ 45%]
tests/test_auth.py::test_user_login PASSED                               [ 54%]
tests/test_maintenance.py::test_maintenance_workflow PASSED              [ 63%]
tests/test_requests.py::test_request_creation_and_visibility PASSED      [ 72%]
tests/test_requests.py::test_requester_updates PASSED                    [ 81%]
tests/test_security.py::test_role_escalation_admin_endpoints PASSED      [ 90%]
tests/test_security.py::test_role_escalation_request_updates PASSED      [100%]

======================= 11 passed, 15 warnings in 16.12s =======================
```

#### Defect and Corrective Actions Log:
1. **Defect ID: DEF-01**
   - *Description:* `sqlite3.OperationalError: no such table: users` in test suite.
   - *Cause:* In-memory SQLite (`:memory:`) closed connection and deleted tables between fixture setup and test execution.
   - *Corrective Action:* Switched connection parameters to use a file-based temporary test database (`test.db`) with schema cleanups in setup/teardown.
2. **Defect ID: DEF-02**
   - *Description:* `NameError: name 'User' is not defined` in `test_requests.py`.
   - *Cause:* Missing model import at the top of the test module.
   - *Corrective Action:* Imported `User` model from `app.models.user` explicitly.
3. **Defect ID: DEF-03**
   - *Description:* `OperationalError: attempt to write a readonly database` in teardown.
   - *Cause:* Trying to delete `test.db` file while SQL connections were still held in the connection pool.
   - *Corrective Action:* Replaced file deletion with `Base.metadata.drop_all(bind=engine)` which cleans database tables safely.

# Software Requirements Specification (SRS)
## Campus Service Request Management System (CSRMS)

---

### 1. Introduction
This document specifies the software requirements for the Campus Service Request Management System (CSRMS). CSRMS is a web-based, role-based platform designed to organize, track, assign, and resolve physical maintenance and utility service requests within a university campus.

### 2. Purpose
The purpose of this document is to establish a clear, unambiguous specification of the functional and non-functional requirements of the CSRMS system. This serves as the contract between stakeholders, the development team, and the academic assessment panel, ensuring complete traceability from initial requirements through code implementation and verification.

### 3. Scope
The scope of CSRMS is limited to campus maintenance operations. It provides a secure portal for:
- Requesters (students and faculty) to submit and track maintenance requests.
- Maintenance Staff to view, claim, progress, and mark tasks as resolved.
- Administrators to manage allocations, adjust priority rankings, and oversee completion statistics.

Out of scope for the MVP: automatic email notifications, SMS alerts, automated sensor triggers (IoT), and predictive SLA scheduling.

### 4. Stakeholders
- **University Administration:** Needs visibility into overall campus maintenance performance and staff workloads.
- **Maintenance Staff:** Needs a simple, mobile-friendly interface to view assigned tasks and report resolutions.
- **Campus Community (Requesters):** Needs a self-service portal to quickly submit and monitor repair tickets.
- **Academic Examiner (Exam Context):** Evaluates the implementation, quality assurance, system design, and software engineering rigor.

### 5. System Overview
CSRMS is built using a decoupled **Layered Architecture**:
1. **Presentation Layer:** Serves static HTML interfaces styled with CSS variables and driven by client-side Javascript.
2. **Business Logic Layer:** Service modules (`AuthService`, `UserService`, `RequestService`) validating business rules and state machines.
3. **Data Access Layer:** CRUD repositories wrapping ORM models.
4. **Database:** SQLite file storage persisting accounts, category catalogs, and tickets.

---

### 6. Functional Requirements (FR)

| Req ID | Title | Description | Priority |
|---|---|---|---|
| **FR-01** | User Registration | The system shall allow users to register a requester account. | Must Have |
| **FR-02** | Secure Authentication | The system shall authenticate registered users using secure credentials. | Must Have |
| **FR-03** | Role-Based Access Control | The system shall restrict interface pages and API endpoints based on User roles. | Must Have |
| **FR-04** | Submit Service Request | The system shall allow Requesters to submit service requests specifying category, subject, description, and location. | Must Have |
| **FR-05** | View Own Requests | The system shall allow Requesters to view a list of only their submitted requests. | Must Have |
| **FR-06** | Track Request Status | The system shall show Requesters real-time status and resolution details of their requests. | Must Have |
| **FR-07** | View All Requests | The system shall allow Administrators to view all service requests across the campus. | Must Have |
| **FR-08** | Assign Requests | The system shall allow Administrators to assign maintenance staff to submitted requests. | Must Have |
| **FR-09** | Prioritize Requests | The system shall allow Administrators to adjust ticket priority (LOW, MEDIUM, HIGH, URGENT). | Must Have |
| **FR-10** | View Assigned Requests | The system shall allow Maintenance Staff to view requests assigned only to them. | Must Have |
| **FR-11** | Update Request Status | The system shall allow Maintenance Staff to transition assigned requests (ASSIGNED -> IN_PROGRESS -> RESOLVED). | Must Have |
| **FR-12** | Resolution Notes | The system shall require Maintenance Staff to enter resolution notes (min 5 chars) to set a ticket to RESOLVED. | Must Have |
| **FR-13** | User Management | The system shall allow Administrators to list and delete user accounts. | Should Have |
| **FR-14** | Basic Dashboard | The system shall display aggregated statistics of requests on Admin and Staff dashboards. | Should Have |
| **FR-15** | Secure Logout | The system shall allow users to terminate their active sessions securely. | Must Have |

---

### 7. Non-Functional Requirements (NFR)

| Req ID | Category | Specification |
|---|---|---|
| **NFR-01** | Performance | Web API requests shall respond within 3 seconds under typical loading parameters. |
| **NFR-02** | Security | Passwords must never be stored in plain text. Secure bcrypt hashing must be applied. |
| **NFR-03** | Authorization | Requesters and Maintenance Staff must be blocked from accessing unauthorized administrative actions (e.g. user deletion). |
| **NFR-04** | Usability | The user interface shall provide clean navigation, forms, empty states, and descriptive error alerts. |
| **NFR-05** | Responsiveness | The interface layout must scale properly across mobile, tablet, and desktop screens. |
| **NFR-06** | Maintainability | Code must utilize a modular, layered structure conforming to SOLID principles. |
| **NFR-07** | Availability | The cloud-deployed application must remain reachable through a public URL during examination auditing. |

---

### 8. User Roles & Capabilities
1. **REQUESTER:** Can Register, Login, Submit Requests, View Own Requests, View details, Close resolved requests, Logout.
2. **MAINTENANCE STAFF:** Can Login, View Assigned Requests, Update Status (Start work, Resolve), Add resolution notes, Logout.
3. **ADMINISTRATOR:** Can Login, View All Requests, Update Priority, Assign Tickets to Staff, List/Delete Users, View Dashboard stats, Logout.

---

### 9. Use Case Scenario: Submit and Assign Request
- **Precondition:** Requester is registered. Admin and Staff accounts are pre-seeded.
- **Flow:**
  1. Requester logs in, navigates to "Submit Request", chooses "Plumbing", fills location "Room 201", and submits.
  2. Status is initialized as `SUBMITTED`.
  3. Administrator logs in, views the dashboard, sees the new ticket, adjusts priority to `HIGH`, and selects `John Maintenance` from the staff list.
  4. Status transitions automatically to `ASSIGNED`.
  5. Maintenance Staff logs in, views their dashboard, clicks on the ticket, marks it as `IN_PROGRESS`.
  6. Upon completing repairs, Staff enters resolution notes and marks it as `RESOLVED`.
  7. Requester logs in, checks status, clicks "Close Request". Status transitions to `CLOSED`.

---

### 10. Constraints & Assumptions
- **Constraints:** Must be completed individually under exam timeline constraints. SQLite is mandated for the MVP, restricting database operations to a single node.
- **Assumptions:** Campus network is available. SQLite file locks will not bottleneck concurrent requests during grading.

---

### 11. Requirement Prioritization (MoSCoW)
- **Must Have:** Registration, Login, RBAC, Submit Ticket, View Own Tickets, Admin view, Assign Staff, Prioritize, Maintenance progression, Resolution notes, Database persistence.
- **Should Have:** Dashboard stats, search/filtering, user management (list/delete).
- **Could Have:** Email notifications, real-time WebSockets, CSV reporting.

---

### 12. Requirements Traceability Matrix (RTM)

This matrix maps functional requirements to design layers, implementation source files, and verifying test cases:

| Req ID | Functional Requirement | Design Component | Implementation Files | Test Case ID |
|---|---|---|---|---|
| **FR-01** | User Registration | Presentation / Logic | [auth.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/routes/auth.py), [user_service.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/services/user_service.py) | `tests/test_auth.py::test_user_registration` |
| **FR-02** | Secure Authentication | Presentation / Security | [auth.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/routes/auth.py), [auth_service.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/services/auth_service.py) | `tests/test_auth.py::test_user_login` |
| **FR-03** | Role-Based Access Control | Logic Middleware | [dependencies.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/dependencies.py) | `tests/test_security.py::test_role_escalation_admin_endpoints` |
| **FR-04** | Submit Service Request | Presentation / Logic | [requests.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/routes/requests.py), [request_service.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/services/request_service.py) | `tests/test_requests.py::test_request_creation_and_visibility` |
| **FR-05** | View Own Requests | Presentation / Repository | [requests.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/routes/requests.py), [request_repository.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/repositories/request_repository.py) | `tests/test_requests.py::test_request_creation_and_visibility` |
| **FR-06** | Track Request Status | Presentation / UI | [request_details.html](file:///Users/nurudeenmuniru/Desktop/CSRMS/frontend/request_details.html), [request.js](file:///Users/nurudeenmuniru/Desktop/CSRMS/frontend/js/request.js) | `tests/test_maintenance.py::test_maintenance_workflow` |
| **FR-07** | View All Requests | Presentation / Repository | [requests.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/routes/requests.py), [request_repository.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/repositories/request_repository.py) | `tests/test_admin.py::test_admin_assignment_and_prioritization` |
| **FR-08** | Assign Requests | Logic Service | [admin.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/routes/admin.py), [request_service.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/services/request_service.py) | `tests/test_admin.py::test_admin_assignment_and_prioritization` |
| **FR-09** | Prioritize Requests | Logic Service | [requests.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/routes/requests.py), [request_service.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/services/request_service.py) | `tests/test_admin.py::test_admin_assignment_and_prioritization` |
| **FR-10** | View Assigned Requests | Repository | [requests.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/routes/requests.py), [request_repository.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/repositories/request_repository.py) | `tests/test_maintenance.py::test_maintenance_workflow` |
| **FR-11** | Update Request Status | Logic Service | [requests.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/routes/requests.py), [request_service.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/services/request_service.py) | `tests/test_maintenance.py::test_maintenance_workflow` |
| **FR-12** | Resolution Notes | Validation Logic | [request_service.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/services/request_service.py) | `tests/test_maintenance.py::test_maintenance_workflow` |
| **FR-13** | User Management | Admin Presentation | [admin.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/routes/admin.py), [user_service.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/services/user_service.py) | `tests/test_admin.py::test_admin_user_deletion` |
| **FR-14** | Basic Dashboard | Presentation Statistics | [admin.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/routes/admin.py), [maintenance.py](file:///Users/nurudeenmuniru/Desktop/CSRMS/app/routes/maintenance.py) | `tests/test_admin.py::test_admin_dashboard_stats` |
| **FR-15** | Secure Logout | Client UI / Persistence | [api.js](file:///Users/nurudeenmuniru/Desktop/CSRMS/frontend/js/api.js), [auth.js](file:///Users/nurudeenmuniru/Desktop/CSRMS/frontend/js/auth.js) | Manual Usability Checklist |

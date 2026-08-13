# Campus Service Request Management System (CSRMS)

An MSc-level Advanced Software Engineering project implementing a web-based platform for managing campus maintenance and service requests.

---

## 1. Project Overview
The Campus Service Request Management System (CSRMS) is a centralized web platform designed to streamline campus service request lifecycles. It enables campus members (Requesters) to report maintenance, plumbing, electrical, and other service issues; permits Administrators to prioritize and assign requests to Maintenance Staff; and allows Maintenance Staff to progress, update, and resolve work orders.

## 2. Problem Statement
Campus service and maintenance problems are frequently reported through informal, unstructured channels (e.g., verbal notifications, WhatsApp, emails), leading to:
- Absence of systematic tracking and audit logs.
- Inability to prioritize critical safety and security issues.
- Lack of accountability and feedback loops for requesters.
- Poor visibility for campus administrators to assess response time and staff workloads.

## 3. Objectives
1. **Secure Registration & Auth:** Role-based access control (RBAC) separating Requesters, Admins, and Maintenance Staff.
2. **End-to-End Workflow:** Requests move through a structured state machine (`SUBMITTED` -> `ASSIGNED` -> `IN_PROGRESS` -> `RESOLVED` -> `CLOSED`).
3. **Admin Dashboard:** Central view for prioritization, assignment, and basic analytics.
4. **Maintenance Workflow:** Interface for assigned staff to update status and submit resolution details.
5. **Quality Assurance:** Unit, integration, and security test suites verifying behavior and preventing role escalation.

## 4. Features
- **Authentication:** Password hashing (bcrypt) and JWT-based session persistence.
- **Requester Workspace:** Submit requests with categories ("Electrical", "Plumbing", etc.), location, and detailed descriptions; view self-submitted requests.
- **Admin Workspace:** View all service requests, re-assign tickets, adjust priority levels (`LOW`, `MEDIUM`, `HIGH`, `URGENT`), and view statistical metrics.
- **Maintenance Workspace:** Interactive workbench showing only requests assigned to the logged-in staff member, with actions to update progress and add resolution notes.
- **Audit Trails:** Automatic timestamps (`created_at`, `updated_at`) tracking request lifecycles.

## 5. Architecture
The system uses a strictly decoupled **Layered Architecture**:
```
          [ Presentation Layer ]  <-- HTML, CSS, JavaScript (Static Web App)
                    │
                    ▼
         [ Business Logic Layer ] <-- Services (Auth, User, Request Services)
                    │
                    ▼
          [ Data Access Layer ]   <-- Repositories (CRUD operations via SQLAlchemy)
                    │
                    ▼
             [ Database ]         <-- SQLite (Persistent storage)
```

## 6. Technology Stack
- **Backend Framework:** FastAPI (Python 3.9+)
- **Database Engine:** SQLite
- **ORM:** SQLAlchemy
- **Frontend:** Vanilla HTML5, CSS3, JavaScript (dynamic DOM rendering via Fetch API)
- **Security:** JWT Tokens, Passlib (Bcrypt)
- **Testing:** Pytest, HTTPX

## 7. Requirements
- Python 3.9 or higher
- Pip (Python Package Installer)

## 8. Installation
1. Clone the repository and navigate to the directory:
   ```bash
   cd CSRMS
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 9. Configuration
Environment-specific variables are defined in `app/config.py`. You can override them using environment variables:
- `SECRET_KEY`: Custom cryptographic key (default: `super-secret-exam-key`)
- `DATABASE_URL`: SQLAlchemy connection string (default: `sqlite:///./csrms.db`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration time (default: `60`)

## 10. Database Setup & Seeding
The database schema will automatically initialize on application startup. To pre-populate categories and default accounts, we provide an automatic seed script integrated into database initialization.

## 11. Running Locally
Start the local development server:
```bash
python -m uvicorn app.main:app --reload
```
Once started, access the application by opening:
[http://127.0.0.1:8000](http://127.0.0.1:8000)

## 12. Testing
Run the automated test suite covering unit, integration, and security checks:
```bash
pytest -v
```

## 13. Deployment
The application is pre-configured for simple cloud hosting environments like Render or Heroku.
For complete instructions, refer to [DEPLOYMENT_GUIDE.md](file:///Users/nurudeenmuniru/Desktop/CSRMS/docs/DEPLOYMENT_AND_USER_GUIDE.md).

## 14. User Roles
- **REQUESTER:** Submits and tracks requests.
- **ADMINISTRATOR:** Oversees assignment, priority management, and statistics.
- **MAINTENANCE:** Progresses and resolves assigned tasks.

## 15. Demo Accounts
The database is pre-seeded with the following credentials for testing:
- **Admin:** `admin@campus.edu` / `AdminPass123!`
- **Maintenance Staff:** `staff@campus.edu` / `StaffPass123!`
- **Requester:** `requester@campus.edu` / `RequesterPass123!`

## 16. Known Limitations
- SQLite is utilized for localized persistence. It is not recommended for highly concurrent multi-node writes.
- Stateless REST sessions are used. Direct browser-based cookie management is simulated via frontend token storage.

## 17. Technical Debt
Real technical debt has been deliberately and accidentally identified and documented, including lack of SMS/email notification systems, simplified single-assigned models, and lack of historical assignment logs. Refer to [TECHNICAL_DEBT.md](file:///Users/nurudeenmuniru/Desktop/CSRMS/docs/TECHNICAL_DEBT.md) for details.

## 18. Future Improvements
- Migration to PostgreSQL for production environments.
- Integration of SMTP mail server for auto-notifications.
- Real-time updates via WebSockets.

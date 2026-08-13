# System Design & UML Diagrams
## Campus Service Request Management System (CSRMS)

This document provides system design diagrams representing the architecture, database schema, use cases, and workflows implemented in the CSRMS project.

---

### 1. Use Case Diagram
This diagram outlines the interactions between our three actors (Requester, Administrator, and Maintenance Staff) and the core use cases.

```mermaid
usecaseDiagram
    rect "Campus Service Request Management System (CSRMS)"
        usecase UC_Register "Register Account"
        usecase UC_Login "Login Authentication"
        usecase UC_Submit "Submit Service Request"
        usecase UC_ViewOwn "View Personal Requests"
        usecase UC_Close "Close Resolved Request"
        usecase UC_ViewAll "View All Campus Requests"
        usecase UC_Assign "Assign Staff to Request"
        usecase UC_Prioritize "Prioritize Request"
        usecase UC_DeleteUser "Delete User Account"
        usecase UC_Stats "View Dashboard Stats"
        usecase UC_ViewAssigned "View Assigned Tasks"
        usecase UC_Progress "Update Progress (In Progress)"
        usecase UC_Resolve "Resolve Request (with Notes)"
    end

    actor Requester
    actor Administrator
    actor "Maintenance Staff" as Staff

    Requester --> UC_Register
    Requester --> UC_Login
    Requester --> UC_Submit
    Requester --> UC_ViewOwn
    Requester --> UC_Close

    Administrator --> UC_Login
    Administrator --> UC_ViewAll
    Administrator --> UC_Assign
    Administrator --> UC_Prioritize
    Administrator --> UC_DeleteUser
    Administrator --> UC_Stats

    Staff --> UC_Login
    Staff --> UC_ViewAssigned
    Staff --> UC_Progress
    Staff --> UC_Resolve
```

---

### 2. Activity Diagram (Submit Service Request)
The following activity diagram traces the workflow of a Requester submitting a maintenance ticket:

```mermaid
stateDiagram-v2
    [*] --> Start
    Start --> NavigateToPortal : Access CSRMS Portal
    NavigateToPortal --> LoggedInCheck : Check if Authenticated
    
    state LoggedInCheck <<choice>>
    LoggedInCheck --> LoginPage : No Token
    LoggedInCheck --> Dashboard : Has Token
    
    LoginPage --> Authenticate : Submit Email & Password
    Authenticate --> Dashboard : Success
    
    Dashboard --> ClickSubmit : Click 'Submit Service Request'
    ClickSubmit --> RenderForm : Request Categories
    RenderForm --> LoadCategoriesDropdown : API fetch /api/requests/categories
    LoadCategoriesDropdown --> InputData : Fill Subject, Location, Priority & Description
    InputData --> ValidateForm : Click Submit
    
    state ValidateForm <<choice>>
    ValidateForm --> ShowError : Input Invalid (Title < 5 chars, Description < 10)
    ValidateForm --> SendAPIRequest : Input Valid
    
    ShowError --> InputData
    
    SendAPIRequest --> DatabaseInsert : POST /api/requests/
    DatabaseInsert --> RenderSuccess : Save Record & Seed Status 'SUBMITTED'
    RenderSuccess --> RedirectDashboard : Redirect
    RedirectDashboard --> [*]
```

---

### 3. Sequence Diagram (Request Creation & Assignment Flow)
This diagram illustrates the message passing sequence across the Presentation, Logic, and Data layers when a Requester submits a request and an Admin assigns it to staff.

```mermaid
sequenceDiagram
    autonumber
    actor R as Requester
    actor A as Admin
    participant UI as Web UI (Javascript)
    participant AP as API Router (requests.py)
    participant RS as Request Service (request_service.py)
    participant RR as Request Repository (request_repository.py)
    participant DB as SQLite DB

    %% Submit Request Flow
    Note over R,DB: Phase A: Requester Submits Request
    R->>UI: Fills Form & Clicks Submit
    UI->>AP: POST /api/requests/ (JSON Body + JWT Token)
    activate AP
    AP->>RS: create_request(db, request_data, requester_id)
    activate RS
    RS->>RS: Validate Category ID
    RS->>RR: create(db, request_data, requester_id)
    activate RR
    RR->>DB: INSERT INTO service_requests (status='SUBMITTED')
    DB-->>RR: Return db_request (id=1)
    RR-->>RS: return db_request
    deactivate RR
    RS-->>AP: return db_request
    deactivate RS
    AP-->>UI: 201 Created (JSON Response)
    deactivate AP
    UI-->>R: Display success message & reload table

    %% Admin Assignment Flow
    Note over A,DB: Phase B: Admin Assigns Staff member
    A->>UI: Selects John Maintenance & Clicks Save
    UI->>AP: PUT /api/requests/1 (JSON: {assigned_to: 2})
    activate AP
    AP->>RS: update_request(db, 1, update_data, admin_user)
    activate RS
    RS->>RS: Validate assignee has MAINTENANCE role
    RS->>RS: Set status = 'ASSIGNED'
    RS->>RR: update(db, db_request, {assigned_to: 2, status: 'ASSIGNED'})
    activate RR
    RR->>DB: UPDATE service_requests SET assigned_to=2, status='ASSIGNED'
    DB-->>RR: Confirm update
    RR-->>RS: return updated db_request
    deactivate RR
    RS-->>AP: return updated db_request
    deactivate RS
    AP-->>UI: 200 OK (JSON Response)
    deactivate AP
    UI-->>A: Refresh details & status badge
```

---

### 4. Class Diagram
The class diagram represents the structure of our core business objects, services, repositories, and relationship mappings.

```mermaid
classDiagram
    class User {
        +int id
        +str name
        +str email
        +str password_hash
        +str role
        +datetime created_at
    }

    class Category {
        +int id
        +str name
        +str description
    }

    class ServiceRequest {
        +int id
        +str title
        +str description
        +str location
        +str priority
        +str status
        +datetime created_at
        +datetime updated_at
        +int requester_id
        +int category_id
        +int assigned_to
        +str resolution_notes
    }

    class UserRepository {
        +get_by_id(db, id) User
        +get_by_email(db, email) User
        +get_all(db, role) List
        +create(db, user_data, hash) User
        +delete(db, user) void
    }

    class RequestRepository {
        +get_by_id(db, id) ServiceRequest
        +get_all(db, requester_id, assigned_to, status, priority, category_id) List
        +create(db, request_data, requester_id) ServiceRequest
        +update(db, db_request, update_data) ServiceRequest
    }

    class RequestService {
        +create_request(db, request_data, requester_id) ServiceRequest
        +get_request(db, id) ServiceRequest
        +get_requests_for_user(db, user_id, role, status, priority, category) List
        +update_request(db, id, update_data, current_user) ServiceRequest
    }

    User "1" --> "0..*" ServiceRequest : submits (requester_id)
    User "1" --> "0..*" ServiceRequest : assigned_to (assignee)
    Category "1" --> "0..*" ServiceRequest : classifies (category_id)
    RequestService ..> RequestRepository : uses
    RequestService ..> UserRepository : uses
```

---

### 5. Entity-Relationship (ER) Diagram
This diagram outlines the physical database schema, data types, indexes, and constraints implemented in SQLite.

```mermaid
erDiagram
    users {
        int id PK
        string name "not null"
        string email "unique, indexed, not null"
        string password_hash "not null"
        string role "not null"
        datetime created_at
    }

    categories {
        int id PK
        string name "unique, indexed, not null"
        string description
    }

    service_requests {
        int id PK
        string title "not null"
        text description "not null"
        string location "not null"
        string priority "not null"
        string status "not null"
        datetime created_at
        datetime updated_at
        int requester_id FK "not null"
        int category_id FK "not null"
        int assigned_to FK "nullable"
        text resolution_notes "nullable"
    }

    users ||--o{ service_requests : "submits (requester_id)"
    users ||--o{ service_requests : "receives assignment (assigned_to)"
    categories ||--o{ service_requests : "classifies (category_id)"
```

---

### 6. Layered Architecture Diagram
This diagram shows the structural layers of our application code, mapping the code modules to their layer boundary responsibilities.

```mermaid
graph TD
    subgraph Presentation Layer [Presentation Layer: Web Clients]
        HTML[HTML5 Layouts: login, dashboard, request_details]
        CSS[CSS Stylesheet: Custom HSL Grid system]
        JS[Javascript Actions: api.js, auth.js, dashboard.js]
    end

    subgraph Service Layer [Business Logic Layer: Services]
        RouterAuth[auth.py APIRouter]
        RouterReq[requests.py APIRouter]
        RouterAdmin[admin.py APIRouter]
        
        AuthService[AuthService: bcrypt hashes, jwt keys]
        UserService[UserService: unique emails registration]
        RequestService[RequestService: RBAC transitions state validation]
    end

    subgraph Access Layer [Data Access Layer: Repositories]
        UR[UserRepository]
        RR[RequestRepository]
        CR[CategoryRepository]
    end

    subgraph Data Layer [Database Layer: SQLite]
        DB[(csrms.db File)]
    end

    %% Dependencies flow
    HTML --> JS
    JS -->|HTTP Requests| RouterAuth
    JS -->|HTTP Requests| RouterReq
    JS -->|HTTP Requests| RouterAdmin

    RouterAuth --> AuthService
    RouterAuth --> UserService
    RouterReq --> RequestService
    RouterAdmin --> RequestService
    RouterAdmin --> UserService

    UserService --> UR
    RequestService --> RR
    RequestService --> UR
    RequestService --> CR

    UR --> DB
    RR --> DB
    CR --> DB
```

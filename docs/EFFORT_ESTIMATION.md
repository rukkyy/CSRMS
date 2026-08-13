# Software Effort Estimation & Work Breakdown Structure (WBS)
## Campus Service Request Management System (CSRMS)

---

### 1. Work Breakdown Structure (WBS)
The project is structured into 11 main work packages, decomposed into concrete sub-tasks:

1. **Requirements & Planning**
   - 1.1 Stakeholder consultation and domain analysis
   - 1.2 Objective definition and scoping
   - 1.3 Technology stack selection and validation
2. **SRS Documentation**
   - 2.1 Writing functional and non-functional specifications
   - 2.2 Constructing the Requirements Traceability Matrix (RTM)
3. **System Design (Architecture & UML)**
   - 3.1 Designing layered presentation-logic-data-access architecture
   - 3.2 Drawing UML diagrams (Use Case, Activity, Sequence, Class, ERD, Architecture)
4. **Database & UI Design**
   - 4.1 Creating SQLAlchemy schemas and mapping models
   - 4.2 Formulating modern CSS layout grid styles and color tokens
5. **Authentication and Users**
   - 5.1 Implementing Passlib password hashing and verify services
   - 5.2 Building JWT creation and verify logic (PyJWT)
   - 5.3 Developing login, registration, and logout API routes
6. **Service Request Management**
   - 6.1 Creating ticket submission schema and CRUD repository functions
   - 6.2 Writing business logic rules in `RequestService`
   - 6.3 Creating HTML interfaces for ticket creation and my-requests tables
7. **Administration**
   - 7.1 Creating admin control APIs for assignments and prioritization updates
   - 7.2 Building user management endpoints (listing staff, deleting accounts)
8. **Dashboard & Statistics**
   - 8.1 Constructing administrative counts query groupings
   - 8.2 Building dynamic DOM renderers showing user stats metrics
9. **Testing & Refinement**
   - 9.1 Configuring Pytest fixtures and mock database overrides
   - 9.2 Writing unit, integration, and role escalation security tests
   - 9.3 Executing tests, fixing NameErrors and OperationalErrors
10. **Deployment**
    - 10.1 Structuring Render-ready configurations (`requirements.txt`, uvicorn binds)
    - 10.2 Documenting environment variables and local run procedures
11. **Technical Debt & Maintenance Planning**
    - 11.1 Classifying deliberate and accidental debt register rows
    - 11.2 Compiling the Maintenance strategy plan and Final Exam Report

---

### 2. Three-Point PERT Estimation
We employ the standard program evaluation and review technique (PERT) formula to determine the expected effort ($E$) for each task:

$$E = \frac{O + 4M + P}{6}$$

Where:
- **$O$ (Optimistic):** Minimum execution duration assuming zero complications.
- **$M$ (Most Likely):** Standard execution duration under ordinary conditions.
- **$P$ (Pessimistic):** Maximum execution duration assuming environment setup, package mismatch, or lock issues.

---

### 3. PERT Calculation Table

Below is the calculation breakdown for each WBS task group:

| Task Name | $O$ (h) | $M$ (h) | $P$ (h) | Calculation | Expected Effort $E$ (h) |
|---|---|---|---|---|---|
| **1. Requirements & Planning** | 1.00 | 1.25 | 1.50 | $(1 + 5.0 + 1.5)/6$ | 1.25 |
| **2. SRS Documentation** | 0.75 | 1.25 | 1.75 | $(0.75 + 5.0 + 1.75)/6$ | 1.25 |
| **3. Architecture + UML** | 0.75 | 1.25 | 1.75 | $(0.75 + 5.0 + 1.75)/6$ | 1.25 |
| **4. Database + UI Design** | 0.75 | 1.25 | 1.75 | $(0.75 + 5.0 + 1.75)/6$ | 1.25 |
| **5. Authentication** | 1.50 | 2.00 | 2.50 | $(1.50 + 8.0 + 2.50)/6$ | 2.00 |
| **6. Service Request Func.** | 2.00 | 3.00 | 4.00 | $(2.00 + 12.0 + 4.00)/6$ | 3.00 |
| **7. Admin Assignment & Status**| 1.50 | 2.50 | 3.50 | $(1.50 + 10.0 + 3.50)/6$ | 2.50 |
| **8. Dashboard** | 0.75 | 1.25 | 1.75 | $(0.75 + 5.0 + 1.75)/6$ | 1.25 |
| **9. Testing & Refinement** | 1.50 | 2.00 | 2.50 | $(1.50 + 8.0 + 2.50)/6$ | 2.00 |
| **10. Deployment** | 0.75 | 1.25 | 1.75 | $(0.75 + 5.0 + 1.75)/6$ | 1.25 |
| **11. Documentation** | 1.50 | 2.50 | 3.50 | $(1.50 + 10.0 + 3.50)/6$ | 2.50 |
| **12. Tech Debt & Maintenance** | 0.50 | 0.75 | 1.00 | $(0.50 + 3.0 + 1.00)/6$ | 0.75 |
| **TOTAL EXPECTED TIME** | **13.25** | **20.25** | **27.25** | **PERT Formula Sum** | **20.25 person-hours** |

---

### 4. Contingency and Buffers
To manage risks associated with individual student delivery constraints, we calculate a standard statistical buffer:
- **Standard Deviation ($\sigma$)** per task: $\sigma = (P - O) / 6$.
- **Project Variance ($V$):** Sum of individual task variances.
  - $\sigma_{\text{typical}} = (1.75 - 0.75)/6 = 0.167$.
  - Sum of variances: approximately $0.45$.
- **Contingency Buffer (15%):** We add a 15% contingency reserve (approximately **3.0 hours**) to the 20.25 expected hours, bringing the planned maximum timeline allocation to **23.25 hours**.

---

### 5. Scope vs. Estimation Analysis
1. **Time Constraint Impact:** The strictly bounded timeline (approx. 20 hours) dictates the exclusion of lower-priority features:
   - *SMTP Email & SMS integration:* Dropped (could compromised MVP delivery if external API keys block grading).
   - *Real-time WebSocket alerts:* Shifted to Version 3 (reduces concurrency test risks).
   - *Advanced PDF generation:* Moved to Version 2 (reduces backend dependency footprint).
2. **Estimation Assumptions:**
   - Single-node developer environment (no distributed team overhead).
   - Python environment dependencies do not conflict with system packages.
   - The user has direct write/read environment command execution access.

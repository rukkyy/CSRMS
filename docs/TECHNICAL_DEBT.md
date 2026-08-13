# Technical Debt Register
## Campus Service Request Management System (CSRMS)

---

### 1. Conceptual Framework
In software engineering, **Technical Debt** is a metaphor representing the future cost of additional refactoring, validation, or infrastructure migration incurred by choosing an expedient design path today.

Technical debt is not inherently negative. In academic examinations or startup contexts, introducing **Deliberate Technical Debt** is a strategic engineering trade-off: it allows developers to meet strict deadlines by prioritizing core MVP functionality (e.g. state transitions) over operational complexity (e.g., configuring multi-node databases or SMS gateways).

We distinguish:
- **Deliberate Technical Debt:** Conscious design decisions made to fit within the 20-hour timeline constraint.
- **Accidental Technical Debt:** Sub-optimal code structures or gaps discovered during development or testing (e.g. SQLite connection pool limits).

---

### 2. Technical Debt Register

Below is the structured registry of technical debt identified in the CSRMS application:

| Debt ID | Classification | Description | Cause / Context | Impact | Severity | Priority | Risk | Resolution Strategy | Future Effort | Timeframe |
|---|---|---|---|---|---|---|---|---|---|---|
| **TD-DB-001** | Deliberate | SQLite chosen over PostgreSQL. | Avoid operational setup complexity during grading. | Read/write lock delays; cannot scale horizontally. | Medium | Medium | Low | Refactor `app/database.py` connection to bind to PostgreSQL. | 3 hours | Version 2.0 |
| **TD-AUT-002**| Deliberate | LocalStorage session token persistence. | Simplifies vanilla JavaScript fetch configurations. | Vulnerable to Cross-Site Scripting (XSS). | High | High | Medium | Migrate JWT storage to Secure HTTPOnly Cookies. | 4 hours | Version 2.0 |
| **TD-NTF-003**| Deliberate | Absence of SMS/Email alerts. | API keys and mail servers configuration limits. | Requesters must log in manually to check progress. | Low | High | Low | Integrate SendGrid SMTP and Twilio SMS packages. | 6 hours | Version 2.0 |
| **TD-AUD-004**| Deliberate | No assignment history audit trail. | Simplified database schema model for MVP. | Admins cannot track who previously worked on a ticket. | Low | Medium | Low | Create `AssignmentAudit` table with foreign key logs. | 3 hours | Version 2.5 |
| **TD-QA-005** | Accidental | No automated E2E frontend tests. | Limited timeline for UI testing frameworks. | UI changes must be verified manually by grading team. | Medium | Low | Low | Install Cypress or Selenium test suites. | 5 hours | Version 3.0 |
| **TD-RT-006** | Deliberate | No real-time dashboard updates. | Complexities of WebSockets under SQLite. | Users must reload browser to view status changes. | Low | Low | Low | Integrate FastAPI WebSockets with Redis Pub/Sub. | 8 hours | Version 3.0 |

---

### 3. Management Strategy
The mitigation of this register is scheduled sequentially as part of the post-release roadmap. The priority is **TD-AUT-002** (Security) followed by **TD-DB-001** (Infrastructure Scaling). Deliberate technical debt will be resolved during the perfective maintenance phase of the software lifecycle.

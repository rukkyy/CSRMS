# Deployment & User Guide
## Campus Service Request Management System (CSRMS)

---

## PART I: DEPLOYMENT GUIDE

### 1. Local Development Setup
1. **Clone the repository:**
   ```bash
   cd CSRMS
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```
4. **Access the interface:**
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your web browser.

---

### 2. Production Configuration

#### Environment Variables
The application reads settings from environment variables. Configure these keys on your cloud provider:

| Variable Name | Description | Default Value | Recommendation |
|---|---|---|---|
| `SECRET_KEY` | Symmetric cryptographic key for JWT signing | `super-secret-exam-key...` | Generate a long random string |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./csrms.db` | Production Postgres database link |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token validity lifetime | `60` | `60` |

#### Startup Bind Command
For production deployment, run the server using Uvicorn or Gunicorn with Uvicorn workers:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
Or with multiple workers for scaling:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

---

### 3. Deploying to Render
1. Create a new account at [Render](https://render.com).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository containing the CSRMS code.
4. Set the following details:
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Click **Advanced** and add the environment variables listed in Section 2 above.
6. Click **Deploy Web Service**.

#### Health Check Verification
To verify the deployment is active, query the health endpoint:
- URL: `https://[your-service-subdomain].onrender.com/health`
- Expected response: `{"status":"healthy","service":"CSRMS"}`

---

## PART II: USER MANUAL

### 1. Requester Workflow
* **Registration:** Open `/register`, fill in your name, campus email, password, and click **Create Account**.
* **Submit request:**
  1. Log in at `/login`.
  2. Click **+ Submit Service Request** in the top right.
  3. Fills in title, location, category (dropdown), priority, description, and click **Submit Ticket**.
* **View & Track:** Your submitted request appears on your dashboard table. Click the title link to view details.
* **Close Request:** When maintenance staff resolves your ticket, status becomes `RESOLVED`. Click on it and click the blue **Close Request** button to transition it to `CLOSED`.

---

### 2. Administrator Workflow
* **Log In:** Use pre-seeded email `admin@campus.edu` and password `AdminPass123!`.
* **Dashboard Overview:** View card metrics showing total requests and totals grouped by status.
* **Assign & Prioritize:**
  1. Click on a ticket title in the dashboard requests table.
  2. In the right-hand **Management Operations** panel, select a staff member from the **Assign Staff** dropdown.
  3. Adjust the priority dropdown (e.g. LOW to URGENT).
  4. Choose status (e.g. ASSIGNED).
  5. Click **Save Changes**. The page reloads, updating the record.

---

### 3. Maintenance Staff Workflow
* **Log In:** Use pre-seeded email `staff@campus.edu` and password `StaffPass123!`.
* **View Assignments:** The dashboard table displays requests assigned exclusively to you.
* **Update Status:**
  1. Click on an assigned request link.
  2. Under **Management Operations** on the right, click **Start Work**. Status transitions to `IN_PROGRESS`.
  3. Once repairs are complete, return to the details page.
  4. Write a descriptive summary (minimum 5 characters) in the **Resolution Notes** text area.
  5. Click **Resolve Issue**. The status changes to `RESOLVED` and resolution details are made visible to the Requester.

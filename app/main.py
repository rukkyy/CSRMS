import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import seed_database
from app.routes import auth, requests, admin, maintenance

app = FastAPI(
    title="Campus Service Request Management System (CSRMS)",
    description="MSc Advanced Software Engineering End-of-Semester Project",
    version="1.0.0"
)

# Enable CORS for development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(requests.router)
app.include_router(admin.router)
app.include_router(maintenance.router)

# Seed database on startup
@app.on_event("startup")
def startup_event():
    seed_database()

# Get the absolute path to the frontend directory
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")

# Mount CSS & JS subdirectories statically
app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")

# Clean URL Routing for HTML frontend files
@app.get("/", response_class=HTMLResponse)
def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/login", response_class=HTMLResponse)
def read_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/register", response_class=HTMLResponse)
def read_register():
    return FileResponse(os.path.join(FRONTEND_DIR, "register.html"))

@app.get("/dashboard", response_class=HTMLResponse)
def read_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))

@app.get("/request/create", response_class=HTMLResponse)
def read_request_create():
    return FileResponse(os.path.join(FRONTEND_DIR, "request_create.html"))

@app.get("/request/details", response_class=HTMLResponse)
def read_request_details():
    return FileResponse(os.path.join(FRONTEND_DIR, "request_details.html"))

# Global health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "CSRMS"}

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.seed import seed_database
from app.models import User, Student, Recruiter, Job, Application

# Setup an isolated in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        # Seed initial admin and demo data
        seed_database(db=db)
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ==========================================
# 1. REGISTRATION TESTS
# ==========================================
def test_student_registration(client):
    payload = {
        "role": "STUDENT",
        "name": "Jane Doe",
        "email": "jane.doe@university.edu",
        "password": "Password@123",
        "college": "MIT",
        "degree": "B.S.",
        "branch": "Computer Science",
        "cgpa": 9.2,
        "skills": ["Python", "FastAPI", "React"]
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "STUDENT"
    assert data["user"]["name"] == "Jane Doe"
    assert data["user"]["email"] == "jane.doe@university.edu"
    assert data["user"]["student_profile"]["cgpa"] == 9.2
    assert "Python" in data["user"]["student_profile"]["skills"]


def test_recruiter_registration(client):
    payload = {
        "role": "RECRUITER",
        "name": "John Recruiter",
        "email": "john@globaltech.com",
        "password": "Password@123",
        "company_name": "Global Tech Corp",
        "company_email": "hr@globaltech.com"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "RECRUITER"
    assert data["user"]["recruiter_profile"]["company_name"] == "Global Tech Corp"


def test_admin_registration_rejected(client):
    payload = {
        "role": "ADMIN",
        "name": "Hacker Admin",
        "email": "fakeadmin@placement.edu",
        "password": "Password@123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert "ADMIN is not permitted" in response.json()["detail"]


def test_duplicate_email_registration(client):
    payload = {
        "role": "STUDENT",
        "name": "Dhanush Duplicate",
        "email": "dhanush@college.edu",  # already seeded
        "password": "Password@123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


# ==========================================
# 2. LOGIN TESTS
# ==========================================
def test_login_success(client):
    payload = {
        "email": "dhanush@college.edu",
        "password": "Student@123"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "STUDENT"
    assert data["user"]["email"] == "dhanush@college.edu"


def test_login_invalid_password(client):
    payload = {
        "email": "dhanush@college.edu",
        "password": "WrongPassword!"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_nonexistent_user(client):
    payload = {
        "email": "nonexistent@college.edu",
        "password": "Student@123"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


# ==========================================
# 3. JWT & CURRENT USER (ME) TESTS
# ==========================================
def test_current_user_me_authenticated(client):
    # Log in first
    login_res = client.post("/api/auth/login", json={
        "email": "admin@placement.edu",
        "password": "Admin@123"
    })
    token = login_res.json()["access_token"]

    # Call /api/auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "admin@placement.edu"
    assert me_res.json()["role"] == "ADMIN"


def test_protected_endpoint_missing_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_protected_endpoint_invalid_token(client):
    headers = {"Authorization": "Bearer this_is_an_invalid_token"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401


# ==========================================
# 4. ROLE-BASED ACCESS CONTROL TESTS
# ==========================================
def test_student_role_authorization(client):
    # Login as student
    student_token = client.post("/api/auth/login", json={
        "email": "dhanush@college.edu",
        "password": "Student@123"
    }).json()["access_token"]

    # Login as recruiter
    recruiter_token = client.post("/api/auth/login", json={
        "email": "recruiter@technova.com",
        "password": "Recruiter@123"
    }).json()["access_token"]

    # Get a job ID
    jobs = client.get("/api/jobs").json()
    job_id = jobs[0]["id"]

    # 1. Student can apply
    res = client.post(
        "/api/applications",
        json={"job_id": job_id},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert res.status_code in [200, 201]

    # 2. Recruiter CANNOT apply as student (403 Forbidden)
    res_forbidden = client.post(
        "/api/applications",
        json={"job_id": job_id},
        headers={"Authorization": f"Bearer {recruiter_token}"}
    )
    assert res_forbidden.status_code == 403


def test_recruiter_role_authorization(client):
    # Login as student
    student_token = client.post("/api/auth/login", json={
        "email": "dhanush@college.edu",
        "password": "Student@123"
    }).json()["access_token"]

    # Login as recruiter
    recruiter_token = client.post("/api/auth/login", json={
        "email": "recruiter@technova.com",
        "password": "Recruiter@123"
    }).json()["access_token"]

    new_job_payload = {
        "title": "Senior Cloud Architect",
        "description": "Lead multi-cloud architecture and DevOps practices.",
        "salary": "18 LPA",
        "location": "Bangalore / Hybrid",
        "skills": ["AWS", "Terraform", "Kubernetes"]
    }

    # 1. Recruiter can create job
    res = client.post(
        "/api/jobs",
        json=new_job_payload,
        headers={"Authorization": f"Bearer {recruiter_token}"}
    )
    assert res.status_code == 201
    assert res.json()["title"] == "Senior Cloud Architect"

    # 2. Student CANNOT create job (403 Forbidden)
    res_forbidden = client.post(
        "/api/jobs",
        json=new_job_payload,
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert res_forbidden.status_code == 403


def test_admin_role_authorization(client):
    # Login as student
    student_token = client.post("/api/auth/login", json={
        "email": "dhanush@college.edu",
        "password": "Student@123"
    }).json()["access_token"]

    # Login as recruiter
    recruiter_token = client.post("/api/auth/login", json={
        "email": "recruiter@technova.com",
        "password": "Recruiter@123"
    }).json()["access_token"]

    # Login as admin
    admin_token = client.post("/api/auth/login", json={
        "email": "admin@placement.edu",
        "password": "Admin@123"
    }).json()["access_token"]

    # 1. Admin can access stats
    res_admin = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    assert "total_students" in res_admin.json()
    assert "total_jobs" in res_admin.json()

    # 2. Student is rejected from admin stats (403 Forbidden)
    res_student = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {student_token}"})
    assert res_student.status_code == 403

    # 3. Recruiter is rejected from admin stats (403 Forbidden)
    res_recruiter = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {recruiter_token}"})
    assert res_recruiter.status_code == 403

    # 4. Unauthenticated is rejected (401 Unauthorized)
    res_anon = client.get("/api/admin/stats")
    assert res_anon.status_code == 401

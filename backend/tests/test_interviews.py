import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app, broadcast
from app.database import Base, get_db
from app.seed import seed_database
from app.models import User, Student, Recruiter, Job, Application, Interview

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

def get_tokens(client):
    admin_tok = client.post("/api/auth/login", json={"email": "admin@placement.edu", "password": "Admin@123"}).json()["access_token"]
    student_tok = client.post("/api/auth/login", json={"email": "dhanush@college.edu", "password": "Student@123"}).json()["access_token"]
    recruiter_abc = client.post("/api/auth/login", json={"email": "recruiter@abc.com", "password": "Recruiter@123"}).json()["access_token"]
    recruiter_technova = client.post("/api/auth/login", json={"email": "recruiter@technova.com", "password": "Recruiter@123"}).json()["access_token"]
    return {
        "admin": admin_tok,
        "student": student_tok,
        "recruiter_abc": recruiter_abc,
        "recruiter_technova": recruiter_technova,
    }


# ==========================================
# 1. CREATE INTERVIEW TESTS
# ==========================================
def test_create_interview_as_recruiter(client):
    tokens = get_tokens(client)
    apps = client.get("/api/applications", headers={"Authorization": f"Bearer {tokens['recruiter_abc']}"}).json()
    assert len(apps) >= 1
    app_id = apps[0]["id"]

    sched_time = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    payload = {
        "application_id": app_id,
        "scheduled_at": sched_time,
        "mode": "ONLINE",
        "meeting_link": "https://meet.google.com/test-recruiter-abc",
        "notes": "First round technical interview"
    }

    res = client.post("/api/interviews", json=payload, headers={"Authorization": f"Bearer {tokens['recruiter_abc']}"})
    assert res.status_code == 201
    data = res.json()
    assert data["application_id"] == app_id
    assert data["mode"] == "ONLINE"
    assert data["status"] == "SCHEDULED"
    assert data["meeting_link"] == "https://meet.google.com/test-recruiter-abc"


def test_create_interview_as_admin(client):
    tokens = get_tokens(client)
    apps = client.get("/api/applications", headers={"Authorization": f"Bearer {tokens['admin']}"}).json()
    assert len(apps) >= 1
    app_id = apps[0]["id"]

    sched_time = (datetime.now(timezone.utc) + timedelta(days=4)).isoformat()
    payload = {
        "application_id": app_id,
        "scheduled_at": sched_time,
        "mode": "HYBRID",
        "location": "Placement Cell, Hall A",
        "meeting_link": "https://meet.google.com/admin-scheduled",
        "notes": "Administrative round"
    }

    res = client.post("/api/interviews", json=payload, headers={"Authorization": f"Bearer {tokens['admin']}"})
    assert res.status_code == 201
    assert res.json()["mode"] == "HYBRID"
    assert res.json()["status"] == "SCHEDULED"


def test_student_cannot_create_interview(client):
    tokens = get_tokens(client)
    sched_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    payload = {
        "application_id": 1,
        "scheduled_at": sched_time,
        "mode": "ONLINE"
    }
    res = client.post("/api/interviews", json=payload, headers={"Authorization": f"Bearer {tokens['student']}"})
    assert res.status_code == 403


def test_recruiter_cannot_access_another_recruiters_application(client):
    tokens = get_tokens(client)
    # Get TechNova's application
    technova_apps = client.get("/api/applications", headers={"Authorization": f"Bearer {tokens['recruiter_technova']}"}).json()
    assert len(technova_apps) >= 1
    technova_app_id = technova_apps[0]["id"]

    # Recruiter ABC tries to schedule interview for TechNova's application
    sched_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    payload = {
        "application_id": technova_app_id,
        "scheduled_at": sched_time,
        "mode": "ONLINE"
    }
    res = client.post("/api/interviews", json=payload, headers={"Authorization": f"Bearer {tokens['recruiter_abc']}"})
    assert res.status_code == 403
    assert "another recruiter's application" in res.json()["detail"]


# ==========================================
# 2. GET INTERVIEWS & ROLE FILTERING
# ==========================================
def test_student_sees_only_own_interviews(client):
    tokens = get_tokens(client)
    res = client.get("/api/interviews", headers={"Authorization": f"Bearer {tokens['student']}"})
    assert res.status_code == 200
    interviews = res.json()
    assert isinstance(interviews, list)
    for i in interviews:
        assert i["student_name"] == "Dhanush"


def test_recruiter_sees_only_their_interviews(client):
    tokens = get_tokens(client)
    res = client.get("/api/interviews", headers={"Authorization": f"Bearer {tokens['recruiter_abc']}"})
    assert res.status_code == 200
    for i in res.json():
        assert "ABC Technologies" in i["company"]


def test_admin_sees_all_interviews(client):
    tokens = get_tokens(client)
    res = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {tokens['admin']}"})
    assert res.status_code == 200
    stats = res.json()
    assert "total_interviews" in stats
    assert "scheduled_interviews" in stats

    interviews_res = client.get("/api/interviews", headers={"Authorization": f"Bearer {tokens['admin']}"})
    assert interviews_res.status_code == 200
    assert len(interviews_res.json()) >= 1


# ==========================================
# 3. UPDATE & CANCEL INTERVIEW TESTS
# ==========================================
def test_update_interview(client):
    tokens = get_tokens(client)
    interviews = client.get("/api/interviews", headers={"Authorization": f"Bearer {tokens['admin']}"}).json()
    assert len(interviews) >= 1
    interview_id = interviews[0]["id"]

    patch_payload = {
        "mode": "OFFLINE",
        "location": "Main Auditorium, Room 102",
        "notes": "Updated to in-person technical panel"
    }
    res = client.patch(f"/api/interviews/{interview_id}", json=patch_payload, headers={"Authorization": f"Bearer {tokens['admin']}"})
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "OFFLINE"
    assert data["location"] == "Main Auditorium, Room 102"


def test_cancel_interview(client):
    tokens = get_tokens(client)
    interviews = client.get("/api/interviews", headers={"Authorization": f"Bearer {tokens['admin']}"}).json()
    assert len(interviews) >= 1
    interview_id = interviews[0]["id"]

    patch_payload = {"status": "CANCELLED"}
    res = client.patch(f"/api/interviews/{interview_id}", json=patch_payload, headers={"Authorization": f"Bearer {tokens['admin']}"})
    assert res.status_code == 200
    assert res.json()["status"] == "CANCELLED"


# ==========================================
# 4. WORKFLOW TRANSITIONS & VALIDATION
# ==========================================
def test_invalid_status_transition(client):
    tokens = get_tokens(client)
    # An application in APPLIED status attempting to transition directly to SELECTED is invalid
    # APPLIED can only go to UNDER_REVIEW or REJECTED
    apps = client.get("/api/applications", headers={"Authorization": f"Bearer {tokens['admin']}"}).json()
    applied_app = next((a for a in apps if a["status"] == "APPLIED"), None)
    if not applied_app:
        # Create one
        job_id = client.get("/api/jobs").json()[0]["id"]
        # register new student
        new_student = client.post("/api/auth/register", json={
            "role": "STUDENT", "name": "Fresh Student", "email": "fresh@campus.edu", "password": "Password@123"
        }).json()
        new_app = client.post("/api/applications", json={"job_id": job_id}, headers={"Authorization": f"Bearer {new_student['access_token']}"}).json()
        app_id = new_app["id"]
    else:
        app_id = applied_app["id"]

    # Try invalid transition from APPLIED -> SELECTED
    bad_transition = client.patch(
        f"/api/applications/{app_id}",
        json={"status": "SELECTED"},
        headers={"Authorization": f"Bearer {tokens['admin']}"}
    )
    assert bad_transition.status_code == 400
    assert "Invalid status transition" in bad_transition.json()["detail"]


def test_interview_not_found(client):
    tokens = get_tokens(client)
    res = client.get("/api/interviews/999999", headers={"Authorization": f"Bearer {tokens['admin']}"})
    assert res.status_code == 404

    patch_res = client.patch("/api/interviews/999999", json={"status": "COMPLETED"}, headers={"Authorization": f"Bearer {tokens['admin']}"})
    assert patch_res.status_code == 404


# ==========================================
# 5. WEBSOCKET BROADCAST VERIFICATION
# ==========================================
def test_websocket_event_generation(client):
    tokens = get_tokens(client)
    apps = client.get("/api/applications", headers={"Authorization": f"Bearer {tokens['admin']}"}).json()
    app_id = apps[0]["id"]

    sched_time = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    payload = {
        "application_id": app_id,
        "scheduled_at": sched_time,
        "mode": "ONLINE",
        "meeting_link": "https://meet.google.com/ws-test"
    }

    with patch("app.main.broadcast", new_callable=AsyncMock) as mock_broadcast:
        res = client.post("/api/interviews", json=payload, headers={"Authorization": f"Bearer {tokens['admin']}"})
        assert res.status_code == 201
        assert mock_broadcast.called
        # Check event structure
        called_args = mock_broadcast.call_args[0][0]
        assert called_args["type"] == "INTERVIEW_SCHEDULED"
        assert "interview_id" in called_args["data"]
        assert called_args["data"]["meeting_link"] == "https://meet.google.com/ws-test"

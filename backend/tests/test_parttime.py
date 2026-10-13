import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.seed import seed_database
from app.database import Base, engine

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    seed_database()

def test_parttime_jobs_hourly_compensation():
    with TestClient(app) as client:
        res = client.get("/api/jobs")
        assert res.status_code == 200
        jobs = res.json()
        assert len(jobs) >= 8
        # Ensure all jobs have hourly/shift compensation and no "LPA"
        for j in jobs:
            assert "LPA" not in j["salary"]
            assert "₹" in j["salary"]
            assert j["job_type"] in ["Part-time", "Weekend-only", "Evening shifts", "Flexible", "Remote", "Freelance", "Temporary"]

def test_search_and_filters():
    with TestClient(app) as client:
        # Search by keyword
        res = client.get("/api/jobs?q=Frontend")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1
        assert "Frontend" in data[0]["title"]

        # Filter by category
        res = client.get("/api/jobs?category=Online%20Tutoring")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1
        assert data[0]["category"] == "Online Tutoring"

        # Filter by shift
        res = client.get("/api/jobs?shift_schedule=Weekends")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1

def test_student_saved_jobs_lifecycle():
    with TestClient(app) as client:
        # Login as student
        login_res = client.post("/api/auth/login", json={"email": "dhanush@college.edu", "password": "Student@123"})
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get jobs
        jobs = client.get("/api/jobs", headers=headers).json()
        job_id = jobs[0]["id"]

        # Save job
        save_res = client.post(f"/api/jobs/{job_id}/save", headers=headers)
        assert save_res.status_code == 200

        # Verify in saved-jobs list
        saved_list = client.get("/api/saved-jobs", headers=headers).json()
        saved_ids = [s["job_id"] for s in saved_list]
        assert job_id in saved_ids

        # Unsave job
        unsave_res = client.delete(f"/api/jobs/{job_id}/save", headers=headers)
        assert unsave_res.status_code == 200

def test_work_shifts_and_notifications():
    with TestClient(app) as client:
        login_res = client.post("/api/auth/login", json={"email": "dhanush@college.edu", "password": "Student@123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Check student shifts
        shifts_res = client.get("/api/shifts", headers=headers)
        assert shifts_res.status_code == 200
        shifts = shifts_res.json()
        assert len(shifts) >= 1
        assert shifts[0]["status"] in ["SCHEDULED", "COMPLETED"]

        # Check notifications
        notif_res = client.get("/api/notifications", headers=headers)
        assert notif_res.status_code == 200
        notifs_data = notif_res.json()
        assert "notifications" in notifs_data
        assert len(notifs_data["notifications"]) >= 1

        # Mark all read
        mark_res = client.post("/api/notifications/read-all", headers=headers)
        assert mark_res.status_code == 200

def test_job_reporting_and_admin_moderation():
    with TestClient(app) as client:
        # Student logs in and reports a job
        std_login = client.post("/api/auth/login", json={"email": "dhanush@college.edu", "password": "Student@123"})
        std_headers = {"Authorization": f"Bearer {std_login.json()['access_token']}"}

        jobs = client.get("/api/jobs").json()
        target_job = jobs[-1]

        report_res = client.post(f"/api/jobs/{target_job['id']}/report", json={
            "reason": "Misleading compensation",
            "details": "Checking compensation details test"
        }, headers=std_headers)
        assert report_res.status_code == 200
        report_id = report_res.json()["id"]

        # Admin logs in and inspects report
        admin_login = client.post("/api/auth/login", json={"email": "admin@placement.edu", "password": "Admin@123"})
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

        reports_list = client.get("/api/admin/reports", headers=admin_headers).json()
        assert any(r["id"] == report_id for r in reports_list)

        # Admin resolves report
        action_res = client.patch(f"/api/admin/reports/{report_id}?action=DISMISSED", headers=admin_headers)
        assert action_res.status_code == 200

def test_delete_job_and_status_filtering():
    with TestClient(app) as client:
        # Recruiter logs in
        rec_login = client.post("/api/auth/login", json={"email": "recruiter@technova.com", "password": "Recruiter@123"})
        rec_token = rec_login.json()["access_token"]
        rec_headers = {"Authorization": f"Bearer {rec_token}"}

        # Create a test gig
        create_res = client.post("/api/jobs", json={
            "title": "Temp Delete Gig",
            "category": "Web Development",
            "pay_rate": "₹350/hr",
            "skills": ["Python"]
        }, headers=rec_headers)
        assert create_res.status_code == 201
        new_job_id = create_res.json()["id"]

        # Pause job
        pause_res = client.patch(f"/api/jobs/{new_job_id}/status?status_str=PAUSED", headers=rec_headers)
        assert pause_res.status_code == 200
        assert pause_res.json()["status"] == "PAUSED"

        # Check filter with status=PAUSED
        paused_jobs = client.get("/api/jobs?status=PAUSED", headers=rec_headers).json()
        assert any(j["id"] == new_job_id for j in paused_jobs)

        # Delete job
        del_res = client.delete(f"/api/jobs/{new_job_id}", headers=rec_headers)
        assert del_res.status_code == 200
        assert del_res.json()["status"] == "DELETED"


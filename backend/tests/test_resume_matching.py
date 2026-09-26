import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from pypdf import PdfWriter

from app.main import app
from app.database import Base, get_db
from app.seed import seed_database
from app.models import User, Student, Recruiter, Job, Application
from app.services.resume_parser import extract_skills, extract_text_from_pdf, parse_resume
from app.services.job_matcher import (
    calculate_job_match,
    remove_duplicate_skills,
    normalize_job_skills,
    normalize_skill_name
)

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
    recruiter_tok = client.post("/api/auth/login", json={"email": "recruiter@abc.com", "password": "Recruiter@123"}).json()["access_token"]
    return {
        "admin": admin_tok,
        "student": student_tok,
        "recruiter": recruiter_tok,
    }

def create_sample_pdf(text: str = "Experienced in Python, React, Docker, and PostgreSQL.") -> bytes:
    """Helper to generate a minimal valid PDF byte sequence."""
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


# ==========================================
# 1. UNIT TESTS: RESUME PARSER & JOB MATCHER
# ==========================================

def test_skill_extraction():
    """Verify controlled dictionary extraction for programming languages, frameworks, and tools."""
    sample_text = (
        "Software Engineer with experience in Python, FastAPI, React, and Node.js. "
        "Proficient with Docker, Kubernetes, AWS, and PostgreSQL. "
        "Also knowledgeable in C++, C, Git, and CI/CD pipelines."
    )
    detected = extract_skills(sample_text)
    
    assert "Python" in detected
    assert "FastAPI" in detected
    assert "React" in detected
    assert "Node.js" in detected
    assert "Docker" in detected
    assert "Kubernetes" in detected
    assert "AWS" in detected
    assert "PostgreSQL" in detected
    assert "C++" in detected
    assert "C" in detected
    assert "Git" in detected
    assert "CI/CD" in detected

def test_extract_skills_boundary_no_false_positives():
    """Ensure standalone 'C' is not falsely detected in words like 'CSS' or 'React'."""
    sample_text = "Specialized in CSS styles, React components, and accessing database records."
    detected = extract_skills(sample_text)
    
    assert "CSS" in detected
    assert "React" in detected
    assert "C" not in detected

def test_duplicate_skill_removal():
    """Verify case-insensitive duplicate skill removal."""
    raw_skills = ["Python", "python", "PYTHON", "Docker", "docker", "React", "react.js"]
    cleaned = remove_duplicate_skills(raw_skills)
    assert len(cleaned) == 3
    assert "Python" in cleaned
    assert "Docker" in cleaned
    assert "React" in cleaned

def test_job_skill_normalization():
    """Verify normalization of job required skills."""
    raw_skills = ["  Java  ", "SQL", "SQL", "  Docker ", "Spring Boot", "spring boot"]
    normalized = normalize_job_skills(raw_skills)
    assert len(normalized) == 4
    assert "Java" in normalized
    assert "SQL" in normalized
    assert "Docker" in normalized
    assert "Spring Boot" in normalized

def test_job_matching_100_percent():
    """Job matching calculation when candidate has all required skills."""
    req = ["Python", "Docker", "PostgreSQL"]
    cand = ["python", "docker", "postgresql", "react"]
    res = calculate_job_match(req, cand)
    assert res["match_percentage"] == 100
    assert len(res["matched_skills"]) == 3
    assert len(res["missing_skills"]) == 0

def test_job_matching_0_percent():
    """Job matching calculation when candidate has none of the required skills."""
    res = calculate_job_match(["Java", "Spring Boot"], ["Python", "React"])
    assert res["match_percentage"] == 0
    assert len(res["matched_skills"]) == 0
    assert len(res["missing_skills"]) == 2

def test_job_matching_partial():
    """Job matching calculation for partial matches."""
    # 2 out of 3 = 67%
    req = ["Python", "FastAPI", "Kubernetes"]
    cand = ["Python", "FastAPI"]
    res = calculate_job_match(req, cand)
    assert res["match_percentage"] == 67
    assert "Kubernetes" in res["missing_skills"]
    assert "Python" in res["matched_skills"]
    assert "FastAPI" in res["matched_skills"]

    # Empty required skills returns 100%
    assert calculate_job_match([], ["Python"])["match_percentage"] == 100


# ==========================================
# 2. INTEGRATION TESTS: STUDENT PROFILE & SKILLS
# ==========================================

def test_get_student_profile(client):
    tokens = get_tokens(client)
    res = client.get(
        "/api/students/profile",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "skills" in data
    assert "resume_url" in data
    assert "branch" in data
    assert "college" in data

def test_update_student_profile(client):
    tokens = get_tokens(client)
    update_data = {
        "branch": "Information Science",
        "cgpa": 9.2,
        "skills": ["Python", "React", "Docker", "FastAPI", "PostgreSQL"],
    }
    res = client.put(
        "/api/students/profile",
        json=update_data,
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["branch"] == "Information Science"
    assert data["cgpa"] == 9.2
    assert "Docker" in data["skills"]

def test_get_student_skills(client):
    tokens = get_tokens(client)
    res = client.get(
        "/api/students/skills",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data["skills"], list)


# ==========================================
# 3. INTEGRATION TESTS: RESUME UPLOAD & ACCESS
# ==========================================

def test_pdf_upload(client, monkeypatch):
    """Test successful PDF upload and skill extraction."""
    tokens = get_tokens(client)
    pdf_bytes = create_sample_pdf()
    
    def mock_extract(file_bytes):
        return "Experienced Python, React, Docker, and PostgreSQL developer with Git and AWS."

    from app.services import resume_parser
    monkeypatch.setattr(resume_parser, "extract_text_from_pdf", mock_extract)

    res = client.post(
        "/api/students/resume",
        headers={"Authorization": f"Bearer {tokens['student']}"},
        files={"file": ("dhanush_resume.pdf", pdf_bytes, "application/pdf")}
    )
    assert res.status_code == 200
    data = res.json()
    assert "resume_url" in data
    assert "detected_skills" in data
    assert "Python" in data["detected_skills"]
    assert "Docker" in data["detected_skills"]
    assert "React" in data["detected_skills"]
    assert "skills" in data

    # Verify student profile reflects updated skills
    prof = client.get("/api/students/profile", headers={"Authorization": f"Bearer {tokens['student']}"}).json()
    assert prof["resume_url"] == data["resume_url"]
    assert "Python" in prof["skills"]
    assert "Docker" in prof["skills"]

def test_invalid_file_type(client):
    """Reject non-PDF file formats."""
    tokens = get_tokens(client)
    res = client.post(
        "/api/students/resume",
        headers={"Authorization": f"Bearer {tokens['student']}"},
        files={"file": ("test.txt", b"plain text", "text/plain")}
    )
    assert res.status_code == 400
    assert "PDF" in res.json()["detail"]

def test_upload_resume_oversized_file(client):
    """Reject resumes exceeding 5MB limit."""
    tokens = get_tokens(client)
    large_data = b"%PDF-1.4 " + b"0" * (5 * 1024 * 1024 + 100)
    res = client.post(
        "/api/students/resume",
        headers={"Authorization": f"Bearer {tokens['student']}"},
        files={"file": ("large.pdf", large_data, "application/pdf")}
    )
    assert res.status_code == 400
    assert "5MB" in res.json()["detail"]

def test_student_resume_access(client, monkeypatch):
    """Test accessing/downloading an uploaded resume via the static/endpoint URL."""
    tokens = get_tokens(client)
    pdf_bytes = create_sample_pdf()
    
    from app.services import resume_parser
    monkeypatch.setattr(resume_parser, "extract_text_from_pdf", lambda b: "Python developer")

    upload_res = client.post(
        "/api/students/resume",
        headers={"Authorization": f"Bearer {tokens['student']}"},
        files={"file": ("my_resume.pdf", pdf_bytes, "application/pdf")}
    )
    assert upload_res.status_code == 200
    resume_url = upload_res.json()["resume_url"]

    # Fetch resume file with student authentication
    fetch_res = client.get(resume_url, headers={"Authorization": f"Bearer {tokens['student']}"})
    assert fetch_res.status_code == 200
    assert fetch_res.headers["content-type"] == "application/pdf"

def test_unauthorized_access(client):
    """Ensure recruiter or unauthenticated users cannot upload student resume."""
    tokens = get_tokens(client)
    pdf_data = create_sample_pdf()
    
    # Recruiter cannot upload to student resume endpoint
    res_recruiter = client.post(
        "/api/students/resume",
        headers={"Authorization": f"Bearer {tokens['recruiter']}"},
        files={"file": ("resume.pdf", pdf_data, "application/pdf")}
    )
    assert res_recruiter.status_code == 403

    # Unauthenticated cannot upload
    res_unauth = client.post(
        "/api/students/resume",
        files={"file": ("resume.pdf", pdf_data, "application/pdf")}
    )
    assert res_unauth.status_code == 401

    # Unauthenticated cannot access student profile
    res_prof_unauth = client.get("/api/students/profile")
    assert res_prof_unauth.status_code == 401


# ==========================================
# 4. INTEGRATION TESTS: MATCHING, RECOMMENDATIONS, RECRUITER
# ==========================================

def test_recommended_jobs(client):
    """Test recommended jobs endpoint returns openings sorted descending by match percentage."""
    tokens = get_tokens(client)
    
    client.put(
        "/api/students/profile",
        json={"skills": ["Python", "FastAPI", "Docker", "PostgreSQL"]},
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )

    res = client.get(
        "/api/jobs/recommended",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert res.status_code == 200
    jobs = res.json()
    assert len(jobs) > 0
    
    prev_pct = 101
    for j in jobs:
        assert "match_percentage" in j
        assert "matched_skills" in j
        assert "missing_skills" in j
        assert j["match_percentage"] <= prev_pct
        prev_pct = j["match_percentage"]

def test_job_details_with_student_match(client):
    """Test single job details includes match details when requested by student."""
    tokens = get_tokens(client)
    
    client.put(
        "/api/students/profile",
        json={"skills": ["Python", "FastAPI", "Docker"]},
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )

    res = client.get(
        "/api/jobs/1",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "match_percentage" in data
    assert "matched_skills" in data
    assert "missing_skills" in data

def test_recruiter_applicant_match_percentage(client):
    """Test recruiter applicant view displays match percentage and candidate skills alignment."""
    tokens = get_tokens(client)
    
    res = client.get(
        "/api/applications",
        headers={"Authorization": f"Bearer {tokens['recruiter']}"}
    )
    assert res.status_code == 200
    apps = res.json()
    assert len(apps) > 0
    app_data = apps[0]
    
    assert "match_percentage" in app_data
    assert "matched_skills" in app_data
    assert "missing_skills" in app_data
    assert "resume_url" in app_data
    assert "interview_status" in app_data

def test_admin_analytics_stats(client):
    """Test admin stats includes skill demand and match percentage analytics."""
    tokens = get_tokens(client)
    res = client.get(
        "/api/admin/stats",
        headers={"Authorization": f"Bearer {tokens['admin']}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "most_demanded_skills" in data
    assert isinstance(data["most_demanded_skills"], list)
    assert "average_job_match_percentage" in data
    assert isinstance(data["average_job_match_percentage"], (int, float))
    assert "total_resumes_uploaded" in data
    assert "total_students_with_resumes" in data

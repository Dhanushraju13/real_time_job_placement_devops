import os
import uuid
import logging
from contextlib import asynccontextmanager
from typing import List, Optional
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db, engine, Base
from app.models import User, Student, Recruiter, Job, Application, Interview, utcnow
from app.schemas import (
    RegisterRequest, LoginRequest, TokenResponse, UserResponse,
    JobCreate, JobResponse, ApplicationCreate, ApplicationStatusUpdate,
    ApplicationResponse, AdminStatsResponse, StudentProfileResponse, RecruiterProfileResponse,
    InterviewCreate, InterviewUpdate, InterviewResponse,
    StudentProfileView, StudentProfileUpdate, StudentSkillsResponse, ResumeUploadResponse
)
from app.auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, get_optional_current_user,
    require_student, require_recruiter, require_admin, require_recruiter_or_admin
)
from app.seed import seed_database
from app.services.resume_parser import parse_resume, extract_skills
from app.services.job_matcher import calculate_job_match

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("placement.api")

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "resumes")
os.makedirs(UPLOAD_DIR, exist_ok=True)

VALID_APPLICATION_STATUSES = [
    "APPLIED",
    "UNDER_REVIEW",
    "SHORTLISTED",
    "INTERVIEW",
    "SELECTED",
    "REJECTED"
]

VALID_APPLICATION_STATUS_TRANSITIONS = {
    "APPLIED": ["UNDER_REVIEW", "REJECTED"],
    "UNDER_REVIEW": ["SHORTLISTED", "REJECTED"],
    "SHORTLISTED": ["INTERVIEW", "REJECTED"],
    "INTERVIEW": ["SELECTED", "REJECTED"],
    "SELECTED": [],
    "REJECTED": []
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize schema, uploads folder, and seed demo data on startup
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        seed_database()
    except Exception as e:
        logger.error(f"Startup seed error: {e}")
    yield

app = FastAPI(
    title="Real-Time Placement API",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for cross-origin local development if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket clients
clients: list[WebSocket] = []

async def broadcast(message: dict):
    dead = []
    for ws in list(clients):
        try:
            await ws.send_json(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in clients:
            clients.remove(ws)

# Helper serialization functions
def build_user_response(user: User) -> dict:
    student_data = None
    if user.student_profile:
        std = user.student_profile
        student_data = {
            "id": std.id,
            "college": std.college,
            "degree": std.degree,
            "branch": std.branch,
            "cgpa": std.cgpa,
            "skills": std.skills or [],
            "resume_url": std.resume_url,
        }

    recruiter_data = None
    if user.recruiter_profile:
        rec = user.recruiter_profile
        recruiter_data = {
            "id": rec.id,
            "company_name": rec.company_name,
            "company_email": rec.company_email,
        }

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at,
        "student_profile": student_data,
        "recruiter_profile": recruiter_data,
    }

def format_job(job: Job, student_skills: Optional[List[str]] = None) -> dict:
    company_name = job.company
    if not company_name and job.recruiter:
        company_name = job.recruiter.company_name
    skills_list = job.skills if isinstance(job.skills, list) else ([job.skills] if job.skills else [])

    job_dict = {
        "id": job.id,
        "recruiter_id": job.recruiter_id,
        "title": job.title,
        "role": job.title,  # backward compatibility alias
        "company": company_name or "Partner Company",
        "description": job.description or "",
        "salary": job.salary or "",
        "package": job.salary or "",  # backward compatibility alias
        "location": job.location or "Remote",
        "skills": skills_list,
        "status": job.status,
        "created_at": job.created_at,
        "match_percentage": None,
        "matched_skills": None,
        "missing_skills": None,
    }

    if student_skills is not None:
        match_data = calculate_job_match(skills_list, student_skills, job_id=job.id)
        job_dict["match_percentage"] = match_data["match_percentage"]
        job_dict["matched_skills"] = match_data["matched_skills"]
        job_dict["missing_skills"] = match_data["missing_skills"]

    return job_dict

def format_application(app_item: Application, include_match: bool = True) -> dict:
    job = app_item.job
    student = app_item.student
    student_user = student.user if student else None

    company_name = job.company if job else ""
    if not company_name and job and job.recruiter:
        company_name = job.recruiter.company_name

    skills_list = student.skills if (student and isinstance(student.skills, list)) else []

    # Get latest interview status if any
    interview_status = None
    if app_item.interviews:
        sorted_interviews = sorted(app_item.interviews, key=lambda x: x.id, reverse=True)
        interview_status = sorted_interviews[0].status

    res = {
        "id": app_item.id,
        "job_id": app_item.job_id,
        "student_id": app_item.student_id,
        "status": app_item.status,
        "applied_at": app_item.applied_at,
        "student": student_user.name if student_user else "Student",  # backward compatibility alias
        "student_name": student_user.name if student_user else None,
        "student_email": student_user.email if student_user else None,
        "college": student.college if student else None,
        "degree": student.degree if student else None,
        "branch": student.branch if student else None,
        "cgpa": student.cgpa if student else None,
        "skills": skills_list,
        "job_title": job.title if job else None,
        "company": company_name,
        "salary": job.salary if job else None,
        "location": job.location if job else None,
        "resume_url": student.resume_url if student else None,
        "interview_status": interview_status,
        "match_percentage": None,
        "matched_skills": None,
        "missing_skills": None,
    }

    if include_match and job:
        match_data = calculate_job_match(job.skills, skills_list, job_id=job.id)
        res["match_percentage"] = match_data["match_percentage"]
        res["matched_skills"] = match_data["matched_skills"]
        res["missing_skills"] = match_data["missing_skills"]

    return res

def format_interview(interview: Interview) -> dict:
    app_item = interview.application
    job = app_item.job if app_item else None
    student = app_item.student if app_item else None
    student_user = student.user if student else None

    company_name = job.company if job else ""
    if not company_name and job and job.recruiter:
        company_name = job.recruiter.company_name

    return {
        "id": interview.id,
        "application_id": interview.application_id,
        "scheduled_at": interview.scheduled_at,
        "mode": interview.mode,
        "meeting_link": interview.meeting_link,
        "location": interview.location,
        "status": interview.status,
        "notes": interview.notes,
        "created_at": interview.created_at,
        "job_id": job.id if job else None,
        "job_title": job.title if job else None,
        "salary": job.salary if job else None,
        "package": job.salary if job else None,
        "student_id": student.id if student else None,
        "student_name": student_user.name if student_user else None,
        "student_email": student_user.email if student_user else None,
        "college": student.college if student else None,
        "degree": student.degree if student else None,
        "branch": student.branch if student else None,
        "cgpa": student.cgpa if student else None,
        "recruiter_id": job.recruiter_id if job else None,
        "company": company_name or "Company",
        "company_name": company_name or "Company",
    }

# ==========================================
# HEALTH ENDPOINTS
# ==========================================
@app.get("/health", tags=["Health"])
@app.get("/api/health", include_in_schema=False)
def health():
    return {"status": "UP", "service": "placement-api"}

# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================
@app.post("/api/auth/register", response_model=TokenResponse, tags=["Authentication"])
@app.post("/auth/register", response_model=TokenResponse, include_in_schema=False)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    role_clean = payload.role.strip().upper()

    # Reject ADMIN registration
    if role_clean == "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Public registration as ADMIN is not permitted"
        )

    if role_clean not in ["STUDENT", "RECRUITER"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be STUDENT or RECRUITER"
        )

    email_clean = payload.email.strip().lower()
    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create User
    new_user = User(
        name=payload.name.strip(),
        email=email_clean,
        password_hash=hash_password(payload.password),
        role=role_clean
    )
    db.add(new_user)
    db.flush()

    # Create associated profile
    if role_clean == "STUDENT":
        skills_clean = []
        if isinstance(payload.skills, list):
            skills_clean = [s.strip() for s in payload.skills if s.strip()]
        elif isinstance(payload.skills, str):
            skills_clean = [s.strip() for s in payload.skills.split(",") if s.strip()]

        student_profile = Student(
            user_id=new_user.id,
            college=payload.college.strip() if payload.college else None,
            degree=payload.degree.strip() if payload.degree else None,
            branch=payload.branch.strip() if payload.branch else None,
            cgpa=payload.cgpa,
            skills=skills_clean,
            resume_url=payload.resume_url.strip() if payload.resume_url else None
        )
        db.add(student_profile)
    elif role_clean == "RECRUITER":
        company = payload.company_name.strip() if payload.company_name else f"{payload.name}'s Company"
        recruiter_profile = Recruiter(
            user_id=new_user.id,
            company_name=company,
            company_email=payload.company_email.strip() if payload.company_email else email_clean
        )
        db.add(recruiter_profile)

    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role, "email": new_user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": new_user.role,
        "user": build_user_response(new_user)
    }

@app.post("/api/auth/login", response_model=TokenResponse, tags=["Authentication"])
@app.post("/auth/login", response_model=TokenResponse, include_in_schema=False)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(data={"sub": str(user.id), "role": user.role, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "user": build_user_response(user)
    }

@app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication"])
@app.get("/auth/me", response_model=UserResponse, include_in_schema=False)
def get_me(current_user: User = Depends(get_current_user)):
    return build_user_response(current_user)

# ==========================================
# STUDENT RESUME & PROFILE ENDPOINTS
# ==========================================
@app.post("/api/students/resume", response_model=ResumeUploadResponse, tags=["Students"])
@app.post("/students/resume", response_model=ResumeUploadResponse, include_in_schema=False)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = current_user.student_profile
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")

    filename = file.filename or "resume.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF resume documents are supported"
        )

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 5MB upload limit"
        )

    if not content.startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF file: corrupted or non-PDF header"
        )

    # Save to safe upload directory
    unique_suffix = uuid.uuid4().hex[:8]
    safe_filename = f"resume_{student.id}_{unique_suffix}.pdf"
    target_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(target_path, "wb") as f:
        f.write(content)

    # Parse resume and detect skills
    try:
        parse_result = parse_resume(content)
        detected_skills = parse_result["skills"]
    except Exception as e:
        logger.warning(f"Error parsing resume PDF text: {e}")
        detected_skills = []

    # Merge detected skills with student's existing skills
    existing_skills = student.skills if isinstance(student.skills, list) else []
    merged_skills = sorted(list(set(existing_skills) | set(detected_skills)))

    student.skills = merged_skills
    student.resume_url = f"/api/uploads/resumes/{safe_filename}"
    db.commit()
    db.refresh(student)

    return {
        "resume_url": student.resume_url,
        "filename": safe_filename,
        "uploaded_at": utcnow(),
        "detected_skills": detected_skills,
        "skills": student.skills
    }

@app.get("/api/uploads/resumes/{filename}", tags=["Students"])
@app.get("/uploads/resumes/{filename}", include_in_schema=False)
def get_uploaded_resume(filename: str):
    safe_name = os.path.basename(filename)
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume file not found")
    return FileResponse(file_path, media_type="application/pdf", filename=safe_name)

@app.get("/api/students/profile", response_model=StudentProfileView, tags=["Students"])
@app.get("/students/profile", response_model=StudentProfileView, include_in_schema=False)
def get_student_profile(current_user: User = Depends(require_student)):
    student = current_user.student_profile
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")

    return {
        "id": student.id,
        "name": current_user.name,
        "email": current_user.email,
        "college": student.college,
        "degree": student.degree,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "skills": student.skills or [],
        "resume_url": student.resume_url,
    }

@app.put("/api/students/profile", response_model=StudentProfileView, tags=["Students"])
@app.put("/students/profile", response_model=StudentProfileView, include_in_schema=False)
def update_student_profile(
    payload: StudentProfileUpdate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = current_user.student_profile
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")

    if payload.name is not None and payload.name.strip():
        current_user.name = payload.name.strip()
    if payload.college is not None:
        student.college = payload.college.strip()
    if payload.degree is not None:
        student.degree = payload.degree.strip()
    if payload.branch is not None:
        student.branch = payload.branch.strip()
    if payload.cgpa is not None:
        student.cgpa = payload.cgpa
    if payload.skills is not None:
        if isinstance(payload.skills, list):
            student.skills = sorted(list(set([s.strip() for s in payload.skills if s.strip()])))
        elif isinstance(payload.skills, str):
            student.skills = sorted(list(set([s.strip() for s in payload.skills.split(",") if s.strip()])))

    db.commit()
    db.refresh(student)
    db.refresh(current_user)

    return {
        "id": student.id,
        "name": current_user.name,
        "email": current_user.email,
        "college": student.college,
        "degree": student.degree,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "skills": student.skills or [],
        "resume_url": student.resume_url,
    }

@app.get("/api/students/skills", response_model=StudentSkillsResponse, tags=["Students"])
@app.get("/students/skills", response_model=StudentSkillsResponse, include_in_schema=False)
def get_student_skills(current_user: User = Depends(require_student)):
    student = current_user.student_profile
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")
    return {"skills": student.skills or []}

# ==========================================
# JOBS & MATCHING ENDPOINTS
# ==========================================
@app.get("/api/jobs/recommended", response_model=List[JobResponse], tags=["Jobs"])
@app.get("/jobs/recommended", response_model=List[JobResponse], include_in_schema=False)
def get_recommended_jobs(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = current_user.student_profile
    student_skills = student.skills if (student and isinstance(student.skills, list)) else []

    jobs = db.query(Job).filter(Job.status == "ACTIVE").all()
    enriched = [format_job(j, student_skills=student_skills) for j in jobs]

    # Sort descending by match_percentage, then by id
    enriched.sort(key=lambda x: (x["match_percentage"] or 0, x["id"]), reverse=True)
    return enriched

@app.get("/api/jobs", response_model=List[JobResponse], tags=["Jobs"])
@app.get("/jobs", response_model=List[JobResponse], include_in_schema=False)
def get_jobs(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).order_by(Job.id.desc()).all()
    student_skills = None
    if current_user and current_user.role == "STUDENT" and current_user.student_profile:
        student_skills = current_user.student_profile.skills

    return [format_job(j, student_skills=student_skills) for j in jobs]

@app.get("/api/jobs/{job_id}", response_model=JobResponse, tags=["Jobs"])
@app.get("/jobs/{job_id}", response_model=JobResponse, include_in_schema=False)
def get_job(
    job_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    student_skills = None
    if current_user and current_user.role == "STUDENT" and current_user.student_profile:
        student_skills = current_user.student_profile.skills

    return format_job(job, student_skills=student_skills)

@app.post("/api/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED, tags=["Jobs"])
@app.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_job(
    payload: JobCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    if current_user and current_user.role == "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: students cannot create job postings"
        )

    title_val = payload.title or payload.role or "Software Engineer"
    salary_val = payload.salary or payload.package or "Competitive"

    recruiter_id = None
    company_name = payload.company

    if current_user:
        if current_user.recruiter_profile:
            recruiter_id = current_user.recruiter_profile.id
            if not company_name:
                company_name = current_user.recruiter_profile.company_name
        elif current_user.role == "ADMIN":
            company_name = payload.company or "Admin Featured"
    else:
        recruiter = db.query(Recruiter).first()
        if recruiter:
            recruiter_id = recruiter.id
            if not company_name:
                company_name = recruiter.company_name

    # Validate and normalize skills
    skills_list = []
    if isinstance(payload.skills, list):
        skills_list = [s.strip() for s in payload.skills if s.strip()]
    elif isinstance(payload.skills, str):
        skills_list = [s.strip() for s in payload.skills.split(",") if s.strip()]
    skills_list = sorted(list(set(skills_list)))

    new_job = Job(
        recruiter_id=recruiter_id,
        title=title_val,
        company=company_name or "Enterprise Partner",
        description=payload.description or "",
        salary=salary_val,
        location=payload.location or "Remote",
        skills=skills_list,
        status="ACTIVE"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    formatted = format_job(new_job)
    await broadcast({"type": "NEW_JOB", "data": formatted})
    return formatted

# ==========================================
# APPLICATIONS ENDPOINTS
# ==========================================
@app.get("/api/applications", response_model=List[ApplicationResponse], tags=["Applications"])
@app.get("/applications", response_model=List[ApplicationResponse], include_in_schema=False)
def get_applications(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Application)

    if current_user:
        if current_user.role == "STUDENT" and current_user.student_profile:
            query = query.filter(Application.student_id == current_user.student_profile.id)
        elif current_user.role == "RECRUITER" and current_user.recruiter_profile:
            query = query.join(Job).filter(Job.recruiter_id == current_user.recruiter_profile.id)

    apps = query.order_by(Application.id.desc()).all()
    return [format_application(a, include_match=True) for a in apps]

@app.post("/api/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED, tags=["Applications"])
@app.post("/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_application(
    payload: ApplicationCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = current_user.student_profile
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found for this user")

    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing_app = db.query(Application).filter(
        Application.job_id == payload.job_id,
        Application.student_id == student.id
    ).first()

    if existing_app:
        return format_application(existing_app)

    new_app = Application(
        job_id=job.id,
        student_id=student.id,
        status="APPLIED"
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    formatted = format_application(new_app)
    await broadcast({"type": "NEW_APPLICATION", "data": formatted})
    return formatted

@app.patch("/api/applications/{application_id}", response_model=ApplicationResponse, tags=["Applications"])
@app.patch("/applications/{application_id}", response_model=ApplicationResponse, include_in_schema=False)
async def update_application(
    application_id: int,
    payload: ApplicationStatusUpdate,
    current_user: User = Depends(require_recruiter_or_admin),
    db: Session = Depends(get_db)
):
    app_item = db.query(Application).filter(Application.id == application_id).first()
    if not app_item:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user.role == "RECRUITER":
        if not current_user.recruiter_profile or app_item.job.recruiter_id != current_user.recruiter_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Recruiter cannot modify application belonging to another recruiter's job"
            )

    target_status = payload.status.strip().upper()
    if target_status not in VALID_APPLICATION_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{payload.status}'. Allowed: {', '.join(VALID_APPLICATION_STATUSES)}"
        )

    current_status = app_item.status.strip().upper()
    if target_status != current_status:
        allowed_next = VALID_APPLICATION_STATUS_TRANSITIONS.get(current_status, [])
        if target_status not in allowed_next:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from '{current_status}' to '{target_status}'"
            )

    app_item.status = target_status
    db.commit()
    db.refresh(app_item)

    formatted = format_application(app_item)
    await broadcast({"type": "APPLICATION_STATUS", "data": formatted})
    return formatted

# ==========================================
# INTERVIEW MANAGEMENT ENDPOINTS
# ==========================================
@app.post("/api/interviews", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED, tags=["Interviews"])
@app.post("/interviews", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_interview(
    payload: InterviewCreate,
    current_user: User = Depends(require_recruiter_or_admin),
    db: Session = Depends(get_db)
):
    app_item = db.query(Application).filter(Application.id == payload.application_id).first()
    if not app_item:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user.role == "RECRUITER":
        if not current_user.recruiter_profile or app_item.job.recruiter_id != current_user.recruiter_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Recruiter cannot schedule interview for another recruiter's application"
            )

    mode_clean = payload.mode.strip().upper()
    if mode_clean not in ["ONLINE", "OFFLINE", "HYBRID"]:
        raise HTTPException(status_code=400, detail="Interview mode must be ONLINE, OFFLINE, or HYBRID")

    if app_item.status in ["APPLIED", "UNDER_REVIEW", "SHORTLISTED"]:
        app_item.status = "INTERVIEW"
        db.commit()
        db.refresh(app_item)
        await broadcast({"type": "APPLICATION_STATUS", "data": format_application(app_item)})

    new_interview = Interview(
        application_id=app_item.id,
        scheduled_at=payload.scheduled_at,
        mode=mode_clean,
        meeting_link=payload.meeting_link.strip() if payload.meeting_link else None,
        location=payload.location.strip() if payload.location else None,
        status="SCHEDULED",
        notes=payload.notes.strip() if payload.notes else None,
        created_at=utcnow()
    )
    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)

    formatted = format_interview(new_interview)

    company_name = app_item.job.company or (app_item.job.recruiter.company_name if app_item.job.recruiter else "Company")
    ws_event = {
        "type": "INTERVIEW_SCHEDULED",
        "data": {
            "interview_id": new_interview.id,
            "application_id": app_item.id,
            "student_id": app_item.student_id,
            "job_title": app_item.job.title,
            "company": company_name,
            "scheduled_at": new_interview.scheduled_at.isoformat(),
            "mode": new_interview.mode,
            "meeting_link": new_interview.meeting_link,
            "location": new_interview.location,
            "status": new_interview.status
        }
    }
    await broadcast(ws_event)
    return formatted

@app.get("/api/interviews", response_model=List[InterviewResponse], tags=["Interviews"])
@app.get("/interviews", response_model=List[InterviewResponse], include_in_schema=False)
def get_interviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Interview).join(Application)

    if current_user.role == "STUDENT":
        if not current_user.student_profile:
            return []
        query = query.filter(Application.student_id == current_user.student_profile.id)
    elif current_user.role == "RECRUITER":
        if not current_user.recruiter_profile:
            return []
        query = query.join(Job).filter(Job.recruiter_id == current_user.recruiter_profile.id)

    interviews = query.order_by(Interview.scheduled_at.asc()).all()
    return [format_interview(i) for i in interviews]

@app.get("/api/interviews/{interview_id}", response_model=InterviewResponse, tags=["Interviews"])
@app.get("/interviews/{interview_id}", response_model=InterviewResponse, include_in_schema=False)
def get_interview_detail(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    app_item = interview.application
    if current_user.role == "STUDENT":
        if not current_user.student_profile or app_item.student_id != current_user.student_profile.id:
            raise HTTPException(status_code=403, detail="Access forbidden: cannot view another student's interview")
    elif current_user.role == "RECRUITER":
        if not current_user.recruiter_profile or app_item.job.recruiter_id != current_user.recruiter_profile.id:
            raise HTTPException(status_code=403, detail="Access forbidden: cannot view interview for another recruiter's job")

    return format_interview(interview)

@app.patch("/api/interviews/{interview_id}", response_model=InterviewResponse, tags=["Interviews"])
@app.patch("/interviews/{interview_id}", response_model=InterviewResponse, include_in_schema=False)
async def update_interview(
    interview_id: int,
    payload: InterviewUpdate,
    current_user: User = Depends(require_recruiter_or_admin),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    if current_user.role == "RECRUITER":
        if not current_user.recruiter_profile or interview.application.job.recruiter_id != current_user.recruiter_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Recruiter cannot modify interview belonging to another recruiter's job"
            )

    if payload.status:
        st_clean = payload.status.strip().upper()
        if st_clean not in ["SCHEDULED", "COMPLETED", "CANCELLED"]:
            raise HTTPException(status_code=400, detail="Status must be SCHEDULED, COMPLETED, or CANCELLED")
        interview.status = st_clean

    if payload.mode:
        m_clean = payload.mode.strip().upper()
        if m_clean not in ["ONLINE", "OFFLINE", "HYBRID"]:
            raise HTTPException(status_code=400, detail="Mode must be ONLINE, OFFLINE, or HYBRID")
        interview.mode = m_clean

    if payload.scheduled_at is not None:
        interview.scheduled_at = payload.scheduled_at
    if payload.meeting_link is not None:
        interview.meeting_link = payload.meeting_link.strip() if payload.meeting_link else None
    if payload.location is not None:
        interview.location = payload.location.strip() if payload.location else None
    if payload.notes is not None:
        interview.notes = payload.notes.strip() if payload.notes else None

    db.commit()
    db.refresh(interview)

    formatted = format_interview(interview)
    event_type = "INTERVIEW_CANCELLED" if interview.status == "CANCELLED" else "INTERVIEW_UPDATED"
    await broadcast({"type": event_type, "data": formatted})
    return formatted

@app.delete("/api/interviews/{interview_id}", tags=["Interviews"])
@app.delete("/interviews/{interview_id}", include_in_schema=False)
async def delete_interview(
    interview_id: int,
    current_user: User = Depends(require_recruiter_or_admin),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    if current_user.role == "RECRUITER":
        if not current_user.recruiter_profile or interview.application.job.recruiter_id != current_user.recruiter_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Recruiter cannot delete interview belonging to another recruiter's job"
            )

    formatted = format_interview(interview)
    db.delete(interview)
    db.commit()

    await broadcast({"type": "INTERVIEW_CANCELLED", "data": formatted})
    return {"message": f"Interview {interview_id} deleted successfully"}

# ==========================================
# ADMIN ENDPOINTS
# ==========================================
@app.get("/api/admin/stats", response_model=AdminStatsResponse, tags=["Admin"])
@app.get("/admin/stats", response_model=AdminStatsResponse, include_in_schema=False)
def get_admin_stats(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    total_students = db.query(Student).count()
    total_recruiters = db.query(Recruiter).count()
    total_jobs = db.query(Job).count()
    total_applications = db.query(Application).count()

    total_interviews = db.query(Interview).count()
    scheduled_interviews = db.query(Interview).filter(Interview.status == "SCHEDULED").count()
    completed_interviews = db.query(Interview).filter(Interview.status == "COMPLETED").count()
    cancelled_interviews = db.query(Interview).filter(Interview.status == "CANCELLED").count()

    # Skill Demand & Match Analytics
    active_jobs = db.query(Job).filter(Job.status == "ACTIVE").all()
    skill_counts = {}
    for j in active_jobs:
        for sk in (j.skills or []):
            if isinstance(sk, str) and sk.strip():
                clean_sk = sk.strip()
                skill_counts[clean_sk] = skill_counts.get(clean_sk, 0) + 1

    most_demanded_skills = sorted(
        [{"skill": k, "count": v} for k, v in skill_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:10]

    students = db.query(Student).all()
    total_students_with_resumes = sum(
        1 for s in students if s.resume_url and str(s.resume_url).strip()
    )
    total_resumes_uploaded = total_students_with_resumes

    total_pairs = 0
    sum_matches = 0
    for s in students:
        s_skills = s.skills or []
        for j in active_jobs:
            match_res = calculate_job_match(j.skills or [], s_skills)
            sum_matches += match_res["match_percentage"]
            total_pairs += 1

    average_job_match_percentage = round(sum_matches / total_pairs, 1) if total_pairs > 0 else 0.0

    return {
        "total_students": total_students,
        "total_recruiters": total_recruiters,
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "total_interviews": total_interviews,
        "scheduled_interviews": scheduled_interviews,
        "completed_interviews": completed_interviews,
        "cancelled_interviews": cancelled_interviews,
        "most_demanded_skills": most_demanded_skills,
        "average_job_match_percentage": average_job_match_percentage,
        "total_resumes_uploaded": total_resumes_uploaded,
        "total_students_with_resumes": total_students_with_resumes,
    }

@app.get("/api/admin/users", response_model=List[UserResponse], tags=["Admin"])
@app.get("/admin/users", response_model=List[UserResponse], include_in_schema=False)
def get_all_users(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).order_by(User.id.desc()).all()
    return [build_user_response(u) for u in users]

@app.delete("/api/admin/users/{user_id}", tags=["Admin"])
@app.delete("/admin/users/{user_id}", include_in_schema=False)
def delete_user(
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if user_id == admin_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete current admin user")

    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(target)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}

# ==========================================
# WEBSOCKET ENDPOINT
# ==========================================
@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    await websocket.send_json({"type": "CONNECTED", "message": "Real-time placement notifications enabled"})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in clients:
            clients.remove(websocket)

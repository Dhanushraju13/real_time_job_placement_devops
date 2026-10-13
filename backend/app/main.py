import os
import uuid
import logging
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from app.database import get_db, engine, Base
from app.models import (
    User, Student, Recruiter, Job, Application, Interview,
    SavedJob, WorkShift, Notification, JobReport, utcnow, ensure_schema_compatibility
)
from app.schemas import (
    RegisterRequest, LoginRequest, TokenResponse, UserResponse,
    JobCreate, JobUpdate, JobResponse, ApplicationCreate, ApplicationStatusUpdate,
    ApplicationResponse, AdminStatsResponse, StudentProfileResponse, RecruiterProfileResponse,
    EmployerProfileUpdate, InterviewCreate, InterviewUpdate, InterviewResponse,
    StudentProfileView, StudentProfileUpdate, StudentSkillsResponse, ResumeUploadResponse,
    SavedJobResponse, WorkShiftCreate, WorkShiftUpdate, WorkShiftResponse,
    NotificationResponse, JobReportCreate, JobReportResponse,
    AdminUserCreate, AdminUserUpdate
)
from app.auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, get_optional_current_user,
    require_student, require_recruiter, require_admin, require_recruiter_or_admin,
    require_employer, require_employer_or_admin
)
from app.seed import seed_database
from app.services.resume_parser import parse_resume, extract_skills
from app.services.job_matcher import calculate_job_match

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("parttime.api")

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "resumes")
os.makedirs(UPLOAD_DIR, exist_ok=True)

VALID_APPLICATION_STATUSES = [
    "APPLIED", "SUBMITTED",
    "UNDER_REVIEW",
    "SHORTLISTED",
    "INTERVIEW", "INTERVIEW_SCHEDULED",
    "OFFERED",
    "ACCEPTED",
    "REJECTED",
    "WITHDRAWN"
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize schema, run column migrations, ensure uploads folder, and seed demo data on startup
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        Base.metadata.create_all(bind=engine)
        ensure_schema_compatibility(engine)
        seed_database()
        logger.info("PartTime Platform initialization completed successfully.")
    except Exception:
        logger.exception("PartTime startup initialization failed; refusing to start an unready API.")
        raise
    yield

app = FastAPI(
    title="PartTime - Student Part-Time Job Portal API",
    description="Modern DevOps-enabled full-stack student part-time job and shifts platform.",
    version="2.0.0",
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

def notify_user(db: Session, user_id: int, title: str, message: str, notification_type: str, link: str):
    """Persist a notification for one user; the frontend polls this feed as source of truth."""
    db.add(Notification(
        user_id=user_id, title=title, message=message,
        type=notification_type, link=link, is_read=False
    ))

def notify_eligible_students(db: Session, title: str, message: str, notification_type: str, link: str = "/find-jobs"):
    """Notify active, approved student accounts only."""
    students = db.query(User).filter(
        User.role == "STUDENT", User.is_active == True, User.is_approved == True
    ).all()
    for student_user in students:
        notify_user(db, student_user.id, title, message, notification_type, link)
    return len(students)

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
            "experience": std.experience,
            "preferred_categories": std.preferred_categories or [],
            "preferred_locations": std.preferred_locations or [],
            "preferred_work_arrangement": std.preferred_work_arrangement or "Any",
            "weekly_availability": std.weekly_availability or "10-15 hrs/week",
            "max_weekly_hours": std.max_weekly_hours or 20,
        }

    recruiter_data = None
    if user.recruiter_profile:
        rec = user.recruiter_profile
        recruiter_data = {
            "id": rec.id,
            "company_name": rec.company_name,
            "company_email": rec.company_email,
            "business_description": rec.business_description,
            "industry": rec.industry,
            "website": rec.website,
            "location": rec.location,
            "contact_phone": rec.contact_phone,
            "is_verified": bool(rec.is_verified),
        }

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": getattr(user, "is_active", True),
        "is_approved": getattr(user, "is_approved", True),
        "created_at": user.created_at,
        "student_profile": student_data,
        "recruiter_profile": recruiter_data,
    }

def format_job(job: Job, student_skills: Optional[List[str]] = None, is_saved: bool = False) -> dict:
    company_name = job.company
    is_verified = False
    if job.recruiter:
        if not company_name:
            company_name = job.recruiter.company_name
        is_verified = bool(job.recruiter.is_verified)

    skills_list = job.skills if isinstance(job.skills, list) else ([job.skills] if job.skills else [])
    pay_display = job.pay_rate or job.salary or "₹250 - ₹400/hr"

    job_dict = {
        "id": job.id,
        "recruiter_id": job.recruiter_id,
        "title": job.title,
        "role": job.title,  # backward compatibility alias
        "company": company_name or "Verified Employer",
        "description": job.description or "",
        "salary": pay_display,
        "package": pay_display,  # backward compatibility alias
        "location": job.location or "Remote",
        "skills": skills_list,
        "status": job.status,
        "created_at": job.created_at,
        "category": job.category or "Web Development",
        "job_type": job.job_type or "Part-time",
        "work_arrangement": job.work_arrangement or "Remote",
        "compensation_type": job.compensation_type or "hourly",
        "pay_rate": pay_display,
        "min_hourly_pay": job.min_hourly_pay,
        "max_hourly_pay": job.max_hourly_pay,
        "weekly_hours": job.weekly_hours or "10-15 hrs/week",
        "shift_schedule": job.shift_schedule or "Flexible",
        "vacancies": job.vacancies or 1,
        "responsibilities": job.responsibilities or "",
        "qualifications": job.qualifications or "",
        "benefits": job.benefits or "",
        "deadline": job.deadline,
        "is_employer_verified": is_verified,
        "is_saved": is_saved,
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

    interview_status = None
    if app_item.interviews:
        interview_status = app_item.interviews[-1].status

    res = {
        "id": app_item.id,
        "job_id": app_item.job_id,
        "student_id": app_item.student_id,
        "status": app_item.status,
        "applied_at": app_item.applied_at,
        "updated_at": getattr(app_item, "updated_at", app_item.applied_at),
        "student": student_user.name if student_user else None,
        "student_name": student_user.name if student_user else None,
        "student_email": student_user.email if student_user else None,
        "college": student.college if student else None,
        "degree": student.degree if student else None,
        "branch": student.branch if student else None,
        "cgpa": student.cgpa if student else None,
        "skills": skills_list,
        "job_title": job.title if job else None,
        "company": company_name,
        "salary": job.pay_rate or job.salary if job else None,
        "location": job.location if job else None,
        "resume_url": student.resume_url if student else None,
        "cover_letter": app_item.cover_letter,
        "availability": app_item.availability,
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

    pay_str = job.pay_rate or job.salary if job else None

    return {
        "id": interview.id,
        "interview_id": interview.id,
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
        "salary": pay_str,
        "package": pay_str,
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

def format_shift(shift: WorkShift) -> dict:
    job = shift.job
    return {
        "id": shift.id,
        "student_id": shift.student_id,
        "job_id": shift.job_id,
        "job_title": job.title if job else "Part-Time Shift",
        "company": job.company if job else "CampusGigs Employer",
        "shift_date": shift.shift_date,
        "start_time": shift.start_time,
        "end_time": shift.end_time,
        "location": shift.location,
        "status": shift.status,
        "notes": shift.notes,
        "created_at": shift.created_at,
    }

# ==========================================
# HEALTH ENDPOINTS
# ==========================================
@app.get("/health", tags=["Health"])
@app.get("/api/health", include_in_schema=False)
def health():
    return {"status": "UP", "service": "parttime-api"}

# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================
@app.post("/api/auth/register", response_model=TokenResponse, tags=["Authentication"])
@app.post("/auth/register", response_model=TokenResponse, include_in_schema=False)
async def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    role_clean = payload.role.strip().upper()

    # Reject ADMIN registration
    if role_clean == "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Public registration as ADMIN is not permitted"
        )

    if role_clean not in ["STUDENT", "RECRUITER", "EMPLOYER"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be STUDENT or EMPLOYER"
        )

    # Standardize EMPLOYER role internally as RECRUITER
    internal_role = "RECRUITER" if role_clean in ["RECRUITER", "EMPLOYER"] else "STUDENT"

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
        role=internal_role,
        is_active=True,
        is_approved=False
    )
    db.add(new_user)
    db.flush()

    # Create associated profile
    if internal_role == "STUDENT":
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
            resume_url=payload.resume_url.strip() if payload.resume_url else None,
            preferred_work_arrangement=payload.preferred_work_arrangement or "Any",
            weekly_availability=payload.weekly_availability or "10-15 hrs/week"
        )
        db.add(student_profile)
    else:
        company = payload.company_name.strip() if payload.company_name else f"{payload.name}'s Company"
        recruiter_profile = Recruiter(
            user_id=new_user.id,
            company_name=company,
            company_email=payload.company_email.strip() if payload.company_email else email_clean,
            business_description=payload.business_description,
            industry=payload.industry,
            location=payload.location,
            is_verified=False  # Must be approved by admin
        )
        db.add(recruiter_profile)

    # Notify administrators about new registration pending approval
    admin_users = db.query(User).filter(User.role == "ADMIN").all()
    for adm in admin_users:
        role_label = "Student" if internal_role == "STUDENT" else "Recruiter"
        db.add(Notification(
            user_id=adm.id,
            title=f"New {role_label} Registration — Approval Needed",
            message=f"{role_label} '{new_user.name}' ({new_user.email}) just registered and is awaiting your approval.",
            type="USER_APPROVAL_PENDING",
            link="/admin"
        ))

    db.commit()
    db.refresh(new_user)

    user_resp = build_user_response(new_user)
    await broadcast({
        "type": "USER_APPROVAL_PENDING",
        "data": user_resp,
        "message": f"New {internal_role.lower()} '{new_user.name}' registered and is awaiting Admin approval."
    })

    token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": new_user.role,
        "user": user_resp
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

    if not getattr(user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended. Please contact platform administrator."
        )

    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "user": build_user_response(user)
    }

@app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication"])
@app.get("/auth/me", response_model=UserResponse, include_in_schema=False)
def get_me(user: User = Depends(get_current_user)):
    return build_user_response(user)

# ==========================================
# STUDENT PROFILE & RESUME ENDPOINTS
# ==========================================
@app.get("/api/students/profile", response_model=StudentProfileView, tags=["Students"])
def get_student_profile(
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = user.student_profile
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return {
        "id": student.id,
        "name": user.name,
        "email": user.email,
        "college": student.college,
        "degree": student.degree,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "skills": student.skills or [],
        "resume_url": student.resume_url,
        "experience": student.experience,
        "preferred_categories": student.preferred_categories or [],
        "preferred_locations": student.preferred_locations or [],
        "preferred_work_arrangement": student.preferred_work_arrangement or "Any",
        "weekly_availability": student.weekly_availability or "10-15 hrs/week",
        "max_weekly_hours": student.max_weekly_hours or 20,
    }

@app.put("/api/students/profile", response_model=StudentProfileView, tags=["Students"])
def update_student_profile(
    payload: StudentProfileUpdate,
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = user.student_profile
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    if payload.name is not None:
        user.name = payload.name.strip()
    if payload.college is not None:
        student.college = payload.college.strip()
    if payload.degree is not None:
        student.degree = payload.degree.strip()
    if payload.branch is not None:
        student.branch = payload.branch.strip()
    if payload.cgpa is not None:
        student.cgpa = payload.cgpa
    if payload.experience is not None:
        student.experience = payload.experience.strip()
    if payload.preferred_categories is not None:
        student.preferred_categories = payload.preferred_categories
    if payload.preferred_locations is not None:
        student.preferred_locations = payload.preferred_locations
    if payload.preferred_work_arrangement is not None:
        student.preferred_work_arrangement = payload.preferred_work_arrangement
    if payload.weekly_availability is not None:
        student.weekly_availability = payload.weekly_availability
    if payload.max_weekly_hours is not None:
        student.max_weekly_hours = payload.max_weekly_hours

    if payload.skills is not None:
        if isinstance(payload.skills, list):
            student.skills = [s.strip() for s in payload.skills if s.strip()]
        elif isinstance(payload.skills, str):
            student.skills = [s.strip() for s in payload.skills.split(",") if s.strip()]

    db.commit()
    db.refresh(user)
    db.refresh(student)

    return {
        "id": student.id,
        "name": user.name,
        "email": user.email,
        "college": student.college,
        "degree": student.degree,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "skills": student.skills or [],
        "resume_url": student.resume_url,
        "experience": student.experience,
        "preferred_categories": student.preferred_categories or [],
        "preferred_locations": student.preferred_locations or [],
        "preferred_work_arrangement": student.preferred_work_arrangement or "Any",
        "weekly_availability": student.weekly_availability or "10-15 hrs/week",
        "max_weekly_hours": student.max_weekly_hours or 20,
    }

@app.get("/api/students/skills", response_model=StudentSkillsResponse, tags=["Students"])
def get_student_skills(
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = user.student_profile
    return {"skills": student.skills if student and student.skills else []}

@app.post("/api/students/resume", response_model=ResumeUploadResponse, tags=["Students"])
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = user.student_profile
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents are supported for resume upload"
        )

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 5MB maximum limit"
        )

    safe_name = f"{user.id}_{uuid.uuid4().hex[:8]}.pdf"
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(file_path, "wb") as f:
        f.write(content)

    parse_result = parse_resume(file_path)
    detected_skills = parse_result["skills"]

    existing_skills = student.skills or []
    merged_skills = sorted(list(set(existing_skills + detected_skills)))

    relative_url = f"/api/uploads/resumes/{safe_name}"
    student.resume_url = relative_url
    student.skills = merged_skills
    db.commit()

    return {
        "resume_url": relative_url,
        "filename": file.filename,
        "uploaded_at": datetime.now(timezone.utc),
        "detected_skills": detected_skills,
        "skills": merged_skills
    }

@app.get("/api/uploads/resumes/{filename}", tags=["Students"])
def get_resume_file(filename: str, current_user: User = Depends(get_current_user)):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume file not found")
    return FileResponse(file_path, media_type="application/pdf", filename=filename)

# ==========================================
# EMPLOYER PROFILE ENDPOINTS
# ==========================================
@app.get("/api/employers/profile", response_model=RecruiterProfileResponse, tags=["Employers"])
def get_employer_profile(
    user: User = Depends(require_employer),
    db: Session = Depends(get_db)
):
    rec = user.recruiter_profile
    if not rec:
        raise HTTPException(status_code=404, detail="Employer profile not found")
    return rec

@app.put("/api/employers/profile", response_model=RecruiterProfileResponse, tags=["Employers"])
def update_employer_profile(
    payload: EmployerProfileUpdate,
    user: User = Depends(require_employer),
    db: Session = Depends(get_db)
):
    rec = user.recruiter_profile
    if not rec:
        raise HTTPException(status_code=404, detail="Employer profile not found")

    if payload.company_name:
        rec.company_name = payload.company_name.strip()
    if payload.company_email:
        rec.company_email = payload.company_email.strip()
    if payload.business_description is not None:
        rec.business_description = payload.business_description.strip()
    if payload.industry is not None:
        rec.industry = payload.industry.strip()
    if payload.website is not None:
        rec.website = payload.website.strip()
    if payload.location is not None:
        rec.location = payload.location.strip()
    if payload.contact_phone is not None:
        rec.contact_phone = payload.contact_phone.strip()

    db.commit()
    db.refresh(rec)
    return rec

# ==========================================
# JOBS ENDPOINTS
# ==========================================
@app.get("/api/jobs", response_model=List[JobResponse], tags=["Jobs"])
@app.get("/jobs", response_model=List[JobResponse], include_in_schema=False)
def list_jobs(
    q: Optional[str] = Query(None, description="Search keyword in title, employer, description, or skill"),
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    work_arrangement: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    shift_schedule: Optional[str] = Query(None),
    min_pay: Optional[float] = Query(None),
    max_pay: Optional[float] = Query(None),
    sort_by: Optional[str] = Query("newest"),  # newest, pay, relevance
    status: Optional[str] = Query(None),
    user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    requested_status = status.upper() if status else None
    # Only authenticated administrators may enumerate pending/closed jobs or request ALL.
    # Public and student job discovery must never expose jobs awaiting approval.
    if requested_status == "ALL":
        if not user or user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Only administrators can view all job statuses")
        query = db.query(Job)
    elif requested_status and requested_status != "ACTIVE":
        if not user or user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Only administrators can view non-active jobs")
        query = db.query(Job).filter(Job.status == requested_status)
    else:
        query = db.query(Job).filter(Job.status == "ACTIVE")

    # Keyword search
    if q and q.strip():
        term = f"%{q.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(Job.title).like(term),
                func.lower(Job.company).like(term),
                func.lower(Job.description).like(term),
                func.lower(Job.category).like(term)
            )
        )

    # Filters
    if category and category.strip() and category != "All":
        query = query.filter(func.lower(Job.category) == category.strip().lower())

    if location and location.strip() and location != "All":
        query = query.filter(func.lower(Job.location).like(f"%{location.strip().lower()}%"))

    if work_arrangement and work_arrangement.strip() and work_arrangement != "All":
        query = query.filter(func.lower(Job.work_arrangement) == work_arrangement.strip().lower())

    if job_type and job_type.strip() and job_type != "All":
        query = query.filter(func.lower(Job.job_type) == job_type.strip().lower())

    if shift_schedule and shift_schedule.strip() and shift_schedule != "All":
        query = query.filter(func.lower(Job.shift_schedule) == shift_schedule.strip().lower())

    if min_pay is not None:
        query = query.filter(or_(Job.min_hourly_pay >= min_pay, Job.min_hourly_pay.is_(None)))

    if max_pay is not None:
        query = query.filter(or_(Job.max_hourly_pay <= max_pay, Job.max_hourly_pay.is_(None)))

    # Sorting
    if sort_by == "pay":
        query = query.order_by(Job.max_hourly_pay.desc().nullslast(), Job.created_at.desc())
    else:
        query = query.order_by(Job.created_at.desc())

    jobs = query.all()

    # Determine student context for matching and saved status
    student_skills = None
    saved_job_ids = set()
    if user and user.role == "STUDENT" and user.student_profile:
        student_skills = user.student_profile.skills
        saved_jobs = db.query(SavedJob.job_id).filter(SavedJob.student_id == user.student_profile.id).all()
        saved_job_ids = {s[0] for s in saved_jobs}

    results = [format_job(j, student_skills=student_skills, is_saved=(j.id in saved_job_ids)) for j in jobs]

    if sort_by == "relevance" and student_skills:
        results.sort(key=lambda x: (x["match_percentage"] or 0), reverse=True)

    return results

@app.get("/api/jobs/recommended", response_model=List[JobResponse], tags=["Jobs"])
def get_recommended_jobs(
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = user.student_profile
    student_skills = student.skills if student and student.skills else []

    saved_jobs = db.query(SavedJob.job_id).filter(SavedJob.student_id == student.id).all()
    saved_job_ids = {s[0] for s in saved_jobs}

    jobs = db.query(Job).filter(Job.status == "ACTIVE").all()
    formatted = [format_job(j, student_skills=student_skills, is_saved=(j.id in saved_job_ids)) for j in jobs]
    formatted.sort(key=lambda x: (x["match_percentage"] or 0, x["created_at"]), reverse=True)
    return formatted

@app.get("/api/jobs/{job_id}", response_model=JobResponse, tags=["Jobs"])
def get_job(
    job_id: int,
    user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    student_skills = None
    is_saved = False
    if user and user.role == "STUDENT" and user.student_profile:
        student_skills = user.student_profile.skills
        is_saved = db.query(SavedJob).filter(
            SavedJob.student_id == user.student_profile.id,
            SavedJob.job_id == job.id
        ).first() is not None

    return format_job(job, student_skills=student_skills, is_saved=is_saved)

@app.post("/api/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED, tags=["Jobs"])
@app.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_job(
    payload: JobCreate,
    user: User = Depends(require_recruiter_or_admin),
    db: Session = Depends(get_db)
):
    if user.role != "ADMIN" and not getattr(user, "is_approved", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your recruiter account is pending Admin approval. You will be able to post jobs once an administrator approves your registration."
        )

    job_title = payload.title or payload.role
    if not job_title or not job_title.strip():
        raise HTTPException(status_code=400, detail="Job title is required")

    recruiter_profile = user.recruiter_profile
    recruiter_id = recruiter_profile.id if recruiter_profile else None
    company = payload.company or (recruiter_profile.company_name if recruiter_profile else user.name)

    skills_clean = []
    if isinstance(payload.skills, list):
        skills_clean = [s.strip() for s in payload.skills if s.strip()]
    elif isinstance(payload.skills, str):
        skills_clean = [s.strip() for s in payload.skills.split(",") if s.strip()]

    pay_str = payload.pay_rate or payload.salary or payload.package or "₹250 - ₹400/hr"
    initial_status = "ACTIVE" if user.role == "ADMIN" else "PENDING_APPROVAL"

    new_job = Job(
        recruiter_id=recruiter_id,
        title=job_title.strip(),
        company=company,
        description=payload.description or "",
        salary=pay_str,
        location=payload.location or "Remote",
        skills=skills_clean,
        category=payload.category or "Web Development",
        job_type=payload.job_type or "Part-time",
        work_arrangement=payload.work_arrangement or "Remote",
        compensation_type=payload.compensation_type or "hourly",
        pay_rate=pay_str,
        min_hourly_pay=payload.min_hourly_pay,
        max_hourly_pay=payload.max_hourly_pay,
        weekly_hours=payload.weekly_hours or "10-15 hrs/week",
        shift_schedule=payload.shift_schedule or "Flexible",
        vacancies=payload.vacancies or 1,
        responsibilities=payload.responsibilities or "",
        qualifications=payload.qualifications or "",
        benefits=payload.benefits or "",
        deadline=payload.deadline,
        status=initial_status
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # If pending approval, notify all administrators
    if initial_status == "PENDING_APPROVAL":
        admin_users = db.query(User).filter(User.role == "ADMIN").all()
        for adm in admin_users:
            db.add(Notification(
                user_id=adm.id,
                title="New Job Offer Pending Approval",
                message=f"Recruiter '{user.name}' ({company}) posted job offer '{new_job.title}'. Approval required.",
                type="JOB_APPROVAL_PENDING",
                link="/admin"
            ))
        db.commit()

    job_data = format_job(new_job)

    # Broadcast real-time WebSocket notification
    await broadcast({
        "type": "NEW_JOB" if initial_status == "ACTIVE" else "JOB_APPROVAL_PENDING",
        "data": job_data,
        "message": f"New gig posted: {new_job.title} at {new_job.company} ({new_job.pay_rate})" if initial_status == "ACTIVE" else f"Job offer '{new_job.title}' submitted for admin review."
    })

    return job_data

@app.put("/api/jobs/{job_id}", response_model=JobResponse, tags=["Jobs"])
async def update_job(
    job_id: int,
    payload: JobUpdate,
    user: User = Depends(require_recruiter_or_admin),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Recruiter data isolation check
    if user.role != "ADMIN" and (not user.recruiter_profile or job.recruiter_id != user.recruiter_profile.id):
        raise HTTPException(status_code=403, detail="Not authorized to edit this job listing")

    was_active = job.status == "ACTIVE"
    old_schedule = (job.shift_schedule, job.weekly_hours, job.deadline, job.location, job.work_arrangement)
    old_details = (
        job.title, job.description, job.salary, job.category, job.job_type,
        job.compensation_type, job.pay_rate, job.min_hourly_pay, job.max_hourly_pay,
        job.vacancies, job.responsibilities, job.qualifications, job.benefits,
        tuple(job.skills or []) if isinstance(job.skills, list) else job.skills
    )
    if payload.title is not None:
        job.title = payload.title.strip()
    if payload.description is not None:
        job.description = payload.description.strip()
    if payload.salary is not None:
        job.salary = payload.salary.strip()
        job.pay_rate = payload.salary.strip()
    if payload.pay_rate is not None:
        job.pay_rate = payload.pay_rate.strip()
        job.salary = payload.pay_rate.strip()
    if payload.location is not None:
        job.location = payload.location.strip()
    if payload.category is not None:
        job.category = payload.category.strip()
    if payload.job_type is not None:
        job.job_type = payload.job_type.strip()
    if payload.work_arrangement is not None:
        job.work_arrangement = payload.work_arrangement.strip()
    if payload.compensation_type is not None:
        job.compensation_type = payload.compensation_type.strip()
    if payload.min_hourly_pay is not None:
        job.min_hourly_pay = payload.min_hourly_pay
    if payload.max_hourly_pay is not None:
        job.max_hourly_pay = payload.max_hourly_pay
    if payload.weekly_hours is not None:
        job.weekly_hours = payload.weekly_hours.strip()
    if payload.shift_schedule is not None:
        job.shift_schedule = payload.shift_schedule.strip()
    if payload.vacancies is not None:
        job.vacancies = payload.vacancies
    if payload.responsibilities is not None:
        job.responsibilities = payload.responsibilities.strip()
    if payload.qualifications is not None:
        job.qualifications = payload.qualifications.strip()
    if payload.benefits is not None:
        job.benefits = payload.benefits.strip()
    if payload.status is not None:
        job.status = payload.status.strip().upper()
    if payload.deadline is not None:
        job.deadline = payload.deadline
    if payload.skills is not None:
        if isinstance(payload.skills, list):
            job.skills = [s.strip() for s in payload.skills if s.strip()]
        elif isinstance(payload.skills, str):
            job.skills = [s.strip() for s in payload.skills.split(",") if s.strip()]

    db.commit()
    db.refresh(job)

    # Approved live listings must notify students when their schedule or key details change.
    new_schedule = (job.shift_schedule, job.weekly_hours, job.deadline, job.location, job.work_arrangement)
    new_details = (
        job.title, job.description, job.salary, job.category, job.job_type,
        job.compensation_type, job.pay_rate, job.min_hourly_pay, job.max_hourly_pay,
        job.vacancies, job.responsibilities, job.qualifications, job.benefits,
        tuple(job.skills or []) if isinstance(job.skills, list) else job.skills
    )
    if was_active and job.status == "ACTIVE" and old_details != new_details or (was_active and job.status == "ACTIVE" and old_schedule != new_schedule):
        schedule_changed = old_schedule != new_schedule
        notification_title = "Job Schedule Updated" if schedule_changed else "Job Details Updated"
        notification_message = (
            f"The schedule or work arrangement for '{job.title}' at {job.company or 'the employer'} has changed. Review the latest details."
            if schedule_changed else
            f"The listing '{job.title}' at {job.company or 'the employer'} has been updated. Review the latest job details."
        )
        event_type = "JOB_SCHEDULE_UPDATED" if schedule_changed else "JOB_DETAILS_UPDATED"
        notify_eligible_students(db, notification_title, notification_message, event_type, "/find-jobs")
        db.commit()
        await broadcast({
            "type": event_type,
            "data": {"id": job.id, "title": job.title},
            "message": f"Job listing updated: {job.title}"
        })
    return format_job(job)

@app.patch("/api/jobs/{job_id}/status", response_model=JobResponse, tags=["Jobs"])
def toggle_job_status(
    job_id: int,
    status_str: str = Query(..., pattern="^(ACTIVE|PAUSED|CLOSED)$"),
    user: User = Depends(require_recruiter_or_admin),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if user.role != "ADMIN" and (not user.recruiter_profile or job.recruiter_id != user.recruiter_profile.id):
        raise HTTPException(status_code=403, detail="Not authorized to modify this job status")

    job.status = status_str
    db.commit()
    db.refresh(job)
    return format_job(job)

@app.delete("/api/jobs/{job_id}", tags=["Jobs"])
def delete_job(
    job_id: int,
    user: User = Depends(require_recruiter_or_admin),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if user.role != "ADMIN" and (not user.recruiter_profile or job.recruiter_id != user.recruiter_profile.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this job listing")

    db.delete(job)
    db.commit()
    return {"status": "DELETED", "id": job_id}

# ==========================================
# SAVED JOBS ENDPOINTS
# ==========================================
@app.post("/api/jobs/{job_id}/save", tags=["Saved Jobs"])
def save_job(
    job_id: int,
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = user.student_profile
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = db.query(SavedJob).filter(
        SavedJob.student_id == student.id,
        SavedJob.job_id == job.id
    ).first()

    if not existing:
        saved_item = SavedJob(student_id=student.id, job_id=job.id)
        db.add(saved_item)
        db.commit()

    return {"status": "saved", "job_id": job.id}

@app.delete("/api/jobs/{job_id}/save", tags=["Saved Jobs"])
def unsave_job(
    job_id: int,
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = user.student_profile
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    existing = db.query(SavedJob).filter(
        SavedJob.student_id == student.id,
        SavedJob.job_id == job_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()

    return {"status": "unsaved", "job_id": job_id}

@app.get("/api/saved-jobs", response_model=List[SavedJobResponse], tags=["Saved Jobs"])
def get_saved_jobs(
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = user.student_profile
    if not student:
        return []

    saved = db.query(SavedJob).filter(SavedJob.student_id == student.id).order_by(SavedJob.saved_at.desc()).all()
    res = []
    for s in saved:
        job_data = format_job(s.job, student_skills=student.skills, is_saved=True)
        res.append({
            "id": s.id,
            "job_id": s.job_id,
            "saved_at": s.saved_at,
            "job": job_data,
            "job_title": job_data.get("title", ""),
            "company": job_data.get("company", ""),
            "location": job_data.get("location", ""),
            "pay_rate": job_data.get("pay_rate", ""),
            "salary": job_data.get("salary", ""),
            "description": job_data.get("description", "")
        })
    return res

# ==========================================
# APPLICATIONS ENDPOINTS
# ==========================================
@app.get("/api/applications", response_model=List[ApplicationResponse], tags=["Applications"])
@app.get("/applications", response_model=List[ApplicationResponse], include_in_schema=False)
def list_applications(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.role == "STUDENT":
        student = user.student_profile
        if not student:
            return []
        apps = db.query(Application).filter(Application.student_id == student.id).order_by(Application.applied_at.desc()).all()
        return [format_application(a, include_match=False) for a in apps]

    elif user.role in ["RECRUITER", "EMPLOYER"]:
        recruiter = user.recruiter_profile
        if not recruiter:
            return []
        apps = (
            db.query(Application)
            .join(Job, Application.job_id == Job.id)
            .filter(Job.recruiter_id == recruiter.id)
            .order_by(Application.applied_at.desc())
            .all()
        )
        return [format_application(a, include_match=True) for a in apps]

    elif user.role == "ADMIN":
        apps = db.query(Application).order_by(Application.applied_at.desc()).all()
        return [format_application(a, include_match=True) for a in apps]

    return []

@app.post("/api/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED, tags=["Applications"])
@app.post("/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def submit_application(
    payload: ApplicationCreate,
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    if not getattr(user, "is_approved", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your student account is pending Admin approval. You will be able to apply once an administrator approves your registration."
        )

    student = user.student_profile
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="This job is closed and is no longer accepting applications")

    if job.deadline:
        now_dt = datetime.now(timezone.utc)
        dl = job.deadline
        if dl.tzinfo is None:
            dl = dl.replace(tzinfo=timezone.utc)
        if dl < now_dt:
            raise HTTPException(status_code=400, detail="Application deadline for this job has passed")

    # Prevent duplicate applications
    existing_app = db.query(Application).filter(
        Application.job_id == payload.job_id,
        Application.student_id == student.id
    ).first()

    if existing_app:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job"
        )

    new_app = Application(
        job_id=job.id,
        student_id=student.id,
        status="APPLIED",
        cover_letter=payload.cover_letter.strip() if payload.cover_letter else None,
        availability=payload.availability.strip() if payload.availability else student.weekly_availability
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    # Notify employer if recruiter user exists
    if job.recruiter and job.recruiter.user_id:
        employer_notif = Notification(
            user_id=job.recruiter.user_id,
            title="New Application Received",
            message=f"{user.name} applied for '{job.title}'.",
            type="NEW_APPLICATION",
            link="/applicants"
        )
        db.add(employer_notif)
        db.commit()

    app_data = format_application(new_app)

    # Broadcast WebSocket notification
    await broadcast({
        "type": "NEW_APPLICATION",
        "data": app_data,
        "message": f"New application: {user.name} applied for {job.title}"
    })

    return app_data

@app.post("/api/applications/{app_id}/withdraw", tags=["Applications"])
async def withdraw_application(
    app_id: int,
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = user.student_profile
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    app_item = db.query(Application).filter(Application.id == app_id).first()
    if not app_item:
        raise HTTPException(status_code=404, detail="Application not found")

    if app_item.student_id != student.id:
        raise HTTPException(status_code=403, detail="Not authorized to withdraw this application")

    if app_item.status in ["ACCEPTED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Cannot withdraw a finalized application")

    app_item.status = "WITHDRAWN"
    app_item.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {"status": "WITHDRAWN", "id": app_item.id}

VALID_APPLICATION_STATUS_TRANSITIONS = {
    "APPLIED": ["UNDER_REVIEW", "REJECTED"],
    "SUBMITTED": ["UNDER_REVIEW", "REJECTED"],
    "UNDER_REVIEW": ["SHORTLISTED", "REJECTED"],
    "SHORTLISTED": ["INTERVIEW", "INTERVIEW_SCHEDULED", "REJECTED"],
    "INTERVIEW": ["SELECTED", "OFFERED", "REJECTED"],
    "INTERVIEW_SCHEDULED": ["SELECTED", "OFFERED", "REJECTED"],
    "OFFERED": ["ACCEPTED", "REJECTED", "WITHDRAWN"],
    "ACCEPTED": [],
    "SELECTED": [],
    "REJECTED": [],
    "WITHDRAWN": []
}

@app.patch("/api/applications/{app_id}", response_model=ApplicationResponse, tags=["Applications"])
@app.patch("/applications/{app_id}", response_model=ApplicationResponse, include_in_schema=False)
async def update_application_status(
    app_id: int,
    payload: ApplicationStatusUpdate,
    user: User = Depends(require_recruiter_or_admin),
    db: Session = Depends(get_db)
):
    app_item = db.query(Application).filter(Application.id == app_id).first()
    if not app_item:
        raise HTTPException(status_code=404, detail="Application not found")

    job = app_item.job
    # Recruiter data isolation
    if user.role != "ADMIN":
        recruiter = user.recruiter_profile
        if not recruiter or job.recruiter_id != recruiter.id:
            raise HTTPException(status_code=403, detail="Not authorized to modify applicants for another employer's job")

    new_status = payload.status.strip().upper()

    curr_status = app_item.status.upper()
    valid_next = VALID_APPLICATION_STATUS_TRANSITIONS.get(curr_status, [])
    if new_status not in valid_next and new_status != curr_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {curr_status} to {new_status}"
        )

    app_item.status = new_status
    app_item.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(app_item)

    # Create persistent notification for student
    student_user_id = app_item.student.user_id if app_item.student else None
    if student_user_id:
        status_readable = new_status.replace("_", " ").title()
        notif = Notification(
            user_id=student_user_id,
            title="Application Status Updated",
            message=f"Your application for '{job.title}' is now: {status_readable}.",
            type="APPLICATION_STATUS",
            link="/my-applications"
        )
        db.add(notif)
        db.commit()

    app_data = format_application(app_item)

    await broadcast({
        "type": "APPLICATION_STATUS",
        "data": app_data,
        "message": f"Application #{app_item.id} updated to {new_status}"
    })

    return app_data

# ==========================================
# INTERVIEW ENDPOINTS
# ==========================================
@app.get("/api/interviews", response_model=List[InterviewResponse], tags=["Interviews"])
@app.get("/interviews", response_model=List[InterviewResponse], include_in_schema=False)
def list_interviews(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.role == "STUDENT":
        student = user.student_profile
        if not student:
            return []
        interviews = (
            db.query(Interview)
            .join(Application, Interview.application_id == Application.id)
            .filter(Application.student_id == student.id)
            .order_by(Interview.scheduled_at.asc())
            .all()
        )
        return [format_interview(i) for i in interviews]

    elif user.role in ["RECRUITER", "EMPLOYER"]:
        recruiter = user.recruiter_profile
        if not recruiter:
            return []
        interviews = (
            db.query(Interview)
            .join(Application, Interview.application_id == Application.id)
            .join(Job, Application.job_id == Job.id)
            .filter(Job.recruiter_id == recruiter.id)
            .order_by(Interview.scheduled_at.asc())
            .all()
        )
        return [format_interview(i) for i in interviews]

    elif user.role == "ADMIN":
        interviews = db.query(Interview).order_by(Interview.scheduled_at.asc()).all()
        return [format_interview(i) for i in interviews]

    return []

@app.get("/api/interviews/{interview_id}", response_model=InterviewResponse, tags=["Interviews"])
@app.get("/interviews/{interview_id}", response_model=InterviewResponse, include_in_schema=False)
def get_interview(
    interview_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if user.role == "STUDENT":
        if not user.student_profile or interview.application.student_id != user.student_profile.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    elif user.role in ["RECRUITER", "EMPLOYER"]:
        if not user.recruiter_profile or interview.application.job.recruiter_id != user.recruiter_profile.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    return format_interview(interview)

@app.post("/api/interviews", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED, tags=["Interviews"])
@app.post("/interviews", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def schedule_interview(
    payload: InterviewCreate,
    user: User = Depends(require_recruiter_or_admin),
    db: Session = Depends(get_db)
):
    app_item = db.query(Application).filter(Application.id == payload.application_id).first()
    if not app_item:
        raise HTTPException(status_code=404, detail="Application not found")

    job = app_item.job
    if user.role != "ADMIN":
        recruiter = user.recruiter_profile
        if not recruiter or job.recruiter_id != recruiter.id:
            raise HTTPException(status_code=403, detail="Cannot schedule interview for another recruiter's application")

    new_interview = Interview(
        application_id=app_item.id,
        scheduled_at=payload.scheduled_at,
        mode=payload.mode.strip().upper(),
        meeting_link=payload.meeting_link.strip() if payload.meeting_link else None,
        location=payload.location.strip() if payload.location else ("Google Meet" if payload.mode == "ONLINE" else "On-site Venue"),
        notes=payload.notes.strip() if payload.notes else None,
        status="SCHEDULED"
    )
    db.add(new_interview)

    # Advance application to INTERVIEW_SCHEDULED
    app_item.status = "INTERVIEW_SCHEDULED"
    app_item.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(new_interview)

    # Create persistent notification for student
    student_user_id = app_item.student.user_id if app_item.student else None
    if student_user_id:
        notif = Notification(
            user_id=student_user_id,
            title="Interview Scheduled!",
            message=f"An interview for '{job.title}' has been scheduled for {new_interview.scheduled_at.strftime('%b %d, %Y at %I:%M %p')}.",
            type="INTERVIEW_SCHEDULED",
            link="/my-applications"
        )
        db.add(notif)
        db.commit()

    interview_data = format_interview(new_interview)

    await broadcast({
        "type": "INTERVIEW_SCHEDULED",
        "data": interview_data,
        "message": f"Interview scheduled for {app_item.student.user.name} ({job.title})"
    })

    return interview_data

@app.patch("/api/interviews/{interview_id}", response_model=InterviewResponse, tags=["Interviews"])
@app.patch("/interviews/{interview_id}", response_model=InterviewResponse, include_in_schema=False)
async def update_interview(
    interview_id: int,
    payload: InterviewUpdate,
    user: User = Depends(require_recruiter_or_admin),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    job = interview.application.job
    if user.role != "ADMIN":
        recruiter = user.recruiter_profile
        if not recruiter or job.recruiter_id != recruiter.id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this interview")

    if payload.status is not None:
        interview.status = payload.status.strip().upper()
    if payload.scheduled_at is not None:
        interview.scheduled_at = payload.scheduled_at
    if payload.mode is not None:
        interview.mode = payload.mode.strip().upper()
    if payload.meeting_link is not None:
        interview.meeting_link = payload.meeting_link.strip()
    if payload.location is not None:
        interview.location = payload.location.strip()
    if payload.notes is not None:
        interview.notes = payload.notes.strip()

    db.commit()
    db.refresh(interview)

    student_user = interview.application.student.user if interview.application and interview.application.student else None
    if student_user:
        if interview.status == "CANCELLED":
            title = "Interview Cancelled"
            message_text = f"The interview for '{job.title}' has been cancelled. Check your applications for updates."
            notif_type = "INTERVIEW_CANCELLED"
        else:
            title = "Interview Details Updated"
            message_text = f"The interview for '{job.title}' has been updated. Scheduled time: {interview.scheduled_at.strftime('%b %d, %Y at %I:%M %p')}. Check your application for details."
            notif_type = "INTERVIEW_UPDATED"
        notify_user(db, student_user.id, title, message_text, notif_type, "/my-applications")
        db.commit()

    interview_data = format_interview(interview)
    await broadcast({
        "type": "INTERVIEW_UPDATED",
        "data": interview_data,
        "message": f"Interview #{interview.id} updated"
    })
    return interview_data

@app.delete("/api/interviews/{interview_id}", tags=["Interviews"])
@app.delete("/interviews/{interview_id}", include_in_schema=False)
async def cancel_interview(
    interview_id: int,
    user: User = Depends(require_recruiter_or_admin),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    job = interview.application.job
    if user.role != "ADMIN":
        recruiter = user.recruiter_profile
        if not recruiter or job.recruiter_id != recruiter.id:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this interview")

    interview.status = "CANCELLED"
    db.commit()

    student_user = interview.application.student.user if interview.application and interview.application.student else None
    if student_user:
        notify_user(
            db, student_user.id, "Interview Cancelled",
            f"The interview for '{job.title}' has been cancelled. Check your applications for updates.",
            "INTERVIEW_CANCELLED", "/my-applications"
        )
        db.commit()

    await broadcast({
        "type": "INTERVIEW_CANCELLED",
        "data": {"id": interview.id},
        "message": f"Interview #{interview.id} was cancelled"
    })
    return {"status": "CANCELLED", "id": interview.id}

# ==========================================
# WORK SHIFTS ENDPOINTS
# ==========================================
@app.get("/api/shifts", response_model=List[WorkShiftResponse], tags=["Work Shifts"])
def list_shifts(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.role == "STUDENT":
        student = user.student_profile
        if not student:
            return []
        shifts = db.query(WorkShift).filter(WorkShift.student_id == student.id).order_by(WorkShift.shift_date.asc()).all()
        return [format_shift(s) for s in shifts]

    elif user.role in ["RECRUITER", "EMPLOYER"]:
        recruiter = user.recruiter_profile
        if not recruiter:
            return []
        shifts = (
            db.query(WorkShift)
            .join(Job, WorkShift.job_id == Job.id)
            .filter(Job.recruiter_id == recruiter.id)
            .order_by(WorkShift.shift_date.asc())
            .all()
        )
        return [format_shift(s) for s in shifts]

    elif user.role == "ADMIN":
        shifts = db.query(WorkShift).order_by(WorkShift.shift_date.asc()).all()
        return [format_shift(s) for s in shifts]

    return []

@app.post("/api/shifts", response_model=WorkShiftResponse, tags=["Work Shifts"])
async def create_shift(
    payload: WorkShiftCreate,
    user: User = Depends(require_recruiter_or_admin),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    new_shift = WorkShift(
        student_id=student.id,
        job_id=payload.job_id,
        application_id=payload.application_id,
        shift_date=payload.shift_date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        location=payload.location,
        notes=payload.notes,
        status="SCHEDULED"
    )
    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)

    # Notify student
    student_user_id = student.user_id
    if student_user_id:
        job_title = new_shift.job.title if new_shift.job else "your assigned work"
        notif = Notification(
            user_id=student_user_id,
            title="New Work Shift Scheduled",
            message=f"A shift for '{job_title}' is scheduled on {new_shift.shift_date.strftime('%b %d, %Y')} ({new_shift.start_time} - {new_shift.end_time}) at {new_shift.location or 'the assigned location'}. {new_shift.notes or ''}".strip(),
            type="SHIFT_REMINDER",
            link="/dashboard"
        )
        db.add(notif)
        db.commit()

    shift_data = format_shift(new_shift)
    await broadcast({
        "type": "SHIFT_SCHEDULED",
        "data": shift_data,
        "message": f"Work shift scheduled for {student.user.name}"
    })
    return shift_data

@app.post("/api/shifts/{shift_id}/complete", tags=["Work Shifts"])
def mark_shift_completed(
    shift_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    shift = db.query(WorkShift).filter(WorkShift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    # Only student assignee, employer owner, or admin can mark complete
    if user.role == "STUDENT" and user.student_profile and shift.student_id != user.student_profile.id:
        raise HTTPException(status_code=403, detail="Not authorized to complete this shift")

    shift.status = "COMPLETED"
    db.commit()
    return {"status": "COMPLETED", "id": shift.id}

# ==========================================
# NOTIFICATIONS ENDPOINTS
# ==========================================
@app.get("/api/notifications", tags=["Notifications"])
def get_user_notifications(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notifs = db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).limit(30).all()
    unread_count = db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read == False).count()
    return {
        "unread_count": unread_count,
        "notifications": [
            {
                "id": n.id,
                "user_id": n.user_id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "is_read": bool(n.is_read),
                "link": n.link,
                "created_at": n.created_at
            }
            for n in notifs
        ]
    }

@app.patch("/api/notifications/{notif_id}/read", tags=["Notifications"])
def mark_notification_read(
    notif_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == user.id).first()
    if notif:
        notif.is_read = True
        db.commit()
    return {"status": "read", "id": notif_id}

@app.post("/api/notifications/read-all", tags=["Notifications"])
def mark_all_notifications_read(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read == False).update({"is_read": True})
    db.commit()
    return {"status": "all_read"}

# ==========================================
# JOB REPORTING & MODERATION ENDPOINTS
# ==========================================
@app.post("/api/jobs/{job_id}/report", tags=["Reports"])
def report_job(
    job_id: int,
    payload: JobReportCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_id = job_id if job_id is not None else payload.job_id
    job = db.query(Job).filter(Job.id == target_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    report = JobReport(
        job_id=job.id,
        user_id=user.id,
        reason=payload.reason.strip(),
        details=payload.details.strip() if payload.details else None,
        status="PENDING"
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {"status": "reported", "id": report.id, "message": "Thank you. Our moderation team will review this listing."}

@app.get("/api/admin/reports", response_model=List[JobReportResponse], tags=["Admin"])
def list_reports(
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    reports = db.query(JobReport).order_by(JobReport.created_at.desc()).all()
    res = []
    for r in reports:
        res.append({
            "id": r.id,
            "job_id": r.job_id,
            "job_title": r.job.title if r.job else "Unknown Job",
            "company": r.job.company if r.job else "Unknown Employer",
            "user_id": r.user_id,
            "reporter_name": r.user.name if r.user else "Anonymous",
            "reason": r.reason,
            "details": r.details,
            "status": r.status,
            "created_at": r.created_at
        })
    return res

@app.patch("/api/admin/reports/{report_id}", tags=["Admin"])
def resolve_report(
    report_id: int,
    action: str = Query(..., pattern="^(DISMISSED|ACTION_TAKEN)$"),
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    report = db.query(JobReport).filter(JobReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = action
    if action == "ACTION_TAKEN" and report.job:
        # Pause or delete fraudulent job
        report.job.status = "CLOSED"

    db.commit()
    return {"status": report.status, "id": report.id}

# ==========================================
# ADMIN MANAGEMENT ENDPOINTS
# ==========================================
@app.get("/api/admin/stats", response_model=AdminStatsResponse, tags=["Admin"])
def get_admin_stats(
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    total_students = db.query(Student).count()
    total_recruiters = db.query(Recruiter).count()
    total_jobs = db.query(Job).count()
    active_jobs = db.query(Job).filter(Job.status == "ACTIVE").count()
    total_applications = db.query(Application).count()

    total_interviews = db.query(Interview).count()
    scheduled_interviews = db.query(Interview).filter(Interview.status == "SCHEDULED").count()
    completed_interviews = db.query(Interview).filter(Interview.status == "COMPLETED").count()
    cancelled_interviews = db.query(Interview).filter(Interview.status == "CANCELLED").count()

    pending_verifications = db.query(Recruiter).filter(Recruiter.is_verified == False).count()
    pending_user_approvals = db.query(User).filter(User.is_approved == False).count()
    pending_job_approvals = db.query(Job).filter(Job.status == "PENDING_APPROVAL").count()
    total_placed = db.query(Application).filter(Application.status.in_(["ACCEPTED", "OFFERED"])).count()
    reported_jobs = db.query(JobReport).filter(JobReport.status == "PENDING").count()
    upcoming_shifts = db.query(WorkShift).filter(WorkShift.status == "SCHEDULED").count()

    # Skill demand counting
    all_jobs = db.query(Job).all()
    skill_counts = {}
    for j in all_jobs:
        if j.skills and isinstance(j.skills, list):
            for s in j.skills:
                skill_counts[s] = skill_counts.get(s, 0) + 1

    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    most_demanded = [{"skill": k, "count": v} for k, v in sorted_skills]

    # Calculate average match percentage
    all_students = db.query(Student).all()
    student_skills_list = [s.skills for s in all_students if s.skills]
    avg_match = 0.0
    if student_skills_list and all_jobs:
        total_pct = 0
        pairs = 0
        for std_s in student_skills_list[:10]:
            for j in all_jobs[:10]:
                match_res = calculate_job_match(j.skills, std_s)
                total_pct += match_res["match_percentage"]
                pairs += 1
        if pairs > 0:
            avg_match = round(total_pct / pairs, 1)

    total_resumes = db.query(Student).filter(Student.resume_url.isnot(None)).count()

    return {
        "total_students": total_students,
        "total_recruiters": total_recruiters,
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_applications": total_applications,
        "total_interviews": total_interviews,
        "scheduled_interviews": scheduled_interviews,
        "completed_interviews": completed_interviews,
        "cancelled_interviews": cancelled_interviews,
        "pending_verifications": pending_verifications,
        "pending_user_approvals": pending_user_approvals,
        "pending_job_approvals": pending_job_approvals,
        "total_placed": total_placed,
        "reported_jobs": reported_jobs,
        "upcoming_shifts": upcoming_shifts,
        "most_demanded_skills": most_demanded,
        "average_job_match_percentage": avg_match,
        "total_resumes_uploaded": total_resumes,
        "total_students_with_resumes": total_resumes
    }

@app.get("/api/admin/pending-approvals", tags=["Admin"])
def get_pending_approvals(
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    pending_users = db.query(User).filter(User.is_approved == False).order_by(User.created_at.desc()).all()
    pending_jobs = db.query(Job).filter(Job.status == "PENDING_APPROVAL").order_by(Job.created_at.desc()).all()

    return {
        "pending_users": [build_user_response(u) for u in pending_users],
        "pending_jobs": [format_job(j) for j in pending_jobs]
    }

@app.post("/api/admin/users/{user_id}/approve", tags=["Admin"])
async def approve_admin_user(
    user_id: int,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    target.is_approved = True
    if target.recruiter_profile:
        target.recruiter_profile.is_verified = True

    notif = Notification(
        user_id=target.id,
        title="Account Approved by Admin!",
        message="Your account has been officially approved. You now have full access to apply for jobs or post job listings.",
        type="ACCOUNT_APPROVED",
        link="/find-jobs" if target.role == "STUDENT" else "/employer-dashboard"
    )
    db.add(notif)
    db.commit()
    db.refresh(target)

    user_data = build_user_response(target)
    await broadcast({
        "type": "USER_APPROVED",
        "data": user_data,
        "message": f"User {target.name} ({target.role}) has been approved by Admin."
    })
    return {"status": "APPROVED", "user": user_data}

@app.post("/api/admin/jobs/{job_id}/approve", tags=["Admin"])
async def approve_job_offer(
    job_id: int,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == "ACTIVE":
        raise HTTPException(status_code=409, detail="This job is already approved and live")
    if job.status != "PENDING_APPROVAL":
        raise HTTPException(status_code=409, detail="Only pending job listings can be approved")

    job.status = "ACTIVE"
    db.flush()

    # A job offer reaches students only after this explicit admin approval.
    notify_eligible_students(
        db,
        "New Job Offer Approved",
        f"'{job.title}' at {job.company or 'a new employer'} is approved and now available. Pay: {job.pay_rate or job.salary or 'See listing'}. Open Find Jobs to review it.",
        "NEW_JOB",
        "/find-jobs"
    )

    # Tell the recruiter the listing is live.
    if job.recruiter and job.recruiter.user_id:
        notify_user(
            db, job.recruiter.user_id, "Job Offer Approved!",
            f"Your job listing '{job.title}' was approved by Admin and is now live for students to apply.",
            "JOB_APPROVED", "/employer-dashboard"
        )

    db.commit()
    db.refresh(job)
    job_data = format_job(job)
    await broadcast({
        "type": "NEW_JOB",
        "data": job_data,
        "message": f"Job offer approved: {job.title} at {job.company}"
    })
    return job_data

@app.post("/api/admin/jobs/{job_id}/reject", tags=["Admin"])
async def reject_job_offer(
    job_id: int,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "CLOSED"
    db.commit()

    if job.recruiter and job.recruiter.user_id:
        db.add(Notification(
            user_id=job.recruiter.user_id,
            title="Job Offer Rejected",
            message=f"Your job listing '{job.title}' was reviewed and rejected by the Administrator.",
            type="JOB_REJECTED",
            link="/employer-dashboard"
        ))
        db.commit()

    return {"status": "REJECTED", "id": job_id}

@app.get("/api/admin/users", response_model=List[UserResponse], tags=["Admin"])
def get_admin_users(
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).order_by(User.id.asc()).all()
    return [build_user_response(u) for u in users]

@app.post("/api/admin/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Admin"])
def create_admin_user(
    payload: AdminUserCreate,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.email == payload.email.strip().lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    role_clean = payload.role.strip().upper()
    if role_clean not in ["STUDENT", "RECRUITER", "ADMIN"]:
        raise HTTPException(status_code=400, detail="Role must be STUDENT, RECRUITER, or ADMIN")

    new_user = User(
        name=payload.name.strip(),
        email=payload.email.strip().lower(),
        password_hash=hash_password(payload.password),
        role=role_clean,
        is_active=payload.is_active,
        is_approved=payload.is_approved
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if role_clean == "STUDENT":
        std = Student(user_id=new_user.id, college="Campus University", degree="B.Tech", branch="General", skills=["Communication", "Organization"])
        db.add(std)
        db.commit()
    elif role_clean == "RECRUITER":
        rec = Recruiter(user_id=new_user.id, company_name=f"{new_user.name}'s Enterprise", company_email=new_user.email, is_verified=payload.is_approved)
        db.add(rec)
        db.commit()

    return build_user_response(new_user)

@app.patch("/api/admin/users/{user_id}", response_model=UserResponse, tags=["Admin"])
def update_admin_user(
    user_id: int,
    payload: AdminUserUpdate,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.name is not None and payload.name.strip():
        target.name = payload.name.strip()
    if payload.email is not None and payload.email.strip():
        check_dup = db.query(User).filter(User.email == payload.email.strip().lower(), User.id != user_id).first()
        if check_dup:
            raise HTTPException(status_code=400, detail="Email already used by another account")
        target.email = payload.email.strip().lower()
    if payload.role is not None and payload.role.strip().upper() in ["STUDENT", "RECRUITER", "ADMIN"]:
        target.role = payload.role.strip().upper()
    if payload.is_active is not None:
        target.is_active = payload.is_active
    if payload.is_approved is not None:
        target.is_approved = payload.is_approved
        if target.recruiter_profile and payload.is_approved:
            target.recruiter_profile.is_verified = True

    db.commit()
    db.refresh(target)
    return build_user_response(target)

@app.post("/api/admin/users/{user_id}/toggle-status", tags=["Admin"])
def toggle_user_active_status(
    user_id: int,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.role == "ADMIN":
        raise HTTPException(status_code=400, detail="Cannot suspend administrator account")

    target.is_active = not getattr(target, "is_active", True)
    db.commit()
    return {"id": target.id, "is_active": target.is_active}

@app.delete("/api/admin/users/{user_id}", tags=["Admin"])
def delete_admin_user(
    user_id: int,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == user.id:
        raise HTTPException(status_code=400, detail="Cannot delete the administrator account currently in use")

    # ORM relationships cascade profile/application/notification records. Roll back cleanly
    # if a database constraint still prevents deletion.
    try:
        db.delete(target)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Admin user deletion failed for user_id=%s", user_id)
        raise HTTPException(status_code=409, detail="User could not be deleted because related records are still in use")
    return {"status": "DELETED", "id": user_id}

@app.delete("/api/admin/jobs/{job_id}", tags=["Admin"])
def admin_delete_job(
    job_id: int,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete any job status from the administrator's platform-wide job table."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job_title = job.title
    try:
        db.delete(job)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Admin job deletion failed for job_id=%s", job_id)
        raise HTTPException(status_code=409, detail="Job could not be deleted because related records are still in use")
    return {"status": "DELETED", "id": job_id, "title": job_title}

@app.post("/api/admin/employers/verify/{recruiter_id}", tags=["Admin"])
def set_employer_verification(
    recruiter_id: int,
    verify: bool = Query(True),
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    rec = db.query(Recruiter).filter(Recruiter.id == recruiter_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Employer not found")

    rec.is_verified = verify
    rec.verification_notes = "Verified by Administrator." if verify else "Verification revoked by Administrator."
    db.commit()
    return {"id": rec.id, "is_verified": rec.is_verified, "company_name": rec.company_name}

# ==========================================
# WEBSOCKET REAL-TIME BROADCASTER
# ==========================================
@app.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            # Keep-alive loop
            await websocket.receive_text()
    except (WebSocketDisconnect, Exception):
        if websocket in clients:
            clients.remove(websocket)

from datetime import datetime
from typing import List, Optional, Union, Any
from pydantic import BaseModel, ConfigDict

# ==========================================
# AUTHENTICATION & USER SCHEMAS
# ==========================================
class RegisterRequest(BaseModel):
    role: str  # STUDENT, RECRUITER / EMPLOYER
    name: str
    email: str
    password: str
    # Student fields
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    skills: Optional[Union[List[str], str]] = None
    resume_url: Optional[str] = None
    preferred_work_arrangement: Optional[str] = "Any"
    weekly_availability: Optional[str] = "10-15 hrs/week"
    # Recruiter / Employer fields
    company_name: Optional[str] = None
    company_email: Optional[str] = None
    business_description: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class StudentProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    skills: List[str] = []
    resume_url: Optional[str] = None
    experience: Optional[str] = None
    preferred_categories: List[str] = []
    preferred_locations: List[str] = []
    preferred_work_arrangement: Optional[str] = "Any"
    weekly_availability: Optional[str] = "10-15 hrs/week"
    max_weekly_hours: Optional[int] = 20

class StudentProfileView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    skills: List[str] = []
    resume_url: Optional[str] = None
    experience: Optional[str] = None
    preferred_categories: List[str] = []
    preferred_locations: List[str] = []
    preferred_work_arrangement: Optional[str] = "Any"
    weekly_availability: Optional[str] = "10-15 hrs/week"
    max_weekly_hours: Optional[int] = 20

class StudentProfileUpdate(BaseModel):
    name: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    skills: Optional[Union[List[str], str]] = None
    experience: Optional[str] = None
    preferred_categories: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    preferred_work_arrangement: Optional[str] = None
    weekly_availability: Optional[str] = None
    max_weekly_hours: Optional[int] = None

class StudentSkillsResponse(BaseModel):
    skills: List[str]

class ResumeUploadResponse(BaseModel):
    resume_url: str
    filename: str
    uploaded_at: datetime
    detected_skills: List[str] = []
    skills: List[str] = []

class RecruiterProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    company_email: Optional[str] = None
    business_description: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    contact_phone: Optional[str] = None
    is_verified: bool = False

class EmployerProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    company_email: Optional[str] = None
    business_description: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    contact_phone: Optional[str] = None

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    is_active: bool = True
    is_approved: bool = True
    created_at: datetime
    student_profile: Optional[StudentProfileResponse] = None
    recruiter_profile: Optional[RecruiterProfileResponse] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user: UserResponse

class AdminUserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str
    is_active: bool = True
    is_approved: bool = True

class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_approved: Optional[bool] = None

# ==========================================
# JOB SCHEMAS
# ==========================================
class JobCreate(BaseModel):
    title: Optional[str] = None
    role: Optional[str] = None  # alias for backwards compatibility
    company: Optional[str] = None
    description: Optional[str] = ""
    salary: Optional[str] = None  # alias for pay_rate
    package: Optional[str] = None  # alias
    location: Optional[str] = "Remote"
    skills: Optional[Union[List[str], str]] = []
    category: Optional[str] = "Web Development"
    job_type: Optional[str] = "Part-time"
    work_arrangement: Optional[str] = "Remote"
    compensation_type: Optional[str] = "hourly"
    pay_rate: Optional[str] = "₹250 - ₹400/hr"
    min_hourly_pay: Optional[float] = None
    max_hourly_pay: Optional[float] = None
    weekly_hours: Optional[str] = "10-15 hrs/week"
    shift_schedule: Optional[str] = "Flexible"
    vacancies: Optional[int] = 1
    responsibilities: Optional[str] = None
    qualifications: Optional[str] = None
    benefits: Optional[str] = None
    deadline: Optional[datetime] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    salary: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[Union[List[str], str]] = None
    category: Optional[str] = None
    job_type: Optional[str] = None
    work_arrangement: Optional[str] = None
    compensation_type: Optional[str] = None
    pay_rate: Optional[str] = None
    min_hourly_pay: Optional[float] = None
    max_hourly_pay: Optional[float] = None
    weekly_hours: Optional[str] = None
    shift_schedule: Optional[str] = None
    vacancies: Optional[int] = None
    responsibilities: Optional[str] = None
    qualifications: Optional[str] = None
    benefits: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[datetime] = None

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recruiter_id: Optional[int] = None
    title: str
    role: str  # alias for backward-compatibility
    company: str
    description: Optional[str] = ""
    salary: str
    package: str  # alias for backward-compatibility
    location: Optional[str] = ""
    skills: List[str] = []
    status: str = "ACTIVE"
    created_at: datetime

    # Part-time additions
    category: str = "Web Development"
    job_type: str = "Part-time"
    work_arrangement: str = "Remote"
    compensation_type: str = "hourly"
    pay_rate: str = "₹250 - ₹400/hr"
    min_hourly_pay: Optional[float] = None
    max_hourly_pay: Optional[float] = None
    weekly_hours: str = "10-15 hrs/week"
    shift_schedule: str = "Flexible"
    vacancies: int = 1
    responsibilities: Optional[str] = None
    qualifications: Optional[str] = None
    benefits: Optional[str] = None
    deadline: Optional[datetime] = None
    is_employer_verified: bool = False
    is_saved: Optional[bool] = False

    # Match Engine Extensions (Student View)
    match_percentage: Optional[int] = None
    matched_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None

# ==========================================
# APPLICATION SCHEMAS
# ==========================================
class ApplicationCreate(BaseModel):
    job_id: int
    cover_letter: Optional[str] = None
    availability: Optional[str] = None

class ApplicationStatusUpdate(BaseModel):
    status: str

class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    student_id: int
    status: str
    applied_at: datetime
    updated_at: Optional[datetime] = None
    student: Optional[str] = None  # backward-compatibility alias
    student_name: Optional[str] = None
    student_email: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    skills: Optional[List[str]] = []
    job_title: Optional[str] = None
    company: Optional[str] = None
    salary: Optional[str] = None
    location: Optional[str] = None
    resume_url: Optional[str] = None
    cover_letter: Optional[str] = None
    availability: Optional[str] = None

    # Match Engine Extensions (Recruiter View)
    match_percentage: Optional[int] = None
    matched_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    interview_status: Optional[str] = None

# ==========================================
# INTERVIEW & SHIFT SCHEMAS
# ==========================================
class InterviewCreate(BaseModel):
    application_id: int
    scheduled_at: datetime
    mode: str = "ONLINE"  # ONLINE, OFFLINE, HYBRID
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

class InterviewUpdate(BaseModel):
    status: Optional[str] = None  # SCHEDULED, COMPLETED, CANCELLED
    scheduled_at: Optional[datetime] = None
    mode: Optional[str] = None
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

class InterviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    scheduled_at: datetime
    mode: str
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime

    job_id: Optional[int] = None
    job_title: Optional[str] = None
    salary: Optional[str] = None
    package: Optional[str] = None

    student_id: Optional[int] = None
    student_name: Optional[str] = None
    student_email: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = None

    recruiter_id: Optional[int] = None
    company: Optional[str] = None
    company_name: Optional[str] = None

class WorkShiftCreate(BaseModel):
    student_id: int
    job_id: Optional[int] = None
    application_id: Optional[int] = None
    shift_date: datetime
    start_time: str = "17:00"
    end_time: str = "21:00"
    location: str = "Remote / Work from home"
    notes: Optional[str] = None

class WorkShiftUpdate(BaseModel):
    status: Optional[str] = None  # SCHEDULED, COMPLETED, CANCELLED
    notes: Optional[str] = None

class WorkShiftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    job_id: Optional[int] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    shift_date: datetime
    start_time: str
    end_time: str
    location: str
    status: str
    notes: Optional[str] = None
    created_at: datetime

# ==========================================
# SAVED JOBS, NOTIFICATIONS & REPORTS
# ==========================================
class SavedJobResponse(BaseModel):
    id: int
    job_id: int
    saved_at: datetime
    job: JobResponse
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    pay_rate: Optional[str] = None
    salary: Optional[str] = None
    description: Optional[str] = None

class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    link: Optional[str] = None
    created_at: datetime

class JobReportCreate(BaseModel):
    job_id: Optional[int] = None
    reason: str  # Scam, Misleading compensation, Fake employer, Inappropriate, Other
    details: Optional[str] = None

class JobReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    job_title: Optional[str] = None
    company: Optional[str] = None
    user_id: int
    reporter_name: Optional[str] = None
    reason: str
    details: Optional[str] = None
    status: str
    created_at: datetime

# ==========================================
# ADMIN ANALYTICS SCHEMAS
# ==========================================
class SkillDemand(BaseModel):
    skill: str
    count: int

class AdminStatsResponse(BaseModel):
    total_students: int
    total_recruiters: int
    total_jobs: int
    total_applications: int
    total_interviews: int = 0
    scheduled_interviews: int = 0
    completed_interviews: int = 0
    cancelled_interviews: int = 0
    # PartTime extensions
    active_jobs: int = 0
    pending_verifications: int = 0
    pending_user_approvals: int = 0
    pending_job_approvals: int = 0
    total_placed: int = 0
    reported_jobs: int = 0
    upcoming_shifts: int = 0
    # Resume & Matching Analytics
    most_demanded_skills: List[SkillDemand] = []
    average_job_match_percentage: float = 0.0
    total_resumes_uploaded: int = 0
    total_students_with_resumes: int = 0

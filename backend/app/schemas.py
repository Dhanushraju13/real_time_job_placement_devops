from datetime import datetime
from typing import List, Optional, Union, Any
from pydantic import BaseModel, ConfigDict

class RegisterRequest(BaseModel):
    role: str
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
    # Recruiter fields
    company_name: Optional[str] = None
    company_email: Optional[str] = None

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

class StudentProfileUpdate(BaseModel):
    name: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    skills: Optional[Union[List[str], str]] = None

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

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    created_at: datetime
    student_profile: Optional[StudentProfileResponse] = None
    recruiter_profile: Optional[RecruiterProfileResponse] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user: UserResponse

class JobCreate(BaseModel):
    title: Optional[str] = None
    role: Optional[str] = None  # alias for backwards compatibility
    company: Optional[str] = None
    description: Optional[str] = ""
    salary: Optional[str] = None
    package: Optional[str] = None  # alias
    location: Optional[str] = "Remote"
    skills: Optional[Union[List[str], str]] = []

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

    # Match Engine Extensions (Student View)
    match_percentage: Optional[int] = None
    matched_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None

class ApplicationCreate(BaseModel):
    job_id: int

class ApplicationStatusUpdate(BaseModel):
    status: str

class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    student_id: int
    status: str
    applied_at: datetime
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

    # Match Engine Extensions (Recruiter View)
    match_percentage: Optional[int] = None
    matched_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    interview_status: Optional[str] = None

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

    # Job information
    job_id: Optional[int] = None
    job_title: Optional[str] = None
    salary: Optional[str] = None
    package: Optional[str] = None

    # Student information
    student_id: Optional[int] = None
    student_name: Optional[str] = None
    student_email: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = None

    # Recruiter/Company information
    recruiter_id: Optional[int] = None
    company: Optional[str] = None
    company_name: Optional[str] = None

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
    # Resume & Matching Analytics
    most_demanded_skills: List[SkillDemand] = []
    average_job_match_percentage: float = 0.0
    total_resumes_uploaded: int = 0
    total_students_with_resumes: int = 0

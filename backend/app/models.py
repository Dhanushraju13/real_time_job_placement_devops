from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, Boolean, UniqueConstraint, inspect, text
from sqlalchemy.orm import relationship
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # 'STUDENT', 'RECRUITER'/'EMPLOYER', 'ADMIN'
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    # 1-to-1 relationships
    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    recruiter_profile = relationship("Recruiter", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    job_reports = relationship("JobReport", back_populates="user", cascade="all, delete-orphan")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    college = Column(String(255), nullable=True)
    degree = Column(String(100), nullable=True)
    branch = Column(String(100), nullable=True)
    cgpa = Column(Float, nullable=True)
    skills = Column(JSON, default=list)
    resume_url = Column(String(500), nullable=True)

    # Part-time profile extensions
    experience = Column(Text, nullable=True)
    preferred_categories = Column(JSON, default=list)
    preferred_locations = Column(JSON, default=list)
    preferred_work_arrangement = Column(String(50), default="Any")  # Remote, On-site, Hybrid, Any
    weekly_availability = Column(String(100), default="10-15 hrs/week")
    max_weekly_hours = Column(Integer, default=20)

    user = relationship("User", back_populates="student_profile")
    applications = relationship("Application", back_populates="student", cascade="all, delete-orphan")
    saved_jobs = relationship("SavedJob", back_populates="student", cascade="all, delete-orphan")
    shifts = relationship("WorkShift", back_populates="student", cascade="all, delete-orphan")

class Recruiter(Base):
    __tablename__ = "recruiters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    company_email = Column(String(255), nullable=True)

    # Employer profile extensions
    business_description = Column(Text, nullable=True)
    industry = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="recruiter_profile")
    jobs = relationship("Job", back_populates="recruiter", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("recruiters.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    salary = Column(String(100), nullable=True)  # Backward compat alias for pay
    location = Column(String(255), nullable=True)
    skills = Column(JSON, default=list)
    status = Column(String(50), default="ACTIVE")  # ACTIVE, PAUSED, CLOSED
    created_at = Column(DateTime(timezone=True), default=utcnow)

    # Part-time job specifications
    category = Column(String(100), default="Web Development")
    job_type = Column(String(50), default="Part-time")  # Part-time, Weekend-only, Evening shifts, Flexible, Remote, Freelance
    work_arrangement = Column(String(50), default="Remote")  # Remote, On-site, Hybrid
    compensation_type = Column(String(50), default="hourly")  # hourly, shift, monthly
    pay_rate = Column(String(100), default="₹250 - ₹400/hr")
    min_hourly_pay = Column(Float, nullable=True)
    max_hourly_pay = Column(Float, nullable=True)
    weekly_hours = Column(String(100), default="10-15 hrs/week")
    shift_schedule = Column(String(100), default="Flexible")  # Weekdays, Evenings, Weekends, Flexible
    vacancies = Column(Integer, default=1)
    responsibilities = Column(Text, nullable=True)
    qualifications = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)

    recruiter = relationship("Recruiter", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    saved_by = relationship("SavedJob", back_populates="job", cascade="all, delete-orphan")
    reports = relationship("JobReport", back_populates="job", cascade="all, delete-orphan")
    shifts = relationship("WorkShift", back_populates="job", cascade="all, delete-orphan")

class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    saved_at = Column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (UniqueConstraint("student_id", "job_id", name="uq_student_saved_job"),)

    student = relationship("Student", back_populates="saved_jobs")
    job = relationship("Job", back_populates="saved_by")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="APPLIED")  # APPLIED/SUBMITTED, UNDER_REVIEW, SHORTLISTED, INTERVIEW, OFFERED, ACCEPTED, REJECTED, WITHDRAWN
    applied_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # Application details
    cover_letter = Column(Text, nullable=True)
    availability = Column(String(255), nullable=True)

    job = relationship("Job", back_populates="applications")
    student = relationship("Student", back_populates="applications")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")
    shifts = relationship("WorkShift", back_populates="application", cascade="all, delete-orphan")

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    mode = Column(String(50), nullable=False, default="ONLINE")  # 'ONLINE', 'OFFLINE', 'HYBRID'
    meeting_link = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="SCHEDULED")  # 'SCHEDULED', 'COMPLETED', 'CANCELLED'
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    application = relationship("Application", back_populates="interviews")

class WorkShift(Base):
    __tablename__ = "work_shifts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)
    shift_date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(String(20), default="17:00")
    end_time = Column(String(20), default="21:00")
    location = Column(String(255), default="Remote / Work from home")
    status = Column(String(50), default="SCHEDULED")  # SCHEDULED, COMPLETED, CANCELLED
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    student = relationship("Student", back_populates="shifts")
    job = relationship("Job", back_populates="shifts")
    application = relationship("Application", back_populates="shifts")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="GENERAL")  # APPLICATION_STATUS, INTERVIEW_SCHEDULED, JOB_OFFER, NEW_JOB, SHIFT_REMINDER
    is_read = Column(Boolean, default=False)
    link = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    user = relationship("User", back_populates="notifications")

class JobReport(Base):
    __tablename__ = "job_reports"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reason = Column(String(100), nullable=False)  # Scam, Misleading compensation, Fake employer, Inappropriate, Other
    details = Column(Text, nullable=True)
    status = Column(String(50), default="PENDING")  # PENDING, REVIEWED, DISMISSED, ACTION_TAKEN
    created_at = Column(DateTime(timezone=True), default=utcnow)

    job = relationship("Job", back_populates="reports")
    user = relationship("User", back_populates="job_reports")

def ensure_schema_compatibility(engine):
    """
    Safely inspects existing tables and adds missing columns without dropping data.
    Works seamlessly on both PostgreSQL and SQLite.
    """
    inspector = inspect(engine)
    dialect_name = engine.dialect.name

    columns_to_check = {
        "users": [
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("is_approved", "BOOLEAN DEFAULT TRUE")
        ],
        "students": [
            ("experience", "TEXT"),
            ("preferred_categories", "JSON" if dialect_name == "postgresql" else "TEXT"),
            ("preferred_locations", "JSON" if dialect_name == "postgresql" else "TEXT"),
            ("preferred_work_arrangement", "VARCHAR(50) DEFAULT 'Any'"),
            ("weekly_availability", "VARCHAR(100) DEFAULT '10-15 hrs/week'"),
            ("max_weekly_hours", "INTEGER DEFAULT 20")
        ],
        "recruiters": [
            ("business_description", "TEXT"),
            ("industry", "VARCHAR(100)"),
            ("website", "VARCHAR(255)"),
            ("location", "VARCHAR(255)"),
            ("contact_phone", "VARCHAR(50)"),
            ("is_verified", "BOOLEAN DEFAULT FALSE"),
            ("verification_notes", "TEXT")
        ],
        "jobs": [
            ("category", "VARCHAR(100) DEFAULT 'Web Development'"),
            ("job_type", "VARCHAR(50) DEFAULT 'Part-time'"),
            ("work_arrangement", "VARCHAR(50) DEFAULT 'Remote'"),
            ("compensation_type", "VARCHAR(50) DEFAULT 'hourly'"),
            ("pay_rate", "VARCHAR(100) DEFAULT '₹250 - ₹400/hr'"),
            ("min_hourly_pay", "FLOAT"),
            ("max_hourly_pay", "FLOAT"),
            ("weekly_hours", "VARCHAR(100) DEFAULT '10-15 hrs/week'"),
            ("shift_schedule", "VARCHAR(100) DEFAULT 'Flexible'"),
            ("vacancies", "INTEGER DEFAULT 1"),
            ("responsibilities", "TEXT"),
            ("qualifications", "TEXT"),
            ("benefits", "TEXT"),
            ("deadline", "TIMESTAMP WITH TIME ZONE" if dialect_name == "postgresql" else "DATETIME")
        ],
        "applications": [
            ("cover_letter", "TEXT"),
            ("availability", "VARCHAR(255)"),
            ("updated_at", "TIMESTAMP WITH TIME ZONE" if dialect_name == "postgresql" else "DATETIME")
        ]
    }

    with engine.connect() as conn:
        for table_name, cols in columns_to_check.items():
            if inspector.has_table(table_name):
                existing_cols = {c["name"] for c in inspector.get_columns(table_name)}
                for col_name, col_def in cols:
                    if col_name not in existing_cols:
                        try:
                            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}"))
                            conn.commit()
                        except Exception:
                            pass

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
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
    role = Column(String(50), nullable=False)  # 'STUDENT', 'RECRUITER', 'ADMIN'
    created_at = Column(DateTime(timezone=True), default=utcnow)

    # 1-to-1 relationships
    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    recruiter_profile = relationship("Recruiter", back_populates="user", uselist=False, cascade="all, delete-orphan")

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

    user = relationship("User", back_populates="student_profile")
    applications = relationship("Application", back_populates="student", cascade="all, delete-orphan")

class Recruiter(Base):
    __tablename__ = "recruiters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    company_email = Column(String(255), nullable=True)

    user = relationship("User", back_populates="recruiter_profile")
    jobs = relationship("Job", back_populates="recruiter", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("recruiters.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    salary = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    skills = Column(JSON, default=list)
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime(timezone=True), default=utcnow)

    recruiter = relationship("Recruiter", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="APPLIED")
    applied_at = Column(DateTime(timezone=True), default=utcnow)

    job = relationship("Job", back_populates="applications")
    student = relationship("Student", back_populates="applications")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")

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

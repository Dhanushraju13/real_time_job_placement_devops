import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import User, Student, Recruiter, Job, Application, Interview
from app.auth import hash_password
from app.config import (
    INITIAL_ADMIN_NAME,
    INITIAL_ADMIN_EMAIL,
    INITIAL_ADMIN_PASSWORD
)

logger = logging.getLogger("placement.seed")

def seed_database(db: Session = None):
    Base.metadata.create_all(bind=engine)

    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True

    try:
        # Check if users already exist
        admin_exists = db.query(User).filter(User.role == "ADMIN").first()
        if not admin_exists:
            logger.info("Seeding initial admin user...")
            admin_user = User(
                name=INITIAL_ADMIN_NAME,
                email=INITIAL_ADMIN_EMAIL.lower(),
                password_hash=hash_password(INITIAL_ADMIN_PASSWORD),
                role="ADMIN"
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

        # Check if sample recruiters and students exist
        technova_user = db.query(User).filter(User.email == "recruiter@technova.com").first()
        if not technova_user:
            logger.info("Seeding sample recruiter: TechNova...")
            technova_user = User(
                name="TechNova Recruiter",
                email="recruiter@technova.com",
                password_hash=hash_password("Recruiter@123"),
                role="RECRUITER"
            )
            db.add(technova_user)
            db.commit()
            db.refresh(technova_user)

            technova_recruiter = Recruiter(
                user_id=technova_user.id,
                company_name="TechNova",
                company_email="careers@technova.com"
            )
            db.add(technova_recruiter)
            db.commit()
            db.refresh(technova_recruiter)

        abc_user = db.query(User).filter(User.email == "recruiter@abc.com").first()
        if not abc_user:
            logger.info("Seeding sample recruiter: ABC Technologies...")
            abc_user = User(
                name="ABC HR",
                email="recruiter@abc.com",
                password_hash=hash_password("Recruiter@123"),
                role="RECRUITER"
            )
            db.add(abc_user)
            db.commit()
            db.refresh(abc_user)

            abc_recruiter = Recruiter(
                user_id=abc_user.id,
                company_name="ABC Technologies",
                company_email="jobs@abctech.com"
            )
            db.add(abc_recruiter)
            db.commit()
            db.refresh(abc_recruiter)

        student_user = db.query(User).filter(User.email == "dhanush@college.edu").first()
        if not student_user:
            logger.info("Seeding sample student: Dhanush...")
            student_user = User(
                name="Dhanush",
                email="dhanush@college.edu",
                password_hash=hash_password("Student@123"),
                role="STUDENT"
            )
            db.add(student_user)
            db.commit()
            db.refresh(student_user)

            dhanush_student = Student(
                user_id=student_user.id,
                college="National Institute of Technology",
                degree="B.Tech",
                branch="Computer Science",
                cgpa=8.9,
                skills=["Python", "FastAPI", "React", "Docker", "PostgreSQL"],
                resume_url="https://example.com/resumes/dhanush.pdf"
            )
            db.add(dhanush_student)
            db.commit()
            db.refresh(dhanush_student)

        # Check and seed sample jobs
        job_count = db.query(Job).count()
        if job_count == 0:
            logger.info("Seeding initial jobs...")
            abc_rec = db.query(Recruiter).filter(Recruiter.company_name == "ABC Technologies").first()
            technova_rec = db.query(Recruiter).filter(Recruiter.company_name == "TechNova").first()

            job1 = Job(
                recruiter_id=abc_rec.id if abc_rec else None,
                title="Backend Developer",
                company="ABC Technologies",
                description="Looking for an experienced backend developer proficient in Java, SQL, and RESTful APIs to build scalable microservices.",
                salary="8 LPA",
                location="Bangalore",
                skills=["Java", "SQL", "REST API"],
                status="ACTIVE"
            )
            job2 = Job(
                recruiter_id=technova_rec.id if technova_rec else None,
                title="Python Developer",
                company="TechNova",
                description="Fast-growing startup looking for Python FastAPI developers with strong database design and DevOps knowledge.",
                salary="7 LPA",
                location="Remote",
                skills=["Python", "FastAPI", "PostgreSQL"],
                status="ACTIVE"
            )
            job3 = Job(
                recruiter_id=technova_rec.id if technova_rec else None,
                title="DevOps Engineer",
                company="TechNova",
                description="Build, maintain, and optimize CI/CD pipelines, Docker containers, and Kubernetes clusters for cloud deployments.",
                salary="10 LPA",
                location="Hyderabad",
                skills=["Docker", "Kubernetes", "CI/CD", "AWS"],
                status="ACTIVE"
            )
            db.add_all([job1, job2, job3])
            db.commit()
            db.refresh(job1)
            db.refresh(job2)
            db.refresh(job3)

            # Check and seed sample application
            dhanush_std = db.query(Student).filter(Student.cgpa == 8.9).first()
            if dhanush_std and job1:
                app1 = Application(
                    job_id=job1.id,
                    student_id=dhanush_std.id,
                    status="INTERVIEW"
                )
                app2 = Application(
                    job_id=job2.id,
                    student_id=dhanush_std.id,
                    status="APPLIED"
                )
                db.add_all([app1, app2])
                db.commit()
                db.refresh(app1)

                # Seed sample interview
                interview1 = Interview(
                    application_id=app1.id,
                    scheduled_at=datetime.now(timezone.utc) + timedelta(days=2, hours=3),
                    mode="ONLINE",
                    meeting_link="https://meet.google.com/placement-abctech-interview",
                    location="Google Meet",
                    status="SCHEDULED",
                    notes="Technical round covering Java, SQL, and System Design."
                )
                db.add(interview1)
                db.commit()

        # Ensure at least one sample interview exists
        interview_count = db.query(Interview).count()
        if interview_count == 0:
            first_app = db.query(Application).first()
            if first_app:
                first_app.status = "INTERVIEW"
                interview1 = Interview(
                    application_id=first_app.id,
                    scheduled_at=datetime.now(timezone.utc) + timedelta(days=2, hours=3),
                    mode="ONLINE",
                    meeting_link="https://meet.google.com/placement-technova-interview",
                    location="Google Meet",
                    status="SCHEDULED",
                    notes="Technical round covering core engineering and coding skills."
                )
                db.add(interview1)
                db.commit()

        logger.info("Database seeding completed successfully.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        if owns_session:
            db.close()

if __name__ == "__main__":
    seed_database()

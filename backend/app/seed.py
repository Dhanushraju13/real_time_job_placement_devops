import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import (
    User, Student, Recruiter, Job, Application, Interview,
    SavedJob, WorkShift, Notification, JobReport, ensure_schema_compatibility
)
from app.auth import hash_password
from app.config import (
    INITIAL_ADMIN_NAME,
    INITIAL_ADMIN_EMAIL,
    INITIAL_ADMIN_PASSWORD
)

logger = logging.getLogger("parttime.seed")

def seed_database(db: Session = None):
    # Ensure all tables exist and any new columns are present
    Base.metadata.create_all(bind=engine)
    ensure_schema_compatibility(engine)

    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True

    try:
        # 1. Seed or update Initial Admin User
        admin_user = db.query(User).filter(User.role == "ADMIN").first()
        if not admin_user:
            logger.info("Seeding initial admin user...")
            admin_user = User(
                name=INITIAL_ADMIN_NAME,
                email=INITIAL_ADMIN_EMAIL.lower(),
                password_hash=hash_password(INITIAL_ADMIN_PASSWORD),
                role="ADMIN",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

        # 2. Seed Employers (TechNova - Verified, ABC - Unverified)
        technova_user = db.query(User).filter(User.email == "recruiter@technova.com").first()
        if not technova_user:
            logger.info("Seeding TechNova Employer...")
            technova_user = User(
                name="TechNova Hiring Team",
                email="recruiter@technova.com",
                password_hash=hash_password("Recruiter@123"),
                role="RECRUITER",
                is_active=True
            )
            db.add(technova_user)
            db.commit()
            db.refresh(technova_user)

            technova_recruiter = Recruiter(
                user_id=technova_user.id,
                company_name="TechNova Solutions",
                company_email="careers@technova.com",
                business_description="Innovative software and digital media agency connecting student talent with flexible tech projects.",
                industry="Software & Digital Media",
                website="https://technova.io",
                location="Bangalore (Hybrid)",
                contact_phone="+91 98765 43210",
                is_verified=True,
                verification_notes="Verified registered business entity."
            )
            db.add(technova_recruiter)
            db.commit()
            db.refresh(technova_recruiter)
        else:
            rec = technova_user.recruiter_profile
            if rec and not rec.is_verified:
                rec.is_verified = True
                db.commit()

        abc_user = db.query(User).filter(User.email == "recruiter@abc.com").first()
        if not abc_user:
            logger.info("Seeding ABC Technologies Employer...")
            abc_user = User(
                name="ABC Tech HR",
                email="recruiter@abc.com",
                password_hash=hash_password("Recruiter@123"),
                role="RECRUITER",
                is_active=True,
                is_approved=True
            )
            db.add(abc_user)
            db.commit()
            db.refresh(abc_user)

            abc_recruiter = Recruiter(
                user_id=abc_user.id,
                company_name="ABC Technologies",
                company_email="jobs@abctech.com",
                business_description="Emerging educational and logistics platform providing on-demand student shifts.",
                industry="Education & Logistics",
                website="https://abctech.example.com",
                location="Hyderabad",
                contact_phone="+91 91234 56789",
                is_verified=False,
                verification_notes="Pending official registration review."
            )
            db.add(abc_recruiter)
            db.commit()
            db.refresh(abc_recruiter)

        # PixelPulse Studios
        pixel_user = db.query(User).filter(User.email == "recruiter@pixelpulse.com").first()
        if not pixel_user:
            pixel_user = User(
                name="PixelPulse Creative",
                email="recruiter@pixelpulse.com",
                password_hash=hash_password("Recruiter@123"),
                role="RECRUITER",
                is_active=True,
                is_approved=True
            )
            db.add(pixel_user)
            db.commit()
            db.refresh(pixel_user)

            pixel_rec = Recruiter(
                user_id=pixel_user.id,
                company_name="PixelPulse Studios",
                company_email="careers@pixelpulse.com",
                business_description="Digital media and video production studio hiring college video editors and graphic designers.",
                industry="Media & Entertainment",
                website="https://pixelpulse.media",
                location="Mumbai (Remote)",
                contact_phone="+91 98111 22334",
                is_verified=True,
                verification_notes="Verified digital agency partner."
            )
            db.add(pixel_rec)
            db.commit()

        # EduSpark Tutoring
        eduspark_user = db.query(User).filter(User.email == "recruiter@eduspark.com").first()
        if not eduspark_user:
            eduspark_user = User(
                name="EduSpark Academy",
                email="recruiter@eduspark.com",
                password_hash=hash_password("Recruiter@123"),
                role="RECRUITER",
                is_active=True,
                is_approved=True
            )
            db.add(eduspark_user)
            db.commit()
            db.refresh(eduspark_user)

            eduspark_rec = Recruiter(
                user_id=eduspark_user.id,
                company_name="EduSpark Tutoring",
                company_email="tutors@eduspark.org",
                business_description="K-12 peer-to-peer tutoring network offering high hourly pay for top college students.",
                industry="EdTech & Tutoring",
                website="https://eduspark.org",
                location="Delhi / Remote",
                contact_phone="+91 98222 33445",
                is_verified=True,
                verification_notes="Verified online tutoring partner."
            )
            db.add(eduspark_rec)
            db.commit()

        # CodeCraft Labs - Pending Admin Approval for demo testing!
        codecraft_user = db.query(User).filter(User.email == "recruiter@codecraft.com").first()
        if not codecraft_user:
            codecraft_user = User(
                name="CodeCraft Founders",
                email="recruiter@codecraft.com",
                password_hash=hash_password("Recruiter@123"),
                role="RECRUITER",
                is_active=True,
                is_approved=False  # Pending approval!
            )
            db.add(codecraft_user)
            db.commit()
            db.refresh(codecraft_user)

            codecraft_rec = Recruiter(
                user_id=codecraft_user.id,
                company_name="CodeCraft Labs",
                company_email="hello@codecraftlabs.dev",
                business_description="Early stage developer tools and cloud consultancy.",
                industry="Cloud & DevOps",
                website="https://codecraftlabs.dev",
                location="Bangalore",
                contact_phone="+91 98333 44556",
                is_verified=False,
                verification_notes="New employer awaiting admin verification."
            )
            db.add(codecraft_rec)
            db.commit()
            db.refresh(codecraft_rec)
        else:
            codecraft_rec = codecraft_user.recruiter_profile

        # 3. Seed Students
        # Dhanush
        student_user = db.query(User).filter(User.email == "dhanush@college.edu").first()
        if not student_user:
            logger.info("Seeding sample student: Dhanush...")
            student_user = User(
                name="Dhanush",
                email="dhanush@college.edu",
                password_hash=hash_password("Student@123"),
                role="STUDENT",
                is_active=True,
                is_approved=True
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
                skills=["Python", "FastAPI", "React", "Video Editing", "Content Writing", "Docker", "SQL"],
                resume_url="https://example.com/resumes/dhanush.pdf",
                experience="Freelance web development and video editor for college tech fest.",
                preferred_categories=["Web Development", "Video Editing", "Online Tutoring"],
                preferred_locations=["Remote", "Bangalore"],
                preferred_work_arrangement="Remote",
                weekly_availability="15-20 hrs/week (Evenings & Weekends)",
                max_weekly_hours=20
            )
            db.add(dhanush_student)
            db.commit()
            db.refresh(dhanush_student)
        else:
            dhanush_student = student_user.student_profile

        # Priya Sharma
        priya_user = db.query(User).filter(User.email == "priya.sharma@college.edu").first()
        if not priya_user:
            priya_user = User(
                name="Priya Sharma",
                email="priya.sharma@college.edu",
                password_hash=hash_password("Student@123"),
                role="STUDENT",
                is_active=True,
                is_approved=True
            )
            db.add(priya_user)
            db.commit()
            db.refresh(priya_user)

            priya_student = Student(
                user_id=priya_user.id,
                college="BITS Pilani",
                degree="B.E.",
                branch="Computer Science",
                cgpa=9.2,
                skills=["React", "TypeScript", "UI/UX", "Figma", "Node.js", "Tailwind CSS"],
                resume_url="https://example.com/resumes/priya.pdf",
                experience="Built dashboard components and interactive prototypes for college startup club.",
                preferred_categories=["Web Development", "Graphic Design"],
                preferred_locations=["Remote"],
                preferred_work_arrangement="Remote",
                weekly_availability="12-15 hrs/week",
                max_weekly_hours=18
            )
            db.add(priya_student)
            db.commit()

        # Ananya Roy
        ananya_user = db.query(User).filter(User.email == "ananya.roy@college.edu").first()
        if not ananya_user:
            ananya_user = User(
                name="Ananya Roy",
                email="ananya.roy@college.edu",
                password_hash=hash_password("Student@123"),
                role="STUDENT",
                is_active=True,
                is_approved=True
            )
            db.add(ananya_user)
            db.commit()
            db.refresh(ananya_user)

            ananya_student = Student(
                user_id=ananya_user.id,
                college="Delhi University",
                degree="B.A. Hons",
                branch="English & Communications",
                cgpa=8.7,
                skills=["Content Writing", "SEO", "Copywriting", "Social Media Management", "Canva"],
                resume_url="https://example.com/resumes/ananya.pdf",
                experience="Chief Editor of college magazine, managed campus brand ambassador social channels.",
                preferred_categories=["Content Writing", "Social Media Management"],
                preferred_locations=["Remote"],
                preferred_work_arrangement="Remote",
                weekly_availability="10-15 hrs/week",
                max_weekly_hours=15
            )
            db.add(ananya_student)
            db.commit()

        # Rahul Verma
        rahul_user = db.query(User).filter(User.email == "rahul.v@college.edu").first()
        if not rahul_user:
            rahul_user = User(
                name="Rahul Verma",
                email="rahul.v@college.edu",
                password_hash=hash_password("Student@123"),
                role="STUDENT",
                is_active=True,
                is_approved=True
            )
            db.add(rahul_user)
            db.commit()
            db.refresh(rahul_user)

            rahul_student = Student(
                user_id=rahul_user.id,
                college="SRM Institute",
                degree="B.Com",
                branch="Accounting & Finance",
                cgpa=8.1,
                skills=["Excel", "Data Entry", "Accounting", "Tally", "Financial Modeling"],
                resume_url="https://example.com/resumes/rahul.pdf",
                experience="Spreadsheet management and bookkeeping for local small business.",
                preferred_categories=["Data Entry", "Retail and Sales"],
                preferred_locations=["Chennai", "Remote"],
                preferred_work_arrangement="Hybrid",
                weekly_availability="15-20 hrs/week",
                max_weekly_hours=20
            )
            db.add(rahul_student)
            db.commit()

        # Sneha Patel
        sneha_user = db.query(User).filter(User.email == "sneha.p@college.edu").first()
        if not sneha_user:
            sneha_user = User(
                name="Sneha Patel",
                email="sneha.p@college.edu",
                password_hash=hash_password("Student@123"),
                role="STUDENT",
                is_active=True,
                is_approved=True
            )
            db.add(sneha_user)
            db.commit()
            db.refresh(sneha_user)

            sneha_student = Student(
                user_id=sneha_user.id,
                college="IIT Madras",
                degree="B.Tech",
                branch="Electrical Engineering",
                cgpa=8.8,
                skills=["Video Editing", "Premiere Pro", "After Effects", "Motion Graphics", "YouTube SEO"],
                resume_url="https://example.com/resumes/sneha.pdf",
                experience="Edited 40+ educational video modules with over 150K views.",
                preferred_categories=["Video Editing", "Graphic Design"],
                preferred_locations=["Remote"],
                preferred_work_arrangement="Remote",
                weekly_availability="12-16 hrs/week",
                max_weekly_hours=20
            )
            db.add(sneha_student)
            db.commit()

        # Rohan Gupta - Pending Admin Approval!
        rohan_user = db.query(User).filter(User.email == "rohan.g@college.edu").first()
        if not rohan_user:
            rohan_user = User(
                name="Rohan Gupta",
                email="rohan.g@college.edu",
                password_hash=hash_password("Student@123"),
                role="STUDENT",
                is_active=True,
                is_approved=False  # Pending approval!
            )
            db.add(rohan_user)
            db.commit()
            db.refresh(rohan_user)

            rohan_student = Student(
                user_id=rohan_user.id,
                college="Vellore Institute of Technology",
                degree="B.Tech",
                branch="Information Technology",
                cgpa=7.9,
                skills=["Java", "SQL", "HTML/CSS", "Customer Support"],
                resume_url="https://example.com/resumes/rohan.pdf",
                experience="Campus lab technician and peer tutor.",
                preferred_categories=["Customer Support", "Campus Assistant"],
                preferred_locations=["Remote"],
                preferred_work_arrangement="Remote",
                weekly_availability="10-12 hrs/week",
                max_weekly_hours=15
            )
            db.add(rohan_student)
            db.commit()

        # 4. Seed 8 Realistic Part-Time Job Listings in INR (₹)
        technova_rec = db.query(Recruiter).filter(Recruiter.company_name == "TechNova Solutions").first()
        abc_rec = db.query(Recruiter).filter(Recruiter.company_name == "ABC Technologies").first()

        sample_parttime_jobs = [
            {
                "title": "Frontend Developer Assistant",
                "company": "TechNova Solutions",
                "recruiter_id": technova_rec.id if technova_rec else None,
                "category": "Web Development",
                "job_type": "Part-time",
                "work_arrangement": "Remote",
                "compensation_type": "hourly",
                "pay_rate": "₹250 - ₹400/hr",
                "min_hourly_pay": 250.0,
                "max_hourly_pay": 400.0,
                "salary": "₹250 - ₹400/hr",
                "weekly_hours": "10-15 hrs/week",
                "shift_schedule": "Flexible",
                "location": "Remote",
                "vacancies": 2,
                "skills": ["React", "JavaScript", "HTML", "CSS", "Git"],
                "description": "Assist our UI team in building interactive, responsive web components and landing pages for client products. Flexible hours around your lecture schedule.",
                "responsibilities": "Develop modular React components, test cross-browser compatibility, fix CSS styling bugs, and collaborate via GitHub.",
                "qualifications": "Undergraduate pursuing CS or related branch. Good working knowledge of HTML, CSS, JavaScript, and React.",
                "benefits": "Mentorship from senior engineers, certificate of experience, 100% remote work.",
                "deadline": datetime.now(timezone.utc) + timedelta(days=30),
                "status": "ACTIVE"
            },
            {
                "title": "Online Mathematics Tutor",
                "company": "ABC Technologies",
                "recruiter_id": abc_rec.id if abc_rec else None,
                "category": "Online Tutoring",
                "job_type": "Part-time",
                "work_arrangement": "Remote",
                "compensation_type": "hourly",
                "pay_rate": "₹300 - ₹500/hr",
                "min_hourly_pay": 300.0,
                "max_hourly_pay": 500.0,
                "salary": "₹300 - ₹500/hr",
                "weekly_hours": "8-12 hrs/week",
                "shift_schedule": "Evenings & Weekends",
                "location": "Online",
                "vacancies": 3,
                "skills": ["Mathematics", "Tutoring", "Communication"],
                "description": "Provide 1-on-1 and small group online tutoring for high school students in calculus, algebra, and physics via Google Meet.",
                "responsibilities": "Deliver 1-hour interactive sessions, prepare practice problems, and clarify student doubts.",
                "qualifications": "Strong foundation in 11th/12th grade mathematics. Patient and articulate communication style.",
                "benefits": "Flexible scheduling, choose your own hours between 5 PM and 9 PM.",
                "deadline": datetime.now(timezone.utc) + timedelta(days=25),
                "status": "ACTIVE"
            },
            {
                "title": "Video Editor & Reels Creator",
                "company": "TechNova Solutions",
                "recruiter_id": technova_rec.id if technova_rec else None,
                "category": "Video Editing",
                "job_type": "Freelance",
                "work_arrangement": "Hybrid",
                "compensation_type": "hourly",
                "pay_rate": "₹400 - ₹700/hr",
                "min_hourly_pay": 400.0,
                "max_hourly_pay": 700.0,
                "salary": "₹400 - ₹700/hr",
                "weekly_hours": "12-15 hrs/week",
                "shift_schedule": "Flexible",
                "location": "Bangalore / Hybrid",
                "vacancies": 1,
                "skills": ["Video Editing", "Premiere Pro", "Photoshop", "Social Media"],
                "description": "Edit high-engagement short-form videos (Reels, TikToks, YouTube Shorts) and tech product demos.",
                "responsibilities": "Cut raw video footage, add subtitles, motion graphics, audio sync, and export optimized assets.",
                "qualifications": "Proficiency with Adobe Premiere Pro or DaVinci Resolve. Portfolio or links to prior reels required.",
                "benefits": "Creative freedom, fast weekly payouts, high project bonuses.",
                "deadline": datetime.now(timezone.utc) + timedelta(days=20),
                "status": "ACTIVE"
            },
            {
                "title": "Campus IT Support Assistant",
                "company": "ABC Technologies",
                "recruiter_id": abc_rec.id if abc_rec else None,
                "category": "Campus Assistant",
                "job_type": "Evening shifts",
                "work_arrangement": "On-site",
                "compensation_type": "hourly",
                "pay_rate": "₹150 - ₹250/hr",
                "min_hourly_pay": 150.0,
                "max_hourly_pay": 250.0,
                "salary": "₹150 - ₹250/hr",
                "weekly_hours": "10-12 hrs/week",
                "shift_schedule": "Evening shifts",
                "location": "Campus Computer Labs",
                "vacancies": 4,
                "skills": ["Linux", "Hardware", "Troubleshooting", "Customer Support"],
                "description": "Assist students and faculty with lab PC maintenance, projector setup, Wi-Fi connectivity, and printer configurations.",
                "responsibilities": "Supervise computer labs during 5 PM - 8 PM shifts, log hardware issues, troubleshoot basic OS problems.",
                "qualifications": "Basic computer hardware and networking knowledge. Punctual and reliable.",
                "benefits": "Work directly on campus, free access to lab resources during off-hours.",
                "deadline": datetime.now(timezone.utc) + timedelta(days=15),
                "status": "ACTIVE"
            },
            {
                "title": "Social Media & Community Assistant",
                "company": "TechNova Solutions",
                "recruiter_id": technova_rec.id if technova_rec else None,
                "category": "Social Media Management",
                "job_type": "Part-time",
                "work_arrangement": "Remote",
                "compensation_type": "hourly",
                "pay_rate": "₹200 - ₹350/hr",
                "min_hourly_pay": 200.0,
                "max_hourly_pay": 350.0,
                "salary": "₹200 - ₹350/hr",
                "weekly_hours": "10 hrs/week",
                "shift_schedule": "Flexible",
                "location": "Remote",
                "vacancies": 2,
                "skills": ["Social Media", "Canva", "Content Writing", "Communication"],
                "description": "Manage student community channels, draft engaging Instagram posts, LinkedIn updates, and reply to community inquiries.",
                "responsibilities": "Design graphics using Canva, schedule social posts, engage in discussions on Discord/LinkedIn.",
                "qualifications": "Active on social platforms, creative eye for design, good written English.",
                "benefits": "Work from anywhere, flexible hours, building personal brand presence.",
                "deadline": datetime.now(timezone.utc) + timedelta(days=28),
                "status": "ACTIVE"
            },
            {
                "title": "Weekend Retail & Inventory Assistant",
                "company": "ABC Technologies",
                "recruiter_id": abc_rec.id if abc_rec else None,
                "category": "Retail and Sales",
                "job_type": "Weekend-only",
                "work_arrangement": "On-site",
                "compensation_type": "hourly",
                "pay_rate": "₹180 - ₹250/hr",
                "min_hourly_pay": 180.0,
                "max_hourly_pay": 250.0,
                "salary": "₹180 - ₹250/hr",
                "weekly_hours": "14-16 hrs/week",
                "shift_schedule": "Weekends",
                "location": "Campus Store, Student Union",
                "vacancies": 2,
                "skills": ["Customer Support", "Excel", "Inventory"],
                "description": "Manage checkout counters, organize merchandise shelves, and perform weekend inventory audits at the campus store.",
                "responsibilities": "Greet customers, ring up orders on POS system, maintain clean displays, count stock.",
                "qualifications": "Friendly demeanor, basic math skills, availability on Saturdays and Sundays.",
                "benefits": "Store discounts, weekend-only commitment leaving weekdays free for study.",
                "deadline": datetime.now(timezone.utc) + timedelta(days=18),
                "status": "ACTIVE"
            },
            {
                "title": "Data Entry & Catalog Assistant",
                "company": "ABC Technologies",
                "recruiter_id": abc_rec.id if abc_rec else None,
                "category": "Data Entry",
                "job_type": "Part-time",
                "work_arrangement": "Remote",
                "compensation_type": "hourly",
                "pay_rate": "₹150 - ₹220/hr",
                "min_hourly_pay": 150.0,
                "max_hourly_pay": 220.0,
                "salary": "₹150 - ₹220/hr",
                "weekly_hours": "10-15 hrs/week",
                "shift_schedule": "Flexible",
                "location": "Remote",
                "vacancies": 3,
                "skills": ["Data Entry", "Excel", "Fast Typing"],
                "description": "Enter, verify, and clean product catalog data, customer spreadsheets, and survey responses.",
                "responsibilities": "Input data into spreadsheets and CMS with high accuracy, check for duplicate records.",
                "qualifications": "High typing accuracy (40+ WPM), familiar with Microsoft Excel or Google Sheets.",
                "benefits": "Set your own schedule, work from your hostel room.",
                "deadline": datetime.now(timezone.utc) + timedelta(days=22),
                "status": "ACTIVE"
            },
            {
                "title": "Campus Tech Fest Event Assistant",
                "company": "TechNova Solutions",
                "recruiter_id": technova_rec.id if technova_rec else None,
                "category": "Event Assistant",
                "job_type": "Temporary",
                "work_arrangement": "On-site",
                "compensation_type": "shift",
                "pay_rate": "₹1,000 - ₹1,500/shift",
                "min_hourly_pay": 200.0,
                "max_hourly_pay": 300.0,
                "salary": "₹1,000 - ₹1,500/shift",
                "weekly_hours": "1-2 shifts/weekend",
                "shift_schedule": "Weekends / Events",
                "location": "Auditorium & Exhibition Hall",
                "vacancies": 5,
                "skills": ["Event Coordination", "Customer Support", "Communication"],
                "description": "Assist event organizers with registration desks, badge printing, stage audio-visual checks, and VIP ushering during weekend tech conferences.",
                "responsibilities": "Coordinate attendee check-in, hand out welcome kits, guide guest speakers to seminar halls.",
                "qualifications": "Proactive, enthusiastic attitude. Able to stand and coordinate for 5-6 hour shifts.",
                "benefits": "Free food coupons, conference pass access, instant cash / UPI payout per shift.",
                "deadline": datetime.now(timezone.utc) + timedelta(days=12),
                "status": "ACTIVE"
            },
            {
                "title": "Cloud & DevOps Student Intern",
                "company": "CodeCraft Labs",
                "recruiter_id": codecraft_rec.id if codecraft_rec else None,
                "category": "Web Development",
                "job_type": "Part-time",
                "work_arrangement": "Remote",
                "compensation_type": "hourly",
                "pay_rate": "₹350 - ₹500/hr",
                "min_hourly_pay": 350.0,
                "max_hourly_pay": 500.0,
                "salary": "₹350 - ₹500/hr",
                "weekly_hours": "12-15 hrs/week",
                "shift_schedule": "Flexible",
                "location": "Remote",
                "vacancies": 2,
                "skills": ["Docker", "Linux", "Python", "CI/CD", "Git"],
                "description": "Assist in automating container builds, writing GitHub Actions workflows, and monitoring test pipelines.",
                "responsibilities": "Create Dockerfiles, test GitHub Actions, write deployment documentation.",
                "qualifications": "Familiarity with Linux terminal and basic Docker concepts.",
                "benefits": "Mentorship from senior DevOps engineers, flexible working hours.",
                "deadline": datetime.now(timezone.utc) + timedelta(days=20),
                "status": "PENDING_APPROVAL"  # Demo pending job offer!
            }
        ]

        # Clean up any legacy LPA placement jobs so users don't see corporate placement items
        legacy_jobs = db.query(Job).filter(Job.salary.like("%LPA%")).all()
        for lj in legacy_jobs:
            db.delete(lj)
        if legacy_jobs:
            db.commit()

        # Seed or update each part-time job
        for item in sample_parttime_jobs:
            existing_job = db.query(Job).filter(Job.title == item["title"]).first()
            if not existing_job:
                new_job = Job(**item)
                db.add(new_job)
            else:
                # Update attributes to ensure PartTime fields are populated
                for k, v in item.items():
                    setattr(existing_job, k, v)
        db.commit()

        # 5. Seed Applications, Saved Jobs, Interviews, and Shifts
        dhanush_std = db.query(Student).join(User).filter(User.email == "dhanush@college.edu").first()
        priya_std = db.query(Student).join(User).filter(User.email == "priya.sharma@college.edu").first()
        ananya_std = db.query(Student).join(User).filter(User.email == "ananya.roy@college.edu").first()
        rahul_std = db.query(Student).join(User).filter(User.email == "rahul.v@college.edu").first()
        sneha_std = db.query(Student).join(User).filter(User.email == "sneha.p@college.edu").first()

        job_abc = db.query(Job).filter(Job.company == "ABC Technologies").first()
        job_technova = db.query(Job).filter(Job.company == "TechNova Solutions").first()
        job_social = db.query(Job).filter(Job.title == "Social Media & Community Assistant").first()
        job_data_entry = db.query(Job).filter(Job.title == "Data Entry & Catalog Assistant").first()

        if dhanush_std and job_abc:
            app1 = db.query(Application).filter(Application.student_id == dhanush_std.id, Application.job_id == job_abc.id).first()
            if not app1:
                app1 = Application(
                    job_id=job_abc.id,
                    student_id=dhanush_std.id,
                    status="INTERVIEW",
                    cover_letter="I am passionate about teaching and mentoring students.",
                    availability="Weekdays 5 PM - 8 PM, Saturday full day"
                )
                db.add(app1)
                db.commit()
                db.refresh(app1)

                interview1 = Interview(
                    application_id=app1.id,
                    scheduled_at=datetime.now(timezone.utc) + timedelta(days=2, hours=3),
                    mode="ONLINE",
                    meeting_link="https://meet.google.com/test-recruiter-abc",
                    location="Google Meet",
                    status="SCHEDULED",
                    notes="Discussion on tutoring curriculum and student mentoring."
                )
                db.add(interview1)
                db.commit()

        if dhanush_std and job_technova:
            app2 = db.query(Application).filter(Application.student_id == dhanush_std.id, Application.job_id == job_technova.id).first()
            if not app2:
                app2 = Application(
                    job_id=job_technova.id,
                    student_id=dhanush_std.id,
                    status="APPLIED",
                    cover_letter="I have built several React projects and can dedicate 15 hours per week.",
                    availability="Flexible weekly 12 hours"
                )
                db.add(app2)
                db.commit()

        # Priya Sharma applied to TechNova -> OFFERED
        if priya_std and job_technova:
            app_priya = db.query(Application).filter(Application.student_id == priya_std.id, Application.job_id == job_technova.id).first()
            if not app_priya:
                app_priya = Application(
                    job_id=job_technova.id,
                    student_id=priya_std.id,
                    status="OFFERED",
                    cover_letter="I have extensive experience in React and component libraries. Ready to start immediately.",
                    availability="Evenings and weekends (15 hrs/week)"
                )
                db.add(app_priya)
                db.commit()

        # Sneha Patel applied to TechNova Social Media -> SHORTLISTED
        if sneha_std and (job_social or job_technova):
            target_j = job_social or job_technova
            app_sneha = db.query(Application).filter(Application.student_id == sneha_std.id, Application.job_id == target_j.id).first()
            if not app_sneha:
                app_sneha = Application(
                    job_id=target_j.id,
                    student_id=sneha_std.id,
                    status="SHORTLISTED",
                    cover_letter="Experienced in creating viral reels and engaging posts with Premiere and Canva.",
                    availability="Flexible 15 hrs/week"
                )
                db.add(app_sneha)
                db.commit()

        # Rahul Verma applied to Data Entry -> APPLIED
        if rahul_std and (job_data_entry or job_abc):
            target_j = job_data_entry or job_abc
            app_rahul = db.query(Application).filter(Application.student_id == rahul_std.id, Application.job_id == target_j.id).first()
            if not app_rahul:
                app_rahul = Application(
                    job_id=target_j.id,
                    student_id=rahul_std.id,
                    status="APPLIED",
                    cover_letter="Fast typist with advanced spreadsheet and data verification skills.",
                    availability="Saturday and Sunday (16 hrs/week)"
                )
                db.add(app_rahul)
                db.commit()

        # Ananya Roy applied to Social Media -> ACCEPTED
        if ananya_std and (job_social or job_technova):
            target_j = job_social or job_technova
            app_ananya = db.query(Application).filter(Application.student_id == ananya_std.id, Application.job_id == target_j.id).first()
            if not app_ananya:
                app_ananya = Application(
                    job_id=target_j.id,
                    student_id=ananya_std.id,
                    status="ACCEPTED",
                    cover_letter="Content strategist with proven copy performance on student channels.",
                    availability="12 hrs/week"
                )
                db.add(app_ananya)
                db.commit()

        # Seed Saved Job
        if dhanush_std and job_abc:
            saved1 = db.query(SavedJob).filter(SavedJob.student_id == dhanush_std.id, SavedJob.job_id == job_abc.id).first()
            if not saved1:
                saved1 = SavedJob(
                    student_id=dhanush_std.id,
                    job_id=job_abc.id
                )
                db.add(saved1)
                db.commit()

        # Seed Upcoming Work Shift
        if dhanush_std and job_technova:
            existing_shift = db.query(WorkShift).filter(WorkShift.student_id == dhanush_std.id).first()
            if not existing_shift:
                shift1 = WorkShift(
                    student_id=dhanush_std.id,
                    job_id=job_technova.id,
                    shift_date=datetime.now(timezone.utc) + timedelta(days=1),
                    start_time="17:00",
                    end_time="20:00",
                    location="Remote / Google Meet sync",
                    status="SCHEDULED",
                    notes="Frontend UI sprint: Responsive header and card component updates."
                )
                db.add(shift1)
                db.commit()

        # Seed Notifications
        if student_user:
            existing_notif = db.query(Notification).filter(Notification.user_id == student_user.id).first()
            if not existing_notif:
                notif1 = Notification(
                    user_id=student_user.id,
                    title="Interview Scheduled",
                    message="TechNova scheduled your interview for 'Frontend Developer Assistant' on Google Meet.",
                    type="INTERVIEW_SCHEDULED",
                    is_read=False,
                    link="/my-applications"
                )
                notif2 = Notification(
                    user_id=student_user.id,
                    title="Upcoming Shift Reminder",
                    message="You have a scheduled 3-hour shift tomorrow starting at 5:00 PM.",
                    type="SHIFT_REMINDER",
                    is_read=False,
                    link="/dashboard"
                )
                db.add_all([notif1, notif2])
                db.commit()

        # Seed Notifications for Admin
        if admin_user:
            adm_notifs = [
                Notification(
                    user_id=admin_user.id,
                    title="New Student Registration Pending",
                    message="Rohan Gupta (rohan.g@college.edu) registered as Student and is awaiting your approval.",
                    type="USER_APPROVAL_PENDING",
                    is_read=False,
                    link="/admin"
                ),
                Notification(
                    user_id=admin_user.id,
                    title="New Recruiter Registration Pending",
                    message="CodeCraft Founders (recruiter@codecraft.com) registered as Recruiter and is awaiting your approval.",
                    type="USER_APPROVAL_PENDING",
                    is_read=False,
                    link="/admin"
                ),
                Notification(
                    user_id=admin_user.id,
                    title="New Job Offer Pending Approval",
                    message="Recruiter 'CodeCraft Founders' submitted job offer 'Cloud & DevOps Student Intern'. Approval required.",
                    type="JOB_APPROVAL_PENDING",
                    is_read=False,
                    link="/admin"
                )
            ]
            for an in adm_notifs:
                exist = db.query(Notification).filter(Notification.user_id == admin_user.id, Notification.title == an.title).first()
                if not exist:
                    db.add(an)
            db.commit()

        # Seed Notifications for TechNova Recruiter
        if technova_user:
            rec_notifs = [
                Notification(
                    user_id=technova_user.id,
                    title="New Application Received",
                    message="Dhanush applied for 'Frontend Developer Assistant'.",
                    type="NEW_APPLICATION",
                    is_read=False,
                    link="/employer-dashboard"
                ),
                Notification(
                    user_id=technova_user.id,
                    title="New Application Received",
                    message="Priya Sharma applied for 'Frontend Developer Assistant'.",
                    type="NEW_APPLICATION",
                    is_read=False,
                    link="/employer-dashboard"
                )
            ]
            for rn in rec_notifs:
                exist = db.query(Notification).filter(Notification.user_id == technova_user.id, Notification.message == rn.message).first()
                if not exist:
                    db.add(rn)
            db.commit()

        logger.info("PartTime database seeding completed successfully.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        if owns_session:
            db.close()

if __name__ == "__main__":
    seed_database()

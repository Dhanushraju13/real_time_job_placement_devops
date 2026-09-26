# DevOps-Enabled Real-Time Job and Placement Management Platform

A DevOps-focused campus recruitment and placement platform engineered with **React (Vite SPA)**, **FastAPI**, **PostgreSQL**, **Nginx Reverse Proxy**, **Docker Compose**, and **Jenkins CI/CD**.

Featuring **JWT Authentication**, **Role-Based Access Control (RBAC)** across **STUDENT**, **RECRUITER**, and **ADMIN** roles, an integrated **Application Workflow Pipeline**, and **Real-Time Interview Management**.

---

## 🏗️ Architecture

```
                       +---------------------------------------+
                       |             Client Browser            |
                       +-------------------+-------------------+
                                           |
                                  HTTP:80  | WebSocket:80
                                           v
+----------------------------------------------------------------------------------+
|                                  NGINX (Reverse Proxy)                           |
|  - /health       --> Backend Health Endpoint (:8000/health)                     |
|  - /             --> Frontend (React SPA on Nginx)                               |
|  - /api/         --> Backend (FastAPI :8000)                                     |
|  - /ws/          --> Backend WebSocket (/ws/notifications)                      |
|  - /openapi.json --> Backend OpenAPI spec                                        |
+--------------------------+-------------------------------+-----------------------+
                           |                               |
                           v                               v
             +---------------------------+   +---------------------------+
             |     Frontend Container    |   |     Backend Container     |
             |   React + Vite SPA        |   |   FastAPI + Uvicorn       |
             |   (Nginx fallback router) |   |   JWT + Bcrypt Auth       |
             +---------------------------+   +-------------+-------------+
                                                           |
                                                SQLAlchemy | (psycopg 3)
                                                           v
                                             +---------------------------+
                                             |     Database Container    |
                                             |     PostgreSQL 17         |
                                             |     Volume: pgdata        |
                                             +---------------------------+
```

---

## 🔄 Recruitment Workflow Pipeline

Applications follow a strict, enforced transition lifecycle:

```
[ APPLIED ] ──────> [ UNDER_REVIEW ] ──────> [ SHORTLISTED ] ──────> [ INTERVIEW ] ──────> [ SELECTED ]
     │                      │                       │                      │
     └──────────────────────┴───────────────────────┴──────────────────────┴───────> [ REJECTED ]
```

- Invalid transitions (e.g. `APPLIED` ➔ `SELECTED` directly) are rejected with **HTTP 400 Bad Request**.
- Status updates trigger immediate **WebSocket broadcast notifications** to connected clients.

---

## 🗓️ Real-Time Interview Management

- **Scheduling**: Authenticated recruiters and administrators schedule interviews for candidates.
  - Supports interview modes: `ONLINE` (with meeting link), `OFFLINE` (with venue/location), and `HYBRID`.
  - Recruiter access is isolated: recruiters cannot schedule interviews or modify applications for jobs belonging to another company.
- **Student Dashboard**: Live "My Interviews" listing, 1-click Join meeting links, and visual application progress timeline.
- **Recruiter Dashboard**: Interview Management tab to schedule rounds, track statuses (`SCHEDULED`, `COMPLETED`, `CANCELLED`), and conduct rounds.
- **Admin Dashboard**: System-wide interview metrics (Total, Scheduled, Completed, Cancelled) and real-time interview audit table.
- **WebSocket Broadcasts**:
  - `INTERVIEW_SCHEDULED`
  - `INTERVIEW_UPDATED`
  - `INTERVIEW_CANCELLED`

---

## 🗄️ Database Structure

Implemented via SQLAlchemy models backed by PostgreSQL:

### 1. `users`
- `id` (PK, Integer)
- `name` (String)
- `email` (String, Unique, Indexed)
- `password_hash` (String)
- `role` (Enum/String: `STUDENT`, `RECRUITER`, `ADMIN`)
- `created_at` (DateTime UTC)

### 2. `students`
- `id` (PK, Integer)
- `user_id` (FK ➔ `users.id`, 1-to-1, CASCADE)
- `college` (String)
- `degree` (String)
- `branch` (String)
- `cgpa` (Float)
- `skills` (JSON Array)
- `resume_url` (String, Nullable)

### 3. `recruiters`
- `id` (PK, Integer)
- `user_id` (FK ➔ `users.id`, 1-to-1, CASCADE)
- `company_name` (String)
- `company_email` (String)

### 4. `jobs`
- `id` (PK, Integer)
- `recruiter_id` (FK ➔ `recruiters.id`, Nullable, SET NULL)
- `title` (String, with `role` alias)
- `company` (String)
- `description` (Text)
- `salary` (String, with `package` alias)
- `location` (String)
- `skills` (JSON Array)
- `status` (String: `ACTIVE`)
- `created_at` (DateTime UTC)

### 5. `applications`
- `id` (PK, Integer)
- `job_id` (FK ➔ `jobs.id`, CASCADE)
- `student_id` (FK ➔ `students.id`, CASCADE)
- `status` (String: `APPLIED`, `UNDER_REVIEW`, `SHORTLISTED`, `INTERVIEW`, `SELECTED`, `REJECTED`)
- `applied_at` (DateTime UTC)

### 6. `interviews`
- `id` (PK, Integer)
- `application_id` (FK ➔ `applications.id`, CASCADE)
- `scheduled_at` (DateTime UTC)
- `mode` (String: `ONLINE`, `OFFLINE`, `HYBRID`)
- `meeting_link` (String, Nullable)
- `location` (String, Nullable)
- `status` (String: `SCHEDULED`, `COMPLETED`, `CANCELLED`)
- `notes` (Text, Nullable)
- `created_at` (DateTime UTC)

---

---

## 🎯 Resume Management, Skill Extraction & Job Matching

An intelligent, rule-based skill extraction and matching engine powered by local PDF parsing (`pypdf`) without external paid AI APIs.

### 1. Controlled Skill Pattern Dictionary
Extracts standardized technical skills across languages, frameworks, databases, and DevOps tools:
- **Languages**: Python, Java, C++, C#, C, JavaScript, TypeScript, Go, Rust, Kotlin, Swift, PHP, Ruby, SQL
- **Frameworks / Libraries**: React, Angular, Vue.js, Node.js, Express, FastAPI, Django, Flask, Spring Boot, .NET, Next.js
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis, SQLite, Oracle, Cassandra
- **DevOps & Cloud**: Docker, Kubernetes, AWS, Azure, GCP, Jenkins, Git, GitHub Actions, CI/CD, Terraform, Linux, Nginx

Regex boundary protections prevent false positives (e.g. standalone `C` does not trigger falsely on `CSS`, `React`, or general vocabulary).

### 2. Matching Engine Formula
Calculates precise candidate-to-job compatibility:

$$\text{match\_percentage} = \operatorname{round}\left(\frac{\text{matched required skills}}{\text{total required skills}} \times 100\right)$$

- If a job specifies zero required skills, match percentage defaults to 100%.
- Returns `matched_skills` (skills possessed by student) and `missing_skills` (skills required but not yet in candidate profile).

### 3. Student & Recruiter Experience
- **Student Dashboard**:
  - Drag-and-drop / file picker for PDF resumes (strict 5MB limit).
  - Instant skill extraction & automatic profile update.
  - Interactive skill pill manager to add or remove custom skills.
  - "Recommended Jobs" tab sorted descending by match percentage with color-coded match badges (`>=70%` High, `40-69%` Mid, `<40%` Low).
- **Recruiter Portal**:
  - Applicant pipeline table displays candidate match percentage, matched skills (`✓`), and missing skills (`✗`).
  - Direct 1-click **View PDF** link to inspect candidate's uploaded resume.
  - View real-time interview status alongside recruitment workflow.

---

## 🌐 API Endpoints

| Method | Endpoint | Access Level | Description |
|---|---|---|---|
| `GET` | `/health` | Public | System health check (`{"status": "UP", "service": "placement-api"}`) |
| `POST` | `/api/auth/register` | Public | Register Student or Recruiter (Admin registration disallowed) |
| `POST` | `/api/auth/login` | Public | Authenticate user & return JWT access token |
| `GET` | `/api/auth/me` | Authenticated | Fetch authenticated user profile & details |
| `POST` | `/api/students/resume` | Student | Upload & parse PDF resume (<=5MB), extract skills, update profile |
| `GET` | `/api/uploads/resumes/{filename}` | Authenticated | View / download uploaded PDF resume |
| `GET` | `/api/students/profile` | Student | Retrieve student academic profile and verified skills |
| `PUT` | `/api/students/profile` | Student | Update student profile and skills |
| `GET` | `/api/students/skills` | Student | Get list of student's current skills |
| `GET` | `/api/jobs` | Public | List active job listings |
| `GET` | `/api/jobs/recommended` | Student | Retrieve recommended jobs sorted by match percentage |
| `GET` | `/api/jobs/{id}` | Public / Student | Get job details (includes match details if caller is student) |
| `POST` | `/api/jobs` | Recruiter / Admin | Publish new job and broadcast via WebSocket |
| `GET` | `/api/applications` | Authenticated | View applications (includes match metrics & resume link for recruiters) |
| `POST` | `/api/applications` | Student | Submit application for a job |
| `PATCH` | `/api/applications/{id}`| Recruiter / Admin | Update application status along valid workflow |
| `POST` | `/api/interviews` | Recruiter / Admin | Schedule interview for an application |
| `GET` | `/api/interviews` | Authenticated | List interviews (Student: own, Recruiter: company, Admin: all) |
| `GET` | `/api/interviews/{id}` | Authenticated | Retrieve interview details (authorization enforced) |
| `PATCH` | `/api/interviews/{id}` | Recruiter / Admin | Update interview schedule, mode, meeting link, status |
| `DELETE`| `/api/interviews/{id}` | Recruiter / Admin | Cancel and delete an interview |
| `GET` | `/api/admin/stats` | Admin | System statistics including interview metrics |
| `GET` | `/api/admin/users` | Admin | List all registered users |
| `DELETE`| `/api/admin/users/{id}` | Admin | Delete a user from platform |
| `WS` | `/ws/notifications` | Public | Real-time WebSocket notifications broadcaster |

- **Interactive Swagger Documentation**: `http://localhost/api/docs`
- **OpenAPI Schema Specification**: `http://localhost/openapi.json`

---

## ⚡ Quick Demo Accounts

Pre-seeded out-of-the-box upon startup:

| Role | Email | Password | Features & Privileges |
|---|---|---|---|
| **Admin** | `admin@placement.edu` | `Admin@123` | System stats, User management, Cross-company interview oversight |
| **Recruiter** | `recruiter@technova.com` | `Recruiter@123` | Post jobs, Candidate review, Schedule interviews, Mark outcomes |
| **Recruiter** | `recruiter@abc.com` | `Recruiter@123` | ABC Technologies portal & interviews |
| **Student** | `dhanush@college.edu` | `Student@123` | Profile, Skills, 1-Click apply, Interview tracker with meeting links |

---

## 🚀 Running the Project

### 1. Start Services
```bash
docker compose up --build -d
```

### 2. Verify Services
```bash
docker compose ps
```

### 3. Run Backend Test Suite
```bash
docker compose exec -T backend python -m pytest -v
```

### 4. Create First Admin User via CLI
```bash
docker compose exec backend python -m app.create_admin --name "Dean Placement" --email "dean@placement.edu" --password "Dean@Secure2026"
```

---

## 🛠️ Jenkins CI/CD Pipeline

The project features an automated, multi-stage Jenkins Declarative Pipeline ([Jenkinsfile](file:///c:/Users/hp5cd/Downloads/real_time_job_placement_devops/Jenkinsfile)) designed for continuous integration, security verification, automated testing, container versioning, registry distribution, and zero-downtime deployment.

```
+-------------+     +---------------+     +----------------+     +--------------------+
|  1.Checkout | --> | 2.Backend     | --> | 3.Frontend     | --> | 4.Docker Image     |
|  (SCM)      |     |   Tests       |     |   Build        |     |   Build & Version  |
+-------------+     +---------------+     +----------------+     +--------------------+
                                                                            |
                                                                            v
+-------------+     +---------------+     +----------------+     +--------------------+
| 8.Smoke     | <-- | 7.Health      | <-- | 6.Deployment   | <-- | 5.Docker Hub Push  |
|   Tests     |     |   Check       |     |   (Compose)    |     |   & Security Scan  |
+-------------+     +---------------+     +----------------+     +--------------------+
       |
       v
+-------------------------------+
| 9.Reporting & Cleanup (Post)  |
+-------------------------------+
```

### Pipeline Stages Overview

1. **Checkout**: Clones the latest commit from the SCM repository.
2. **Backend Tests**:
   - Builds an isolated test image (`placement-backend:test`).
   - Executes all 46 pytest unit & integration tests using an isolated file-backed SQLite database (`sqlite:///test.db`).
   - Produces and publishes JUnit XML test report (`backend-test-results.xml`).
3. **Frontend Build**:
   - Executes inside an isolated `node:22-alpine` container.
   - Runs `npm install && npm run build` to validate React/Vite transpilation and bundle creation.
4. **Docker Image Build & Versioning**:
   - Builds production-ready images for backend and frontend.
   - Tags both images with `${BUILD_NUMBER}` (e.g. `placement-backend:42`) and `:latest`.
5. **Security Scanning**:
   - Scans the generated Docker image using **Aqua Security Trivy** for `HIGH` and `CRITICAL` Common Vulnerabilities and Exposures (CVEs).
6. **Docker Hub Registry Push (Secure Credentials)**:
   - When enabled via pipeline parameter `PUSH_TO_DOCKERHUB=true`, authenticates with Docker Hub via Jenkins Credential Store (`dockerhub-credentials` of type Username with password).
   - Never exposes or hard-codes credentials in source code.
   - Pushes `${DOCKER_USER}/placement-backend:${BUILD_NUMBER}` and `${DOCKER_USER}/placement-frontend:${BUILD_NUMBER}`.
7. **Deployment**:
   - Deploys container services via Docker Compose parameterized with the versioned images (`BACKEND_IMAGE` and `FRONTEND_IMAGE`).
8. **Health Check**:
   - Implements a resilient polling loop with exponential backoff (up to 15 retries).
   - Validates that FastAPI and PostgreSQL database connectivity report `UP`.
9. **Smoke Tests**:
   - Automatically executes end-to-end smoke verification tests against the running ingress stack:
     - Health API (`GET /health`)
     - OpenAPI Schema (`GET /openapi.json`)
     - Jobs API (`GET /api/jobs`)
     - React SPA Ingress (`GET /`)
     - Authentication Login (`POST /api/auth/login`)
10. **Post Execution Reporting**:
    - **Always**: Cleans up dangling test containers and runner images.
    - **Success**: Emits deployment report with access endpoints.
    - **Failure**: Automatically dumps diagnostic container logs (`docker compose logs --tail=50`).

### Running Smoke Tests Manually
```bash
python scripts/smoke_test.py http://localhost
```


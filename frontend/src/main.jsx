import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

// Helper for API requests with Auth Bearer token
function authFetch(url, options = {}) {
  const token = localStorage.getItem("token");
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {})
  };
  return fetch(url, { ...options, headers });
}

// Application workflow stages for the timeline
const WORKFLOW_STEPS = [
  { key: "APPLIED", label: "Applied" },
  { key: "UNDER_REVIEW", label: "Under Review" },
  { key: "SHORTLISTED", label: "Shortlisted" },
  { key: "INTERVIEW", label: "Interview" },
  { key: "SELECTED", label: "Selected" }
];

function ApplicationTimeline({ currentStatus }) {
  if (currentStatus === "REJECTED") {
    return (
      <div className="timeline-container">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: "#64748b" }}>Status Workflow</span>
          <span className="badge badge-REJECTED">Application Rejected</span>
        </div>
      </div>
    );
  }

  const currentIndex = WORKFLOW_STEPS.findIndex((s) => s.key === currentStatus);
  const activeIdx = currentIndex >= 0 ? currentIndex : 0;
  const progressPercent = (activeIdx / (WORKFLOW_STEPS.length - 1)) * 100;

  return (
    <div className="timeline-container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
        <span style={{ fontSize: 12, fontWeight: 700, color: "#475569", textTransform: "uppercase", letterSpacing: 0.5 }}>
          Recruitment Timeline
        </span>
        <span className={`badge badge-${currentStatus}`}>{currentStatus.replaceAll("_", " ")}</span>
      </div>

      <div className="timeline">
        <div className="timeline-line">
          <div className="timeline-progress" style={{ width: `${progressPercent}%` }} />
        </div>

        {WORKFLOW_STEPS.map((step, idx) => {
          let stepClass = "";
          if (idx < activeIdx) stepClass = "completed";
          else if (idx === activeIdx) stepClass = "current";

          return (
            <div className={`timeline-step ${stepClass}`} key={step.key}>
              <div className="timeline-dot">{idx < activeIdx ? "✓" : idx + 1}</div>
              <div className="timeline-label">{step.label}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function App() {
  const [route, setRoute] = useState(window.location.pathname || "/");
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("user") || "null");
    } catch {
      return null;
    }
  });

  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [interviews, setInterviews] = useState([]);
  const [adminStats, setAdminStats] = useState(null);
  const [adminUsers, setAdminUsers] = useState([]);
  const [events, setEvents] = useState([]);
  const [wsStatus, setWsStatus] = useState("Connecting...");
  const [liveAlert, setLiveAlert] = useState(null);

  // Navigation helper
  const navigate = (path) => {
    window.history.pushState({}, "", path);
    setRoute(path);
    window.scrollTo(0, 0);
  };

  useEffect(() => {
    const onPopState = () => setRoute(window.location.pathname);
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  // Sync session on mount or token change
  useEffect(() => {
    if (token) {
      authFetch("/api/auth/me")
        .then((r) => {
          if (r.ok) return r.json();
          throw new Error("Invalid session");
        })
        .then((userData) => {
          setUser(userData);
          localStorage.setItem("user", JSON.stringify(userData));
        })
        .catch(() => logout());
    }
  }, [token]);

  // Load jobs
  const loadJobs = () => {
    authFetch("/api/jobs")
      .then((r) => r.json())
      .then((data) => {
        if (Array.isArray(data)) setJobs(data);
      })
      .catch((err) => console.error("Error loading jobs:", err));
  };

  // Load applications
  const loadApplications = () => {
    if (!token) return;
    authFetch("/api/applications")
      .then((r) => r.json())
      .then((data) => {
        if (Array.isArray(data)) setApplications(data);
      })
      .catch((err) => console.error("Error loading applications:", err));
  };

  // Load interviews
  const loadInterviews = () => {
    if (!token) return;
    authFetch("/api/interviews")
      .then((r) => (r.ok ? r.json() : []))
      .then((data) => {
        if (Array.isArray(data)) setInterviews(data);
      })
      .catch((err) => console.error("Error loading interviews:", err));
  };

  // Load Admin Data
  const loadAdminData = () => {
    if (!token || user?.role !== "ADMIN") return;
    authFetch("/api/admin/stats")
      .then((r) => (r.ok ? r.json() : null))
      .then((stats) => {
        if (stats) setAdminStats(stats);
      });

    authFetch("/api/admin/users")
      .then((r) => (r.ok ? r.json() : []))
      .then((usersList) => {
        if (Array.isArray(usersList)) setAdminUsers(usersList);
      });
  };

  useEffect(() => {
    loadJobs();
    if (token) {
      loadApplications();
      loadInterviews();
      if (user?.role === "ADMIN") {
        loadAdminData();
      }
    }
  }, [token, user?.role]);

  // WebSocket for Real-Time notifications
  useEffect(() => {
    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${protocol}//${location.host}/ws/notifications`);

    ws.onopen = () => setWsStatus("Live");
    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        setEvents((prev) => [msg, ...prev].slice(0, 15));

        if (msg.type === "NEW_JOB") {
          setJobs((prev) => [msg.data, ...prev.filter((j) => j.id !== msg.data.id)]);
        } else if (msg.type === "APPLICATION_STATUS") {
          setApplications((prev) =>
            prev.map((app) => (app.id === msg.data.id ? { ...app, status: msg.data.status } : app))
          );
        } else if (msg.type === "NEW_APPLICATION") {
          loadApplications();
        } else if (msg.type === "INTERVIEW_SCHEDULED") {
          loadInterviews();
          loadApplications();
          setLiveAlert({
            title: `🔔 Interview Scheduled!`,
            body: `${msg.data.job_title} at ${msg.data.company} - ${new Date(msg.data.scheduled_at).toLocaleString()}`,
            link: msg.data.meeting_link,
            mode: msg.data.mode
          });
        } else if (msg.type === "INTERVIEW_UPDATED" || msg.type === "INTERVIEW_CANCELLED") {
          loadInterviews();
        }
      } catch (err) {
        console.error("WS error parsing message:", err);
      }
    };
    ws.onclose = () => setWsStatus("Offline");
    return () => ws.close();
  }, []);

  const loginUser = (authData) => {
    setToken(authData.access_token);
    setUser(authData.user);
    localStorage.setItem("token", authData.access_token);
    localStorage.setItem("user", JSON.stringify(authData.user));

    if (authData.role === "STUDENT") navigate("/student/dashboard");
    else if (authData.role === "RECRUITER") navigate("/recruiter/dashboard");
    else if (authData.role === "ADMIN") navigate("/admin/dashboard");
    else navigate("/");
  };

  const logout = () => {
    setToken("");
    setUser(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <div className="page">
      <header>
        <div className="header-left">
          <div className="brand" onClick={() => navigate("/")}>
            <h1>PlacementHub</h1>
            <p>Real-Time Job & Campus Placement Platform</p>
          </div>
        </div>

        <div className="header-right">
          <span className={`status-badge ${wsStatus === "Live" ? "live" : "offline"}`}>
            ● {wsStatus}
          </span>

          <nav className="nav-links">
            <button className="nav-btn" onClick={() => navigate("/")}>
              Jobs
            </button>

            {user ? (
              <>
                {user.role === "STUDENT" && (
                  <button className="nav-btn primary" onClick={() => navigate("/student/dashboard")}>
                    My Dashboard
                  </button>
                )}
                {user.role === "RECRUITER" && (
                  <button className="nav-btn primary" onClick={() => navigate("/recruiter/dashboard")}>
                    Recruiter Portal
                  </button>
                )}
                {user.role === "ADMIN" && (
                  <button className="nav-btn primary" onClick={() => navigate("/admin/dashboard")}>
                    Admin Console
                  </button>
                )}

                <div className="user-pill">
                  <span>{user.name}</span>
                  <span className={`role-tag role-${user.role.toLowerCase()}`}>{user.role}</span>
                </div>

                <button className="nav-btn" onClick={logout}>
                  Sign Out
                </button>
              </>
            ) : (
              <>
                <button className="nav-btn" onClick={() => navigate("/login")}>
                  Sign In
                </button>
                <button className="nav-btn primary" onClick={() => navigate("/register")}>
                  Register
                </button>
              </>
            )}
          </nav>
        </div>
      </header>

      {/* Real-Time Live Toast / Alert for new Interview Notification */}
      {liveAlert && (
        <div className="interview-alert-card">
          <div className="interview-alert-left">
            <h4>{liveAlert.title}</h4>
            <p>{liveAlert.body} · Mode: <b>{liveAlert.mode}</b></p>
          </div>
          <div className="interview-alert-right">
            {liveAlert.link && (
              <a
                href={liveAlert.link}
                target="_blank"
                rel="noreferrer"
                className="btn success sm"
              >
                Join Interview ↗
              </a>
            )}
            <button className="btn secondary sm" onClick={() => setLiveAlert(null)}>
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Routes */}
      {route === "/login" && <LoginPage onLogin={loginUser} navigate={navigate} />}
      {route === "/register" && <RegisterPage onRegister={loginUser} navigate={navigate} />}
      {route === "/student/dashboard" && (
        <StudentDashboard
          user={user}
          jobs={jobs}
          applications={applications}
          loadApplications={loadApplications}
          interviews={interviews}
          loadInterviews={loadInterviews}
          events={events}
        />
      )}
      {route === "/recruiter/dashboard" && (
        <RecruiterDashboard
          user={user}
          jobs={jobs}
          loadJobs={loadJobs}
          applications={applications}
          loadApplications={loadApplications}
          interviews={interviews}
          loadInterviews={loadInterviews}
          events={events}
        />
      )}
      {route === "/admin/dashboard" && (
        <AdminDashboard
          user={user}
          stats={adminStats}
          users={adminUsers}
          loadAdminData={loadAdminData}
          jobs={jobs}
          applications={applications}
          interviews={interviews}
          loadInterviews={loadInterviews}
          events={events}
        />
      )}
      {(route === "/" || route === "/jobs") && (
        <PublicHomeView
          jobs={jobs}
          events={events}
          user={user}
          applications={applications}
          loadApplications={loadApplications}
          navigate={navigate}
        />
      )}
    </div>
  );
}

// ==========================================
// 1. PUBLIC JOBS VIEW
// ==========================================
function PublicHomeView({ jobs, events, user, applications, loadApplications, navigate }) {
  const [applyingJobId, setApplyingJobId] = useState(null);
  const appliedJobIds = new Set(applications.map((a) => a.job_id));

  const handleApply = async (jobId) => {
    if (!user) {
      navigate("/login");
      return;
    }
    if (user.role !== "STUDENT") {
      alert("Only registered students can apply for jobs.");
      return;
    }

    setApplyingJobId(jobId);
    try {
      const res = await authFetch("/api/applications", {
        method: "POST",
        body: JSON.stringify({ job_id: jobId })
      });
      if (res.ok) {
        loadApplications();
      } else {
        const err = await res.json();
        alert(err.detail || "Failed to apply");
      }
    } catch {
      alert("Error submitting application");
    } finally {
      setApplyingJobId(null);
    }
  };

  return (
    <>
      <section className="stats">
        <div className="stat-card">
          <b>{jobs.length}</b>
          <span>Active Openings</span>
        </div>
        <div className="stat-card">
          <b>1,248</b>
          <span>Registered Students</span>
        </div>
        <div className="stat-card">
          <b>86</b>
          <span>Partner Companies</span>
        </div>
        <div className="stat-card">
          <b>87</b>
          <span>Placed Candidates</span>
        </div>
      </section>

      <main>
        <section>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <h2>Available Jobs & Opportunities</h2>
            <span style={{ fontSize: 13, color: "#687386" }}>Showing {jobs.length} positions</span>
          </div>

          {jobs.length === 0 ? (
            <p style={{ color: "#687386" }}>No active job listings found.</p>
          ) : (
            jobs.map((j) => {
              const isApplied = appliedJobIds.has(j.id);
              return (
                <article className="job" key={j.id}>
                  <div className="job-info">
                    <h3>{j.title || j.role}</h3>
                    <div className="job-meta">
                      <b>{j.company}</b> · {j.salary || j.package} · 📍 {j.location || "Remote"}
                    </div>
                    {j.description && <p className="job-desc">{j.description}</p>}
                    <div className="tags">
                      {(j.skills || []).map((s) => (
                        <span className="tag" key={s}>
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    {isApplied ? (
                      <button className="secondary" disabled>
                        Applied ✓
                      </button>
                    ) : (
                      <button
                        onClick={() => handleApply(j.id)}
                        disabled={applyingJobId === j.id}
                      >
                        {applyingJobId === j.id ? "Applying..." : "Apply Now"}
                      </button>
                    )}
                  </div>
                </article>
              );
            })
          )}
        </section>

        <aside>
          <h2>Live Stream Activity</h2>
          {events.length ? (
            events.map((e, i) => (
              <div className={`event ${e.type?.includes("INTERVIEW") ? "interview-event" : ""}`} key={i}>
                <b>{(e.type || "").replaceAll("_", " ")}</b>
                <p>
                  {e.message ||
                    (e.type === "INTERVIEW_SCHEDULED"
                      ? `Interview scheduled for ${e.data?.job_title} at ${e.data?.company}`
                      : e.data?.status
                      ? `Application #${e.data.id} is now ${e.data.status}`
                      : e.data?.title
                      ? `${e.data.title} posted`
                      : "Live update")}
                </p>
                <time>{new Date().toLocaleTimeString()}</time>
              </div>
            ))
          ) : (
            <p style={{ color: "#687386", fontSize: 14 }}>Waiting for real-time WebSocket events...</p>
          )}
        </aside>
      </main>
    </>
  );
}

// ==========================================
// 2. LOGIN PAGE
// ==========================================
function LoginPage({ onLogin, navigate }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "Invalid login credentials");
        setLoading(false);
        return;
      }
      onLogin(data);
    } catch {
      setError("Network error connecting to placement service");
      setLoading(false);
    }
  };

  const fillDemo = (demoEmail, demoPass) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError("");
  };

  return (
    <div className="auth-box">
      <h2>Welcome Back</h2>
      <p className="auth-subtitle">Sign in to your PlacementHub account</p>

      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Email Address</label>
          <input
            type="email"
            required
            value={email}
            placeholder="e.g. dhanush@college.edu"
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            required
            value={password}
            placeholder="••••••••"
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button type="submit" style={{ width: "100%", marginTop: 8 }} disabled={loading}>
          {loading ? "Authenticating..." : "Sign In"}
        </button>
      </form>

      <div style={{ marginTop: 18, textAlign: "center", fontSize: 14, color: "#687386" }}>
        Don't have an account?{" "}
        <a
          href="/register"
          onClick={(e) => {
            e.preventDefault();
            navigate("/register");
          }}
          style={{ color: "#315dbd", fontWeight: 600, textDecoration: "none" }}
        >
          Create an account
        </a>
      </div>

      <div className="demo-logins">
        <p>⚡ Quick Demo Logins</p>
        <div className="demo-buttons">
          <button
            type="button"
            className="demo-btn"
            onClick={() => fillDemo("dhanush@college.edu", "Student@123")}
          >
            👤 Demo Student
          </button>
          <button
            type="button"
            className="demo-btn"
            onClick={() => fillDemo("recruiter@technova.com", "Recruiter@123")}
          >
            🏢 Demo Recruiter
          </button>
          <button
            type="button"
            className="demo-btn"
            onClick={() => fillDemo("admin@placement.edu", "Admin@123")}
          >
            ⚙️ Demo Admin
          </button>
        </div>
      </div>
    </div>
  );
}

// ==========================================
// 3. REGISTRATION PAGE
// ==========================================
function RegisterPage({ onRegister, navigate }) {
  const [role, setRole] = useState("STUDENT");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [college, setCollege] = useState("");
  const [degree, setDegree] = useState("B.Tech");
  const [branch, setBranch] = useState("Computer Science");
  const [cgpa, setCgpa] = useState("8.5");
  const [skills, setSkills] = useState("Python, FastAPI, React, Docker");

  const [companyName, setCompanyName] = useState("");
  const [companyEmail, setCompanyEmail] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const payload = {
      role,
      name,
      email,
      password,
      ...(role === "STUDENT"
        ? {
            college,
            degree,
            branch,
            cgpa: parseFloat(cgpa) || null,
            skills: skills.split(",").map((s) => s.trim()).filter(Boolean)
          }
        : {
            company_name: companyName,
            company_email: companyEmail || email
          })
    };

    try {
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "Registration failed");
        setLoading(false);
        return;
      }
      onRegister(data);
    } catch {
      setError("Network error during registration");
      setLoading(false);
    }
  };

  return (
    <div className="auth-box" style={{ maxWidth: 540 }}>
      <h2>Create Your Account</h2>
      <p className="auth-subtitle">Join the placement ecosystem today</p>

      <div className="role-switch">
        <div
          className={`role-tab ${role === "STUDENT" ? "active" : ""}`}
          onClick={() => setRole("STUDENT")}
        >
          🎓 Student
        </div>
        <div
          className={`role-tab ${role === "RECRUITER" ? "active" : ""}`}
          onClick={() => setRole("RECRUITER")}
        >
          🏢 Recruiter
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Full Name</label>
          <input
            type="text"
            required
            value={name}
            placeholder={role === "STUDENT" ? "e.g. Dhanush Kumar" : "e.g. Sarah Jenkins"}
            onChange={(e) => setName(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Email Address</label>
          <input
            type="email"
            required
            value={email}
            placeholder={role === "STUDENT" ? "student@college.edu" : "recruiter@company.com"}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            required
            minLength={6}
            value={password}
            placeholder="At least 6 characters"
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {role === "STUDENT" ? (
          <>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div className="form-group">
                <label>College / University</label>
                <input
                  type="text"
                  required
                  value={college}
                  placeholder="e.g. National Inst of Tech"
                  onChange={(e) => setCollege(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Degree</label>
                <input
                  type="text"
                  required
                  value={degree}
                  placeholder="e.g. B.Tech / B.E."
                  onChange={(e) => setDegree(e.target.value)}
                />
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: 12 }}>
              <div className="form-group">
                <label>Branch / Major</label>
                <input
                  type="text"
                  required
                  value={branch}
                  placeholder="e.g. Computer Science"
                  onChange={(e) => setBranch(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>CGPA</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="10"
                  required
                  value={cgpa}
                  placeholder="e.g. 8.75"
                  onChange={(e) => setCgpa(e.target.value)}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Skills (comma separated)</label>
              <input
                type="text"
                value={skills}
                placeholder="e.g. Python, Docker, React, AWS"
                onChange={(e) => setSkills(e.target.value)}
              />
            </div>
          </>
        ) : (
          <>
            <div className="form-group">
              <label>Company Name</label>
              <input
                type="text"
                required
                value={companyName}
                placeholder="e.g. TechNova Solutions"
                onChange={(e) => setCompanyName(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Official Company Email</label>
              <input
                type="email"
                value={companyEmail}
                placeholder="careers@technova.com"
                onChange={(e) => setCompanyEmail(e.target.value)}
              />
            </div>
          </>
        )}

        <button type="submit" style={{ width: "100%", marginTop: 10 }} disabled={loading}>
          {loading ? "Registering..." : `Register as ${role === "STUDENT" ? "Student" : "Recruiter"}`}
        </button>
      </form>

      <div style={{ marginTop: 18, textAlign: "center", fontSize: 14, color: "#687386" }}>
        Already have an account?{" "}
        <a
          href="/login"
          onClick={(e) => {
            e.preventDefault();
            navigate("/login");
          }}
          style={{ color: "#315dbd", fontWeight: 600, textDecoration: "none" }}
        >
          Sign In
        </a>
      </div>
    </div>
  );
}

// ==========================================
// 4. STUDENT DASHBOARD
// ==========================================
function StudentDashboard({ user, jobs, applications, loadApplications, interviews, loadInterviews, events }) {
  const [activeTab, setActiveTab] = useState("recommended"); // 'recommended' | 'resume' | 'jobs' | 'applications' | 'interviews'
  const [applyingJobId, setApplyingJobId] = useState(null);
  const [studentProfile, setStudentProfile] = useState(user?.student_profile || {});
  const [recommendedJobs, setRecommendedJobs] = useState([]);
  const [loadingRecommended, setLoadingRecommended] = useState(false);

  // Resume upload state
  const [resumeFile, setResumeFile] = useState(null);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [resumeMsg, setResumeMsg] = useState("");
  const [newSkillsExtracted, setNewSkillsExtracted] = useState([]);

  // Skills input state
  const [newSkillInput, setNewSkillInput] = useState("");

  const [viewingJob, setViewingJob] = useState(null);
  const [isEditingSkills, setIsEditingSkills] = useState(false);
  const [resumeSuccess, setResumeSuccess] = useState(false);

  const appliedJobIds = new Set(applications.map((a) => a.job_id));

  const loadProfile = () => {
    authFetch("/api/students/profile")
      .then((r) => (r.ok ? r.json() : null))
      .then((p) => {
        if (p) setStudentProfile(p);
      })
      .catch((err) => console.error("Error loading student profile:", err));
  };

  const loadRecommendedJobs = () => {
    setLoadingRecommended(true);
    authFetch("/api/jobs/recommended")
      .then((r) => (r.ok ? r.json() : []))
      .then((data) => {
        if (Array.isArray(data)) setRecommendedJobs(data);
      })
      .catch((err) => console.error("Error loading recommended jobs:", err))
      .finally(() => setLoadingRecommended(false));
  };

  useEffect(() => {
    loadProfile();
    loadRecommendedJobs();
  }, []);

  const handleApply = async (jobId) => {
    setApplyingJobId(jobId);
    try {
      const res = await authFetch("/api/applications", {
        method: "POST",
        body: JSON.stringify({ job_id: jobId })
      });
      if (res.ok) {
        loadApplications();
        loadRecommendedJobs();
        if (viewingJob && viewingJob.id === jobId) {
          setViewingJob(null);
        }
      } else {
        const err = await res.json();
        alert(err.detail || "Failed to apply");
      }
    } catch {
      alert("Network error");
    } finally {
      setApplyingJobId(null);
    }
  };

  const handleResumeUpload = async (e) => {
    e.preventDefault();
    if (!resumeFile) {
      alert("Please select a PDF resume file to upload.");
      return;
    }
    if (!resumeFile.name.toLowerCase().endsWith(".pdf")) {
      alert("Only PDF files are supported.");
      return;
    }
    if (resumeFile.size > 5 * 1024 * 1024) {
      alert("File size exceeds 5MB limit.");
      return;
    }

    setUploadingResume(true);
    setResumeMsg("");
    setResumeSuccess(false);
    setNewSkillsExtracted([]);

    const formData = new FormData();
    formData.append("file", resumeFile);

    try {
      const token = localStorage.getItem("token");
      const res = await fetch("/api/students/resume", {
        method: "POST",
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setResumeSuccess(true);
        setResumeMsg("Resume uploaded successfully.");
        setNewSkillsExtracted(data.detected_skills || []);
        setStudentProfile((prev) => ({
          ...prev,
          resume_url: data.resume_url,
          skills: data.skills || prev.skills
        }));
        loadRecommendedJobs();
        loadProfile();
      } else {
        setResumeSuccess(false);
        setResumeMsg(`Error: ${data.detail || "Failed to upload resume"}`);
      }
    } catch {
      setResumeSuccess(false);
      setResumeMsg("Network error uploading resume");
    } finally {
      setUploadingResume(false);
    }
  };

  const handleAddSkill = async (e) => {
    e.preventDefault();
    const trimmed = newSkillInput.trim();
    if (!trimmed) return;
    const current = studentProfile.skills || [];
    if (current.some((s) => s.toLowerCase() === trimmed.toLowerCase())) {
      setNewSkillInput("");
      return;
    }
    const updated = [...current, trimmed];
    try {
      const res = await authFetch("/api/students/profile", {
        method: "PUT",
        body: JSON.stringify({ skills: updated })
      });
      if (res.ok) {
        const data = await res.json();
        setStudentProfile((prev) => ({ ...prev, skills: data.skills }));
        setNewSkillInput("");
        loadRecommendedJobs();
      }
    } catch (err) {
      console.error("Error adding skill:", err);
    }
  };

  const handleRemoveSkill = async (skillToRemove) => {
    const current = studentProfile.skills || [];
    const updated = current.filter((s) => s !== skillToRemove);
    try {
      const res = await authFetch("/api/students/profile", {
        method: "PUT",
        body: JSON.stringify({ skills: updated })
      });
      if (res.ok) {
        const data = await res.json();
        setStudentProfile((prev) => ({ ...prev, skills: data.skills }));
        loadRecommendedJobs();
      }
    } catch (err) {
      console.error("Error removing skill:", err);
    }
  };

  return (
    <>
      <div className="profile-card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 }}>
          <div>
            <h3>Welcome back, {user?.name}!</h3>
            <p style={{ margin: 0, opacity: 0.8, fontSize: 14 }}>
              {studentProfile?.degree || user?.student_profile?.degree} in {studentProfile?.branch || user?.student_profile?.branch} · {studentProfile?.college || "Campus Placement"}
            </p>
          </div>
          <div>
            {studentProfile?.resume_url ? (
              <a
                href={studentProfile.resume_url}
                target="_blank"
                rel="noreferrer"
                className="btn secondary sm"
                style={{ background: "rgba(255,255,255,0.2)", color: "white", border: "1px solid rgba(255,255,255,0.3)" }}
              >
                📄 View Active Resume
              </a>
            ) : (
              <button
                className="btn sm"
                style={{ background: "#fbbf24", color: "#78350f" }}
                onClick={() => setActiveTab("resume")}
              >
                ⚠️ Upload Resume
              </button>
            )}
          </div>
        </div>

        <div className="profile-grid">
          <div className="profile-item">
            <span>CGPA Score</span>
            <b>{studentProfile?.cgpa ? `${studentProfile.cgpa} / 10.0` : "Not specified"}</b>
          </div>
          <div className="profile-item">
            <span>Applications</span>
            <b>{applications.length} Submitted</b>
          </div>
          <div className="profile-item">
            <span>Interviews</span>
            <b>{interviews.length} Scheduled</b>
          </div>
          <div className="profile-item">
            <span>Verified Skills</span>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 4 }}>
              {(studentProfile?.skills || []).map((s) => (
                <span
                  key={s}
                  style={{
                    background: "rgba(255,255,255,0.18)",
                    padding: "2px 8px",
                    borderRadius: 12,
                    fontSize: 11
                  }}
                >
                  {s}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="dash-tabs">
        <div
          className={`dash-tab ${activeTab === "recommended" ? "active" : ""}`}
          onClick={() => setActiveTab("recommended")}
        >
          🎯 Recommended Jobs ({recommendedJobs.length})
        </div>
        <div
          className={`dash-tab ${activeTab === "resume" ? "active" : ""}`}
          onClick={() => setActiveTab("resume")}
        >
          📄 Resume & Skills
        </div>
        <div
          className={`dash-tab ${activeTab === "jobs" ? "active" : ""}`}
          onClick={() => setActiveTab("jobs")}
        >
          💼 Campus Openings ({jobs.length})
        </div>
        <div
          className={`dash-tab ${activeTab === "applications" ? "active" : ""}`}
          onClick={() => setActiveTab("applications")}
        >
          📝 My Applications ({applications.length})
        </div>
        <div
          className={`dash-tab ${activeTab === "interviews" ? "active" : ""}`}
          onClick={() => setActiveTab("interviews")}
        >
          📅 My Interviews ({interviews.length})
        </div>
      </div>

      <main>
        <div>
          {/* 1. RECOMMENDED JOBS TAB */}
          {activeTab === "recommended" && (
            <section>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <div>
                  <h2 style={{ margin: "0 0 4px" }}>Recommended Jobs</h2>
                  <p style={{ margin: 0, fontSize: 13, color: "#64748b" }}>
                    Automated match engine calculated from your verified skills and resume profile.
                  </p>
                </div>
                <button className="secondary sm" onClick={loadRecommendedJobs} disabled={loadingRecommended}>
                  {loadingRecommended ? "Analyzing..." : "↻ Refresh Matches"}
                </button>
              </div>

              {recommendedJobs.length === 0 ? (
                <div style={{ padding: 24, textAlign: "center", background: "white", borderRadius: 12, border: "1px solid #e2e8f0" }}>
                  <p style={{ color: "#64748b", margin: "0 0 12px" }}>
                    No job recommendations yet. Upload your resume in the Resume & Skills tab to extract skills and find matching jobs.
                  </p>
                  <button className="primary sm" onClick={() => setActiveTab("resume")}>
                    Upload Resume Now
                  </button>
                </div>
              ) : (
                recommendedJobs.map((j) => {
                  const isApplied = appliedJobIds.has(j.id);
                  const pct = j.match_percentage ?? 0;
                  const matchClass = pct >= 70 ? "match-high" : pct >= 40 ? "match-mid" : "match-low";

                  return (
                    <article className="job" key={j.id} style={{ display: "block", marginBottom: 16 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 14 }}>
                        <div className="job-info" style={{ flex: 1 }}>
                          <h3 style={{ margin: "0 0 2px" }}>{j.title || j.role}</h3>
                          <div style={{ fontSize: 15, fontWeight: 700, color: "#1e293b", marginBottom: 4 }}>
                            {j.company}
                          </div>
                          <div className="job-meta">
                            <b>{j.salary || j.package}</b> · 📍 {j.location || "Remote"}
                          </div>

                          <div style={{ marginTop: 10, display: "flex", alignItems: "center", gap: 8 }}>
                            <span className={`match-score-badge ${matchClass}`} style={{ fontSize: 13, padding: "5px 12px" }}>
                              Skill Match: {pct}%
                            </span>
                          </div>

                          {/* Skill Alignment Tags with checkmarks */}
                          <div style={{ marginTop: 10 }}>
                            <div className="tags">
                              {(j.matched_skills || []).map((s) => (
                                <span className="tag tag-matched" key={s}>
                                  {s} ✓
                                </span>
                              ))}
                              {(j.missing_skills || []).map((s) => (
                                <span className="tag tag-missing" key={s}>
                                  Missing: {s}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>

                        <div style={{ display: "flex", flexDirection: "column", gap: 8, minWidth: 110 }}>
                          <button
                            type="button"
                            className="secondary sm"
                            onClick={() => setViewingJob(j)}
                          >
                            View Job
                          </button>
                          {isApplied ? (
                            <button className="secondary sm" disabled>
                              Applied ✓
                            </button>
                          ) : (
                            <button
                              className="primary sm"
                              onClick={() => handleApply(j.id)}
                              disabled={applyingJobId === j.id}
                            >
                              {applyingJobId === j.id ? "Applying..." : "Apply"}
                            </button>
                          )}
                        </div>
                      </div>
                    </article>
                  );
                })
              )}
            </section>
          )}

          {/* 2. RESUME & SKILLS TAB */}
          {activeTab === "resume" && (
            <section>
              <h2>Resume & Skills</h2>
              
              <div className="resume-card">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12, flexWrap: "wrap", gap: 10 }}>
                  <div>
                    <h3 style={{ margin: 0 }}>Current Resume</h3>
                    <p style={{ margin: "4px 0 0", fontSize: 13, color: "#64748b" }}>
                      {studentProfile?.resume_url ? (
                        <span>
                          📄 Active: <a href={studentProfile.resume_url} target="_blank" rel="noreferrer" style={{ fontWeight: 600, color: "#2563eb" }}>
                            {studentProfile.resume_url.split("/").pop()}
                          </a>
                        </span>
                      ) : (
                        <span style={{ color: "#94a3b8" }}>No resume uploaded yet</span>
                      )}
                    </p>
                  </div>

                  {studentProfile?.resume_url && (
                    <a
                      href={studentProfile.resume_url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn secondary sm"
                      style={{ textDecoration: "none" }}
                    >
                      Download PDF ↗
                    </a>
                  )}
                </div>

                <form onSubmit={handleResumeUpload} className="resume-upload-zone" style={{ marginTop: 12 }}>
                  <input
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={(e) => setResumeFile(e.target.files[0] || null)}
                    style={{ marginBottom: 12 }}
                  />
                  <div style={{ fontSize: 12, color: "#64748b", marginBottom: 12 }}>
                    {resumeFile ? `Selected: ${resumeFile.name} (${Math.round(resumeFile.size / 1024)} KB)` : "Supported format: PDF only. Maximum file size: 5MB."}
                  </div>
                  <button type="submit" disabled={uploadingResume || !resumeFile} className="primary sm">
                    {uploadingResume ? "Parsing..." : "Upload Resume"}
                  </button>
                </form>

                {/* Upload Success Feedback Banner */}
                {resumeSuccess && (
                  <div style={{ marginTop: 16, padding: "16px 20px", background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: 10 }}>
                    <div style={{ fontSize: 15, fontWeight: 700, color: "#166534", marginBottom: 8 }}>
                      Resume uploaded successfully.
                    </div>
                    {newSkillsExtracted.length > 0 && (
                      <div>
                        <div style={{ fontSize: 13, fontWeight: 600, color: "#14532d", marginBottom: 6 }}>
                          Extracted Skills:
                        </div>
                        <ul style={{ margin: 0, paddingLeft: 22, fontSize: 13, color: "#15803d", lineHeight: 1.6 }}>
                          {newSkillsExtracted.map((s) => (
                            <li key={s} style={{ fontWeight: 600 }}>{s}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {resumeMsg && !resumeSuccess && (
                  <div className="alert alert-error" style={{ marginTop: 12 }}>
                    {resumeMsg}
                  </div>
                )}
              </div>

              {/* Detected Skills & Skills Editor */}
              <div className="resume-card">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <div>
                    <h3 style={{ margin: 0 }}>Detected Skills</h3>
                    <p style={{ margin: "2px 0 0", fontSize: 13, color: "#64748b" }}>
                      Skills extracted from your resume and used for real-time job matching.
                    </p>
                  </div>
                  <button
                    type="button"
                    className="secondary sm"
                    onClick={() => setIsEditingSkills(!isEditingSkills)}
                  >
                    {isEditingSkills ? "Done Editing" : "Edit Skills"}
                  </button>
                </div>

                <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: isEditingSkills ? 16 : 0 }}>
                  {(studentProfile?.skills || []).length === 0 ? (
                    <span style={{ fontSize: 13, color: "#94a3b8" }}>No detected skills yet. Upload your resume above to extract skills.</span>
                  ) : (
                    (studentProfile?.skills || []).map((skill) => (
                      <span key={skill} className="skill-pill-editable">
                        {skill}
                        {isEditingSkills && (
                          <button
                            type="button"
                            className="skill-pill-remove"
                            onClick={() => handleRemoveSkill(skill)}
                            title="Remove skill"
                          >
                            ×
                          </button>
                        )}
                      </span>
                    ))
                  )}
                </div>

                {isEditingSkills && (
                  <form onSubmit={handleAddSkill} style={{ display: "flex", gap: 10, maxWidth: 420, marginTop: 14 }}>
                    <input
                      type="text"
                      placeholder="Add custom skill (e.g. Python, SQL)"
                      value={newSkillInput}
                      onChange={(e) => setNewSkillInput(e.target.value)}
                      style={{ flex: 1, padding: "8px 12px", borderRadius: 8, border: "1px solid #cbd5e1", fontSize: 13 }}
                    />
                    <button type="submit" className="primary sm" disabled={!newSkillInput.trim()}>
                      + Add
                    </button>
                  </form>
                )}
              </div>
            </section>
          )}

          {/* 3. CAMPUS JOBS TAB */}
          {activeTab === "jobs" && (
            <section>
              <h2>Available Campus Jobs ({jobs.length})</h2>
              {jobs.map((j) => {
                const isApplied = appliedJobIds.has(j.id);
                return (
                  <article className="job" key={j.id}>
                    <div className="job-info">
                      <h3>{j.title || j.role}</h3>
                      <div className="job-meta">
                        <b>{j.company}</b> · {j.salary || j.package} · 📍 {j.location || "Remote"}
                      </div>
                      {j.description && <p className="job-desc">{j.description}</p>}
                      <div className="tags">
                        {(j.skills || []).map((s) => (
                          <span className="tag" key={s}>
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      {isApplied ? (
                        <button className="secondary" disabled>
                          Applied ✓
                        </button>
                      ) : (
                        <button
                          onClick={() => handleApply(j.id)}
                          disabled={applyingJobId === j.id}
                        >
                          {applyingJobId === j.id ? "Applying..." : "Apply Now"}
                        </button>
                      )}
                    </div>
                  </article>
                );
              })}
            </section>
          )}

          {/* 4. MY APPLICATIONS TAB */}
          {activeTab === "applications" && (
            <section>
              <h2>My Applications ({applications.length})</h2>
              {applications.length === 0 ? (
                <p style={{ color: "#687386", fontSize: 14 }}>
                  You have not applied for any jobs yet. Browse recommended or campus openings to apply.
                </p>
              ) : (
                applications.map((app) => (
                  <div
                    key={app.id}
                    style={{
                      border: "1px solid #e7eaf0",
                      borderRadius: 12,
                      padding: "16px 18px",
                      marginBottom: 16,
                      background: "white"
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div>
                        <h3 style={{ margin: "0 0 4px" }}>{app.job_title}</h3>
                        <div style={{ fontSize: 13, color: "#64748b" }}>
                          <b>{app.company}</b> · {app.salary || "Competitive"} · Applied on {new Date(app.applied_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>

                    {/* Visual Status Progression Timeline */}
                    <ApplicationTimeline currentStatus={app.status} />
                  </div>
                ))
              )}
            </section>
          )}

          {/* 5. MY INTERVIEWS TAB */}
          {activeTab === "interviews" && (
            <section>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <h2>My Interviews ({interviews.length})</h2>
                <button className="secondary sm" onClick={loadInterviews}>
                  ↻ Refresh
                </button>
              </div>

              {interviews.length === 0 ? (
                <p style={{ color: "#687386", fontSize: 14 }}>
                  No interviews scheduled yet. Once a recruiter shortlists your application, your interview invitation will appear here.
                </p>
              ) : (
                interviews.map((item) => {
                  const schedDate = new Date(item.scheduled_at);
                  return (
                    <div className="interview-card" key={item.id}>
                      <div className="interview-card-left">
                        <h4>{item.job_title} · {item.company}</h4>
                        <div className="interview-card-meta">
                          <span>📅 {schedDate.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric", year: "numeric" })}</span>
                          <span>⏰ {schedDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                          <span className={`mode-badge mode-${item.mode}`}>{item.mode}</span>
                          <span className={`badge badge-${item.status}`}>{item.status}</span>
                        </div>
                        {item.notes && <div className="interview-notes">📝 Notes: {item.notes}</div>}
                        {item.location && <div style={{ fontSize: 12, color: "#64748b", marginTop: 4 }}>📍 Location: {item.location}</div>}
                      </div>

                      <div>
                        {item.meeting_link && item.status === "SCHEDULED" && (
                          <a
                            href={item.meeting_link}
                            target="_blank"
                            rel="noreferrer"
                            className="btn success sm"
                          >
                            Join Interview ↗
                          </a>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </section>
          )}
        </div>

        <aside>
          <h2>Real-Time Activity</h2>
          {events.length ? (
            events.map((e, i) => (
              <div className={`event ${e.type?.includes("INTERVIEW") ? "interview-event" : ""}`} key={i}>
                <b>{(e.type || "").replaceAll("_", " ")}</b>
                <p>
                  {e.message ||
                    (e.type === "INTERVIEW_SCHEDULED"
                      ? `Interview scheduled for ${e.data?.job_title}`
                      : e.data?.status
                      ? `Application #${e.data.id} is now ${e.data.status}`
                      : e.data?.title
                      ? `${e.data.title} posted`
                      : "Live update")}
                </p>
                <time>{new Date().toLocaleTimeString()}</time>
              </div>
            ))
          ) : (
            <p style={{ color: "#687386", fontSize: 14 }}>Listening for placement events...</p>
          )}
        </aside>
      </main>

      {/* VIEW JOB DETAILS MODAL */}
      {viewingJob && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <div>
                <h3 style={{ margin: "0 0 4px" }}>{viewingJob.title || viewingJob.role}</h3>
                <div style={{ fontSize: 14, color: "#64748b" }}>
                  <b>{viewingJob.company}</b> · {viewingJob.salary || viewingJob.package} · 📍 {viewingJob.location || "Remote"}
                </div>
              </div>
              <button className="modal-close" onClick={() => setViewingJob(null)}>
                &times;
              </button>
            </div>

            <div style={{ margin: "16px 0" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <span className={`match-score-badge ${viewingJob.match_percentage >= 70 ? "match-high" : viewingJob.match_percentage >= 40 ? "match-mid" : "match-low"}`}>
                  Skill Match: {viewingJob.match_percentage ?? 0}%
                </span>
              </div>

              <div style={{ marginBottom: 16 }}>
                <h4 style={{ margin: "0 0 6px", fontSize: 14, color: "#1e293b" }}>Job Description</h4>
                <p style={{ margin: 0, fontSize: 13, color: "#475569", lineHeight: 1.6 }}>
                  {viewingJob.description || "No detailed description provided."}
                </p>
              </div>

              <div style={{ marginBottom: 16 }}>
                <h4 style={{ margin: "0 0 6px", fontSize: 14, color: "#1e293b" }}>Required Skills Alignment</h4>
                <div className="tags">
                  {(viewingJob.matched_skills || []).map((s) => (
                    <span key={s} className="tag tag-matched">
                      {s} ✓
                    </span>
                  ))}
                  {(viewingJob.missing_skills || []).map((s) => (
                    <span key={s} className="tag tag-missing">
                      Missing: {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 20 }}>
              <button type="button" className="secondary sm" onClick={() => setViewingJob(null)}>
                Close
              </button>
              {appliedJobIds.has(viewingJob.id) ? (
                <button className="secondary sm" disabled>
                  Applied ✓
                </button>
              ) : (
                <button
                  type="button"
                  className="primary sm"
                  onClick={() => handleApply(viewingJob.id)}
                  disabled={applyingJobId === viewingJob.id}
                >
                  {applyingJobId === viewingJob.id ? "Applying..." : "Apply"}
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// ==========================================
// 5. RECRUITER DASHBOARD
// ==========================================
function RecruiterDashboard({ user, jobs, loadJobs, applications, loadApplications, interviews, loadInterviews, events }) {
  const [activeTab, setActiveTab] = useState("applicants"); // 'applicants' | 'interviews' | 'post_job' | 'my_jobs'
  const recruiter = user?.recruiter_profile;

  // Schedule Interview Modal State
  const [schedulingApp, setSchedulingApp] = useState(null);
  const [schedDate, setSchedDate] = useState("");
  const [schedTime, setSchedTime] = useState("10:00");
  const [schedMode, setSchedMode] = useState("ONLINE");
  const [schedLink, setSchedLink] = useState("https://meet.google.com/new-interview-room");
  const [schedLocation, setSchedLocation] = useState("Google Meet");
  const [schedNotes, setSchedNotes] = useState("Round 1 Technical Interview");
  const [submittingSched, setSubmittingSched] = useState(false);
  const [scheduleMsg, setScheduleMsg] = useState("");

  // Post Job Form State
  const [title, setTitle] = useState("");
  const [company, setCompany] = useState(recruiter?.company_name || "");
  const [description, setDescription] = useState("");
  const [salary, setSalary] = useState("9 LPA");
  const [location, setLocation] = useState("Bangalore");
  const [jobSkills, setJobSkills] = useState(["Java", "SQL", "Docker", "Spring Boot"]);
  const [jobSkillInput, setJobSkillInput] = useState("");
  const [posting, setPosting] = useState(false);
  const [postMsg, setPostMsg] = useState("");

  const handleAddJobSkill = (skillName) => {
    const clean = (skillName || jobSkillInput).trim();
    if (!clean) return;
    if (!jobSkills.some((s) => s.toLowerCase() === clean.toLowerCase())) {
      setJobSkills([...jobSkills, clean]);
    }
    setJobSkillInput("");
  };

  const handleRemoveJobSkill = (skillToRemove) => {
    setJobSkills(jobSkills.filter((s) => s !== skillToRemove));
  };

  const handleCreateJob = async (e) => {
    e.preventDefault();
    setPosting(true);
    setPostMsg("");

    const payload = {
      title,
      company: company || recruiter?.company_name,
      description,
      salary,
      location,
      skills: jobSkills
    };

    try {
      const res = await authFetch("/api/jobs", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setPostMsg("Job successfully posted and broadcasted to candidates!");
        setTitle("");
        setDescription("");
        loadJobs();
        setTimeout(() => setActiveTab("my_jobs"), 1200);
      } else {
        const err = await res.json();
        setPostMsg(`Error: ${err.detail || "Failed to create job"}`);
      }
    } catch {
      setPostMsg("Network error creating job");
    } finally {
      setPosting(false);
    }
  };

  const handleUpdateAppStatus = async (applicationId, newStatus) => {
    try {
      const res = await authFetch(`/api/applications/${applicationId}`, {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus })
      });
      if (res.ok) {
        loadApplications();
      } else {
        const err = await res.json();
        alert(err.detail || "Failed to update status");
      }
    } catch {
      alert("Error communicating with server");
    }
  };

  const handleOpenScheduleModal = (app) => {
    setSchedulingApp(app);
    setScheduleMsg("");
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setSchedDate(tomorrow.toISOString().split("T")[0]);
  };

  const handleScheduleSubmit = async (e) => {
    e.preventDefault();
    if (!schedulingApp) return;

    setSubmittingSched(true);
    setScheduleMsg("");

    const combinedDateTime = new Date(`${schedDate}T${schedTime}:00`);

    const payload = {
      application_id: schedulingApp.id,
      scheduled_at: combinedDateTime.toISOString(),
      mode: schedMode,
      meeting_link: schedMode !== "OFFLINE" ? schedLink : null,
      location: schedLocation,
      notes: schedNotes
    };

    try {
      const res = await authFetch("/api/interviews", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setScheduleMsg("Interview scheduled and broadcasted in real-time!");
        loadInterviews();
        loadApplications();
        setTimeout(() => {
          setSchedulingApp(null);
          setActiveTab("interviews");
        }, 1200);
      } else {
        const err = await res.json();
        setScheduleMsg(`Error: ${err.detail || "Failed to schedule interview"}`);
      }
    } catch {
      setScheduleMsg("Network error scheduling interview");
    } finally {
      setSubmittingSched(false);
    }
  };

  const handleUpdateInterviewStatus = async (interviewId, newStatus) => {
    try {
      const res = await authFetch(`/api/interviews/${interviewId}`, {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus })
      });
      if (res.ok) {
        loadInterviews();
      } else {
        const err = await res.json();
        alert(err.detail || "Failed to update interview");
      }
    } catch {
      alert("Network error updating interview");
    }
  };

  const handleDeleteInterview = async (interviewId) => {
    if (!confirm("Are you sure you want to cancel and remove this interview?")) return;
    try {
      const res = await authFetch(`/api/interviews/${interviewId}`, { method: "DELETE" });
      if (res.ok) {
        loadInterviews();
      } else {
        alert("Failed to delete interview");
      }
    } catch {
      alert("Error deleting interview");
    }
  };

  return (
    <>
      <div className="profile-card">
        <h3>{recruiter?.company_name || "Company"} Recruiter Hub</h3>
        <p style={{ margin: 0, opacity: 0.8, fontSize: 14 }}>
          Lead Recruiter: {user?.name} · Contact: {recruiter?.company_email || user?.email}
        </p>
        <div className="profile-grid">
          <div className="profile-item">
            <span>Posted Jobs</span>
            <b>{jobs.length} Active</b>
          </div>
          <div className="profile-item">
            <span>Total Applicants</span>
            <b>{applications.length} Candidates</b>
          </div>
          <div className="profile-item">
            <span>Interviews Scheduled</span>
            <b>{interviews.length} Scheduled</b>
          </div>
        </div>
      </div>

      <div className="dash-tabs">
        <div
          className={`dash-tab ${activeTab === "applicants" ? "active" : ""}`}
          onClick={() => setActiveTab("applicants")}
        >
          👥 Candidate Workflow ({applications.length})
        </div>
        <div
          className={`dash-tab ${activeTab === "interviews" ? "active" : ""}`}
          onClick={() => setActiveTab("interviews")}
        >
          📅 Interview Management ({interviews.length})
        </div>
        <div
          className={`dash-tab ${activeTab === "post_job" ? "active" : ""}`}
          onClick={() => setActiveTab("post_job")}
        >
          ➕ Post New Job
        </div>
        <div
          className={`dash-tab ${activeTab === "my_jobs" ? "active" : ""}`}
          onClick={() => setActiveTab("my_jobs")}
        >
          📋 Active Postings ({jobs.length})
        </div>
      </div>

      <main>
        <div>
          {/* APPLICANTS WORKFLOW TAB */}
          {activeTab === "applicants" && (
            <section>
              <h2>Applicant Status & Workflow Pipeline</h2>
              {applications.length === 0 ? (
                <p style={{ color: "#687386" }}>No student applications received yet.</p>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Candidate</th>
                        <th>College / CGPA</th>
                        <th>Position</th>
                        <th>Skill Match</th>
                        <th>Resume</th>
                        <th>Status</th>
                        <th>Workflow Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {applications.map((app) => {
                        const pct = app.match_percentage;
                        const matchClass = pct >= 70 ? "match-high" : pct >= 40 ? "match-mid" : "match-low";

                        return (
                          <tr key={app.id}>
                            <td>
                              <b>{app.student_name || "Candidate"}</b>
                              <div style={{ fontSize: 12, color: "#687386" }}>{app.student_email}</div>
                            </td>
                            <td>
                              <div>{app.college || "University"}</div>
                              <span style={{ fontSize: 12, fontWeight: 600, color: "#2563eb" }}>
                                CGPA: {app.cgpa || "N/A"}
                              </span>
                            </td>
                            <td>
                              <b>{app.job_title}</b>
                            </td>
                            <td>
                              {pct != null ? (
                                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                                  <span className={`match-score-badge ${matchClass}`}>
                                    🎯 {pct}% Match
                                  </span>
                                  <div style={{ display: "flex", flexWrap: "wrap", gap: 3, maxWidth: 220 }}>
                                    {(app.matched_skills || []).map((s) => (
                                      <span key={s} className="tag tag-matched" style={{ fontSize: 10, padding: "1px 6px" }}>
                                        ✓ {s}
                                      </span>
                                    ))}
                                    {(app.missing_skills || []).map((s) => (
                                      <span key={s} className="tag tag-missing" style={{ fontSize: 10, padding: "1px 6px" }}>
                                        ✗ {s}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              ) : (
                                <span style={{ fontSize: 12, color: "#94a3b8" }}>Pending Match</span>
                              )}
                            </td>
                            <td>
                              {app.resume_url ? (
                                <a
                                  href={app.resume_url}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="btn secondary sm"
                                  style={{ display: "inline-flex", alignItems: "center", gap: 4, textDecoration: "none" }}
                                >
                                  📄 View PDF
                                </a>
                              ) : (
                                <span style={{ fontSize: 12, color: "#94a3b8" }}>No resume</span>
                              )}
                            </td>
                            <td>
                              <span className={`badge badge-${app.status}`}>{app.status}</span>
                              {app.interview_status && (
                                <div style={{ marginTop: 4 }}>
                                  <span className={`badge badge-${app.interview_status}`} style={{ fontSize: 10, padding: "1px 6px" }}>
                                    🗓️ {app.interview_status}
                                  </span>
                                </div>
                              )}
                            </td>
                            <td>
                              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                                {app.status === "APPLIED" && (
                                  <button
                                    className="secondary sm"
                                    onClick={() => handleUpdateAppStatus(app.id, "UNDER_REVIEW")}
                                  >
                                    Review
                                  </button>
                                )}
                                {app.status === "UNDER_REVIEW" && (
                                  <button
                                    className="primary sm"
                                    onClick={() => handleUpdateAppStatus(app.id, "SHORTLISTED")}
                                  >
                                    Shortlist
                                  </button>
                                )}
                                {(app.status === "SHORTLISTED" || app.status === "UNDER_REVIEW" || app.status === "APPLIED") && (
                                  <button
                                    className="btn success sm"
                                    onClick={() => handleOpenScheduleModal(app)}
                                  >
                                    🗓️ Schedule Interview
                                  </button>
                                )}
                                {app.status === "INTERVIEW" && (
                                  <>
                                    <button
                                      className="btn success sm"
                                      onClick={() => handleUpdateAppStatus(app.id, "SELECTED")}
                                    >
                                      Accept / Hire
                                    </button>
                                    <button
                                      className="btn secondary sm"
                                      onClick={() => handleOpenScheduleModal(app)}
                                    >
                                      + Add Round
                                    </button>
                                  </>
                                )}
                                {app.status !== "REJECTED" && app.status !== "SELECTED" && (
                                  <button
                                    className="danger sm"
                                    onClick={() => handleUpdateAppStatus(app.id, "REJECTED")}
                                  >
                                    Reject
                                  </button>
                                )}
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          )}

          {/* INTERVIEW MANAGEMENT TAB */}
          {activeTab === "interviews" && (
            <section>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <h2>Interview Management ({interviews.length})</h2>
                <button className="secondary sm" onClick={loadInterviews}>
                  ↻ Refresh
                </button>
              </div>

              {interviews.length === 0 ? (
                <p style={{ color: "#687386", fontSize: 14 }}>
                  No interviews scheduled yet. Switch to the Candidate Workflow tab and click "Schedule Interview" on any candidate.
                </p>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Candidate</th>
                        <th>Position</th>
                        <th>Scheduled At</th>
                        <th>Mode</th>
                        <th>Link / Location</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {interviews.map((item) => (
                        <tr key={item.id}>
                          <td>
                            <b>{item.student_name}</b>
                            <div style={{ fontSize: 12, color: "#687386" }}>{item.student_email}</div>
                          </td>
                          <td>
                            <b>{item.job_title}</b>
                          </td>
                          <td>
                            <div>{new Date(item.scheduled_at).toLocaleDateString()}</div>
                            <div style={{ fontSize: 12, color: "#687386" }}>
                              {new Date(item.scheduled_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                            </div>
                          </td>
                          <td>
                            <span className={`mode-badge mode-${item.mode}`}>{item.mode}</span>
                          </td>
                          <td>
                            {item.meeting_link ? (
                              <a
                                href={item.meeting_link}
                                target="_blank"
                                rel="noreferrer"
                                style={{ color: "#315dbd", fontWeight: 600, fontSize: 13 }}
                              >
                                Join Link ↗
                              </a>
                            ) : (
                              item.location || "On-Campus"
                            )}
                          </td>
                          <td>
                            <span className={`badge badge-${item.status}`}>{item.status}</span>
                          </td>
                          <td>
                            <div style={{ display: "flex", gap: 6 }}>
                              {item.status === "SCHEDULED" && (
                                <button
                                  className="btn success sm"
                                  onClick={() => handleUpdateInterviewStatus(item.id, "COMPLETED")}
                                >
                                  Complete
                                </button>
                              )}
                              {item.status !== "CANCELLED" && (
                                <button
                                  className="btn secondary sm"
                                  onClick={() => handleUpdateInterviewStatus(item.id, "CANCELLED")}
                                >
                                  Cancel
                                </button>
                              )}
                              <button
                                className="btn danger sm"
                                onClick={() => handleDeleteInterview(item.id)}
                              >
                                ✕
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          )}

          {/* POST NEW JOB TAB */}
          {activeTab === "post_job" && (
            <section>
              <h2>Publish a New Job Opening</h2>
              {postMsg && (
                <div className={`alert ${postMsg.includes("Error") ? "alert-error" : "alert-success"}`}>
                  {postMsg}
                </div>
              )}
              <form onSubmit={handleCreateJob}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                  <div className="form-group">
                    <label>Job Title / Role</label>
                    <input
                      type="text"
                      required
                      value={title}
                      placeholder="e.g. Full Stack Developer"
                      onChange={(e) => setTitle(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Company Name</label>
                    <input
                      type="text"
                      required
                      value={company}
                      placeholder={recruiter?.company_name}
                      onChange={(e) => setCompany(e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Job Description & Responsibilities</label>
                  <textarea
                    rows={4}
                    required
                    value={description}
                    placeholder="Describe role requirements, expectations, and day-to-day work..."
                    onChange={(e) => setDescription(e.target.value)}
                  />
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                  <div className="form-group">
                    <label>Compensation / Package</label>
                    <input
                      type="text"
                      required
                      value={salary}
                      placeholder="e.g. 10 LPA or $80,000"
                      onChange={(e) => setSalary(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Location</label>
                    <input
                      type="text"
                      required
                      value={location}
                      placeholder="e.g. Bangalore / Remote"
                      onChange={(e) => setLocation(e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Required Skills</label>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 10 }}>
                    {jobSkills.map((s) => (
                      <span key={s} className="skill-pill-editable">
                        {s}
                        <button
                          type="button"
                          className="skill-pill-remove"
                          onClick={() => handleRemoveJobSkill(s)}
                          title="Remove skill"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>

                  <div style={{ display: "flex", gap: 8 }}>
                    <input
                      type="text"
                      placeholder="Type a skill and press Add or Enter (e.g. Java, Docker)"
                      value={jobSkillInput}
                      onChange={(e) => setJobSkillInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          handleAddJobSkill();
                        }
                      }}
                      style={{ flex: 1 }}
                    />
                    <button
                      type="button"
                      className="secondary sm"
                      onClick={() => handleAddJobSkill()}
                      disabled={!jobSkillInput.trim()}
                    >
                      + Add
                    </button>
                  </div>

                  <div style={{ marginTop: 8, fontSize: 12, color: "#64748b" }}>
                    Quick suggestions:{" "}
                    {["Java", "SQL", "Docker", "Spring Boot", "Python", "React", "FastAPI", "AWS", "Kubernetes", "Node.js"].map((s) => (
                      <button
                        key={s}
                        type="button"
                        onClick={() => handleAddJobSkill(s)}
                        style={{
                          background: jobSkills.includes(s) ? "#315dbd" : "#e2e8f0",
                          color: jobSkills.includes(s) ? "white" : "#334155",
                          border: "none",
                          borderRadius: 12,
                          padding: "2px 8px",
                          fontSize: 11,
                          margin: "2px 4px",
                          cursor: "pointer"
                        }}
                      >
                        {jobSkills.includes(s) ? `✓ ${s}` : `+ ${s}`}
                      </button>
                    ))}
                  </div>
                </div>

                <button type="submit" disabled={posting} style={{ marginTop: 10 }}>
                  {posting ? "Publishing..." : "🚀 Publish & Broadcast Job"}
                </button>
              </form>
            </section>
          )}

          {/* MY JOBS TAB */}
          {activeTab === "my_jobs" && (
            <section>
              <h2>Manage Job Postings</h2>
              {jobs.map((j) => (
                <article className="job" key={j.id}>
                  <div className="job-info">
                    <h3>{j.title || j.role}</h3>
                    <div className="job-meta">
                      <b>{j.company}</b> · {j.salary || j.package} · 📍 {j.location || "Remote"}
                    </div>
                    {j.description && <p className="job-desc">{j.description}</p>}
                    <div className="tags">
                      {(j.skills || []).map((s) => (
                        <span className="tag" key={s}>
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="badge badge-APPLIED" style={{ marginRight: 10 }}>
                      Active
                    </span>
                  </div>
                </article>
              ))}
            </section>
          )}
        </div>

        <aside>
          <h2>Live Stream</h2>
          {events.length ? (
            events.map((e, i) => (
              <div className={`event ${e.type?.includes("INTERVIEW") ? "interview-event" : ""}`} key={i}>
                <b>{(e.type || "").replaceAll("_", " ")}</b>
                <p>
                  {e.message ||
                    (e.type === "INTERVIEW_SCHEDULED"
                      ? `Interview scheduled for ${e.data?.job_title}`
                      : e.data?.status
                      ? `Candidate status updated to ${e.data.status}`
                      : e.data?.title
                      ? `${e.data.title} posted`
                      : "Placement event")}
                </p>
                <time>{new Date().toLocaleTimeString()}</time>
              </div>
            ))
          ) : (
            <p style={{ color: "#687386", fontSize: 14 }}>Listening for placement events...</p>
          )}
        </aside>
      </main>

      {/* SCHEDULE INTERVIEW MODAL */}
      {schedulingApp && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Schedule Interview with {schedulingApp.student_name || "Candidate"}</h3>
              <button className="modal-close" onClick={() => setSchedulingApp(null)}>
                &times;
              </button>
            </div>

            {scheduleMsg && (
              <div className={`alert ${scheduleMsg.includes("Error") ? "alert-error" : "alert-success"}`}>
                {scheduleMsg}
              </div>
            )}

            <form onSubmit={handleScheduleSubmit}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div className="form-group">
                  <label>Candidate</label>
                  <input type="text" disabled value={schedulingApp.student_name || "Student"} />
                </div>
                <div className="form-group">
                  <label>Position</label>
                  <input type="text" disabled value={schedulingApp.job_title || "Job"} />
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: 12 }}>
                <div className="form-group">
                  <label>Interview Date</label>
                  <input
                    type="date"
                    required
                    value={schedDate}
                    onChange={(e) => setSchedDate(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Interview Time</label>
                  <input
                    type="time"
                    required
                    value={schedTime}
                    onChange={(e) => setSchedTime(e.target.value)}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Interview Mode</label>
                <select value={schedMode} onChange={(e) => setSchedMode(e.target.value)}>
                  <option value="ONLINE">ONLINE (Video Call)</option>
                  <option value="OFFLINE">OFFLINE (In-Person / On-Campus)</option>
                  <option value="HYBRID">HYBRID (Flexible)</option>
                </select>
              </div>

              {schedMode !== "OFFLINE" && (
                <div className="form-group">
                  <label>Meeting Link</label>
                  <input
                    type="url"
                    required
                    value={schedLink}
                    placeholder="https://meet.google.com/xyz or Zoom link"
                    onChange={(e) => setSchedLink(e.target.value)}
                  />
                </div>
              )}

              <div className="form-group">
                <label>Location / Room</label>
                <input
                  type="text"
                  value={schedLocation}
                  placeholder="e.g. Google Meet, Placement Cell Hall 2"
                  onChange={(e) => setSchedLocation(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Interviewer Notes & Instructions</label>
                <textarea
                  rows={3}
                  value={schedNotes}
                  placeholder="e.g. Technical round covering Python, DS/Algo, and past project architecture."
                  onChange={(e) => setSchedNotes(e.target.value)}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 20 }}>
                <button
                  type="button"
                  className="secondary"
                  onClick={() => setSchedulingApp(null)}
                >
                  Cancel
                </button>
                <button type="submit" disabled={submittingSched}>
                  {submittingSched ? "Scheduling..." : "Confirm & Broadcast Interview"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

// ==========================================
// 6. ADMIN DASHBOARD
// ==========================================
function AdminDashboard({ user, stats, users, loadAdminData, jobs, applications, interviews, loadInterviews, events }) {
  const [deleteMsg, setDeleteMsg] = useState("");

  const handleDeleteUser = async (userId) => {
    if (!confirm(`Are you sure you want to delete user #${userId}?`)) return;
    try {
      const res = await authFetch(`/api/admin/users/${userId}`, { method: "DELETE" });
      if (res.ok) {
        setDeleteMsg(`User #${userId} deleted successfully.`);
        loadAdminData();
      } else {
        const err = await res.json();
        alert(err.detail || "Failed to delete user");
      }
    } catch {
      alert("Error deleting user");
    }
  };

  return (
    <>
      <div className="profile-card">
        <h3>Master Administration Console</h3>
        <p style={{ margin: 0, opacity: 0.8, fontSize: 14 }}>
          Administrator: {user?.name} · Elevated Role: ADMIN · Full Platform Access
        </p>
      </div>

      {/* Admin Stats Row with Interview Metrics */}
      <section className="stats">
        <div className="stat-card">
          <b>{stats?.total_students ?? "—"}</b>
          <span>Total Students</span>
        </div>
        <div className="stat-card">
          <b>{stats?.total_recruiters ?? "—"}</b>
          <span>Total Recruiters</span>
        </div>
        <div className="stat-card">
          <b>{stats?.total_jobs ?? jobs.length}</b>
          <span>Active Jobs</span>
        </div>
        <div className="stat-card">
          <b>{stats?.total_applications ?? applications.length}</b>
          <span>Total Applications</span>
        </div>
      </section>

      <section className="stats" style={{ marginTop: -8 }}>
        <div className="stat-card">
          <b>{stats?.total_interviews ?? interviews.length}</b>
          <span>Total Interviews</span>
        </div>
        <div className="stat-card">
          <b style={{ color: "#0284c7" }}>{stats?.scheduled_interviews ?? 0}</b>
          <span>Scheduled</span>
        </div>
        <div className="stat-card">
          <b style={{ color: "#16a34a" }}>{stats?.completed_interviews ?? 0}</b>
          <span>Completed</span>
        </div>
        <div className="stat-card">
          <b style={{ color: "#64748b" }}>{stats?.cancelled_interviews ?? 0}</b>
          <span>Cancelled</span>
        </div>
      </section>

      {/* Resume & Match Analytics Row */}
      <section className="stats" style={{ marginTop: -8 }}>
        <div className="stat-card">
          <b style={{ color: "#2563eb" }}>{stats?.average_job_match_percentage ?? 0}%</b>
          <span>Avg Job Match</span>
        </div>
        <div className="stat-card">
          <b style={{ color: "#7c3aed" }}>{stats?.total_resumes_uploaded ?? 0}</b>
          <span>Resumes Uploaded</span>
        </div>
        <div className="stat-card">
          <b style={{ color: "#059669" }}>{stats?.total_students_with_resumes ?? 0}</b>
          <span>Students with Resume</span>
        </div>
        <div className="stat-card">
          <b>{stats?.most_demanded_skills?.length ?? 0}</b>
          <span>Tracked Skills</span>
        </div>
      </section>

      <main>
        <div>
          {deleteMsg && <div className="alert alert-success">{deleteMsg}</div>}

          {/* MOST DEMANDED SKILLS ANALYTICS */}
          <section style={{ marginBottom: 24, background: "white", padding: "20px 24px", borderRadius: 14, border: "1px solid #e2e8f0" }}>
            <h2 style={{ margin: "0 0 4px" }}>Most Demanded Skills</h2>
            <p style={{ margin: "0 0 16px", fontSize: 13, color: "#64748b" }}>
              Top technology requirements requested by recruiters across campus job openings.
            </p>

            {(!stats?.most_demanded_skills || stats.most_demanded_skills.length === 0) ? (
              <p style={{ color: "#687386", fontSize: 14, margin: 0 }}>No skill demand data available.</p>
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12 }}>
                {stats.most_demanded_skills.map((item) => (
                  <div
                    key={item.skill}
                    style={{
                      background: "#f8fafc",
                      border: "1px solid #e2e8f0",
                      borderRadius: 10,
                      padding: "10px 14px",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center"
                    }}
                  >
                    <b style={{ color: "#1e293b", fontSize: 14 }}>{item.skill}</b>
                    <span style={{ background: "#e0e7ff", color: "#3730a3", fontWeight: 700, padding: "2px 10px", borderRadius: 12, fontSize: 12 }}>
                      {item.count} {item.count === 1 ? "job" : "jobs"}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* RECENT INTERVIEWS TABLE */}
          <section style={{ marginBottom: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <h2>Recent Interviews Across System ({interviews.length})</h2>
              <button className="secondary sm" onClick={loadInterviews}>
                ↻ Refresh
              </button>
            </div>

            {interviews.length === 0 ? (
              <p style={{ color: "#687386", fontSize: 14 }}>No interviews scheduled across the system.</p>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Student</th>
                      <th>Company</th>
                      <th>Job Title</th>
                      <th>Date & Time</th>
                      <th>Mode</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {interviews.map((item) => (
                      <tr key={item.id}>
                        <td>
                          <b>{item.student_name}</b>
                          <div style={{ fontSize: 12, color: "#687386" }}>{item.student_email}</div>
                        </td>
                        <td>{item.company}</td>
                        <td>
                          <b>{item.job_title}</b>
                        </td>
                        <td>
                          <div>{new Date(item.scheduled_at).toLocaleDateString()}</div>
                          <div style={{ fontSize: 12, color: "#687386" }}>
                            {new Date(item.scheduled_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                          </div>
                        </td>
                        <td>
                          <span className={`mode-badge mode-${item.mode}`}>{item.mode}</span>
                        </td>
                        <td>
                          <span className={`badge badge-${item.status}`}>{item.status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {/* USER MANAGEMENT SECTION */}
          <section style={{ marginBottom: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
              <h2>User Management ({users.length})</h2>
              <button className="secondary sm" onClick={loadAdminData}>
                ↻ Refresh Users
              </button>
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>User ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Joined</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id}>
                      <td>#{u.id}</td>
                      <td>
                        <b>{u.name}</b>
                        {u.student_profile && (
                          <div style={{ fontSize: 11, color: "#687386" }}>
                            {u.student_profile.degree} - {u.student_profile.college}
                          </div>
                        )}
                        {u.recruiter_profile && (
                          <div style={{ fontSize: 11, color: "#687386" }}>
                            Company: {u.recruiter_profile.company_name}
                          </div>
                        )}
                      </td>
                      <td>{u.email}</td>
                      <td>
                        <span className={`role-tag role-${u.role.toLowerCase()}`}>{u.role}</span>
                      </td>
                      <td>{new Date(u.created_at).toLocaleDateString()}</td>
                      <td>
                        {u.id !== user?.id ? (
                          <button
                            className="danger sm"
                            onClick={() => handleDeleteUser(u.id)}
                          >
                            Delete
                          </button>
                        ) : (
                          <span style={{ fontSize: 12, color: "#687386" }}>Current User</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* SYSTEM APPLICATIONS OVERVIEW */}
          <section>
            <h2>System-Wide Applications ({applications.length})</h2>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>App ID</th>
                    <th>Candidate</th>
                    <th>Role Applied</th>
                    <th>Company</th>
                    <th>Date</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {applications.map((a) => (
                    <tr key={a.id}>
                      <td>#{a.id}</td>
                      <td>{a.student_name || `Student #${a.student_id}`}</td>
                      <td>
                        <b>{a.job_title}</b>
                      </td>
                      <td>{a.company}</td>
                      <td>{new Date(a.applied_at).toLocaleDateString()}</td>
                      <td>
                        <span className={`badge badge-${a.status}`}>{a.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>

        <aside>
          <h2>Real-Time Audit Trail</h2>
          {events.length ? (
            events.map((e, i) => (
              <div className={`event ${e.type?.includes("INTERVIEW") ? "interview-event" : ""}`} key={i}>
                <b>{(e.type || "").replaceAll("_", " ")}</b>
                <p>{e.message || JSON.stringify(e.data || {})}</p>
                <time>{new Date().toLocaleTimeString()}</time>
              </div>
            ))
          ) : (
            <p style={{ color: "#687386", fontSize: 14 }}>Real-time event stream active...</p>
          )}
        </aside>
      </main>
    </>
  );
}

createRoot(document.getElementById("root")).render(<App />);
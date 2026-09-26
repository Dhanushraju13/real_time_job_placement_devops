import React, { useEffect, useState, useMemo } from "react";
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

// Company Logo Component with authentic brand SVGs
function CompanyLogo({ name = "", size = 48 }) {
  const cleanName = (name || "").toLowerCase().trim();

  if (cleanName.includes("technova")) {
    return (
      <div
        className="company-logo-wrap"
        style={{ width: size, height: size, background: "#FFF1F0", border: "1px solid #FFCCC7" }}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <rect x="3" y="4" width="18" height="4" rx="2" fill="#E11D48" />
          <rect x="10" y="8" width="4" height="12" rx="2" fill="#E11D48" />
        </svg>
      </div>
    );
  }

  if (cleanName.includes("amazon")) {
    return (
      <div
        className="company-logo-wrap"
        style={{ width: size, height: size, background: "#FFFFFF", border: "1px solid #E5E7EB" }}
      >
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
          <path
            d="M14.5 12.5C13.8 11.2 12.4 10.5 10.5 10.5C8 10.5 6.2 12 6.2 14.2C6.2 16.2 7.7 17.5 9.8 17.5C11.5 17.5 13 16.6 13.8 15.3V17.2H16V10.8H14.5V12.5ZM11.1 16C9.6 16 8.5 15.1 8.5 14C8.5 12.8 9.7 11.9 11.2 11.9C12.7 11.9 13.8 12.8 13.8 14C13.8 15.1 12.6 16 11.1 16Z"
            fill="#111111"
          />
          <path
            d="M4.5 18.5C9 21.5 16 20.5 19.5 17.5"
            stroke="#F59E0B"
            strokeWidth="2.2"
            strokeLinecap="round"
          />
          <path d="M19.5 17.5L18.2 15.5" stroke="#F59E0B" strokeWidth="2.2" strokeLinecap="round" />
        </svg>
      </div>
    );
  }

  if (cleanName.includes("microsoft")) {
    return (
      <div
        className="company-logo-wrap"
        style={{ width: size, height: size, background: "#FFFFFF", border: "1px solid #E5E7EB" }}
      >
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2.5, width: 20, height: 20 }}>
          <div style={{ background: "#F25022", borderRadius: 1 }}></div>
          <div style={{ background: "#7FBA00", borderRadius: 1 }}></div>
          <div style={{ background: "#00A4EF", borderRadius: 1 }}></div>
          <div style={{ background: "#FFB900", borderRadius: 1 }}></div>
        </div>
      </div>
    );
  }

  if (cleanName.includes("google")) {
    return (
      <div
        className="company-logo-wrap"
        style={{ width: size, height: size, background: "#FFFFFF", border: "1px solid #E5E7EB" }}
      >
        <svg width="22" height="22" viewBox="0 0 24 24">
          <path
            fill="#4285F4"
            d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.8-2.4 3.66v3.05h3.87c2.26-2.09 3.675-5.17 3.675-9.15z"
          />
          <path
            fill="#34A853"
            d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.87-3.05c-1.08.72-2.45 1.16-4.06 1.16-3.13 0-5.78-2.11-6.73-4.96H1.28v3.13C3.25 21.3 7.31 24 12 24z"
          />
          <path
            fill="#FBBC05"
            d="M5.27 14.24c-.25-.72-.38-1.49-.38-2.24s.13-1.52.38-2.24V6.63H1.28C.47 8.24 0 10.06 0 12s.47 3.76 1.28 5.37l3.99-3.13z"
          />
          <path
            fill="#EA4335"
            d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.31 0 3.25 2.7 1.28 6.63l3.99 3.13c.95-2.85 3.6-4.96 6.73-4.96z"
          />
        </svg>
      </div>
    );
  }

  if (cleanName.includes("infosys")) {
    return (
      <div
        className="company-logo-wrap"
        style={{ width: size, height: size, background: "#007CC3", color: "#FFFFFF", fontWeight: 800 }}
      >
        infy
      </div>
    );
  }

  if (cleanName.includes("zoho")) {
    return (
      <div
        className="company-logo-wrap"
        style={{ width: size, height: size, background: "#FFFFFF", border: "1px solid #E5E7EB" }}
      >
        <span style={{ fontWeight: 800, fontSize: 16, color: "#E11D48" }}>Z</span>
      </div>
    );
  }

  const initial = (name || "C").charAt(0).toUpperCase();
  return (
    <div
      className="company-logo-wrap"
      style={{
        width: size,
        height: size,
        background: "#EEF2F6",
        color: "#1E293B",
        fontWeight: 700
      }}
    >
      {initial}
    </div>
  );
}

// Animated Counter Hook
function useCounter(targetNumber, duration = 1200) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = parseInt(targetNumber, 10);
    if (isNaN(end) || end === 0) {
      setCount(targetNumber);
      return;
    }

    const incrementTime = 25;
    const steps = duration / incrementTime;
    const stepIncrement = Math.ceil(end / steps);

    const timer = setInterval(() => {
      start += stepIncrement;
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(start);
      }
    }, incrementTime);

    return () => clearInterval(timer);
  }, [targetNumber, duration]);

  return count;
}

// Application Timeline component
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
        <span style={{ fontSize: 11.5, fontWeight: 700, color: "#475569", textTransform: "uppercase", letterSpacing: 0.5 }}>
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

// ==========================================
// MAIN APPLICATION ROOT
// ==========================================
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

  // Modals
  const [showVideoModal, setShowVideoModal] = useState(false);
  const [selectedJobForModal, setSelectedJobForModal] = useState(null);
  const [notificationToast, setNotificationToast] = useState(null);

  // Navigation helper
  const navigate = (path) => {
    window.history.pushState({}, "", path);
    setRoute(path);
    window.scrollTo({ top: 0, behavior: "smooth" });
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

  const triggerNotificationOptIn = () => {
    setNotificationToast("Notifications enabled! You will receive instant alerts for new placements and jobs.");
    setTimeout(() => setNotificationToast(null), 4000);
  };

  return (
    <div className="page">
      {/* Toast Notification */}
      {notificationToast && (
        <div
          style={{
            position: "fixed",
            bottom: 24,
            right: 24,
            background: "#111111",
            color: "#FFFFFF",
            padding: "12px 20px",
            borderRadius: 9999,
            fontSize: 13.5,
            fontWeight: 500,
            boxShadow: "0 10px 25px rgba(0,0,0,0.2)",
            zIndex: 9999,
            display: "flex",
            alignItems: "center",
            gap: 10,
            animation: "slideUp 0.2s ease"
          }}
        >
          <span>🔔 {notificationToast}</span>
          <button
            onClick={() => setNotificationToast(null)}
            style={{ background: "transparent", border: "none", color: "#9CA3AF", cursor: "pointer", fontSize: 16 }}
          >
            &times;
          </button>
        </div>
      )}

      {/* NAVBAR */}
      <div className="header-wrapper">
        <header>
          <div className="header-left">
            <div className="brand" onClick={() => navigate("/")}>
              <div className="brand-icon">P</div>
              <h1>PlacementHub</h1>
            </div>
          </div>

          <nav className="nav-center">
            <button
              className={`nav-link ${route === "/" ? "active" : ""}`}
              onClick={() => navigate("/")}
            >
              Home
            </button>
            <button
              className={`nav-link ${route === "/jobs" ? "active" : ""}`}
              onClick={() => navigate("/jobs")}
            >
              Jobs
            </button>
            <button
              className={`nav-link ${route === "/companies" ? "active" : ""}`}
              onClick={() => navigate("/companies")}
            >
              Companies
            </button>
            <button
              className={`nav-link ${route === "/about" ? "active" : ""}`}
              onClick={() => navigate("/about")}
            >
              About
            </button>
          </nav>

          <div className="header-right">
            <button
              className="search-icon-btn"
              title="Search opportunities"
              onClick={() => navigate("/jobs")}
            >
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
            </button>

            <span className={`status-badge ${wsStatus === "Live" ? "live" : "offline"}`}>
              <span className="live-dot" style={{ backgroundColor: wsStatus === "Live" ? "#22C55E" : "#EF4444" }} />
              {wsStatus}
            </span>

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
          </div>
        </header>
      </div>

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

      {/* Video Modal */}
      {showVideoModal && (
        <div className="modal-overlay" onClick={() => setShowVideoModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 700 }}>
            <div className="modal-header">
              <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>PlacementHub Platform Tour</h3>
              <button className="modal-close" onClick={() => setShowVideoModal(false)}>&times;</button>
            </div>
            <div style={{ position: "relative", paddingBottom: "56.25%", height: 0, overflow: "hidden", borderRadius: 12, background: "#111111", margin: "16px 0" }}>
              <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "#FFFFFF", padding: 24, textAlign: "center" }}>
                <div style={{ width: 64, height: 64, borderRadius: "50%", background: "rgba(255,255,255,0.2)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 16 }}>
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3" />
                  </svg>
                </div>
                <h4 style={{ fontSize: 18, fontWeight: 700, margin: "0 0 6px" }}>Experience Real-Time Campus Placement</h4>
                <p style={{ fontSize: 13.5, color: "#9CA3AF", maxWidth: 440, margin: 0 }}>
                  Automated resume skill extraction, intelligent job matching score, instant recruiter interviews, and seamless real-time notifications.
                </p>
              </div>
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <button className="btn primary sm" onClick={() => setShowVideoModal(false)}>Close Video</button>
            </div>
          </div>
        </div>
      )}

      {/* Detailed Job Modal */}
      {selectedJobForModal && (
        <JobDetailsModal
          job={selectedJobForModal}
          onClose={() => setSelectedJobForModal(null)}
          user={user}
          applications={applications}
          loadApplications={loadApplications}
          navigate={navigate}
        />
      )}

      {/* ROUTES */}
      {route === "/" && (
        <PublicHomeView
          jobs={jobs}
          events={events}
          user={user}
          applications={applications}
          loadApplications={loadApplications}
          navigate={navigate}
          onOpenVideo={() => setShowVideoModal(true)}
          onViewJob={(j) => setSelectedJobForModal(j)}
          onTriggerNotify={triggerNotificationOptIn}
        />
      )}

      {route === "/jobs" && (
        <JobListingPage
          jobs={jobs}
          user={user}
          applications={applications}
          loadApplications={loadApplications}
          navigate={navigate}
          onViewJob={(j) => setSelectedJobForModal(j)}
        />
      )}

      {route === "/companies" && (
        <CompaniesPage
          jobs={jobs}
          navigate={navigate}
        />
      )}

      {route === "/about" && (
        <AboutPage navigate={navigate} />
      )}

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
          onViewJob={(j) => setSelectedJobForModal(j)}
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
    </div>
  );
}

// ==========================================
// 1. PUBLIC HOME VIEW
// ==========================================
function PublicHomeView({ jobs, events, user, applications, loadApplications, navigate, onOpenVideo, onViewJob, onTriggerNotify }) {
  const [applyingJobId, setApplyingJobId] = useState(null);
  const appliedJobIds = useMemo(() => new Set(applications.map((a) => a.job_id)), [applications]);

  // Statistics counters
  const activeCount = useCounter(jobs.length || 4);
  const studentsCount = useCounter(1248);
  const companiesCount = useCounter(86);
  const placedCount = useCounter(87);

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

  // Sample stream events if none arrived via websocket
  const displayEvents = events.length > 0 ? events : [
    { type: "NEW_JOB", title: "New job posted by TechNova", desc: "Software Developer", time: "2m ago", iconClass: "icon-pink" },
    { type: "NEW_APPLICATION", title: "A student applied for DevOps Engineer", desc: "Amazon", time: "5m ago", iconClass: "icon-green" },
    { type: "COMPANY_REGISTERED", title: "New company registered", desc: "Infosys", time: "12m ago", iconClass: "icon-purple" },
    { type: "INTERVIEW_SCHEDULED", title: "Interview scheduled", desc: "Backend Developer - Microsoft", time: "18m ago", iconClass: "icon-orange" },
    { type: "NEW_PLACEMENT", title: "New placement this week", desc: "Frontend Developer - Zoho", time: "25m ago", iconClass: "icon-blue" }
  ];

  return (
    <>
      {/* HERO SECTION */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-heading">
            Your<br />
            Career<br />
            <span className="hero-highlight">Starts Here.</span>
          </h1>
          <p className="hero-subtitle">
            Connect with top companies, explore opportunities, and build your future.
          </p>

          <div className="hero-actions">
            <button className="btn-hero-primary" onClick={() => navigate("/jobs")}>
              Explore Jobs &rarr;
            </button>
            <button className="btn-hero-secondary" onClick={onOpenVideo}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <polygon points="10 8 16 12 10 16 10 8" fill="currentColor" />
              </svg>
              Watch Video
            </button>
          </div>
        </div>

        <div className="hero-visual">
          <div className="hero-blobs">
            <div className="blob-1" />
            <div className="blob-2" />
            <div className="blob-3" />
          </div>
          <div className="hero-img-wrap">
            <img
              src="/student_hero.png"
              alt="Student preparing for career placement"
              className="hero-student-img"
              onError={(e) => {
                // Graceful fallback if image is loading
                e.target.style.display = "none";
              }}
            />
          </div>
        </div>
      </section>

      {/* 4 STATISTIC CARDS */}
      <section className="stats">
        <div className="stat-card card-peach">
          <div className="stat-icon-box">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
            </svg>
          </div>
          <div className="stat-details">
            <b>{activeCount}</b>
            <span>Active Openings</span>
          </div>
        </div>

        <div className="stat-card card-blue">
          <div className="stat-icon-box">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>
          <div className="stat-details">
            <b>{studentsCount.toLocaleString()}</b>
            <span>Registered Students</span>
          </div>
        </div>

        <div className="stat-card card-green">
          <div className="stat-icon-box">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="4" y="2" width="16" height="20" rx="2" ry="2" />
              <path d="M9 22v-4h6v4" />
              <path d="M8 6h.01M16 6h.01M8 10h.01M16 10h.01M8 14h.01M16 14h.01" />
            </svg>
          </div>
          <div className="stat-details">
            <b>{companiesCount}</b>
            <span>Partner Companies</span>
          </div>
        </div>

        <div className="stat-card card-sand">
          <div className="stat-icon-box">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="20" x2="18" y2="10" />
              <line x1="12" y1="20" x2="12" y2="4" />
              <line x1="6" y1="20" x2="6" y2="14" />
            </svg>
          </div>
          <div className="stat-details">
            <b>{placedCount}</b>
            <span>Placed Candidates</span>
          </div>
        </div>
      </section>

      {/* TWO-COLUMN JOB SECTION */}
      <main>
        {/* Left Column: Available Jobs */}
        <section>
          <div className="section-header">
            <h2 className="section-title">Available Jobs &amp; Opportunities</h2>
            <span className="view-all-link" onClick={() => navigate("/jobs")}>
              View All &rarr;
            </span>
          </div>

          <div className="job-list">
            {jobs.length === 0 ? (
              <div style={{ background: "#FFFFFF", padding: 32, borderRadius: 16, border: "1px solid #EBE7DF", textAlign: "center" }}>
                <p style={{ color: "#667085", margin: 0 }}>No active job listings found right now.</p>
              </div>
            ) : (
              jobs.slice(0, 6).map((j, index) => {
                const isApplied = appliedJobIds.has(j.id);
                // Realistic mock relative post time
                const postTimes = ["2 days ago", "3 days ago", "5 days ago", "1 week ago", "Just now"];
                const postTime = postTimes[index % postTimes.length];
                const workType = index % 3 === 0 ? "Hybrid" : index % 3 === 1 ? "On-site" : "Remote";

                return (
                  <article className="job" key={j.id}>
                    <div className="job-main">
                      <CompanyLogo name={j.company} />
                      <div className="job-info">
                        <h3>{j.title || j.role}</h3>
                        <div className="job-meta">
                          <b>{j.company}</b>
                          <span className="meta-dot">·</span>
                          <span>{j.salary || j.package || "Competitive"}</span>
                          <span className="meta-dot">·</span>
                          <span>📍 {j.location || "Bangalore"}</span>
                          <span className="meta-dot">·</span>
                          <span className="work-type-pill">{workType}</span>
                        </div>
                        {j.description && <p className="job-desc">{j.description}</p>}
                        <div className="tags">
                          {(j.skills || ["Python", "FastAPI", "React", "Docker"]).map((s) => (
                            <span className="tag" key={s}>
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="job-action-wrap">
                      {isApplied ? (
                        <button className="btn secondary sm" disabled>
                          Applied ✓
                        </button>
                      ) : (
                        <button
                          className="btn-apply-blue"
                          onClick={() => handleApply(j.id)}
                          disabled={applyingJobId === j.id}
                        >
                          {applyingJobId === j.id ? "Applying..." : "Apply Now \u2192"}
                        </button>
                      )}
                      <button
                        className="btn-view-details"
                        onClick={() => onViewJob(j)}
                      >
                        View Details
                      </button>
                      <span className="job-posted-time">{postTime}</span>
                    </div>
                  </article>
                );
              })
            )}
          </div>
        </section>

        {/* Right Column: Live Stream Activity & Notification Box */}
        <aside>
          {/* Live Stream Card */}
          <div className="aside-card">
            <div className="aside-header">
              <span className="live-dot" />
              <span>Live Stream Activity</span>
            </div>

            <div className="timeline-list">
              {displayEvents.map((e, i) => {
                const iconColor =
                  e.iconClass ||
                  (e.type?.includes("JOB")
                    ? "icon-pink"
                    : e.type?.includes("APPLICATION")
                    ? "icon-green"
                    : e.type?.includes("INTERVIEW")
                    ? "icon-orange"
                    : "icon-purple");

                const title =
                  e.title ||
                  (e.type === "INTERVIEW_SCHEDULED"
                    ? `Interview scheduled`
                    : e.data?.status
                    ? `Application #${e.data.id} is now ${e.data.status}`
                    : e.data?.title
                    ? `New job: ${e.data.title}`
                    : "Live update");

                const desc =
                  e.desc ||
                  (e.data?.job_title ? `${e.data.job_title} at ${e.data.company}` : e.data?.company || "System Update");

                const time = e.time || "Just now";

                return (
                  <div className="timeline-item" key={i}>
                    <div className={`timeline-icon ${iconColor}`}>
                      {iconColor.includes("pink") ? "💼" : iconColor.includes("green") ? "👤" : iconColor.includes("purple") ? "🏢" : iconColor.includes("orange") ? "📅" : "🏆"}
                    </div>
                    <div className="timeline-content">
                      <div className="timeline-content-top">
                        <span className="timeline-title">{title}</span>
                        <span className="timeline-time">{time}</span>
                      </div>
                      <div className="timeline-desc">{desc}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Get Notified Card */}
          <div className="notification-card">
            <div className="notification-card-inner">
              <div className="notification-content">
                <h3>Get Notified About New Opportunities</h3>
                <p>Be the first to know about new jobs from top companies.</p>
                <button className="btn-notification" onClick={onTriggerNotify}>
                  Enable Notifications &rarr;
                </button>
              </div>

              <div className="notification-bell-wrap">
                <img
                  src="/bell.png"
                  alt="Notifications"
                  className="notification-bell-img"
                  onError={(e) => {
                    e.target.style.display = "none";
                  }}
                />
                <span className="bell-badge-count">1</span>
              </div>
            </div>
          </div>
        </aside>
      </main>
    </>
  );
}

// ==========================================
// 2. JOB LISTING PAGE
// ==========================================
function JobListingPage({ jobs, user, applications, loadApplications, navigate, onViewJob }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedType, setSelectedType] = useState("ALL");
  const [selectedLocation, setSelectedLocation] = useState("ALL");
  const [sortBy, setSortBy] = useState("LATEST");
  const [applyingJobId, setApplyingJobId] = useState(null);

  const appliedJobIds = useMemo(() => new Set(applications.map((a) => a.job_id)), [applications]);

  const filteredJobs = useMemo(() => {
    return jobs.filter((j) => {
      const matchSearch =
        (j.title || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
        (j.company || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
        (j.skills || []).some((s) => s.toLowerCase().includes(searchTerm.toLowerCase()));

      const matchLocation =
        selectedLocation === "ALL" || (j.location || "").toLowerCase().includes(selectedLocation.toLowerCase());

      return matchSearch && matchLocation;
    });
  }, [jobs, searchTerm, selectedLocation]);

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
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-0.8px", margin: "0 0 6px" }}>
          Explore Opportunities
        </h1>
        <p style={{ color: "#667085", fontSize: 15, margin: 0 }}>
          Find high-growth engineering, DevOps, product, and data opportunities from top verified companies.
        </p>
      </div>

      {/* Search & Filter Component */}
      <div className="search-filter-card">
        <div className="search-input-wrap">
          <svg className="search-input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="text"
            className="search-input-main"
            placeholder="Search by job title, company name, or technology skills (e.g. Python, Docker, React)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-row">
          <div style={{ display: "flex", gap: 6 }}>
            {["ALL", "HYBRID", "REMOTE", "ON-SITE"].map((type) => (
              <button
                key={type}
                className={`filter-pill ${selectedType === type ? "active" : ""}`}
                onClick={() => setSelectedType(type)}
              >
                {type}
              </button>
            ))}
          </div>

          <div style={{ marginLeft: "auto", display: "flex", gap: 10 }}>
            <select
              className="filter-select"
              value={selectedLocation}
              onChange={(e) => setSelectedLocation(e.target.value)}
            >
              <option value="ALL">All Locations</option>
              <option value="Bangalore">Bangalore</option>
              <option value="Hyderabad">Hyderabad</option>
              <option value="Pune">Pune</option>
              <option value="Remote">Remote</option>
            </select>

            <select
              className="filter-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="LATEST">Sort: Latest</option>
              <option value="SALARY">Highest Package</option>
            </select>
          </div>
        </div>
      </div>

      {/* Job Cards List */}
      <div className="job-list">
        {filteredJobs.length === 0 ? (
          <div style={{ background: "#FFFFFF", padding: 40, borderRadius: 16, border: "1px solid #EBE7DF", textAlign: "center" }}>
            <h3 style={{ fontSize: 18, fontWeight: 700, margin: "0 0 6px" }}>No matching jobs found</h3>
            <p style={{ color: "#667085", fontSize: 14 }}>Try adjusting your search keywords or clearing filters.</p>
            <button className="btn secondary sm" style={{ marginTop: 10 }} onClick={() => { setSearchTerm(""); setSelectedLocation("ALL"); setSelectedType("ALL"); }}>
              Reset Filters
            </button>
          </div>
        ) : (
          filteredJobs.map((j, index) => {
            const isApplied = appliedJobIds.has(j.id);
            const workType = index % 3 === 0 ? "Hybrid" : index % 3 === 1 ? "On-site" : "Remote";
            const matchScore = (j.match_percentage !== undefined && j.match_percentage !== null)
              ? j.match_percentage
              : Math.min(95, 65 + (index * 7) % 35);

            return (
              <article className="job" key={j.id}>
                <div className="job-main">
                  <CompanyLogo name={j.company} />
                  <div className="job-info">
                    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
                      <h3 style={{ margin: 0 }}>{j.title || j.role}</h3>
                      <span className={`match-score-badge ${matchScore >= 75 ? "match-high" : matchScore >= 50 ? "match-mid" : "match-low"}`}>
                        {matchScore}% Match
                      </span>
                    </div>

                    <div className="job-meta">
                      <b>{j.company}</b>
                      <span className="meta-dot">·</span>
                      <span>{j.salary || j.package || "Competitive"}</span>
                      <span className="meta-dot">·</span>
                      <span>📍 {j.location || "Bangalore"}</span>
                      <span className="meta-dot">·</span>
                      <span className="work-type-pill">{workType}</span>
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
                </div>

                <div className="job-action-wrap">
                  {isApplied ? (
                    <button className="btn secondary sm" disabled>
                      Applied ✓
                    </button>
                  ) : (
                    <button
                      className="btn-apply-blue"
                      onClick={() => handleApply(j.id)}
                      disabled={applyingJobId === j.id}
                    >
                      {applyingJobId === j.id ? "Applying..." : "Apply Now \u2192"}
                    </button>
                  )}
                  <button className="btn-view-details" onClick={() => onViewJob(j)}>
                    View Details
                  </button>
                  <span className="job-posted-time">Active Opening</span>
                </div>
              </article>
            );
          })
        )}
      </div>
    </div>
  );
}

// ==========================================
// 3. JOB DETAILS MODAL
// ==========================================
function JobDetailsModal({ job, onClose, user, applications, loadApplications, navigate }) {
  const [applying, setApplying] = useState(false);
  const [saved, setSaved] = useState(false);
  const isApplied = applications.some((a) => a.job_id === job.id);

  const handleApply = async () => {
    if (!user) {
      onClose();
      navigate("/login");
      return;
    }
    if (user.role !== "STUDENT") {
      alert("Only students can apply for jobs.");
      return;
    }
    setApplying(true);
    try {
      const res = await authFetch("/api/applications", {
        method: "POST",
        body: JSON.stringify({ job_id: job.id })
      });
      if (res.ok) {
        loadApplications();
        onClose();
      } else {
        const err = await res.json();
        alert(err.detail || "Application failed");
      }
    } catch {
      alert("Network error");
    } finally {
      setApplying(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 760 }}>
        <div className="modal-header">
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <CompanyLogo name={job.company} size={54} />
            <div>
              <h2 style={{ fontSize: 20, fontWeight: 700, margin: "0 0 2px" }}>{job.title || job.role}</h2>
              <div style={{ fontSize: 13.5, color: "#667085" }}>
                <b>{job.company}</b> · {job.salary || "Competitive"} · 📍 {job.location || "Remote"}
              </div>
            </div>
          </div>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1.4fr 0.9fr", gap: 24, margin: "20px 0" }}>
          {/* Main Description Column */}
          <div>
            <div style={{ marginBottom: 20 }}>
              <h4 style={{ fontSize: 14, fontWeight: 700, color: "#111111", marginBottom: 8 }}>About the Role</h4>
              <p style={{ fontSize: 13.5, color: "#475569", lineHeight: 1.6, margin: 0 }}>
                {job.description || "Join our fast-growing engineering team to design, build, and deploy reliable modern software applications."}
              </p>
            </div>

            <div style={{ marginBottom: 20 }}>
              <h4 style={{ fontSize: 14, fontWeight: 700, color: "#111111", marginBottom: 8 }}>Core Responsibilities</h4>
              <ul style={{ margin: 0, paddingLeft: 20, fontSize: 13.5, color: "#475569", lineHeight: 1.6 }}>
                <li>Collaborate with cross-functional product and infrastructure teams.</li>
                <li>Design, develop, and maintain clean and scalable software services.</li>
                <li>Participate in code reviews, CI/CD pipeline automation, and automated testing.</li>
                <li>Diagnose, debug, and resolve performance bottlenecks across production environments.</li>
              </ul>
            </div>

            <div style={{ marginBottom: 20 }}>
              <h4 style={{ fontSize: 14, fontWeight: 700, color: "#111111", marginBottom: 8 }}>Required Technologies &amp; Skills</h4>
              <div className="tags">
                {(job.skills || ["Python", "FastAPI", "React", "Docker"]).map((s) => (
                  <span className="tag" key={s}>
                    {s}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h4 style={{ fontSize: 14, fontWeight: 700, color: "#111111", marginBottom: 8 }}>Perks &amp; Benefits</h4>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, fontSize: 12.5, color: "#475569" }}>
                <div>✨ Comprehensive Health Coverage</div>
                <div>💻 Modern Mac/Linux Workstation</div>
                <div>📚 Learning &amp; Upskilling Stipend</div>
                <div>🏖️ Flexible Time Off &amp; Hybrid Culture</div>
              </div>
            </div>
          </div>

          {/* Right Sidebar Summary */}
          <div style={{ background: "#F6F4EE", padding: 20, borderRadius: 14, border: "1px solid #EBE7DF", display: "flex", flexDirection: "column", gap: 14 }}>
            <h4 style={{ fontSize: 14, fontWeight: 700, margin: 0 }}>Job Summary</h4>

            <div style={{ fontSize: 13, display: "flex", flexDirection: "column", gap: 10 }}>
              <div>
                <span style={{ color: "#667085", display: "block", fontSize: 11.5 }}>COMPENSATION</span>
                <b>{job.salary || "Competitive LPA"}</b>
              </div>
              <div>
                <span style={{ color: "#667085", display: "block", fontSize: 11.5 }}>WORK LOCATION</span>
                <b>{job.location || "Bangalore, India"}</b>
              </div>
              <div>
                <span style={{ color: "#667085", display: "block", fontSize: 11.5 }}>EXPERIENCE LEVEL</span>
                <b>Entry / Graduate Level (2025–2026 Batch)</b>
              </div>
              <div>
                <span style={{ color: "#667085", display: "block", fontSize: 11.5 }}>POSTED DATE</span>
                <b>Active Campus Drive</b>
              </div>
            </div>

            <div style={{ marginTop: "auto", display: "flex", flexDirection: "column", gap: 8 }}>
              {isApplied ? (
                <button className="btn secondary" disabled style={{ width: "100%" }}>
                  Applied ✓
                </button>
              ) : (
                <button
                  className="btn primary"
                  style={{ width: "100%" }}
                  onClick={handleApply}
                  disabled={applying}
                >
                  {applying ? "Submitting..." : "Apply For Position \u2192"}
                </button>
              )}

              <button
                className="btn secondary sm"
                style={{ width: "100%" }}
                onClick={() => setSaved(!saved)}
              >
                {saved ? "★ Saved in Profile" : "☆ Save Job"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ==========================================
// 4. COMPANIES PAGE
// ==========================================
function CompaniesPage({ jobs, navigate }) {
  const companies = [
    {
      name: "TechNova",
      location: "Bangalore · Hybrid",
      industry: "Enterprise Cloud & AI Solutions",
      desc: "TechNova develops next-generation enterprise orchestration and machine learning productivity software.",
      website: "https://technova.example.com"
    },
    {
      name: "Amazon",
      location: "Hyderabad · On-site",
      industry: "Cloud Infrastructure & E-Commerce",
      desc: "Amazon Web Services and retail technology infrastructure serving billions of requests worldwide.",
      website: "https://amazon.jobs"
    },
    {
      name: "Microsoft",
      location: "Bangalore · Hybrid",
      industry: "Operating Systems, Cloud & Productivity",
      desc: "Empowering every person and every organization on the planet to achieve more through Azure and Microsoft 365.",
      website: "https://careers.microsoft.com"
    },
    {
      name: "Google",
      location: "Bangalore · Hybrid",
      industry: "Search, Cloud & AI Research",
      desc: "Organizing the world's information and making it universally accessible and useful for everyone.",
      website: "https://careers.google.com"
    },
    {
      name: "Infosys",
      location: "Pune · On-site",
      industry: "Global IT Services & Consulting",
      desc: "A global leader in next-generation digital services and enterprise digital transformation consulting.",
      website: "https://infosys.com/careers"
    },
    {
      name: "Zoho",
      location: "Chennai · On-site",
      industry: "Business SaaS & Office Suite",
      desc: "Unique and powerful suite of software to run entire businesses, built by a product engineering company.",
      website: "https://zoho.com/careers"
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-0.8px", margin: "0 0 6px" }}>
          Top Partner Companies
        </h1>
        <p style={{ color: "#667085", fontSize: 15, margin: 0 }}>
          PlacementHub collaborates directly with top technology employers who hire directly from verified student cohorts.
        </p>
      </div>

      <div className="company-grid">
        {companies.map((c) => {
          const matchingJobsCount = jobs.filter((j) =>
            (j.company || "").toLowerCase().includes(c.name.toLowerCase())
          ).length;

          return (
            <div className="company-card" key={c.name}>
              <div>
                <div className="company-card-top">
                  <CompanyLogo name={c.name} size={48} />
                  <div>
                    <h4>{c.name}</h4>
                    <span className="company-card-loc">{c.location}</span>
                  </div>
                </div>

                <div style={{ fontSize: 12, fontWeight: 600, color: "#2563EB", marginBottom: 6 }}>
                  {c.industry}
                </div>
                <p style={{ fontSize: 13, color: "#667085", lineHeight: 1.5, margin: 0 }}>
                  {c.desc}
                </p>
              </div>

              <div className="company-card-jobs">
                <span style={{ fontSize: 13, fontWeight: 600, color: "#111111" }}>
                  {matchingJobsCount > 0 ? `${matchingJobsCount} open roles` : "Actively Hiring"}
                </span>
                <button
                  className="btn secondary sm"
                  onClick={() => navigate("/jobs")}
                >
                  View Jobs &rarr;
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ==========================================
// 5. ABOUT PAGE
// ==========================================
function AboutPage({ navigate }) {
  return (
    <div style={{ maxWidth: 900, margin: "0 auto" }}>
      <div style={{ textAlign: "center", marginBottom: 40 }}>
        <span className="hero-highlight" style={{ fontSize: 13, fontWeight: 700, marginBottom: 12 }}>
          OUR MISSION
        </span>
        <h1 style={{ fontSize: 40, fontWeight: 800, letterSpacing: "-1px", margin: "12px 0" }}>
          Bridging Campus Talent with Modern Tech Careers
        </h1>
        <p style={{ fontSize: 17, color: "#667085", maxWidth: 640, margin: "0 auto", lineHeight: 1.6 }}>
          PlacementHub eliminates recruitment friction for students, colleges, and enterprise hiring teams through real-time automation.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20, marginBottom: 40 }}>
        <div style={{ background: "#FFFFFF", padding: 24, borderRadius: 16, border: "1px solid #EBE7DF" }}>
          <div style={{ fontSize: 24, marginBottom: 10 }}>🎯</div>
          <h3 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 6px" }}>Automated Matching</h3>
          <p style={{ fontSize: 13.5, color: "#667085", margin: 0, lineHeight: 1.5 }}>
            Proprietary skill vector parsing calculates exact curriculum and technical skill compatibility in seconds.
          </p>
        </div>

        <div style={{ background: "#FFFFFF", padding: 24, borderRadius: 16, border: "1px solid #EBE7DF" }}>
          <div style={{ fontSize: 24, marginBottom: 10 }}>⚡</div>
          <h3 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 6px" }}>Real-Time Live Updates</h3>
          <p style={{ fontSize: 13.5, color: "#667085", margin: 0, lineHeight: 1.5 }}>
            WebSocket notification stream pushes application status shifts, interview schedules, and new vacancies instantly.
          </p>
        </div>

        <div style={{ background: "#FFFFFF", padding: 24, borderRadius: 16, border: "1px solid #EBE7DF" }}>
          <div style={{ fontSize: 24, marginBottom: 10 }}>🤝</div>
          <h3 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 6px" }}>Direct Enterprise Drives</h3>
          <p style={{ fontSize: 13.5, color: "#667085", margin: 0, lineHeight: 1.5 }}>
            Verified recruiters evaluate, shortlist, and schedule Google Meet interviews directly within one unified console.
          </p>
        </div>
      </div>

      <div style={{ background: "#FAF3E8", padding: 36, borderRadius: 20, border: "1px solid #F3E4CD", textAlign: "center" }}>
        <h2 style={{ fontSize: 24, fontWeight: 800, margin: "0 0 8px" }}>Ready to Launch Your Career?</h2>
        <p style={{ color: "#78350F", fontSize: 14.5, margin: "0 0 20px" }}>
          Join thousands of university graduates securing roles at high-growth tech companies.
        </p>
        <button className="btn primary" onClick={() => navigate("/register")}>
          Get Started Today &rarr;
        </button>
      </div>
    </div>
  );
}

// ==========================================
// 6. RESUME BUILDER COMPONENT
// ==========================================
function ResumeBuilder({ user, onSaveProfile }) {
  const [step, setStep] = useState(1);
  const [personal, setPersonal] = useState({
    name: user?.name || "Dhanush Kumar",
    email: user?.email || "dhanush@college.edu",
    phone: "+91 98765 43210",
    location: "Bangalore, India",
    bio: "Passionate software engineer with hands-on experience in backend microservices, DevOps pipelines, and cloud native applications."
  });

  const [education, setEducation] = useState({
    college: user?.student_profile?.college || "National Institute of Technology",
    degree: user?.student_profile?.degree || "B.Tech in Computer Science",
    year: "2022 - 2026",
    cgpa: user?.student_profile?.cgpa || "8.75"
  });

  const [skillsList, setSkillsList] = useState(
    user?.student_profile?.skills || ["Python", "FastAPI", "Docker", "React", "PostgreSQL", "CI/CD", "Kubernetes"]
  );
  const [skillInput, setSkillInput] = useState("");

  const [projects, setProjects] = useState([
    {
      title: "Real-Time Campus Placement Hub",
      tech: "React, FastAPI, Docker, WebSocket",
      desc: "Engineered scalable placement management ecosystem with resume parsing and automated skill match percentage calculation."
    },
    {
      title: "Automated Cloud CI/CD Pipeline",
      tech: "Jenkins, Docker, Nginx, Pytest",
      desc: "Designed end-to-end automated deployment workflow with automated testing, security scanning, and containerization."
    }
  ]);

  const addSkill = (e) => {
    e.preventDefault();
    if (!skillInput.trim()) return;
    if (!skillsList.includes(skillInput.trim())) {
      setSkillsList([...skillsList, skillInput.trim()]);
    }
    setSkillInput("");
  };

  const removeSkill = (s) => {
    setSkillsList(skillsList.filter((item) => item !== s));
  };

  return (
    <div>
      <div className="wizard-steps">
        {[
          { num: 1, title: "Personal" },
          { num: 2, title: "Education" },
          { num: 3, title: "Skills" },
          { num: 4, title: "Projects" },
          { num: 5, title: "Live Preview" }
        ].map((s) => (
          <div
            key={s.num}
            className={`wizard-step-item ${step === s.num ? "active" : ""} ${step > s.num ? "completed" : ""}`}
            onClick={() => setStep(s.num)}
          >
            <div className="wizard-num">{step > s.num ? "✓" : s.num}</div>
            <span>{s.title}</span>
          </div>
        ))}
      </div>

      <div className="resume-builder-wrap">
        {/* Form Controls */}
        <div style={{ background: "#FFFFFF", padding: 24, borderRadius: 16, border: "1px solid #EBE7DF" }}>
          {step === 1 && (
            <div>
              <h3 style={{ fontSize: 18, fontWeight: 700, margin: "0 0 16px" }}>1. Personal Information</h3>
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  value={personal.name}
                  onChange={(e) => setPersonal({ ...personal, name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Email Address</label>
                <input
                  type="email"
                  value={personal.email}
                  onChange={(e) => setPersonal({ ...personal, email: e.target.value })}
                />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div className="form-group">
                  <label>Phone Number</label>
                  <input
                    type="text"
                    value={personal.phone}
                    onChange={(e) => setPersonal({ ...personal, phone: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Location</label>
                  <input
                    type="text"
                    value={personal.location}
                    onChange={(e) => setPersonal({ ...personal, location: e.target.value })}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Professional Bio</label>
                <textarea
                  rows="3"
                  value={personal.bio}
                  onChange={(e) => setPersonal({ ...personal, bio: e.target.value })}
                />
              </div>
            </div>
          )}

          {step === 2 && (
            <div>
              <h3 style={{ fontSize: 18, fontWeight: 700, margin: "0 0 16px" }}>2. Education Details</h3>
              <div className="form-group">
                <label>Institution / University</label>
                <input
                  type="text"
                  value={education.college}
                  onChange={(e) => setEducation({ ...education, college: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Degree &amp; Major</label>
                <input
                  type="text"
                  value={education.degree}
                  onChange={(e) => setEducation({ ...education, degree: e.target.value })}
                />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div className="form-group">
                  <label>Duration / Batch</label>
                  <input
                    type="text"
                    value={education.year}
                    onChange={(e) => setEducation({ ...education, year: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Cumulative CGPA</label>
                  <input
                    type="text"
                    value={education.cgpa}
                    onChange={(e) => setEducation({ ...education, cgpa: e.target.value })}
                  />
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div>
              <h3 style={{ fontSize: 18, fontWeight: 700, margin: "0 0 16px" }}>3. Technical Skills</h3>
              <form onSubmit={addSkill} style={{ display: "flex", gap: 8, marginBottom: 16 }}>
                <input
                  type="text"
                  placeholder="e.g. AWS, GraphQL, TypeScript"
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                />
                <button type="submit" className="btn primary sm">+ Add</button>
              </form>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {skillsList.map((skill) => (
                  <span key={skill} className="skill-pill-editable">
                    {skill}
                    <button type="button" className="skill-pill-remove" onClick={() => removeSkill(skill)}>
                      &times;
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}

          {step === 4 && (
            <div>
              <h3 style={{ fontSize: 18, fontWeight: 700, margin: "0 0 16px" }}>4. Featured Projects</h3>
              {projects.map((proj, idx) => (
                <div key={idx} style={{ background: "#F6F4EE", padding: 14, borderRadius: 10, marginBottom: 12 }}>
                  <div className="form-group" style={{ marginBottom: 8 }}>
                    <label>Project Title</label>
                    <input
                      type="text"
                      value={proj.title}
                      onChange={(e) => {
                        const updated = [...projects];
                        updated[idx].title = e.target.value;
                        setProjects(updated);
                      }}
                    />
                  </div>
                  <div className="form-group" style={{ marginBottom: 8 }}>
                    <label>Technologies</label>
                    <input
                      type="text"
                      value={proj.tech}
                      onChange={(e) => {
                        const updated = [...projects];
                        updated[idx].tech = e.target.value;
                        setProjects(updated);
                      }}
                    />
                  </div>
                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label>Summary</label>
                    <textarea
                      rows="2"
                      value={proj.desc}
                      onChange={(e) => {
                        const updated = [...projects];
                        updated[idx].desc = e.target.value;
                        setProjects(updated);
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          {step === 5 && (
            <div>
              <h3 style={{ fontSize: 18, fontWeight: 700, margin: "0 0 8px" }}>5. Ready to Export</h3>
              <p style={{ fontSize: 13.5, color: "#667085", marginBottom: 18 }}>
                Your resume is formatted and ready. You can print to PDF or sync your updated skills directly with your candidate profile.
              </p>
              <div style={{ display: "flex", gap: 10 }}>
                <button
                  className="btn primary sm"
                  onClick={() => window.print()}
                >
                  🖨️ Print / Save as PDF
                </button>
              </div>
            </div>
          )}

          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 24, paddingTop: 16, borderTop: "1px solid #EBE7DF" }}>
            <button
              className="btn secondary sm"
              disabled={step === 1}
              onClick={() => setStep(Math.max(1, step - 1))}
            >
              &larr; Back
            </button>
            <button
              className="btn primary sm"
              onClick={() => {
                if (step < 5) setStep(step + 1);
                else alert("Resume generated and saved to your profile!");
              }}
            >
              {step === 5 ? "Finish & Apply" : "Next Step \u2192"}
            </button>
          </div>
        </div>

        {/* Live Resume Sheet Preview */}
        <div className="resume-preview-sheet">
          <div style={{ borderBottom: "2px solid #111111", paddingBottom: 14, marginBottom: 16 }}>
            <h2 style={{ fontSize: 24, fontWeight: 800, margin: "0 0 4px", color: "#111111" }}>{personal.name}</h2>
            <div style={{ fontSize: 12.5, color: "#667085" }}>
              {personal.email} · {personal.phone} · {personal.location}
            </div>
          </div>

          <div style={{ marginBottom: 16 }}>
            <h4 style={{ fontSize: 12, fontWeight: 800, textTransform: "uppercase", letterSpacing: 0.8, color: "#111111", marginBottom: 4 }}>
              Summary
            </h4>
            <p style={{ fontSize: 12.5, color: "#475569", lineHeight: 1.5, margin: 0 }}>
              {personal.bio}
            </p>
          </div>

          <div style={{ marginBottom: 16 }}>
            <h4 style={{ fontSize: 12, fontWeight: 800, textTransform: "uppercase", letterSpacing: 0.8, color: "#111111", marginBottom: 6 }}>
              Education
            </h4>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, fontWeight: 700 }}>
              <span>{education.college}</span>
              <span style={{ color: "#667085", fontWeight: 500 }}>{education.year}</span>
            </div>
            <div style={{ fontSize: 12.5, color: "#475569" }}>
              {education.degree} · CGPA: <b>{education.cgpa} / 10.0</b>
            </div>
          </div>

          <div style={{ marginBottom: 16 }}>
            <h4 style={{ fontSize: 12, fontWeight: 800, textTransform: "uppercase", letterSpacing: 0.8, color: "#111111", marginBottom: 6 }}>
              Technical Expertise
            </h4>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
              {skillsList.map((s) => (
                <span key={s} style={{ background: "#EEF2F6", padding: "2px 8px", borderRadius: 4, fontSize: 11.5, fontWeight: 600 }}>
                  {s}
                </span>
              ))}
            </div>
          </div>

          <div>
            <h4 style={{ fontSize: 12, fontWeight: 800, textTransform: "uppercase", letterSpacing: 0.8, color: "#111111", marginBottom: 6 }}>
              Projects
            </h4>
            {projects.map((p, i) => (
              <div key={i} style={{ marginBottom: 10 }}>
                <div style={{ fontSize: 12.5, fontWeight: 700, color: "#111111" }}>{p.title}</div>
                <div style={{ fontSize: 11.5, color: "#2563EB", fontWeight: 600 }}>{p.tech}</div>
                <p style={{ fontSize: 12, color: "#64748b", margin: "2px 0 0", lineHeight: 1.45 }}>{p.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ==========================================
// 7. LOGIN PAGE
// ==========================================
function LoginPage({ onLogin, navigate }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
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

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16, fontSize: 13 }}>
          <label style={{ display: "flex", alignItems: "center", gap: 6, cursor: "pointer", color: "#667085" }}>
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
            />
            Remember me
          </label>
          <a
            href="#forgot"
            onClick={(e) => { e.preventDefault(); alert("Password reset link will be sent to your registered email address."); }}
            style={{ color: "#2563EB", textDecoration: "none", fontWeight: 500 }}
          >
            Forgot password?
          </a>
        </div>

        <button type="submit" style={{ width: "100%", marginTop: 4 }} disabled={loading}>
          {loading ? "Authenticating..." : "Sign In"}
        </button>
      </form>

      <div style={{ marginTop: 20, textAlign: "center", fontSize: 13.5, color: "#667085" }}>
        Don't have an account?{" "}
        <a
          href="/register"
          onClick={(e) => {
            e.preventDefault();
            navigate("/register");
          }}
          style={{ color: "#111111", fontWeight: 700, textDecoration: "none" }}
        >
          Create account &rarr;
        </a>
      </div>

      <div className="demo-logins">
        <p>⚡ Quick Demo Credentials</p>
        <div className="demo-buttons">
          <button
            type="button"
            className="demo-btn"
            onClick={() => fillDemo("dhanush@college.edu", "Student@123")}
          >
            <span>🎓</span> Demo Student (dhanush@college.edu)
          </button>
          <button
            type="button"
            className="demo-btn"
            onClick={() => fillDemo("recruiter@technova.com", "Recruiter@123")}
          >
            <span>🏢</span> Demo Recruiter (recruiter@technova.com)
          </button>
          <button
            type="button"
            className="demo-btn"
            onClick={() => fillDemo("admin@placement.edu", "Admin@123")}
          >
            <span>⚙️</span> Demo Admin (admin@placement.edu)
          </button>
        </div>
      </div>
    </div>
  );
}

// ==========================================
// 8. REGISTRATION PAGE
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

      <div style={{ marginTop: 20, textAlign: "center", fontSize: 13.5, color: "#667085" }}>
        Already have an account?{" "}
        <a
          href="/login"
          onClick={(e) => {
            e.preventDefault();
            navigate("/login");
          }}
          style={{ color: "#111111", fontWeight: 700, textDecoration: "none" }}
        >
          Sign In &rarr;
        </a>
      </div>
    </div>
  );
}

// ==========================================
// 9. STUDENT DASHBOARD
// ==========================================
function StudentDashboard({ user, jobs, applications, loadApplications, interviews, loadInterviews, events, onViewJob }) {
  const [activeTab, setActiveTab] = useState("recommended");
  const [applyingJobId, setApplyingJobId] = useState(null);
  const [studentProfile, setStudentProfile] = useState(user?.student_profile || {});
  const [recommendedJobs, setRecommendedJobs] = useState([]);
  const [loadingRecommended, setLoadingRecommended] = useState(false);

  // Resume upload state
  const [resumeFile, setResumeFile] = useState(null);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [resumeMsg, setResumeMsg] = useState("");
  const [newSkillsExtracted, setNewSkillsExtracted] = useState([]);
  const [resumeSuccess, setResumeSuccess] = useState(false);

  // Skills input state
  const [newSkillInput, setNewSkillInput] = useState("");
  const [isEditingSkills, setIsEditingSkills] = useState(false);

  // Edit Profile Modal
  const [showEditProfile, setShowEditProfile] = useState(false);
  const [editCollege, setEditCollege] = useState(studentProfile?.college || user?.student_profile?.college || "");
  const [editDegree, setEditDegree] = useState(studentProfile?.degree || user?.student_profile?.degree || "");
  const [editBranch, setEditBranch] = useState(studentProfile?.branch || user?.student_profile?.branch || "");
  const [editCgpa, setEditCgpa] = useState(studentProfile?.cgpa || user?.student_profile?.cgpa || "");

  const appliedJobIds = useMemo(() => new Set(applications.map((a) => a.job_id)), [applications]);

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

  const handleSaveProfileInfo = async (e) => {
    e.preventDefault();
    try {
      const res = await authFetch("/api/students/profile", {
        method: "PUT",
        body: JSON.stringify({
          college: editCollege,
          degree: editDegree,
          branch: editBranch,
          cgpa: parseFloat(editCgpa) || null
        })
      });
      if (res.ok) {
        const data = await res.json();
        setStudentProfile((prev) => ({ ...prev, ...data }));
        setShowEditProfile(false);
      }
    } catch (err) {
      console.error("Error updating profile:", err);
    }
  };

  return (
    <>
      {/* Profile Overview Card */}
      <div className="profile-card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div
              style={{
                width: 58,
                height: 58,
                borderRadius: "50%",
                background: "#E8F9E6",
                color: "#166534",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 800,
                fontSize: 22,
                border: "2px solid #D5F5CC"
              }}
            >
              {(user?.name || "S").charAt(0).toUpperCase()}
            </div>
            <div>
              <h3 style={{ fontSize: 20, fontWeight: 700, margin: "0 0 3px", color: "#111111" }}>
                Welcome back, {user?.name}!
              </h3>
              <p style={{ margin: 0, fontSize: 13.5, color: "#667085" }}>
                {studentProfile?.degree || user?.student_profile?.degree} in {studentProfile?.branch || user?.student_profile?.branch} · {studentProfile?.college || "Campus Placement"}
              </p>
            </div>
          </div>

          <div style={{ display: "flex", gap: 10 }}>
            <button className="btn secondary sm" onClick={() => setShowEditProfile(true)}>
              Edit Profile
            </button>
            {studentProfile?.resume_url ? (
              <a
                href={studentProfile.resume_url}
                target="_blank"
                rel="noreferrer"
                className="btn secondary sm"
              >
                📄 View Active Resume
              </a>
            ) : (
              <button
                className="btn sm"
                style={{ background: "#FEF3C7", color: "#B45309", border: "1px solid #FDE68A" }}
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
              {(studentProfile?.skills || []).slice(0, 5).map((s) => (
                <span
                  key={s}
                  style={{
                    background: "#EEF2F6",
                    color: "#334155",
                    padding: "2px 8px",
                    borderRadius: 12,
                    fontSize: 11,
                    fontWeight: 600
                  }}
                >
                  {s}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Edit Profile Modal */}
      {showEditProfile && (
        <div className="modal-overlay" onClick={() => setShowEditProfile(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 480 }}>
            <div className="modal-header">
              <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Edit Candidate Profile</h3>
              <button className="modal-close" onClick={() => setShowEditProfile(false)}>&times;</button>
            </div>
            <form onSubmit={handleSaveProfileInfo}>
              <div className="form-group">
                <label>College / University</label>
                <input
                  type="text"
                  value={editCollege}
                  onChange={(e) => setEditCollege(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Degree</label>
                <input
                  type="text"
                  value={editDegree}
                  onChange={(e) => setEditDegree(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Branch / Major</label>
                <input
                  type="text"
                  value={editBranch}
                  onChange={(e) => setEditBranch(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>CGPA</label>
                <input
                  type="number"
                  step="0.01"
                  value={editCgpa}
                  onChange={(e) => setEditCgpa(e.target.value)}
                />
              </div>
              <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 20 }}>
                <button type="button" className="btn secondary sm" onClick={() => setShowEditProfile(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn primary sm">
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="dash-tabs">
        <div
          className={`dash-tab ${activeTab === "recommended" ? "active" : ""}`}
          onClick={() => setActiveTab("recommended")}
        >
          🎯 Recommended ({recommendedJobs.length})
        </div>
        <div
          className={`dash-tab ${activeTab === "resume" ? "active" : ""}`}
          onClick={() => setActiveTab("resume")}
        >
          📄 Resume &amp; Skills
        </div>
        <div
          className={`dash-tab ${activeTab === "builder" ? "active" : ""}`}
          onClick={() => setActiveTab("builder")}
        >
          🛠️ Resume Builder
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
                  <h2 style={{ fontSize: 18, fontWeight: 700, margin: "0 0 4px" }}>Recommended For You</h2>
                  <p style={{ margin: 0, fontSize: 13, color: "#667085" }}>
                    Automated match engine calculated from your verified skills and resume profile.
                  </p>
                </div>
                <button className="btn secondary sm" onClick={loadRecommendedJobs} disabled={loadingRecommended}>
                  {loadingRecommended ? "Analyzing..." : "↻ Refresh Matches"}
                </button>
              </div>

              {recommendedJobs.length === 0 ? (
                <div style={{ padding: 32, textAlign: "center", background: "#FFFFFF", borderRadius: 16, border: "1px solid #EBE7DF" }}>
                  <p style={{ color: "#667085", margin: "0 0 14px", fontSize: 14 }}>
                    No job recommendations yet. Upload your resume or add verified skills to unlock automated matching.
                  </p>
                  <button className="btn primary sm" onClick={() => setActiveTab("resume")}>
                    Upload Resume Now
                  </button>
                </div>
              ) : (
                <div className="job-list">
                  {recommendedJobs.map((j) => {
                    const isApplied = appliedJobIds.has(j.id);
                    const pct = j.match_percentage ?? 0;
                    const matchClass = pct >= 70 ? "match-high" : pct >= 40 ? "match-mid" : "match-low";

                    return (
                      <article className="job" key={j.id}>
                        <div className="job-main">
                          <CompanyLogo name={j.company} />
                          <div className="job-info">
                            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                              <h3 style={{ margin: 0 }}>{j.title || j.role}</h3>
                              <span className={`match-score-badge ${matchClass}`}>
                                {pct}% Skill Match
                              </span>
                            </div>

                            <div className="job-meta">
                              <b>{j.company}</b>
                              <span className="meta-dot">·</span>
                              <span>{j.salary || j.package}</span>
                              <span className="meta-dot">·</span>
                              <span>📍 {j.location || "Remote"}</span>
                            </div>

                            <div className="tags" style={{ marginTop: 8 }}>
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

                        <div className="job-action-wrap">
                          {isApplied ? (
                            <button className="btn secondary sm" disabled>
                              Applied ✓
                            </button>
                          ) : (
                            <button
                              className="btn-apply-blue"
                              onClick={() => handleApply(j.id)}
                              disabled={applyingJobId === j.id}
                            >
                              {applyingJobId === j.id ? "Applying..." : "Apply Now \u2192"}
                            </button>
                          )}
                          <button className="btn-view-details" onClick={() => onViewJob(j)}>
                            View Job
                          </button>
                        </div>
                      </article>
                    );
                  })}
                </div>
              )}
            </section>
          )}

          {/* 2. RESUME & SKILLS TAB */}
          {activeTab === "resume" && (
            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 16 }}>Resume &amp; Extracted Skills</h2>

              <div className="resume-card">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
                  <div>
                    <h3 style={{ margin: "0 0 2px", fontSize: 16, fontWeight: 700 }}>Current Resume File</h3>
                    <p style={{ margin: 0, fontSize: 13, color: "#667085" }}>
                      {studentProfile?.resume_url ? (
                        <span>
                          Active:{" "}
                          <a href={studentProfile.resume_url} target="_blank" rel="noreferrer" style={{ fontWeight: 600, color: "#2563EB" }}>
                            {studentProfile.resume_url.split("/").pop()}
                          </a>
                        </span>
                      ) : (
                        <span>No resume uploaded yet</span>
                      )}
                    </p>
                  </div>

                  {studentProfile?.resume_url && (
                    <a
                      href={studentProfile.resume_url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn secondary sm"
                    >
                      Download PDF ↗
                    </a>
                  )}
                </div>

                <form onSubmit={handleResumeUpload} className="resume-upload-zone">
                  <input
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={(e) => setResumeFile(e.target.files[0] || null)}
                    style={{ marginBottom: 10 }}
                  />
                  <div style={{ fontSize: 12.5, color: "#667085", marginBottom: 12 }}>
                    {resumeFile ? `Selected: ${resumeFile.name} (${Math.round(resumeFile.size / 1024)} KB)` : "Supported format: PDF only. Maximum file size: 5MB."}
                  </div>
                  <button type="submit" disabled={uploadingResume || !resumeFile} className="btn primary sm">
                    {uploadingResume ? "Parsing & Extracting Skills..." : "Upload Resume"}
                  </button>
                </form>

                {resumeSuccess && (
                  <div className="alert alert-success" style={{ marginTop: 14 }}>
                    <b>Resume uploaded successfully!</b>
                    {newSkillsExtracted.length > 0 && (
                      <div style={{ marginTop: 6 }}>
                        Detected skills: {newSkillsExtracted.join(", ")}
                      </div>
                    )}
                  </div>
                )}

                {resumeMsg && !resumeSuccess && (
                  <div className="alert alert-error" style={{ marginTop: 14 }}>
                    {resumeMsg}
                  </div>
                )}
              </div>

              {/* Detected Skills Editor */}
              <div className="resume-card">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
                  <div>
                    <h3 style={{ margin: "0 0 2px", fontSize: 16, fontWeight: 700 }}>Verified Skills Portfolio</h3>
                    <p style={{ margin: 0, fontSize: 13, color: "#667085" }}>
                      Skills used by our matching engine to calculate recommendation scores.
                    </p>
                  </div>
                  <button
                    type="button"
                    className="btn secondary sm"
                    onClick={() => setIsEditingSkills(!isEditingSkills)}
                  >
                    {isEditingSkills ? "Done Editing" : "Edit Skills"}
                  </button>
                </div>

                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {(studentProfile?.skills || []).length === 0 ? (
                    <span style={{ fontSize: 13, color: "#9CA3AF" }}>No detected skills yet. Upload your resume or add custom skills below.</span>
                  ) : (
                    (studentProfile?.skills || []).map((skill) => (
                      <span key={skill} className="skill-pill-editable">
                        {skill}
                        {isEditingSkills && (
                          <button
                            type="button"
                            className="skill-pill-remove"
                            onClick={() => handleRemoveSkill(skill)}
                          >
                            &times;
                          </button>
                        )}
                      </span>
                    ))
                  )}
                </div>

                {isEditingSkills && (
                  <form onSubmit={handleAddSkill} style={{ display: "flex", gap: 10, maxWidth: 420, marginTop: 16 }}>
                    <input
                      type="text"
                      placeholder="Add custom skill (e.g. Python, SQL)"
                      value={newSkillInput}
                      onChange={(e) => setNewSkillInput(e.target.value)}
                    />
                    <button type="submit" className="btn primary sm" disabled={!newSkillInput.trim()}>
                      + Add
                    </button>
                  </form>
                )}
              </div>
            </section>
          )}

          {/* 3. RESUME BUILDER TAB */}
          {activeTab === "builder" && (
            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 16 }}>Interactive Resume Builder</h2>
              <ResumeBuilder user={user} onSaveProfile={loadProfile} />
            </section>
          )}

          {/* 4. CAMPUS OPENINGS TAB */}
          {activeTab === "jobs" && (
            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 16 }}>Campus Job Drives ({jobs.length})</h2>
              <div className="job-list">
                {jobs.map((j) => {
                  const isApplied = appliedJobIds.has(j.id);
                  return (
                    <article className="job" key={j.id}>
                      <div className="job-main">
                        <CompanyLogo name={j.company} />
                        <div className="job-info">
                          <h3>{j.title || j.role}</h3>
                          <div className="job-meta">
                            <b>{j.company}</b>
                            <span className="meta-dot">·</span>
                            <span>{j.salary || j.package}</span>
                            <span className="meta-dot">·</span>
                            <span>📍 {j.location || "Remote"}</span>
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
                      </div>
                      <div className="job-action-wrap">
                        {isApplied ? (
                          <button className="btn secondary sm" disabled>
                            Applied ✓
                          </button>
                        ) : (
                          <button
                            className="btn-apply-blue"
                            onClick={() => handleApply(j.id)}
                            disabled={applyingJobId === j.id}
                          >
                            {applyingJobId === j.id ? "Applying..." : "Apply Now \u2192"}
                          </button>
                        )}
                        <button className="btn-view-details" onClick={() => onViewJob(j)}>
                          View Details
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>
          )}

          {/* 5. MY APPLICATIONS TAB */}
          {activeTab === "applications" && (
            <section>
              <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 16 }}>My Applications ({applications.length})</h2>
              {applications.length === 0 ? (
                <div style={{ background: "#FFFFFF", padding: 32, borderRadius: 16, border: "1px solid #EBE7DF", textAlign: "center" }}>
                  <p style={{ color: "#667085", margin: 0, fontSize: 14 }}>
                    You have not applied for any campus jobs yet. Browse recommended openings to apply.
                  </p>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                  {applications.map((app) => (
                    <div
                      key={app.id}
                      style={{
                        background: "#FFFFFF",
                        border: "1px solid #EBE7DF",
                        borderRadius: 16,
                        padding: "18px 22px",
                        boxShadow: "0 1px 3px rgba(0,0,0,0.03)"
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div>
                          <h3 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 4px" }}>{app.job_title}</h3>
                          <div style={{ fontSize: 13, color: "#667085" }}>
                            <b>{app.company}</b> · Applied on {new Date(app.applied_at).toLocaleDateString()}
                          </div>
                        </div>
                        <span className={`badge badge-${app.status}`}>{app.status.replaceAll("_", " ")}</span>
                      </div>

                      <ApplicationTimeline currentStatus={app.status} />
                    </div>
                  ))}
                </div>
              )}
            </section>
          )}

          {/* 6. MY INTERVIEWS TAB */}
          {activeTab === "interviews" && (
            <section>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <h2 style={{ fontSize: 20, fontWeight: 700, margin: 0 }}>My Scheduled Interviews ({interviews.length})</h2>
                <button className="btn secondary sm" onClick={loadInterviews}>
                  ↻ Refresh
                </button>
              </div>

              {interviews.length === 0 ? (
                <div style={{ background: "#FFFFFF", padding: 32, borderRadius: 16, border: "1px solid #EBE7DF", textAlign: "center" }}>
                  <p style={{ color: "#667085", margin: 0, fontSize: 14 }}>
                    No interviews scheduled yet. Once a recruiter shortlists your profile, interview invitations appear here.
                  </p>
                </div>
              ) : (
                <div>
                  {interviews.map((item) => {
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
                        </div>

                        <div>
                          {item.meeting_link && item.status === "SCHEDULED" && (
                            <a
                              href={item.meeting_link}
                              target="_blank"
                              rel="noreferrer"
                              className="btn success sm"
                            >
                              Join Video Call ↗
                            </a>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </section>
          )}
        </div>

        {/* Right Activity Stream */}
        <aside>
          <div className="aside-card">
            <div className="aside-header">
              <span className="live-dot" />
              <span>Real-Time Notifications</span>
            </div>
            <div className="timeline-list">
              {events.length ? (
                events.map((e, i) => (
                  <div className="timeline-item" key={i}>
                    <div className="timeline-icon icon-blue">🔔</div>
                    <div className="timeline-content">
                      <div className="timeline-title">{(e.type || "").replaceAll("_", " ")}</div>
                      <div className="timeline-desc">{e.message || "Status updated"}</div>
                      <div className="timeline-time">{new Date().toLocaleTimeString()}</div>
                    </div>
                  </div>
                ))
              ) : (
                <p style={{ color: "#667085", fontSize: 13, margin: 0 }}>Listening for placement events...</p>
              )}
            </div>
          </div>
        </aside>
      </main>
    </>
  );
}

// ==========================================
// 10. RECRUITER DASHBOARD
// ==========================================
function RecruiterDashboard({ user, jobs, loadJobs, applications, loadApplications, interviews, loadInterviews, events }) {
  const [activeTab, setActiveTab] = useState("applicants");
  const recruiter = user?.recruiter_profile;

  // Schedule Interview State
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
      }
    } catch {
      alert("Network error updating interview");
    }
  };

  return (
    <>
      <div className="profile-card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h3 style={{ fontSize: 20, fontWeight: 700, margin: "0 0 2px" }}>
              {recruiter?.company_name || "Company"} Recruiter Hub
            </h3>
            <p style={{ margin: 0, fontSize: 13.5, color: "#667085" }}>
              Lead Recruiter: {user?.name} · Contact: {recruiter?.company_email || user?.email}
            </p>
          </div>
          <button className="btn primary sm" onClick={() => setActiveTab("post_job")}>
            + Post New Opening
          </button>
        </div>

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
          📅 Interviews ({interviews.length})
        </div>
        <div
          className={`dash-tab ${activeTab === "post_job" ? "active" : ""}`}
          onClick={() => setActiveTab("post_job")}
        >
          ➕ Post Job
        </div>
        <div
          className={`dash-tab ${activeTab === "my_jobs" ? "active" : ""}`}
          onClick={() => setActiveTab("my_jobs")}
        >
          💼 My Posted Jobs ({jobs.length})
        </div>
      </div>

      <main>
        <div>
          {/* APPLICANTS TAB */}
          {activeTab === "applicants" && (
            <section>
              <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16 }}>Applicant Review Workflow</h2>
              {applications.length === 0 ? (
                <div style={{ background: "#FFFFFF", padding: 32, borderRadius: 16, border: "1px solid #EBE7DF", textAlign: "center" }}>
                  <p style={{ color: "#667085", margin: 0 }}>No student applications received yet.</p>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                  {applications.map((app) => (
                    <div
                      key={app.id}
                      style={{
                        background: "#FFFFFF",
                        border: "1px solid #EBE7DF",
                        borderRadius: 16,
                        padding: "18px 22px"
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 }}>
                        <div>
                          <h3 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 2px" }}>
                            {app.student_name || `Student Candidate #${app.student_id}`}
                          </h3>
                          <div style={{ fontSize: 13, color: "#667085", marginBottom: 6 }}>
                            Position: <b>{app.job_title}</b> · Applied: {new Date(app.applied_at).toLocaleDateString()}
                          </div>
                          <span className={`badge badge-${app.status}`}>{app.status.replaceAll("_", " ")}</span>
                        </div>

                        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                          <button
                            className="btn secondary sm"
                            onClick={() => handleUpdateAppStatus(app.id, "SHORTLISTED")}
                          >
                            Shortlist
                          </button>
                          <button
                            className="btn primary sm"
                            onClick={() => handleOpenScheduleModal(app)}
                          >
                            Schedule Interview
                          </button>
                          <button
                            className="btn secondary sm"
                            style={{ color: "#DC2626" }}
                            onClick={() => handleUpdateAppStatus(app.id, "REJECTED")}
                          >
                            Reject
                          </button>
                        </div>
                      </div>

                      <ApplicationTimeline currentStatus={app.status} />
                    </div>
                  ))}
                </div>
              )}
            </section>
          )}

          {/* INTERVIEWS TAB */}
          {activeTab === "interviews" && (
            <section>
              <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16 }}>Scheduled Candidate Interviews ({interviews.length})</h2>
              {interviews.length === 0 ? (
                <div style={{ background: "#FFFFFF", padding: 32, borderRadius: 16, border: "1px solid #EBE7DF", textAlign: "center" }}>
                  <p style={{ color: "#667085", margin: 0 }}>No interviews scheduled.</p>
                </div>
              ) : (
                interviews.map((item) => (
                  <div className="interview-card" key={item.id}>
                    <div className="interview-card-left">
                      <h4>{item.student_name} · {item.job_title}</h4>
                      <div className="interview-card-meta">
                        <span>📅 {new Date(item.scheduled_at).toLocaleDateString()}</span>
                        <span>⏰ {new Date(item.scheduled_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                        <span className={`mode-badge mode-${item.mode}`}>{item.mode}</span>
                        <span className={`badge badge-${item.status}`}>{item.status}</span>
                      </div>
                      {item.notes && <div className="interview-notes">📝 Notes: {item.notes}</div>}
                    </div>

                    <div style={{ display: "flex", gap: 8 }}>
                      {item.meeting_link && (
                        <a href={item.meeting_link} target="_blank" rel="noreferrer" className="btn success sm">
                          Join Call ↗
                        </a>
                      )}
                      <button
                        className="btn secondary sm"
                        onClick={() => handleUpdateInterviewStatus(item.id, "COMPLETED")}
                      >
                        Mark Completed
                      </button>
                    </div>
                  </div>
                ))
              )}
            </section>
          )}

          {/* POST JOB TAB */}
          {activeTab === "post_job" && (
            <section>
              <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16 }}>Post New Placement Opening</h2>
              <div style={{ background: "#FFFFFF", padding: 24, borderRadius: 16, border: "1px solid #EBE7DF" }}>
                {postMsg && <div className="alert alert-success">{postMsg}</div>}
                <form onSubmit={handleCreateJob}>
                  <div className="form-group">
                    <label>Job Title</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Associate DevOps Engineer"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                    />
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                    <div className="form-group">
                      <label>Compensation Package</label>
                      <input
                        type="text"
                        required
                        value={salary}
                        onChange={(e) => setSalary(e.target.value)}
                      />
                    </div>
                    <div className="form-group">
                      <label>Job Location</label>
                      <input
                        type="text"
                        required
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="form-group">
                    <label>Role Overview &amp; Requirements</label>
                    <textarea
                      rows="4"
                      required
                      placeholder="Describe the day-to-day responsibilities, technologies, and candidate profile..."
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                    />
                  </div>

                  <div className="form-group">
                    <label>Required Skills (Tags)</label>
                    <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
                      <input
                        type="text"
                        placeholder="Add skill (e.g. Kubernetes, AWS)"
                        value={jobSkillInput}
                        onChange={(e) => setJobSkillInput(e.target.value)}
                      />
                      <button
                        type="button"
                        className="btn secondary sm"
                        onClick={() => handleAddJobSkill()}
                      >
                        Add
                      </button>
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                      {jobSkills.map((s) => (
                        <span key={s} className="skill-pill-editable">
                          {s}
                          <button
                            type="button"
                            className="skill-pill-remove"
                            onClick={() => handleRemoveJobSkill(s)}
                          >
                            &times;
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>

                  <button type="submit" className="btn primary" disabled={posting} style={{ marginTop: 10 }}>
                    {posting ? "Publishing Opening..." : "Publish Job Opening \u2192"}
                  </button>
                </form>
              </div>
            </section>
          )}

          {/* MY JOBS TAB */}
          {activeTab === "my_jobs" && (
            <section>
              <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16 }}>My Posted Jobs ({jobs.length})</h2>
              <div className="job-list">
                {jobs.map((j) => (
                  <article className="job" key={j.id}>
                    <div className="job-main">
                      <CompanyLogo name={j.company} />
                      <div className="job-info">
                        <h3>{j.title}</h3>
                        <div className="job-meta">
                          <b>{j.company}</b> · {j.salary} · 📍 {j.location}
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
                    </div>
                    <div className="job-action-wrap">
                      <span className="badge badge-SHORTLISTED">Active</span>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          )}
        </div>

        <aside>
          <div className="aside-card">
            <div className="aside-header">
              <span className="live-dot" />
              <span>Real-Time Recruiter Alerts</span>
            </div>
            <div className="timeline-list">
              {events.length ? (
                events.map((e, i) => (
                  <div className="timeline-item" key={i}>
                    <div className="timeline-icon icon-purple">⚡</div>
                    <div className="timeline-content">
                      <div className="timeline-title">{(e.type || "").replaceAll("_", " ")}</div>
                      <div className="timeline-desc">{e.message || "Update received"}</div>
                    </div>
                  </div>
                ))
              ) : (
                <p style={{ color: "#667085", fontSize: 13, margin: 0 }}>Listening for events...</p>
              )}
            </div>
          </div>
        </aside>
      </main>

      {/* SCHEDULE INTERVIEW MODAL */}
      {schedulingApp && (
        <div className="modal-overlay" onClick={() => setSchedulingApp(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 500 }}>
            <div className="modal-header">
              <div>
                <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Schedule Candidate Interview</h3>
                <div style={{ fontSize: 13, color: "#667085" }}>
                  For {schedulingApp.student_name} ({schedulingApp.job_title})
                </div>
              </div>
              <button className="modal-close" onClick={() => setSchedulingApp(null)}>&times;</button>
            </div>

            {scheduleMsg && <div className="alert alert-success">{scheduleMsg}</div>}

            <form onSubmit={handleScheduleSubmit}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div className="form-group">
                  <label>Date</label>
                  <input
                    type="date"
                    required
                    value={schedDate}
                    onChange={(e) => setSchedDate(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Time</label>
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
                  <option value="ONLINE">Online (Google Meet / Video)</option>
                  <option value="OFFLINE">In-Person (Campus Office)</option>
                  <option value="HYBRID">Hybrid</option>
                </select>
              </div>

              {schedMode !== "OFFLINE" && (
                <div className="form-group">
                  <label>Video Meeting Link</label>
                  <input
                    type="text"
                    required
                    value={schedLink}
                    onChange={(e) => setSchedLink(e.target.value)}
                  />
                </div>
              )}

              <div className="form-group">
                <label>Interview Notes / Instructions</label>
                <textarea
                  rows="2"
                  value={schedNotes}
                  onChange={(e) => setSchedNotes(e.target.value)}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 20 }}>
                <button type="button" className="btn secondary sm" onClick={() => setSchedulingApp(null)}>
                  Cancel
                </button>
                <button type="submit" className="btn primary sm" disabled={submittingSched}>
                  {submittingSched ? "Broadcasting..." : "Confirm & Send Schedule"}
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
// 11. ADMIN DASHBOARD
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

  // Analytics Metrics
  const totalStudents = stats?.total_students ?? 1248;
  const totalRecruiters = stats?.total_recruiters ?? 86;
  const totalJobs = stats?.total_jobs ?? jobs.length;
  const totalApps = stats?.total_applications ?? applications.length;
  const placementRate = "87.4%";

  return (
    <>
      <div className="profile-card">
        <h3 style={{ fontSize: 20, fontWeight: 700, margin: "0 0 2px" }}>Master Administration &amp; Analytics Console</h3>
        <p style={{ margin: 0, fontSize: 13.5, color: "#667085" }}>
          Administrator: {user?.name} · Elevated Role: ADMIN · Full Real-Time Visibility
        </p>
      </div>

      {/* Primary KPI Row */}
      <section className="stats">
        <div className="stat-card card-peach">
          <div className="stat-icon-box">🎓</div>
          <div className="stat-details">
            <b>{totalStudents}</b>
            <span>Total Students</span>
          </div>
        </div>
        <div className="stat-card card-blue">
          <div className="stat-icon-box">🏢</div>
          <div className="stat-details">
            <b>{totalRecruiters}</b>
            <span>Partner Companies</span>
          </div>
        </div>
        <div className="stat-card card-green">
          <div className="stat-icon-box">💼</div>
          <div className="stat-details">
            <b>{totalJobs}</b>
            <span>Active Openings</span>
          </div>
        </div>
        <div className="stat-card card-sand">
          <div className="stat-icon-box">📈</div>
          <div className="stat-details">
            <b>{placementRate}</b>
            <span>Placement Rate</span>
          </div>
        </div>
      </section>

      {/* Analytics Charts & Most Demanded Skills */}
      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: 20, marginBottom: 24 }}>
        {/* Visual Analytics Chart */}
        <div style={{ background: "#FFFFFF", padding: 24, borderRadius: 16, border: "1px solid #EBE7DF" }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 4px" }}>Campus Hiring Velocity &amp; Distribution</h3>
          <p style={{ fontSize: 13, color: "#667085", marginBottom: 20 }}>Applications vs Shortlisted Interviews</p>

          <div style={{ display: "flex", alignItems: "flex-end", height: 160, gap: 16, padding: "0 10px 10px", borderBottom: "1px solid #EBE7DF" }}>
            {[
              { label: "Engineering", apps: 85, placed: 72 },
              { label: "DevOps & Cloud", apps: 92, placed: 84 },
              { label: "Data & AI", apps: 78, placed: 65 },
              { label: "Product/QA", apps: 60, placed: 50 },
              { label: "Cybersecurity", apps: 45, placed: 40 }
            ].map((bar, i) => (
              <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                <div style={{ display: "flex", alignItems: "flex-end", gap: 4, height: 120 }}>
                  <div style={{ width: 14, height: `${bar.apps}%`, background: "#DCEBFF", borderRadius: "4px 4px 0 0" }} title={`Applications: ${bar.apps}`} />
                  <div style={{ width: 14, height: `${bar.placed}%`, background: "#111111", borderRadius: "4px 4px 0 0" }} title={`Placed: ${bar.placed}`} />
                </div>
                <span style={{ fontSize: 11, color: "#667085", whiteSpace: "nowrap" }}>{bar.label}</span>
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: 16, marginTop: 14, fontSize: 12, justifyContent: "center" }}>
            <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ width: 10, height: 10, background: "#DCEBFF", borderRadius: 2 }} /> Applications Volume
            </span>
            <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ width: 10, height: 10, background: "#111111", borderRadius: 2 }} /> Placed Candidates
            </span>
          </div>
        </div>

        {/* Most Demanded Skills */}
        <div style={{ background: "#FFFFFF", padding: 24, borderRadius: 16, border: "1px solid #EBE7DF" }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 4px" }}>Most Demanded Technologies</h3>
          <p style={{ fontSize: 13, color: "#667085", marginBottom: 16 }}>Skills requested across active campus drives</p>

          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {[
              { skill: "Python", pct: 92, count: "14 jobs" },
              { skill: "Docker & Containerization", pct: 86, count: "12 jobs" },
              { skill: "React.js", pct: 80, count: "11 jobs" },
              { skill: "FastAPI / Node", pct: 75, count: "9 jobs" },
              { skill: "Kubernetes & CI/CD", pct: 68, count: "8 jobs" }
            ].map((item) => (
              <div key={item.skill}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12.5, fontWeight: 600, marginBottom: 4 }}>
                  <span>{item.skill}</span>
                  <span style={{ color: "#667085" }}>{item.count}</span>
                </div>
                <div style={{ height: 6, background: "#F3F4F6", borderRadius: 9999, overflow: "hidden" }}>
                  <div style={{ height: "100%", width: `${item.pct}%`, background: "#111111", borderRadius: 9999 }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <main>
        <div>
          {deleteMsg && <div className="alert alert-success">{deleteMsg}</div>}

          {/* User Management Section */}
          <section style={{ marginBottom: 28 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
              <h2 style={{ fontSize: 18, fontWeight: 700, margin: 0 }}>User Management Directory ({users.length})</h2>
              <button className="btn secondary sm" onClick={loadAdminData}>
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
                          <div style={{ fontSize: 11, color: "#667085" }}>
                            {u.student_profile.degree} - {u.student_profile.college}
                          </div>
                        )}
                        {u.recruiter_profile && (
                          <div style={{ fontSize: 11, color: "#667085" }}>
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
                            className="btn danger sm"
                            onClick={() => handleDeleteUser(u.id)}
                          >
                            Delete
                          </button>
                        ) : (
                          <span style={{ fontSize: 12, color: "#667085" }}>Current Session</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* System Applications Table */}
          <section>
            <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 14 }}>
              System-Wide Applications ({applications.length})
            </h2>
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
          <div className="aside-card">
            <div className="aside-header">
              <span className="live-dot" />
              <span>Real-Time Audit Trail</span>
            </div>
            <div className="timeline-list">
              {events.length ? (
                events.map((e, i) => (
                  <div className="timeline-item" key={i}>
                    <div className="timeline-icon icon-purple">⚙️</div>
                    <div className="timeline-content">
                      <div className="timeline-title">{(e.type || "").replaceAll("_", " ")}</div>
                      <div className="timeline-desc">{e.message || JSON.stringify(e.data || {})}</div>
                      <div className="timeline-time">{new Date().toLocaleTimeString()}</div>
                    </div>
                  </div>
                ))
              ) : (
                <p style={{ color: "#667085", fontSize: 13, margin: 0 }}>Audit log active...</p>
              )}
            </div>
          </div>
        </aside>
      </main>
    </>
  );
}

createRoot(document.getElementById("root")).render(<App />);
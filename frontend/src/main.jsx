import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";
import EditorialHomepage from "./EditorialHomepage";

// Helper for authenticated API requests
function authFetch(url, options = {}) {
  const token = localStorage.getItem("token");
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {})
  };
  return fetch(url, { ...options, headers });
}

// Hiring workflow stages
const WORKFLOW_STEPS = [
  { key: "SUBMITTED", label: "Submitted" },
  { key: "UNDER_REVIEW", label: "Under Review" },
  { key: "SHORTLISTED", label: "Shortlisted" },
  { key: "INTERVIEW_SCHEDULED", label: "Interview" },
  { key: "OFFERED", label: "Offered" },
  { key: "ACCEPTED", label: "Accepted" }
];

function ApplicationTimeline({ currentStatus }) {
  if (currentStatus === "REJECTED") {
    return (
      <div className="timeline-container">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ fontSize: 12, fontWeight: 700, color: "#64748b" }}>Status</span>
          <span className="badge" style={{ background: "#fef2f2", color: "#b91c1c", border: "1px solid #fecaca" }}>
            Not Selected
          </span>
        </div>
      </div>
    );
  }

  if (currentStatus === "WITHDRAWN") {
    return (
      <div className="timeline-container">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ fontSize: 12, fontWeight: 700, color: "#64748b" }}>Status</span>
          <span className="badge" style={{ background: "#f1f5f9", color: "#475569" }}>
            Withdrawn by Student
          </span>
        </div>
      </div>
    );
  }

  let normalized = currentStatus;
  if (normalized === "APPLIED") normalized = "SUBMITTED";
  if (normalized === "INTERVIEW") normalized = "INTERVIEW_SCHEDULED";

  const currentIndex = WORKFLOW_STEPS.findIndex((s) => s.key === normalized);
  const activeIdx = currentIndex >= 0 ? currentIndex : 0;
  const progressPercent = (activeIdx / (WORKFLOW_STEPS.length - 1)) * 100;

  return (
    <div className="timeline-container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: 0.5 }}>
          Hiring Pipeline Stage
        </span>
        <span className="badge" style={{ background: "#eff6ff", color: "#1d4ed8", fontWeight: 700 }}>
          {normalized.replaceAll("_", " ")}
        </span>
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
            <div key={step.key} className={`timeline-step ${stepClass}`}>
              <div className="step-node">
                {idx < activeIdx ? "✓" : idx + 1}
              </div>
              <span className="step-title-text">{step.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// 12 Part-time job categories
const CATEGORIES = [
  "All", "Web Development", "Online Tutoring", "Graphic Design", "Video Editing",
  "Data Entry", "Campus Assistant", "Retail and Sales", "Customer Support",
  "Delivery and Logistics", "Content Writing", "Social Media Management", "Event Assistant"
];

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

  // Toast notifications stack
  const [toasts, setToasts] = useState([]);
  const addToast = (message, type = "success") => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // Data collections
  const [jobs, setJobs] = useState([]);
  const [savedJobs, setSavedJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [interviews, setInterviews] = useState([]);
  const [shifts, setShifts] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const previousUnreadCount = useRef(null);
  const [adminStats, setAdminStats] = useState(null);
  const [adminUsers, setAdminUsers] = useState([]);
  const [adminReports, setAdminReports] = useState([]);
  const [pendingApprovals, setPendingApprovals] = useState({ pending_users: [], pending_jobs: [] });

  // Live WebSocket
  const [events, setEvents] = useState([]);
  const [wsStatus, setWsStatus] = useState("Connecting...");

  // Search & Filters state
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedArrangement, setSelectedArrangement] = useState("All");
  const [selectedShift, setSelectedShift] = useState("All");
  const [selectedJobType, setSelectedJobType] = useState("All");
  const [sortBy, setSortBy] = useState("newest");

  // Dashboard Sub-Tabs
  const [employerTab, setEmployerTab] = useState("pipeline"); // pipeline, jobs, interviews, profile
  const [adminTab, setAdminTab] = useState("pending"); // pending, users, all-jobs, moderation
  const [adminUserSearch, setAdminUserSearch] = useState("");
  const [adminUserRoleFilter, setAdminUserRoleFilter] = useState("ALL");
  const [applicantJobFilter, setApplicantJobFilter] = useState("ALL");

  // Student Profile Edit State
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [profileForm, setProfileForm] = useState({
    name: "", college: "", degree: "", branch: "", cgpa: "",
    weekly_availability: "15 hrs/week", preferred_work_arrangement: "Any",
    max_weekly_hours: 20, experience: ""
  });
  const [newSkillInput, setNewSkillInput] = useState("");

  // Employer Profile Edit State
  const [employerProfileForm, setEmployerProfileForm] = useState({
    company_name: "", company_email: "", business_description: "",
    industry: "", website: "", location: "", contact_phone: ""
  });

  // Modals
  const [selectedJobDetails, setSelectedJobDetails] = useState(null);
  const [applyModalJob, setApplyModalJob] = useState(null);
  const [applyCoverLetter, setApplyCoverLetter] = useState("");
  const [applyAvailability, setApplyAvailability] = useState("");
  const [pendingApplyJob, setPendingApplyJob] = useState(null);

  const [reportModalJob, setReportModalJob] = useState(null);
  const [reportReason, setReportReason] = useState("Misleading compensation");
  const [reportDetails, setReportDetails] = useState("");

  const [interviewModalApp, setInterviewModalApp] = useState(null);
  const [interviewDate, setInterviewDate] = useState("");
  const [interviewMode, setInterviewMode] = useState("ONLINE");
  const [interviewLink, setInterviewLink] = useState("");
  const [interviewNotes, setInterviewNotes] = useState("");

  const [confirmDialog, setConfirmDialog] = useState(null); // { title, message, onConfirm }

  // Admin User Management CRUD State
  const [showCreateUserModal, setShowCreateUserModal] = useState(false);
  const [createUserData, setCreateUserData] = useState({
    name: "", email: "", password: "", role: "STUDENT", is_active: true, is_approved: true
  });
  const [editingUser, setEditingUser] = useState(null);
  const [editUserData, setEditUserData] = useState({
    name: "", email: "", role: "STUDENT", is_active: true, is_approved: true
  });

  // Auth Modal State
  const [authModalMode, setAuthModalMode] = useState(null); // 'login' or 'register'
  const [authRole, setAuthRole] = useState("STUDENT");
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authName, setAuthName] = useState("");
  const [authCompany, setAuthCompany] = useState("");
  const [authCollege, setAuthCollege] = useState("");
  const [authError, setAuthError] = useState("");

  // Post Job State
  const [postJobData, setPostJobData] = useState({
    title: "", category: "Web Development", pay_rate: "₹300 - ₹500/hr",
    weekly_hours: "10-15 hrs/week", shift_schedule: "Flexible", work_arrangement: "Remote",
    location: "Remote", job_type: "Part-time", description: "", responsibilities: "",
    qualifications: "", benefits: "", skills: "React, JavaScript", vacancies: 2
  });

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

  // Fetch current user and sync session
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
          // Pre-fill student profile form
          if (userData.role === "STUDENT" && userData.student_profile) {
            const sp = userData.student_profile;
            setProfileForm({
              name: userData.name || "",
              college: sp.college || "",
              degree: sp.degree || "",
              branch: sp.branch || "",
              cgpa: sp.cgpa || "",
              weekly_availability: sp.weekly_availability || "15 hrs/week",
              preferred_work_arrangement: sp.preferred_work_arrangement || "Any",
              max_weekly_hours: sp.max_weekly_hours || 20,
              experience: sp.experience || ""
            });
          }
          // Pre-fill employer profile form
          if ((userData.role === "RECRUITER" || userData.role === "EMPLOYER") && userData.recruiter_profile) {
            const rp = userData.recruiter_profile;
            setEmployerProfileForm({
              company_name: rp.company_name || "",
              company_email: rp.company_email || "",
              business_description: rp.business_description || "",
              industry: rp.industry || "",
              website: rp.website || "",
              location: rp.location || "",
              contact_phone: rp.contact_phone || ""
            });
          }
        })
        .catch(() => logout());
    }
  }, [token]);

  // Client-side role-based route protection guard
  useEffect(() => {
    const studentRoutes = ["/dashboard", "/saved-jobs", "/my-applications", "/profile"];
    const employerRoutes = ["/employer-dashboard", "/post-job"];
    const adminRoutes = ["/admin"];

    if (!token && [...studentRoutes, ...employerRoutes, ...adminRoutes].includes(route)) {
      addToast("Please sign in to access this page.", "info");
      setAuthModalMode("login");
      navigate("/");
      return;
    }

    if (token && user) {
      if (studentRoutes.includes(route) && user.role !== "STUDENT") {
        addToast("This section is restricted to student accounts.", "info");
        navigate(user.role === "ADMIN" ? "/admin" : "/employer-dashboard");
      } else if (employerRoutes.includes(route) && !["RECRUITER", "EMPLOYER"].includes(user.role)) {
        addToast("Access restricted: Employer account required.", "error");
        navigate(user.role === "ADMIN" ? "/admin" : "/dashboard");
      } else if (adminRoutes.includes(route) && user.role !== "ADMIN") {
        addToast("Access restricted: Administrator privileges required.", "error");
        navigate(user.role === "STUDENT" ? "/dashboard" : "/employer-dashboard");
      }
    }
  }, [route, token, user?.role]);

  // Load jobs with search & filters
  const loadJobs = () => {
    const params = new URLSearchParams();
    if (searchQuery) params.set("q", searchQuery);
    if (selectedCategory !== "All") params.set("category", selectedCategory);
    if (selectedArrangement !== "All") params.set("work_arrangement", selectedArrangement);
    if (selectedShift !== "All") params.set("shift_schedule", selectedShift);
    if (selectedJobType !== "All") params.set("job_type", selectedJobType);
    if (sortBy) params.set("sort_by", sortBy);
    // Admin's platform-wide jobs table must include pending and closed jobs too.
    if (user?.role === "ADMIN") params.set("status", "ALL");

    authFetch(`/api/jobs?${params.toString()}`)
      .then((r) => r.json())
      .then((data) => {
        if (Array.isArray(data)) setJobs(data);
      })
      .catch((err) => console.error("Error loading jobs:", err));
  };

  // Load user data
  const loadUserData = () => {
    if (!token) return;

    if (user?.role === "STUDENT") {
      authFetch("/api/saved-jobs")
        .then((r) => (r.ok ? r.json() : []))
        .then((data) => setSavedJobs(data));
    }

    authFetch("/api/applications")
      .then((r) => (r.ok ? r.json() : []))
      .then((data) => setApplications(data));

    authFetch("/api/interviews")
      .then((r) => (r.ok ? r.json() : []))
      .then((data) => setInterviews(data));

    authFetch("/api/shifts")
      .then((r) => (r.ok ? r.json() : []))
      .then((data) => setShifts(data));

    authFetch("/api/notifications")
      .then((r) => (r.ok ? r.json() : { notifications: [], unread_count: 0 }))
      .then((data) => {
        const nextUnreadCount = Number(data.unread_count || 0);
        setNotifications(data.notifications || []);
        setUnreadCount(nextUnreadCount);
        if (previousUnreadCount.current === null) previousUnreadCount.current = nextUnreadCount;
      })
      .catch((err) => console.error("Unable to load notifications:", err));

    if (user?.role === "ADMIN") {
      authFetch("/api/admin/stats")
        .then((r) => (r.ok ? r.json() : null))
        .then((stats) => { if (stats) setAdminStats(stats); });

      authFetch("/api/admin/users")
        .then((r) => (r.ok ? r.json() : []))
        .then((usersList) => { if (Array.isArray(usersList)) setAdminUsers(usersList); });

      authFetch("/api/admin/reports")
        .then((r) => (r.ok ? r.json() : []))
        .then((reportsList) => { if (Array.isArray(reportsList)) setAdminReports(reportsList); });

      authFetch("/api/admin/pending-approvals")
        .then((r) => (r.ok ? r.json() : { pending_users: [], pending_jobs: [] }))
        .then((data) => setPendingApprovals(data));
    }
  };

  useEffect(() => {
    loadJobs();
  }, [searchQuery, selectedCategory, selectedArrangement, selectedShift, selectedJobType, sortBy, token, user?.role]);

  useEffect(() => {
    if (token) {
      loadUserData();
    }
  }, [token, user?.role]);

  // Poll the authenticated notification feed as a reliable fallback to WebSockets.
  // This also ensures notifications created while the browser was offline appear.
  useEffect(() => {
    if (!token) {
      previousUnreadCount.current = null;
      return undefined;
    }

    let cancelled = false;
    const refreshNotifications = async () => {
      try {
        const response = await authFetch("/api/notifications");
        if (response.status === 401) return;
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        if (cancelled) return;

        const nextUnreadCount = Number(data.unread_count || 0);
        const previous = previousUnreadCount.current;
        setNotifications(data.notifications || []);
        setUnreadCount(nextUnreadCount);
        if (previous !== null && nextUnreadCount > previous) {
          addToast(nextUnreadCount - previous === 1
            ? "You have a new notification."
            : `You have ${nextUnreadCount - previous} new notifications.`, "info");
        }
        previousUnreadCount.current = nextUnreadCount;
      } catch (err) {
        console.warn("Notification refresh failed; will retry:", err);
      }
    };

    refreshNotifications();
    const pollId = window.setInterval(refreshNotifications, 10000);
    return () => {
      cancelled = true;
      window.clearInterval(pollId);
    };
  }, [token]);

  // WebSocket live updates with automatic reconnect. The persistent notification API
  // remains the source of truth; WebSocket events simply prompt a refresh.
  useEffect(() => {
    let disposed = false;
    let socket = null;
    let reconnectTimer = null;
    let heartbeatTimer = null;
    let retryDelay = 1000;

    const connect = () => {
      if (disposed) return;
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      socket = new WebSocket(`${protocol}//${window.location.host}/ws/notifications`);

      socket.onopen = () => {
        retryDelay = 1000;
        setWsStatus("Live");
        heartbeatTimer = window.setInterval(() => {
          if (socket && socket.readyState === WebSocket.OPEN) socket.send("ping");
        }, 25000);
      };

      socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setEvents((current) => [message, ...current].slice(0, 15));
          if (message.type === "NEW_JOB" || message.type === "JOB_APPROVAL_PENDING" || message.type === "NEW_APPLICATION" || message.type === "APPLICATION_STATUS" || message.type === "INTERVIEW_SCHEDULED" || message.type === "INTERVIEW_UPDATED" || message.type === "INTERVIEW_CANCELLED" || message.type === "JOB_SCHEDULE_UPDATED" || message.type === "JOB_DETAILS_UPDATED" || message.type === "SHIFT_SCHEDULED" || message.type === "USER_APPROVAL_PENDING" || message.type === "USER_APPROVED") {
            if (token) loadUserData();
            if (message.type === "NEW_JOB" || message.type === "JOB_SCHEDULE_UPDATED" || message.type === "JOB_DETAILS_UPDATED" || message.type === "USER_APPROVED") loadJobs();
          }
        } catch (err) {
          console.error("WebSocket message error:", err);
        }
      };

      socket.onclose = () => {
        if (heartbeatTimer) window.clearInterval(heartbeatTimer);
        heartbeatTimer = null;
        if (disposed) return;
        setWsStatus("Reconnecting...");
        reconnectTimer = window.setTimeout(connect, retryDelay);
        retryDelay = Math.min(retryDelay * 2, 15000);
      };
      socket.onerror = () => {
        setWsStatus("Offline");
        if (socket) socket.close();
      };
    };

    connect();
    return () => {
      disposed = true;
      if (reconnectTimer) window.clearTimeout(reconnectTimer);
      if (heartbeatTimer) window.clearInterval(heartbeatTimer);
      if (socket) socket.close();
    };
  }, [token]);

  // Auth actions
  const login = async (e) => {
    e.preventDefault();
    setAuthError("");
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: authEmail, password: authPassword })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      setToken(data.access_token);
      setUser(data.user);
      setAuthModalMode(null);
      addToast(`Welcome back, ${data.user.name}!`);

      // Role-based redirection
      if (pendingApplyJob && data.user.role === "STUDENT") {
        setApplyModalJob(pendingApplyJob);
        setPendingApplyJob(null);
        navigate("/find-jobs");
      } else if (data.user.role === "STUDENT") {
        navigate("/dashboard");
      } else if (data.user.role === "RECRUITER" || data.user.role === "EMPLOYER") {
        navigate("/employer-dashboard");
      } else if (data.user.role === "ADMIN") {
        navigate("/admin");
      }
    } catch (err) {
      setAuthError(err.message);
    }
  };

  const register = async (e) => {
    e.preventDefault();
    setAuthError("");
    try {
      const payload = {
        role: authRole,
        name: authName,
        email: authEmail,
        password: authPassword,
        college: authCollege,
        company_name: authCompany
      };
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Registration failed");

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      setToken(data.access_token);
      setUser(data.user);
      setAuthModalMode(null);
      addToast(`🎉 Account created successfully!`);

      if (data.user.role === "STUDENT") {
        navigate("/dashboard");
      } else {
        navigate("/employer-dashboard");
      }
    } catch (err) {
      setAuthError(err.message);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken("");
    setUser(null);
    setApplications([]);
    setSavedJobs([]);
    setInterviews([]);
    setShifts([]);
    addToast("You have been signed out.", "info");
    navigate("/");
  };

  // Job Actions
  const toggleSaveJob = async (jobId, isCurrentlySaved) => {
    if (!token) {
      setAuthModalMode("login");
      return;
    }
    if (user?.role !== "STUDENT") {
      addToast("Only student accounts can save and bookmark jobs.", "info");
      return;
    }
    const method = isCurrentlySaved ? "DELETE" : "POST";
    const res = await authFetch(`/api/jobs/${jobId}/save`, { method });
    if (res.ok) {
      loadJobs();
      const savedRes = await authFetch("/api/saved-jobs");
      if (savedRes.ok) {
        const data = await savedRes.json();
        setSavedJobs(Array.isArray(data) ? data : []);
      }
      if (!isCurrentlySaved) {
        navigate("/dashboard");
      }
      addToast(isCurrentlySaved ? "Job removed from saved bookmarks" : "⭐ Job saved! Viewing in your Student Dashboard...");
    } else {
      const err = await res.json().catch(() => ({}));
      addToast(err.detail || "Failed to update saved job", "error");
    }
  };

  const handleApplyClick = (job) => {
    if (!token) {
      setPendingApplyJob(job);
      setAuthModalMode("login");
      return;
    }
    if (user?.role !== "STUDENT") {
      addToast("Only student accounts can apply for jobs.", "error");
      return;
    }
    if (user?.is_approved === false) {
      addToast("Your student account is pending Admin approval. You will be able to apply once approved.", "error");
      return;
    }
    setApplyModalJob(job);
  };

  const handleApplySubmit = async (e) => {
    e.preventDefault();
    if (!applyModalJob) return;

    try {
      const res = await authFetch("/api/applications", {
        method: "POST",
        body: JSON.stringify({
          job_id: applyModalJob.id,
          cover_letter: applyCoverLetter,
          availability: applyAvailability
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to submit application");

      addToast("🎉 Application submitted successfully!");
      setApplyModalJob(null);
      setApplyCoverLetter("");
      setApplyAvailability("");
      loadUserData();
      navigate("/my-applications");
    } catch (err) {
      addToast(`⚠️ ${err.message}`, "error");
    }
  };

  const handleWithdraw = (appId) => {
    setConfirmDialog({
      title: "Withdraw Application",
      message: "Are you sure you want to withdraw this application? This cannot be undone.",
      onConfirm: async () => {
        const res = await authFetch(`/api/applications/${appId}/withdraw`, { method: "POST" });
        if (res.ok) {
          addToast("Application withdrawn successfully.", "info");
          loadUserData();
        } else {
          addToast("Failed to withdraw application", "error");
        }
        setConfirmDialog(null);
      }
    });
  };

  const handleReportSubmit = async (e) => {
    e.preventDefault();
    if (!reportModalJob) return;

    const res = await authFetch(`/api/jobs/${reportModalJob.id}/report`, {
      method: "POST",
      body: JSON.stringify({ reason: reportReason, details: reportDetails })
    });
    if (res.ok) {
      addToast("Thank you. Listing submitted to moderators for audit.", "info");
      setReportModalJob(null);
      setReportDetails("");
    }
  };

  const handleScheduleInterview = async (e) => {
    e.preventDefault();
    if (!interviewModalApp) return;

    const res = await authFetch("/api/interviews", {
      method: "POST",
      body: JSON.stringify({
        application_id: interviewModalApp.id,
        scheduled_at: new Date(interviewDate).toISOString(),
        mode: interviewMode,
        meeting_link: interviewLink,
        notes: interviewNotes
      })
    });
    if (res.ok) {
      addToast("✅ Interview scheduled and student notified!");
      setInterviewModalApp(null);
      setInterviewDate("");
      setInterviewLink("");
      setInterviewNotes("");
      loadUserData();
    } else {
      addToast("Failed to schedule interview", "error");
    }
  };

  const handleCreateJob = async (e) => {
    e.preventDefault();
    if (user?.is_approved === false) {
      addToast("Your recruiter account is awaiting Admin approval. You will be able to post gigs once approved.", "error");
      return;
    }
    const skillsArray = postJobData.skills.split(",").map((s) => s.trim()).filter(Boolean);
    const res = await authFetch("/api/jobs", {
      method: "POST",
      body: JSON.stringify({
        ...postJobData,
        skills: skillsArray,
        salary: postJobData.pay_rate
      })
    });
    if (res.ok) {
      addToast("✅ Job offer submitted! Notification sent to Admin for review & approval.");
      navigate("/employer-dashboard");
      setEmployerTab("jobs");
      loadJobs();
      loadUserData();
    } else {
      const err = await res.json();
      addToast(`Error: ${err.detail || "Failed to post gig"}`, "error");
    }
  };

  const handleAdminCreateUser = async (e) => {
    e.preventDefault();
    if (!createUserData.name || !createUserData.email || !createUserData.password) {
      addToast("Please fill all required fields", "error");
      return;
    }
    const res = await authFetch("/api/admin/users", {
      method: "POST",
      body: JSON.stringify(createUserData)
    });
    if (res.ok) {
      addToast(`✅ User '${createUserData.name}' created successfully!`);
      setShowCreateUserModal(false);
      setCreateUserData({
        name: "", email: "", password: "", role: "STUDENT", is_active: true, is_approved: true
      });
      loadUserData();
    } else {
      const err = await res.json().catch(() => ({}));
      addToast(err.detail || "Failed to create user account", "error");
    }
  };

  const handleAdminUpdateUser = async (e) => {
    e.preventDefault();
    if (!editingUser) return;
    const res = await authFetch(`/api/admin/users/${editingUser.id}`, {
      method: "PATCH",
      body: JSON.stringify(editUserData)
    });
    if (res.ok) {
      addToast(`✅ User '${editUserData.name}' updated successfully!`);
      setEditingUser(null);
      loadUserData();
    } else {
      const err = await res.json().catch(() => ({}));
      addToast(err.detail || "Failed to update user", "error");
    }
  };

  // Student Profile Updates
  const handleSaveProfile = async (e) => {
    e.preventDefault();
    try {
      const res = await authFetch("/api/students/profile", {
        method: "PUT",
        body: JSON.stringify({
          name: profileForm.name,
          college: profileForm.college,
          degree: profileForm.degree,
          branch: profileForm.branch,
          cgpa: profileForm.cgpa ? parseFloat(profileForm.cgpa) : null,
          weekly_availability: profileForm.weekly_availability,
          preferred_work_arrangement: profileForm.preferred_work_arrangement,
          max_weekly_hours: profileForm.max_weekly_hours ? parseInt(profileForm.max_weekly_hours) : 20,
          experience: profileForm.experience
        })
      });
      if (res.ok) {
        addToast("Profile saved successfully!");
        setIsEditingProfile(false);
        const meRes = await authFetch("/api/auth/me");
        if (meRes.ok) {
          const updatedUser = await meRes.json();
          setUser(updatedUser);
          localStorage.setItem("user", JSON.stringify(updatedUser));
        }
      } else {
        const err = await res.json();
        addToast(`Failed to update profile: ${err.detail}`, "error");
      }
    } catch (err) {
      addToast(`Error: ${err.message}`, "error");
    }
  };

  const handleAddSkill = async (e) => {
    e.preventDefault();
    const cleanSkill = newSkillInput.trim();
    if (!cleanSkill) return;

    const existingSkills = user?.student_profile?.skills || [];
    if (existingSkills.includes(cleanSkill)) {
      addToast("Skill already in profile", "info");
      setNewSkillInput("");
      return;
    }

    const updatedSkills = [...existingSkills, cleanSkill];
    const res = await authFetch("/api/students/profile", {
      method: "PUT",
      body: JSON.stringify({ skills: updatedSkills })
    });
    if (res.ok) {
      addToast(`Skill added: ${cleanSkill}`);
      setNewSkillInput("");
      const meRes = await authFetch("/api/auth/me");
      if (meRes.ok) {
        const u = await meRes.json();
        setUser(u);
        localStorage.setItem("user", JSON.stringify(u));
      }
    }
  };

  const handleRemoveSkill = async (skillToRemove) => {
    const existingSkills = user?.student_profile?.skills || [];
    const updatedSkills = existingSkills.filter((s) => s !== skillToRemove);
    const res = await authFetch("/api/students/profile", {
      method: "PUT",
      body: JSON.stringify({ skills: updatedSkills })
    });
    if (res.ok) {
      addToast(`Removed skill: ${skillToRemove}`, "info");
      const meRes = await authFetch("/api/auth/me");
      if (meRes.ok) {
        const u = await meRes.json();
        setUser(u);
        localStorage.setItem("user", JSON.stringify(u));
      }
    }
  };

  // Employer Profile Updates
  const handleSaveEmployerProfile = async (e) => {
    e.preventDefault();
    const res = await authFetch("/api/employers/profile", {
      method: "PUT",
      body: JSON.stringify(employerProfileForm)
    });
    if (res.ok) {
      addToast("Company profile saved successfully!");
      const meRes = await authFetch("/api/auth/me");
      if (meRes.ok) {
        const u = await meRes.json();
        setUser(u);
        localStorage.setItem("user", JSON.stringify(u));
      }
    } else {
      addToast("Failed to update company profile", "error");
    }
  };

  // Role booleans
  const isEmployer = user?.role === "RECRUITER" || user?.role === "EMPLOYER";
  const isAdmin = user?.role === "ADMIN";
  const isStudent = user?.role === "STUDENT";

  // Filtered jobs by active employer
  const employerJobs = isEmployer && user?.recruiter_profile?.company_name
    ? jobs.filter((j) => j.company === user.recruiter_profile.company_name || j.recruiter_id === user.recruiter_profile.id)
    : [];

  return (
    <>
      {/* TOAST ALERTS STACK */}
      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className={`toast-item toast-${t.type}`}>
            <span>{t.message}</span>
            <button className="toast-close" onClick={() => removeToast(t.id)}>×</button>
          </div>
        ))}
      </div>

      {route === "/" ? (
        <EditorialHomepage
          jobs={jobs}
          navigate={navigate}
          user={user}
          setAuthModalMode={setAuthModalMode}
          setAuthRole={setAuthRole}
          setApplyModalJob={handleApplyClick}
          toggleSaveJob={toggleSaveJob}
          setSelectedCategory={setSelectedCategory}
          logout={logout}
          unreadCount={unreadCount}
        />
      ) : (
        <div className="page-wrapper">
          <div className="cream-container" style={{ minHeight: "88vh" }}>
            {/* SITE NAVIGATION */}
            <nav className="site-nav">
              <div className="nav-brand" onClick={() => navigate("/")}>
                <span className="brand-text">PartTime</span>
                <span className="brand-sparkle">✦</span>
              </div>

              <div className="nav-center">
                <button className={`nav-link ${route === "/" ? "active" : ""}`} onClick={() => navigate("/")}>
                  Home
                </button>
                <button
                  className="nav-link"
                  onClick={() => {
                    navigate("/");
                    setTimeout(() => {
                      const el = document.getElementById("how-it-works");
                      if (el) el.scrollIntoView({ behavior: "smooth" });
                    }, 200);
                  }}
                >
                  How It Works
                </button>

                {isEmployer ? (
                  <button className={`nav-link ${route === "/post-job" ? "active" : ""}`} onClick={() => navigate("/post-job")}>
                    Add Jobs
                  </button>
                ) : (
                  <button className={`nav-link ${route === "/find-jobs" ? "active" : ""}`} onClick={() => navigate("/find-jobs")}>
                    Find Jobs
                  </button>
                )}

                <button className={`nav-link ${route === "/about" ? "active" : ""}`} onClick={() => navigate("/about")}>
                  About
                </button>

                {isStudent && (
                  <>
                    <button className={`nav-link ${route === "/dashboard" ? "active" : ""}`} onClick={() => navigate("/dashboard")}>
                      Dashboard
                    </button>
                    <button className={`nav-link ${route === "/saved-jobs" ? "active" : ""}`} onClick={() => navigate("/saved-jobs")}>
                      Saved ({savedJobs.length})
                    </button>
                    <button className={`nav-link ${route === "/my-applications" ? "active" : ""}`} onClick={() => navigate("/my-applications")}>
                      Applications ({applications.length})
                    </button>
                  </>
                )}

                {isEmployer && (
                  <button className={`nav-link ${route === "/employer-dashboard" ? "active" : ""}`} onClick={() => navigate("/employer-dashboard")}>
                    Recruiter Dashboard
                  </button>
                )}

                {isAdmin && (
                  <button className={`nav-link ${route === "/admin" ? "active" : ""}`} onClick={() => navigate("/admin")}>
                    Admin Dashboard
                  </button>
                )}
              </div>

              <div className="nav-right">
                <div className="ws-indicator" title={`Live connection: ${wsStatus}`}>
                  <span className={`ws-dot ${wsStatus === "Live" ? "live" : "offline"}`} />
                  <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{wsStatus}</span>
                </div>

                {user ? (
                  <>
                    <button className="nav-link" onClick={() => navigate("/notifications")} style={{ position: "relative" }}>
                      🔔 Notifications
                      {unreadCount > 0 && (
                        <span style={{
                          background: "var(--coral)", color: "white", borderRadius: "10px",
                          padding: "1px 6px", fontSize: 10, marginLeft: 4, fontWeight: 700
                        }}>
                          {unreadCount}
                        </span>
                      )}
                    </button>
                    <button className="btn-coral-pill" onClick={logout} style={{ padding: "8px 18px", fontSize: 13 }}>
                      Sign Out
                    </button>
                  </>
                ) : (
                  <>
                    <button className="btn-ghost-dark" onClick={() => setAuthModalMode("login")}>
                      Login
                    </button>
                    <button className="btn-coral-pill" onClick={() => setAuthModalMode("register")}>
                      Get Started
                    </button>
                  </>
                )}
              </div>
            </nav>

            {/* USER GREETING BANNER */}
            {user && (
              <div style={{
                marginBottom: 24, padding: "16px 22px", background: "white",
                borderRadius: 16, border: "1px solid var(--border-cream)",
                display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12
              }}>
                <div>
                  <h2 style={{ fontFamily: "var(--font-serif)", margin: "0 0 4px", fontSize: 22, color: "var(--text-dark)" }}>
                    Welcome back, {user.name}!
                  </h2>
                  <p style={{ margin: 0, fontSize: 13.5, color: "var(--text-muted)" }}>
                    {isStudent && "Find flexible part-time work that fits your college schedule and earn hourly wages."}
                    {isEmployer && `Managing student recruitment for ${user.recruiter_profile?.company_name || "your organization"}.`}
                    {isAdmin && "Platform administration, job moderation, and user management oversight."}
                  </p>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{
                    background: isStudent ? "#e0edfb" : isEmployer ? "#e1f3e7" : "#fee2e2",
                    color: isStudent ? "#1e40af" : isEmployer ? "#166534" : "#991b1b",
                    fontWeight: 700, padding: "4px 12px", borderRadius: 8, fontSize: 12
                  }}>
                    {user.role === "RECRUITER" ? "EMPLOYER" : user.role}
                  </span>
                </div>
              </div>
            )}

            {/* VIEW: STUDENT DASHBOARD */}
            {route === "/dashboard" && isStudent && (
              <div>
                {/* PENDING APPROVAL ALERT */}
                {user?.is_approved === false && (
                  <div style={{
                    marginBottom: 20, padding: "16px 20px", borderRadius: 14,
                    background: "#fef3c7", border: "1px solid #fde68a", color: "#92400e",
                    display: "flex", alignItems: "center", gap: 14
                  }}>
                    <span style={{ fontSize: 24 }}>⏳</span>
                    <div>
                      <strong style={{ fontSize: 15 }}>Student Account Pending Admin Approval</strong>
                      <p style={{ margin: "3px 0 0", fontSize: 13, color: "#78350f" }}>
                        Your registration has been submitted and is awaiting administrator verification. Once accepted by the admin, you will be able to apply for jobs and book shifts.
                      </p>
                    </div>
                  </div>
                )}

                {/* STATS OVERVIEW */}
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-header">
                      <span className="stat-label">Available Gigs</span>
                      <span className="stat-icon">💼</span>
                    </div>
                    <span className="stat-value">{jobs.length}</span>
                    <span className="stat-meta">Active student openings</span>
                  </div>

                  <div className="stat-card">
                    <div className="stat-header">
                      <span className="stat-label">My Applications</span>
                      <span className="stat-icon">📄</span>
                    </div>
                    <span className="stat-value">{applications.length}</span>
                    <span className="stat-meta">Candidate reviews in pipeline</span>
                  </div>

                  <div className="stat-card">
                    <div className="stat-header">
                      <span className="stat-label">Saved Jobs</span>
                      <span className="stat-icon">⭐</span>
                    </div>
                    <span className="stat-value">{savedJobs.length}</span>
                    <span className="stat-meta">Bookmarked opportunities</span>
                  </div>

                  <div className="stat-card">
                    <div className="stat-header">
                      <span className="stat-label">Interviews / Shifts</span>
                      <span className="stat-icon">⏰</span>
                    </div>
                    <span className="stat-value">{interviews.length + shifts.filter((s) => s.status === "SCHEDULED").length}</span>
                    <span className="stat-meta">Upcoming commitments</span>
                  </div>
                </div>

                {/* TWO-COLUMN DASHBOARD */}
                <div className="dashboard-layout">
                  {/* MAIN COLUMN */}
                  <div className="main-column">
                    {/* SAVED JOBS HIGHLIGHT SECTION */}
                    <div className="card" style={{ borderLeft: "4px solid var(--coral)" }}>
                      <div className="card-title">
                        <span>⭐ Bookmarked & Saved Gigs ({savedJobs.length})</span>
                        <button className="btn btn-outline btn-sm" onClick={() => navigate("/saved-jobs")}>
                          View Full List →
                        </button>
                      </div>

                      {savedJobs.length === 0 ? (
                        <div style={{ padding: "16px 8px", color: "#64748b", fontSize: 13.5 }}>
                          <p style={{ margin: 0 }}>
                            You have not saved any jobs yet. Browse <a href="#find-jobs" onClick={(e) => { e.preventDefault(); navigate("/find-jobs"); }} style={{ color: "var(--coral)", fontWeight: 600 }}>Find Jobs</a> and click <strong>☆ Save</strong> on any gig to bookmark it here on your dashboard!
                          </p>
                        </div>
                      ) : (
                        <div className="jobs-list" style={{ gap: 14 }}>
                          {savedJobs.slice(0, 3).map((item) => (
                            <div className="job-card" key={item.id} style={{ padding: "14px 18px" }}>
                              <div className="job-header" style={{ marginBottom: 8 }}>
                                <div>
                                  <h4 style={{ margin: 0, fontSize: 16, color: "var(--text-dark)" }}>{item.job?.title || item.job_title}</h4>
                                  <div style={{ fontSize: 12.5, color: "#64748b", marginTop: 2 }}>
                                    🏢 {item.job?.company || item.company} • 📍 {item.job?.location || item.location}
                                  </div>
                                </div>
                                <span className="badge badge-pay" style={{ fontSize: 11 }}>💰 {item.job?.pay_rate || item.job?.salary || item.salary}</span>
                              </div>
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 8 }}>
                                <span style={{ fontSize: 11.5, color: "#94a3b8" }}>
                                  Saved {new Date(item.saved_at).toLocaleDateString()}
                                </span>
                                <div style={{ display: "flex", gap: 8 }}>
                                  <button
                                    className="btn btn-sm btn-outline"
                                    onClick={() => toggleSaveJob(item.job_id, true)}
                                    style={{ fontSize: 11.5, padding: "3px 8px" }}
                                  >
                                    Remove
                                  </button>
                                  <button
                                    className="btn btn-sm btn-primary"
                                    onClick={() => {
                                      const matchedJob = jobs.find((j) => j.id === item.job_id);
                                      if (matchedJob) handleApplyClick(matchedJob);
                                      else navigate("/find-jobs");
                                    }}
                                    style={{ fontSize: 11.5, padding: "3px 10px" }}
                                  >
                                    Apply Now
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="card">
                      <div className="card-title">
                        <span>Recommended Gigs for You</span>
                        <button className="btn btn-outline btn-sm" onClick={() => navigate("/find-jobs")}>
                          View All ({jobs.length}) →
                        </button>
                      </div>

                      <div className="jobs-list">
                        {jobs.slice(0, 4).map((job) => (
                          <div className="job-card" key={job.id}>
                            <div className="job-header">
                              <div>
                                <div className="job-title-row">
                                  <h3 className="job-title">{job.title}</h3>
                                  {job.is_employer_verified && (
                                    <span className="verified-badge">✓ Verified</span>
                                  )}
                                </div>
                                <div className="employer-name">
                                  🏢 {job.company} • 📍 {job.location}
                                </div>
                              </div>

                              {job.match_percentage !== null && (
                                <span className={`match-pill ${job.match_percentage >= 70 ? "match-high" : job.match_percentage >= 40 ? "match-mid" : "match-low"}`}>
                                  {job.match_percentage}% Match
                                </span>
                              )}
                            </div>

                            <div className="job-badges">
                              <span className="badge badge-pay">💰 {job.pay_rate || job.salary}</span>
                              <span className="badge badge-hours">⏱️ {job.weekly_hours}</span>
                              <span className="badge badge-shift">📅 {job.shift_schedule}</span>
                              <span className="badge badge-arrangement">🌐 {job.work_arrangement}</span>
                            </div>

                            <p className="job-desc">{job.description}</p>

                            <div className="skills-pill-group">
                              {(job.skills || []).map((skill) => {
                                const isMatched = job.matched_skills && job.matched_skills.includes(skill);
                                return (
                                  <span key={skill} className={`skill-pill ${isMatched ? "matched" : ""}`}>
                                    {isMatched ? "✓ " : ""}{skill}
                                  </span>
                                );
                              })}
                            </div>

                            <div className="job-footer">
                              <span className="job-meta-date">Posted {new Date(job.created_at).toLocaleDateString()}</span>
                              <div className="job-actions">
                                <button
                                  className={`btn btn-sm btn-save ${job.is_saved ? "saved" : ""}`}
                                  onClick={() => toggleSaveJob(job.id, job.is_saved)}
                                >
                                  {job.is_saved ? "★ Saved" : "☆ Save"}
                                </button>
                                <button className="btn btn-sm btn-outline" onClick={() => setSelectedJobDetails(job)}>
                                  Details
                                </button>
                                <button className="btn btn-sm btn-primary" onClick={() => handleApplyClick(job)}>
                                  Apply Now
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* SIDE COLUMN */}
                  <div className="side-column">
                    {/* UPCOMING INTERVIEWS */}
                    <div className="card">
                      <div className="card-title">
                        <span>Upcoming Interviews</span>
                        <span className="badge" style={{ background: "#e0edfb", color: "#1e40af" }}>🗓️ Rounds</span>
                      </div>

                      {interviews.length === 0 ? (
                        <div className="empty-state" style={{ padding: "20px 10px" }}>
                          <div className="empty-icon">🗓️</div>
                          <h4 style={{ fontSize: 16 }}>No upcoming interviews</h4>
                          <p style={{ fontSize: 12 }}>Interview invitations will appear with direct meeting links.</p>
                        </div>
                      ) : (
                        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                          {interviews.map((iv) => (
                            <div key={iv.id} style={{ padding: 12, borderRadius: 10, background: "#f8fafc", border: "1px solid #e2e8f0" }}>
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                <strong style={{ fontSize: 13, color: "var(--text-dark)" }}>{iv.job_title}</strong>
                                <span className="badge badge-category">{iv.status}</span>
                              </div>
                              <p style={{ margin: "4px 0", fontSize: 12, color: "#64748b" }}>
                                📅 {new Date(iv.scheduled_at).toLocaleString()} • {iv.mode}
                              </p>
                              {iv.meeting_link && (
                                <a
                                  href={iv.meeting_link}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="btn btn-sm btn-primary"
                                  style={{ marginTop: 6, display: "inline-flex", padding: "4px 10px", fontSize: 11 }}
                                >
                                  Join Video Call ↗
                                </a>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* UPCOMING SHIFTS */}
                    <div className="card">
                      <div className="card-title">
                        <span>Work Shifts</span>
                        <span className="badge badge-shift">📅 Schedule</span>
                      </div>

                      {shifts.filter((s) => s.status === "SCHEDULED").length === 0 ? (
                        <div className="empty-state" style={{ padding: "20px 10px" }}>
                          <div className="empty-icon">⏰</div>
                          <h4 style={{ fontSize: 16 }}>No shifts scheduled</h4>
                          <p style={{ fontSize: 12 }}>Confirmed hours from employers will appear here.</p>
                        </div>
                      ) : (
                        <div>
                          {shifts.filter((s) => s.status === "SCHEDULED").slice(0, 3).map((shift) => (
                            <div className="shift-item" key={shift.id}>
                              <div className="shift-info">
                                <h5>{shift.job_title}</h5>
                                <p>🗓️ {new Date(shift.shift_date).toLocaleDateString()} • {shift.start_time} - {shift.end_time}</p>
                                <p style={{ color: "#2563eb", fontSize: 11 }}>📍 {shift.location}</p>
                              </div>
                              <button
                                className="btn btn-sm btn-outline"
                                onClick={() => {
                                  authFetch(`/api/shifts/${shift.id}/complete`, { method: "POST" })
                                    .then(() => {
                                      addToast("Shift marked completed!");
                                      loadUserData();
                                    });
                                }}
                              >
                                Complete
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* LIVE EVENT STREAM */}
                    <div className="card">
                      <div className="card-title">
                        <span>Live Activity Feed</span>
                        <span className="ws-indicator">
                          <span className="ws-dot live" /> Live
                        </span>
                      </div>
                      {events.length === 0 ? (
                        <p style={{ color: "#94a3b8", fontSize: 12, textAlign: "center" }}>
                          Listening for real-time gig and application events...
                        </p>
                      ) : (
                        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                          {events.slice(0, 5).map((e, idx) => (
                            <div key={idx} style={{ fontSize: 12, padding: "8px 10px", background: "#f8fafc", borderRadius: 8, border: "1px solid #e2e8f0" }}>
                              <span style={{ color: "var(--coral)", fontWeight: 700 }}>[{e.type}]</span> {e.message}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* VIEW: ABOUT PAGE & PLACEMENT DASHBOARD */}
            {route === "/about" && (
              <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
                {/* HERO BANNER */}
                <div className="card" style={{
                  background: "linear-gradient(135deg, #123F36 0%, #1A5448 100%)",
                  color: "white", padding: "36px 32px", border: "none"
                }}>
                  <div style={{ maxWidth: 800 }}>
                    <span style={{
                      display: "inline-block", padding: "4px 12px", borderRadius: 20,
                      background: "rgba(255, 122, 89, 0.2)", color: "var(--coral)",
                      fontSize: 12, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase", marginBottom: 12
                    }}>
                      About PartTime Platform
                    </span>
                    <h1 style={{
                      fontFamily: "var(--font-serif)", fontSize: 34, margin: "0 0 12px",
                      color: "white", lineHeight: 1.2
                    }}>
                      Bridging Academics with High-Value Practical Work
                    </h1>
                    <p style={{ fontSize: 16, color: "#D1E3DC", lineHeight: 1.6, margin: "0 0 24px" }}>
                      PartTime is the modern student gig and placement ecosystem connecting college talent with pre-vetted employers. Our platform enables students to earn competitive hourly wages without compromising exam preparation or attendance.
                    </p>
                    <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                      <button className="btn-coral-pill" onClick={() => navigate("/find-jobs")} style={{ padding: "10px 22px", fontSize: 14 }}>
                        Explore Gigs ({jobs.length}) →
                      </button>
                      {user?.role === "RECRUITER" || user?.role === "EMPLOYER" ? (
                        <button className="btn btn-outline" onClick={() => navigate("/post-job")} style={{ background: "white", color: "#123F36", fontWeight: 700 }}>
                          + Post a Gig Listing
                        </button>
                      ) : (
                        <a href="#how-it-works" onClick={() => {
                          navigate("/");
                          setTimeout(() => {
                            const el = document.getElementById("how-it-works");
                            if (el) el.scrollIntoView({ behavior: "smooth" });
                          }, 200);
                        }} className="btn btn-outline" style={{ background: "rgba(255,255,255,0.1)", color: "white", border: "1px solid rgba(255,255,255,0.3)" }}>
                          How It Works
                        </a>
                      )}
                    </div>
                  </div>
                </div>

                {/* PLACEMENT & HIRING DASHBOARD */}
                <div>
                  <div style={{ marginBottom: 14 }}>
                    <h2 style={{ fontFamily: "var(--font-serif)", fontSize: 24, margin: "0 0 4px", color: "var(--text-dark)" }}>
                      Student Placement & Earnings Dashboard
                    </h2>
                    <p style={{ margin: 0, fontSize: 13.5, color: "var(--text-muted)" }}>
                      Real-time impact metrics and verified statistics of students currently working and placed through PartTime.
                    </p>
                  </div>

                  <div className="stats-grid">
                    <div className="stat-card" style={{ borderTop: "4px solid var(--coral)" }}>
                      <span className="stat-label">Students Placed</span>
                      <span className="stat-value">1,420+</span>
                      <span className="stat-meta">Active student gig placements</span>
                    </div>

                    <div className="stat-card" style={{ borderTop: "4px solid #10b981" }}>
                      <span className="stat-label">Disbursed Earnings</span>
                      <span className="stat-value">₹4.8 Lakhs+</span>
                      <span className="stat-meta">Direct hourly wages paid out</span>
                    </div>

                    <div className="stat-card" style={{ borderTop: "4px solid #3b82f6" }}>
                      <span className="stat-label">Verified Employers</span>
                      <span className="stat-value">280+</span>
                      <span className="stat-meta">Active startups & institutions</span>
                    </div>

                    <div className="stat-card" style={{ borderTop: "4px solid #8b5cf6" }}>
                      <span className="stat-label">Safety & Pay Rating</span>
                      <span className="stat-value">98.6%</span>
                      <span className="stat-meta">Verified zero-scam compliance</span>
                    </div>
                  </div>
                </div>

                {/* DOMAIN BREAKDOWN & HOURLY RATES */}
                <div className="card">
                  <div className="card-title">
                    <span>Placement Domain Breakdown & Average Hourly Pay</span>
                    <span className="badge" style={{ background: "#e0edfb", color: "#1e40af" }}>
                      FY 2026 Metrics
                    </span>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
                    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                      <div>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13.5, marginBottom: 5 }}>
                          <strong>💻 Web & Software Development</strong>
                          <span style={{ fontWeight: 700, color: "var(--coral)" }}>42% • ₹350 - ₹600/hr</span>
                        </div>
                        <div style={{ height: 10, background: "#f1f5f9", borderRadius: 6, overflow: "hidden" }}>
                          <div style={{ width: "42%", height: "100%", background: "var(--coral)", borderRadius: 6 }} />
                        </div>
                      </div>

                      <div>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13.5, marginBottom: 5 }}>
                          <strong>🎬 Video Editing & Motion Graphics</strong>
                          <span style={{ fontWeight: 700, color: "#10b981" }}>24% • ₹300 - ₹500/hr</span>
                        </div>
                        <div style={{ height: 10, background: "#f1f5f9", borderRadius: 6, overflow: "hidden" }}>
                          <div style={{ width: "24%", height: "100%", background: "#10b981", borderRadius: 6 }} />
                        </div>
                      </div>

                      <div>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13.5, marginBottom: 5 }}>
                          <strong>📚 Academic & Peer Tutoring</strong>
                          <span style={{ fontWeight: 700, color: "#3b82f6" }}>18% • ₹250 - ₹450/hr</span>
                        </div>
                        <div style={{ height: 10, background: "#f1f5f9", borderRadius: 6, overflow: "hidden" }}>
                          <div style={{ width: "18%", height: "100%", background: "#3b82f6", borderRadius: 6 }} />
                        </div>
                      </div>

                      <div>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13.5, marginBottom: 5 }}>
                          <strong>✍️ Content Writing & Social Media</strong>
                          <span style={{ fontWeight: 700, color: "#8b5cf6" }}>11% • ₹200 - ₹350/hr</span>
                        </div>
                        <div style={{ height: 10, background: "#f1f5f9", borderRadius: 6, overflow: "hidden" }}>
                          <div style={{ width: "11%", height: "100%", background: "#8b5cf6", borderRadius: 6 }} />
                        </div>
                      </div>

                      <div>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13.5, marginBottom: 5 }}>
                          <strong>📦 Campus Operations & Logistics</strong>
                          <span style={{ fontWeight: 700, color: "#f59e0b" }}>5% • ₹180 - ₹300/hr</span>
                        </div>
                        <div style={{ height: 10, background: "#f1f5f9", borderRadius: 6, overflow: "hidden" }}>
                          <div style={{ width: "5%", height: "100%", background: "#f59e0b", borderRadius: 6 }} />
                        </div>
                      </div>
                    </div>

                    <div style={{ background: "#f8fafc", padding: 20, borderRadius: 14, border: "1px solid #e2e8f0" }}>
                      <h4 style={{ margin: "0 0 10px", fontSize: 16, color: "var(--text-dark)" }}>
                        💡 Why Top Universities Partner With Us
                      </h4>
                      <ul style={{ margin: 0, paddingLeft: 18, color: "#475569", fontSize: 13.5, lineHeight: 1.7 }}>
                        <li><strong>Zero Upfront Fees:</strong> Free registration for verified students across all partner colleges.</li>
                        <li><strong>Safe Work Environments:</strong> Strict employer identity verification and continuous rating audits.</li>
                        <li><strong>Shift Management:</strong> Direct integration with student calendars so commitments never clash with exams.</li>
                        <li><strong>Experience Letters:</strong> Official verifiable completion letters for all successful shifts.</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* SUCCESS STORIES SECTION */}
                <div className="card">
                  <div className="card-title">
                    <span>Recent Student Placement Highlights</span>
                    <span className="badge badge-shift">Verified Hires</span>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
                    <div style={{ padding: 18, borderRadius: 14, background: "#f8fafc", border: "1px solid #e2e8f0" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
                        <div style={{ width: 42, height: 42, borderRadius: "50%", background: "var(--coral)", color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700 }}>
                          PS
                        </div>
                        <div>
                          <strong style={{ fontSize: 15, color: "var(--text-dark)" }}>Priya Sharma</strong>
                          <div style={{ fontSize: 12, color: "#64748b" }}>BITS Pilani • CSE (3rd Year)</div>
                        </div>
                      </div>
                      <div style={{ fontSize: 13, color: "#334155", marginBottom: 8 }}>
                        Placed as <strong>Frontend Assistant</strong> at <em>TechNova Solutions</em> (₹350/hr).
                      </div>
                      <p style={{ margin: 0, fontSize: 12.5, color: "#64748b", fontStyle: "italic" }}>
                        "Working 12 hours a week gave me real production React experience while fully financing my tech fest travels."
                      </p>
                    </div>

                    <div style={{ padding: 18, borderRadius: 14, background: "#f8fafc", border: "1px solid #e2e8f0" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
                        <div style={{ width: 42, height: 42, borderRadius: "50%", background: "#10b981", color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700 }}>
                          DH
                        </div>
                        <div>
                          <strong style={{ fontSize: 15, color: "var(--text-dark)" }}>Dhanush</strong>
                          <div style={{ fontSize: 12, color: "#64748b" }}>NIT Trichy • B.Tech (2nd Year)</div>
                        </div>
                      </div>
                      <div style={{ fontSize: 13, color: "#334155", marginBottom: 8 }}>
                        Placed as <strong>Online Python Tutor</strong> at <em>ABC Technologies</em> (₹300/hr).
                      </div>
                      <p style={{ margin: 0, fontSize: 12.5, color: "#64748b", fontStyle: "italic" }}>
                        "The booking system is seamless. I take evening tutoring sessions from my hostel room without missing any classes."
                      </p>
                    </div>

                    <div style={{ padding: 18, borderRadius: 14, background: "#f8fafc", border: "1px solid #e2e8f0" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
                        <div style={{ width: 42, height: 42, borderRadius: "50%", background: "#8b5cf6", color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700 }}>
                          SP
                        </div>
                        <div>
                          <strong style={{ fontSize: 15, color: "var(--text-dark)" }}>Sneha Patel</strong>
                          <div style={{ fontSize: 12, color: "#64748b" }}>IIT Madras • Electrical (Final Year)</div>
                        </div>
                      </div>
                      <div style={{ fontSize: 13, color: "#334155", marginBottom: 8 }}>
                        Placed as <strong>Motion Video Editor</strong> at <em>PixelPulse Studios</em> (₹400/hr).
                      </div>
                      <p style={{ margin: 0, fontSize: 12.5, color: "#64748b", fontStyle: "italic" }}>
                        "Built a creative commercial portfolio for leading agencies. Payouts arrive directly via UPI on time every weekend."
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* VIEW: FIND JOBS */}
            {route === "/find-jobs" && (
              <div>
                {/* SEARCH & FILTERS PANEL */}
                <div className="filter-card">
                  <div className="filter-grid">
                    <div className="search-input-wrap">
                      <span className="search-icon-pos">🔍</span>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Search by title, skills, employer..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                    </div>

                    <div>
                      <select
                        className="form-control"
                        value={selectedCategory}
                        onChange={(e) => setSelectedCategory(e.target.value)}
                      >
                        <option value="All">All Categories</option>
                        {CATEGORIES.filter((c) => c !== "All").map((cat) => (
                          <option key={cat} value={cat}>{cat}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <select
                        className="form-control"
                        value={selectedArrangement}
                        onChange={(e) => setSelectedArrangement(e.target.value)}
                      >
                        <option value="All">All Arrangements</option>
                        <option value="Remote">Remote</option>
                        <option value="Hybrid">Hybrid</option>
                        <option value="On-site">On-site</option>
                      </select>
                    </div>

                    <div>
                      <select
                        className="form-control"
                        value={selectedShift}
                        onChange={(e) => setSelectedShift(e.target.value)}
                      >
                        <option value="All">All Shifts</option>
                        <option value="Flexible">Flexible Shifts</option>
                        <option value="Weekdays">Weekdays</option>
                        <option value="Weekends">Weekends</option>
                        <option value="Evenings">Evenings</option>
                      </select>
                    </div>

                    <div>
                      <select
                        className="form-control"
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                      >
                        <option value="newest">Sort: Newest</option>
                        <option value="pay">Sort: Highest Pay</option>
                        {isStudent && <option value="relevance">Sort: Skill Match</option>}
                      </select>
                    </div>
                  </div>
                </div>

                {/* RESULTS HEADER */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
                  <h3 style={{ fontFamily: "var(--font-serif)", margin: 0, fontSize: 22, color: "var(--text-dark)" }}>
                    Available Gigs ({jobs.length})
                  </h3>
                  {(searchQuery || selectedCategory !== "All" || selectedArrangement !== "All" || selectedShift !== "All") && (
                    <button
                      className="btn btn-sm btn-outline"
                      onClick={() => {
                        setSearchQuery("");
                        setSelectedCategory("All");
                        setSelectedArrangement("All");
                        setSelectedShift("All");
                      }}
                    >
                      Clear All Filters ✕
                    </button>
                  )}
                </div>

                {/* JOBS LISTING */}
                {jobs.length === 0 ? (
                  <div className="card">
                    <div className="empty-state">
                      <div className="empty-icon">🔍</div>
                      <h4>No jobs matched your filters</h4>
                      <p>Try searching with broader terms or removing filter restrictions.</p>
                      <button
                        className="btn btn-primary"
                        onClick={() => {
                          setSearchQuery("");
                          setSelectedCategory("All");
                          setSelectedArrangement("All");
                          setSelectedShift("All");
                        }}
                      >
                        Reset All Filters
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="jobs-list">
                    {jobs.map((job) => (
                      <div className="job-card" key={job.id}>
                        <div className="job-header">
                          <div>
                            <div className="job-title-row">
                              <h3 className="job-title">{job.title}</h3>
                              {job.is_employer_verified && (
                                <span className="verified-badge">✓ Verified Employer</span>
                              )}
                            </div>
                            <div className="employer-name">
                              🏢 {job.company} • 📍 {job.location} • 🏷️ {job.category}
                            </div>
                          </div>

                          {job.match_percentage !== null && (
                            <span className={`match-pill ${job.match_percentage >= 70 ? "match-high" : job.match_percentage >= 40 ? "match-mid" : "match-low"}`}>
                              {job.match_percentage}% Match
                            </span>
                          )}
                        </div>

                        <div className="job-badges">
                          <span className="badge badge-pay">💰 {job.pay_rate || job.salary}</span>
                          <span className="badge badge-hours">⏱️ {job.weekly_hours}</span>
                          <span className="badge badge-shift">📅 {job.shift_schedule}</span>
                          <span className="badge badge-arrangement">🌐 {job.work_arrangement}</span>
                          <span className="badge badge-category">💼 {job.job_type}</span>
                        </div>

                        <p className="job-desc">{job.description}</p>

                        <div className="skills-pill-group">
                          {(job.skills || []).map((skill) => {
                            const isMatched = job.matched_skills && job.matched_skills.includes(skill);
                            return (
                              <span key={skill} className={`skill-pill ${isMatched ? "matched" : ""}`}>
                                {isMatched ? "✓ " : ""}{skill}
                              </span>
                            );
                          })}
                        </div>

                        <div className="job-footer">
                          <span className="job-meta-date">Posted {new Date(job.created_at).toLocaleDateString()}</span>
                          <div className="job-actions">
                            <button
                              className="btn btn-sm btn-outline"
                              title="Report listing"
                              onClick={() => setReportModalJob(job)}
                            >
                              🚩 Report
                            </button>
                            <button
                              className={`btn btn-sm btn-save ${job.is_saved ? "saved" : ""}`}
                              onClick={() => toggleSaveJob(job.id, job.is_saved)}
                            >
                              {job.is_saved ? "★ Saved" : "☆ Save"}
                            </button>
                            <button className="btn btn-sm btn-outline" onClick={() => setSelectedJobDetails(job)}>
                              Details
                            </button>
                            <button className="btn btn-sm btn-primary" onClick={() => handleApplyClick(job)}>
                              Apply Now
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* VIEW: SAVED JOBS */}
            {route === "/saved-jobs" && isStudent && (
              <div className="card">
                <div className="card-title">
                  <span>My Saved Opportunities ({savedJobs.length})</span>
                  <button className="btn btn-sm btn-outline" onClick={() => navigate("/find-jobs")}>
                    Browse More Gigs →
                  </button>
                </div>

                {savedJobs.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">⭐</div>
                    <h4>No saved jobs yet</h4>
                    <p>Bookmark interesting part-time roles while browsing to apply later.</p>
                    <button className="btn btn-primary" onClick={() => navigate("/find-jobs")}>
                      Explore Available Gigs
                    </button>
                  </div>
                ) : (
                  <div className="jobs-list">
                    {savedJobs.map((item) => (
                      <div className="job-card" key={item.id}>
                        <div className="job-header">
                          <div>
                            <h3 className="job-title">{item.job?.title || item.job_title}</h3>
                            <div className="employer-name">
                              🏢 {item.job?.company || item.company} • 📍 {item.job?.location || item.location}
                            </div>
                          </div>
                          <span className="badge badge-pay">💰 {item.job?.pay_rate || item.job?.salary || item.pay_rate}</span>
                        </div>

                        <p className="job-desc">{item.description}</p>

                        <div className="job-footer">
                          <span className="job-meta-date">Saved on {new Date(item.saved_at).toLocaleDateString()}</span>
                          <div className="job-actions">
                            <button
                              className="btn btn-sm btn-outline"
                              onClick={() => toggleSaveJob(item.job_id, true)}
                            >
                              Remove Bookmark
                            </button>
                            <button
                              className="btn btn-sm btn-primary"
                              onClick={() => handleApplyClick({ id: item.job_id, title: item.job_title, company: item.company, pay_rate: item.pay_rate })}
                            >
                              Apply Now
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* VIEW: MY APPLICATIONS */}
            {route === "/my-applications" && isStudent && (
              <div className="card">
                <div className="card-title">
                  <span>My Applications History ({applications.length})</span>
                </div>

                {applications.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">📄</div>
                    <h4>No applications submitted yet</h4>
                    <p>Apply for part-time gigs that match your class timetable.</p>
                    <button className="btn btn-primary" onClick={() => navigate("/find-jobs")}>
                      Find Part-Time Work
                    </button>
                  </div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                    {applications.map((app) => (
                      <div key={app.id} style={{
                        border: "1px solid var(--border-cream)", borderRadius: 16,
                        padding: 20, background: "white"
                      }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 10 }}>
                          <div>
                            <h4 style={{ fontFamily: "var(--font-serif)", margin: "0 0 4px", fontSize: 18, color: "var(--text-dark)" }}>
                              {app.job_title}
                            </h4>
                            <p style={{ margin: 0, fontSize: 13, color: "var(--text-muted)" }}>
                              🏢 {app.company} • 📍 {app.location} • Applied {new Date(app.applied_at).toLocaleDateString()}
                            </p>
                          </div>

                          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                            {app.status !== "WITHDRAWN" && app.status !== "REJECTED" && (
                              <button
                                className="btn btn-sm btn-outline"
                                onClick={() => handleWithdraw(app.id)}
                              >
                                Withdraw
                              </button>
                            )}
                          </div>
                        </div>

                        {app.availability && (
                          <div style={{ margin: "12px 0 6px", fontSize: 12.5, color: "#475569" }}>
                            <strong>Submitted Availability:</strong> {app.availability}
                          </div>
                        )}

                        {/* HIRING PIPELINE PROGRESS */}
                        <ApplicationTimeline currentStatus={app.status} />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* VIEW: STUDENT PROFILE */}
            {route === "/profile" && isStudent && (
              <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
                <div className="card">
                  <div className="card-title">
                    <span>Student Profile & Preferences</span>
                    <button
                      className="btn btn-sm btn-primary"
                      onClick={() => setIsEditingProfile(!isEditingProfile)}
                    >
                      {isEditingProfile ? "Cancel Editing" : "✎ Edit Profile"}
                    </button>
                  </div>

                  {isEditingProfile ? (
                    <form onSubmit={handleSaveProfile}>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
                        <div className="form-group">
                          <label>Full Name *</label>
                          <input
                            type="text"
                            className="form-control"
                            value={profileForm.name}
                            onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                            required
                          />
                        </div>

                        <div className="form-group">
                          <label>College / University *</label>
                          <input
                            type="text"
                            className="form-control"
                            value={profileForm.college}
                            onChange={(e) => setProfileForm({ ...profileForm, college: e.target.value })}
                            required
                          />
                        </div>

                        <div className="form-group">
                          <label>Degree (e.g. B.Tech, BCA, B.Sc)</label>
                          <input
                            type="text"
                            className="form-control"
                            value={profileForm.degree}
                            onChange={(e) => setProfileForm({ ...profileForm, degree: e.target.value })}
                          />
                        </div>

                        <div className="form-group">
                          <label>Department / Branch (e.g. Computer Science)</label>
                          <input
                            type="text"
                            className="form-control"
                            value={profileForm.branch}
                            onChange={(e) => setProfileForm({ ...profileForm, branch: e.target.value })}
                          />
                        </div>

                        <div className="form-group">
                          <label>CGPA</label>
                          <input
                            type="number"
                            step="0.01"
                            className="form-control"
                            value={profileForm.cgpa}
                            onChange={(e) => setProfileForm({ ...profileForm, cgpa: e.target.value })}
                          />
                        </div>

                        <div className="form-group">
                          <label>Preferred Work Arrangement</label>
                          <select
                            className="form-control"
                            value={profileForm.preferred_work_arrangement}
                            onChange={(e) => setProfileForm({ ...profileForm, preferred_work_arrangement: e.target.value })}
                          >
                            <option value="Any">Any Arrangement</option>
                            <option value="Remote">Remote Only</option>
                            <option value="Hybrid">Hybrid</option>
                            <option value="On-site">On-site Campus</option>
                          </select>
                        </div>

                        <div className="form-group">
                          <label>Weekly Availability (e.g. 15 hrs/week)</label>
                          <input
                            type="text"
                            className="form-control"
                            value={profileForm.weekly_availability}
                            onChange={(e) => setProfileForm({ ...profileForm, weekly_availability: e.target.value })}
                          />
                        </div>

                        <div className="form-group">
                          <label>Max Weekly Hours (Limit for studies balance)</label>
                          <input
                            type="number"
                            className="form-control"
                            value={profileForm.max_weekly_hours}
                            onChange={(e) => setProfileForm({ ...profileForm, max_weekly_hours: e.target.value })}
                          />
                        </div>
                      </div>

                      <div className="form-group">
                        <label>Background Summary / Experience</label>
                        <textarea
                          className="form-control"
                          rows="3"
                          value={profileForm.experience}
                          onChange={(e) => setProfileForm({ ...profileForm, experience: e.target.value })}
                          placeholder="Brief summary of projects, past campus shifts, or freelancing..."
                        />
                      </div>

                      <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
                        <button type="button" className="btn btn-outline" onClick={() => setIsEditingProfile(false)}>
                          Cancel
                        </button>
                        <button type="submit" className="btn btn-primary">
                          Save Academic Profile
                        </button>
                      </div>
                    </form>
                  ) : (
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
                      <div>
                        <h4 style={{ margin: "0 0 12px", color: "#1e293b" }}>Academic Information</h4>
                        <p><strong>Name:</strong> {user.name}</p>
                        <p><strong>Email:</strong> {user.email}</p>
                        <p><strong>College:</strong> {user.student_profile?.college || "Not set"}</p>
                        <p><strong>Branch / Degree:</strong> {user.student_profile?.branch || "N/A"} ({user.student_profile?.degree || "N/A"})</p>
                        <p><strong>CGPA:</strong> {user.student_profile?.cgpa || "N/A"}</p>
                      </div>

                      <div>
                        <h4 style={{ margin: "0 0 12px", color: "#1e293b" }}>Work Preferences</h4>
                        <p><strong>Weekly Availability:</strong> {user.student_profile?.weekly_availability || "15 hrs/week"}</p>
                        <p><strong>Preferred Arrangement:</strong> {user.student_profile?.preferred_work_arrangement || "Any"}</p>
                        <p><strong>Max Weekly Hours:</strong> {user.student_profile?.max_weekly_hours || 20} hours</p>
                        <p><strong>Experience:</strong> {user.student_profile?.experience || "None specified"}</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* SKILLS MANAGER & RESUME UPLOAD */}
                <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: 24 }}>
                  {/* SKILLS MANAGER */}
                  <div className="card">
                    <div className="card-title">
                      <span>Verified Skills</span>
                    </div>

                    <div className="skills-pill-group" style={{ minHeight: 60 }}>
                      {(user.student_profile?.skills || []).length === 0 ? (
                        <p style={{ color: "#94a3b8", fontSize: 13 }}>No skills added yet. Add below or upload your resume.</p>
                      ) : (
                        (user.student_profile?.skills || []).map((s) => (
                          <span
                            key={s}
                            className="skill-pill matched removable"
                            title="Click × to remove skill"
                            onClick={() => handleRemoveSkill(s)}
                          >
                            ✓ {s} <strong style={{ marginLeft: 4 }}>×</strong>
                          </span>
                        ))
                      )}
                    </div>

                    <form onSubmit={handleAddSkill} style={{ display: "flex", gap: 8, marginTop: 12 }}>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Add skill (e.g. Docker, Python, Figma)..."
                        value={newSkillInput}
                        onChange={(e) => setNewSkillInput(e.target.value)}
                      />
                      <button type="submit" className="btn btn-outline" style={{ whiteSpace: "nowrap" }}>
                        + Add Skill
                      </button>
                    </form>
                  </div>

                  {/* RESUME UPLOAD */}
                  <div className="card">
                    <div className="card-title">
                      <span>PDF Resume & Skill Extractor</span>
                    </div>

                    {user.student_profile?.resume_url && (
                      <div style={{ marginBottom: 14, padding: 10, borderRadius: 8, background: "#f0fdf4", border: "1px solid #bbf7d0" }}>
                        <span style={{ fontSize: 13, color: "#166534", fontWeight: 600 }}>
                          ✓ Current Resume on file:
                        </span>
                        <a
                          href={user.student_profile.resume_url}
                          target="_blank"
                          rel="noreferrer"
                          style={{ marginLeft: 8, fontSize: 13, color: "#2563eb", fontWeight: 700 }}
                        >
                          View Uploaded PDF ↗
                        </a>
                      </div>
                    )}

                    <input
                      type="file"
                      accept=".pdf"
                      className="form-control"
                      onChange={async (e) => {
                        const file = e.target.files[0];
                        if (!file) return;
                        const formData = new FormData();
                        formData.append("file", file);

                        const res = await fetch("/api/students/resume", {
                          method: "POST",
                          headers: { Authorization: `Bearer ${token}` },
                          body: formData
                        });
                        if (res.ok) {
                          const data = await res.json();
                          addToast(`Resume uploaded! Extracted ${data.detected_skills?.length || 0} skills.`);
                          authFetch("/api/auth/me").then((r) => r.json()).then((u) => {
                            setUser(u);
                            localStorage.setItem("user", JSON.stringify(u));
                          });
                        } else {
                          const err = await res.json();
                          addToast(`Error: ${err.detail}`, "error");
                        }
                      }}
                    />
                    <p style={{ fontSize: 12, color: "#64748b", marginTop: 8 }}>
                      Max 5MB PDF. Our local parser extracts technical and soft skills automatically into your profile.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* VIEW: EMPLOYER PORTAL */}
            {route === "/employer-dashboard" && isEmployer && (
              <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                {/* STATS OVERVIEW */}
                <div className="stats-grid">
                  <div className="stat-card">
                    <span className="stat-label">Active Gigs</span>
                    <span className="stat-value">{employerJobs.length}</span>
                    <span className="stat-meta">Active job listings</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-label">Applicants</span>
                    <span className="stat-value">{applications.length}</span>
                    <span className="stat-meta">Submitted reviews</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-label">Interviews</span>
                    <span className="stat-value">{interviews.length}</span>
                    <span className="stat-meta">Scheduled rounds</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-label">Assigned Shifts</span>
                    <span className="stat-value">{shifts.length}</span>
                    <span className="stat-meta">Confirmed student shifts</span>
                  </div>
                </div>

                {/* EMPLOYER TABS */}
                <div className="tab-bar">
                  <button
                    className={`tab-btn ${employerTab === "pipeline" ? "active" : ""}`}
                    onClick={() => setEmployerTab("pipeline")}
                  >
                    Applicants Review <span className="tab-badge">{applications.length}</span>
                  </button>
                  <button
                    className={`tab-btn ${employerTab === "jobs" ? "active" : ""}`}
                    onClick={() => setEmployerTab("jobs")}
                  >
                    My Job Postings <span className="tab-badge">{employerJobs.length}</span>
                  </button>
                  <button
                    className={`tab-btn ${employerTab === "interviews" ? "active" : ""}`}
                    onClick={() => setEmployerTab("interviews")}
                  >
                    Interviews <span className="tab-badge">{interviews.length}</span>
                  </button>
                  <button
                    className={`tab-btn ${employerTab === "profile" ? "active" : ""}`}
                    onClick={() => setEmployerTab("profile")}
                  >
                    Company Profile
                  </button>
                </div>

                {/* TAB 1: APPLICANTS PIPELINE */}
                {employerTab === "pipeline" && (
                  <div className="card">
                    <div className="card-title">
                      <span>Candidate Applicant Pipeline</span>
                      <button className="btn btn-sm btn-primary" onClick={() => navigate("/post-job")}>
                        + Post New Gig
                      </button>
                    </div>

                    {applications.length === 0 ? (
                      <div className="empty-state">
                        <div className="empty-icon">👥</div>
                        <h4>No applicants yet</h4>
                        <p>When students apply to your postings, you can review match scores and schedule interviews here.</p>
                      </div>
                    ) : (
                      <div className="table-responsive">
                        <table>
                          <thead>
                            <tr>
                              <th>Candidate</th>
                              <th>Applied Gig</th>
                              <th>Match Score</th>
                              <th>Availability</th>
                              <th>Status</th>
                              <th>Resume</th>
                              <th>Hiring Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {applications.map((app) => (
                              <tr key={app.id}>
                                <td>
                                  <strong>{app.student_name}</strong>
                                  <div style={{ fontSize: 11, color: "#64748b" }}>
                                    {app.college} • {app.branch}
                                  </div>
                                </td>
                                <td>
                                  <strong>{app.job_title}</strong>
                                </td>
                                <td>
                                  <span className={`match-pill ${app.match_percentage >= 70 ? "match-high" : app.match_percentage >= 40 ? "match-mid" : "match-low"}`}>
                                    {app.match_percentage !== null ? `${app.match_percentage}%` : "80%"}
                                  </span>
                                </td>
                                <td>{app.availability || "Flexible"}</td>
                                <td>
                                  <span className="badge badge-category">{app.status}</span>
                                </td>
                                <td>
                                  {app.resume_url ? (
                                    <a
                                      href={app.resume_url}
                                      target="_blank"
                                      rel="noreferrer"
                                      className="btn btn-sm btn-outline"
                                      style={{ padding: "3px 8px", fontSize: 11 }}
                                    >
                                      View PDF ↗
                                    </a>
                                  ) : (
                                    <span style={{ fontSize: 11, color: "#94a3b8" }}>No file</span>
                                  )}
                                </td>
                                <td>
                                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                                    <button
                                      className="btn btn-sm btn-outline"
                                      style={{ borderColor: "#2563eb", color: "#2563eb", fontWeight: 600 }}
                                      onClick={() => setInterviewModalApp(app)}
                                      title="Accept candidate application and send interview schedule"
                                    >
                                      🗓️ Accept & Schedule
                                    </button>
                                    <button
                                      className="btn btn-sm btn-primary"
                                      onClick={async () => {
                                        await authFetch(`/api/applications/${app.id}`, {
                                          method: "PATCH",
                                          body: JSON.stringify({ status: "SHORTLISTED" })
                                        });
                                        addToast("Candidate shortlisted!");
                                        loadUserData();
                                      }}
                                    >
                                      Shortlist
                                    </button>
                                    <button
                                      className="btn btn-sm btn-secondary"
                                      onClick={async () => {
                                        await authFetch(`/api/applications/${app.id}`, {
                                          method: "PATCH",
                                          body: JSON.stringify({ status: "OFFERED" })
                                        });
                                        addToast("Job offer sent!");
                                        loadUserData();
                                      }}
                                    >
                                      Offer
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}

                {/* TAB 2: MY JOB POSTINGS */}
                {employerTab === "jobs" && (
                  <div className="card">
                    <div className="card-title">
                      <span>My Job Postings</span>
                      <button className="btn btn-sm btn-primary" onClick={() => navigate("/post-job")}>
                        + Post Another Gig
                      </button>
                    </div>

                    {employerJobs.length === 0 ? (
                      <div className="empty-state">
                        <div className="empty-icon">💼</div>
                        <h4>No job postings active</h4>
                        <p>Create your first student part-time gig listing.</p>
                        <button className="btn btn-primary" onClick={() => navigate("/post-job")}>
                          + Post a Gig Now
                        </button>
                      </div>
                    ) : (
                      <div className="table-responsive">
                        <table>
                          <thead>
                            <tr>
                              <th>Gig Title</th>
                              <th>Category</th>
                              <th>Pay Rate</th>
                              <th>Arrangement</th>
                              <th>Status</th>
                              <th>Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {employerJobs.map((j) => (
                              <tr key={j.id}>
                                <td><strong>{j.title}</strong></td>
                                <td>{j.category}</td>
                                <td><span className="badge badge-pay">{j.pay_rate}</span></td>
                                <td>{j.work_arrangement}</td>
                                <td>
                                  <span className={`badge ${j.status === "ACTIVE" ? "badge-pay" : "badge-hours"}`}>
                                    {j.status}
                                  </span>
                                </td>
                                <td>
                                  <div style={{ display: "flex", gap: 6 }}>
                                    <button
                                      className="btn btn-sm btn-outline"
                                      onClick={async () => {
                                        const nextStatus = j.status === "ACTIVE" ? "PAUSED" : "ACTIVE";
                                        await authFetch(`/api/jobs/${j.id}/status?status_str=${nextStatus}`, { method: "PATCH" });
                                        addToast(`Listing status updated to ${nextStatus}`);
                                        loadJobs();
                                      }}
                                    >
                                      {j.status === "ACTIVE" ? "Pause" : "Activate"}
                                    </button>
                                    <button
                                      className="btn btn-sm btn-danger"
                                      onClick={() => {
                                        setConfirmDialog({
                                          title: "Delete Job Listing",
                                          message: `Are you sure you want to delete '${j.title}'?`,
                                          onConfirm: async () => {
                                            await authFetch(`/api/jobs/${j.id}`, { method: "DELETE" });
                                            addToast("Job listing deleted");
                                            setConfirmDialog(null);
                                            loadJobs();
                                          }
                                        });
                                      }}
                                    >
                                      Delete
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}

                {/* TAB 3: INTERVIEW MANAGEMENT */}
                {employerTab === "interviews" && (
                  <div className="card">
                    <div className="card-title">
                      <span>Scheduled Interviews</span>
                    </div>

                    {interviews.length === 0 ? (
                      <div className="empty-state">
                        <div className="empty-icon">🗓️</div>
                        <h4>No interviews scheduled</h4>
                        <p>Go to the Applicants tab and click "Interview" on an applicant to set up a round.</p>
                      </div>
                    ) : (
                      <div className="table-responsive">
                        <table>
                          <thead>
                            <tr>
                              <th>Candidate</th>
                              <th>Gig</th>
                              <th>Schedule</th>
                              <th>Mode</th>
                              <th>Status</th>
                              <th>Meeting Link</th>
                              <th>Action</th>
                            </tr>
                          </thead>
                          <tbody>
                            {interviews.map((iv) => (
                              <tr key={iv.id}>
                                <td><strong>{iv.student_name}</strong></td>
                                <td>{iv.job_title}</td>
                                <td>{new Date(iv.scheduled_at).toLocaleString()}</td>
                                <td>{iv.mode}</td>
                                <td><span className="badge badge-category">{iv.status}</span></td>
                                <td>
                                  {iv.meeting_link ? (
                                    <a href={iv.meeting_link} target="_blank" rel="noreferrer" style={{ color: "#2563eb", fontWeight: 700 }}>
                                      Join Call ↗
                                    </a>
                                  ) : "On-site"}
                                </td>
                                <td>
                                  <div style={{ display: "flex", gap: 6 }}>
                                    <button
                                      className="btn btn-sm btn-outline"
                                      onClick={async () => {
                                        await authFetch(`/api/interviews/${iv.id}`, {
                                          method: "PATCH",
                                          body: JSON.stringify({ status: "COMPLETED" })
                                        });
                                        addToast("Interview marked completed");
                                        loadUserData();
                                      }}
                                    >
                                      Complete
                                    </button>
                                    <button
                                      className="btn btn-sm btn-danger"
                                      onClick={async () => {
                                        await authFetch(`/api/interviews/${iv.id}`, { method: "DELETE" });
                                        addToast("Interview cancelled", "info");
                                        loadUserData();
                                      }}
                                    >
                                      Cancel
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}

                {/* TAB 4: COMPANY PROFILE */}
                {employerTab === "profile" && (
                  <div className="card">
                    <div className="card-title">
                      <span>Company Profile Details</span>
                      {user.recruiter_profile?.is_verified && (
                        <span className="verified-badge">✓ Verified PlacementHub Employer</span>
                      )}
                    </div>

                    <form onSubmit={handleSaveEmployerProfile}>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                        <div className="form-group">
                          <label>Organization / Company Name *</label>
                          <input
                            type="text"
                            className="form-control"
                            value={employerProfileForm.company_name}
                            onChange={(e) => setEmployerProfileForm({ ...employerProfileForm, company_name: e.target.value })}
                            required
                          />
                        </div>

                        <div className="form-group">
                          <label>Official Company Email</label>
                          <input
                            type="email"
                            className="form-control"
                            value={employerProfileForm.company_email}
                            onChange={(e) => setEmployerProfileForm({ ...employerProfileForm, company_email: e.target.value })}
                          />
                        </div>

                        <div className="form-group">
                          <label>Industry</label>
                          <input
                            type="text"
                            className="form-control"
                            placeholder="e.g. Software, EdTech, Media"
                            value={employerProfileForm.industry}
                            onChange={(e) => setEmployerProfileForm({ ...employerProfileForm, industry: e.target.value })}
                          />
                        </div>

                        <div className="form-group">
                          <label>Company Website</label>
                          <input
                            type="url"
                            className="form-control"
                            placeholder="https://company.com"
                            value={employerProfileForm.website}
                            onChange={(e) => setEmployerProfileForm({ ...employerProfileForm, website: e.target.value })}
                          />
                        </div>

                        <div className="form-group">
                          <label>Headquarters / Location</label>
                          <input
                            type="text"
                            className="form-control"
                            value={employerProfileForm.location}
                            onChange={(e) => setEmployerProfileForm({ ...employerProfileForm, location: e.target.value })}
                          />
                        </div>

                        <div className="form-group">
                          <label>Contact Phone</label>
                          <input
                            type="text"
                            className="form-control"
                            value={employerProfileForm.contact_phone}
                            onChange={(e) => setEmployerProfileForm({ ...employerProfileForm, contact_phone: e.target.value })}
                          />
                        </div>
                      </div>

                      <div className="form-group">
                        <label>Company Description</label>
                        <textarea
                          className="form-control"
                          rows="3"
                          value={employerProfileForm.business_description}
                          onChange={(e) => setEmployerProfileForm({ ...employerProfileForm, business_description: e.target.value })}
                        />
                      </div>

                      <div style={{ display: "flex", justifyContent: "flex-end" }}>
                        <button type="submit" className="btn btn-primary">
                          Save Company Profile
                        </button>
                      </div>
                    </form>
                  </div>
                )}
              </div>
            )}

            {/* VIEW: POST A JOB */}
            {route === "/post-job" && isEmployer && (
              <div className="card" style={{ maxWidth: 840, margin: "0 auto" }}>
                <div className="card-title">
                  <span>Post a Student Part-Time Gig</span>
                  <button className="btn btn-sm btn-outline" onClick={() => navigate("/employer-dashboard")}>
                    ← Back to Dashboard
                  </button>
                </div>

                <form onSubmit={handleCreateJob}>
                  <div className="form-group">
                    <label>Gig Title *</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="e.g. Frontend Developer Assistant (Part-Time)"
                      value={postJobData.title}
                      onChange={(e) => setPostJobData({ ...postJobData, title: e.target.value })}
                      required
                    />
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                    <div className="form-group">
                      <label>Job Category *</label>
                      <select
                        className="form-control"
                        value={postJobData.category}
                        onChange={(e) => setPostJobData({ ...postJobData, category: e.target.value })}
                      >
                        {CATEGORIES.filter((c) => c !== "All").map((cat) => (
                          <option key={cat} value={cat}>{cat}</option>
                        ))}
                      </select>
                    </div>

                    <div className="form-group">
                      <label>Hourly Pay Rate (₹) *</label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="e.g. ₹350 - ₹500/hr"
                        value={postJobData.pay_rate}
                        onChange={(e) => setPostJobData({ ...postJobData, pay_rate: e.target.value })}
                        required
                      />
                    </div>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
                    <div className="form-group">
                      <label>Work Arrangement</label>
                      <select
                        className="form-control"
                        value={postJobData.work_arrangement}
                        onChange={(e) => setPostJobData({ ...postJobData, work_arrangement: e.target.value })}
                      >
                        <option value="Remote">Remote</option>
                        <option value="Hybrid">Hybrid</option>
                        <option value="On-site">On-site Campus</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label>Shift Schedule</label>
                      <select
                        className="form-control"
                        value={postJobData.shift_schedule}
                        onChange={(e) => setPostJobData({ ...postJobData, shift_schedule: e.target.value })}
                      >
                        <option value="Flexible">Flexible Hours</option>
                        <option value="Weekdays">Weekdays</option>
                        <option value="Weekends">Weekends Only</option>
                        <option value="Evenings">Evening Shifts</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label>Weekly Hours</label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="10-15 hrs/week"
                        value={postJobData.weekly_hours}
                        onChange={(e) => setPostJobData({ ...postJobData, weekly_hours: e.target.value })}
                      />
                    </div>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                    <div className="form-group">
                      <label>Location / City</label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="e.g. Remote or Campus Center"
                        value={postJobData.location}
                        onChange={(e) => setPostJobData({ ...postJobData, location: e.target.value })}
                      />
                    </div>

                    <div className="form-group">
                      <label>Open Positions (Vacancies)</label>
                      <input
                        type="number"
                        min="1"
                        className="form-control"
                        value={postJobData.vacancies}
                        onChange={(e) => setPostJobData({ ...postJobData, vacancies: parseInt(e.target.value) || 1 })}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Required Skills (Comma separated) *</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="e.g. React, JavaScript, CSS, Git"
                      value={postJobData.skills}
                      onChange={(e) => setPostJobData({ ...postJobData, skills: e.target.value })}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>About the Gig (Description) *</label>
                    <textarea
                      className="form-control"
                      rows="3"
                      placeholder="Describe what the student will be doing..."
                      value={postJobData.description}
                      onChange={(e) => setPostJobData({ ...postJobData, description: e.target.value })}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>Key Responsibilities</label>
                    <textarea
                      className="form-control"
                      rows="2"
                      placeholder="Day-to-day deliverables..."
                      value={postJobData.responsibilities}
                      onChange={(e) => setPostJobData({ ...postJobData, responsibilities: e.target.value })}
                    />
                  </div>

                  <div className="form-group">
                    <label>Student Perks & Benefits</label>
                    <textarea
                      className="form-control"
                      rows="2"
                      placeholder="Flexible schedule during exams, letter of recommendation, mentor sessions..."
                      value={postJobData.benefits}
                      onChange={(e) => setPostJobData({ ...postJobData, benefits: e.target.value })}
                    />
                  </div>

                  <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
                    <button type="button" className="btn btn-outline" onClick={() => navigate("/employer-dashboard")}>
                      Cancel
                    </button>
                    <button type="submit" className="btn btn-primary">
                      Publish Student Gig
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* VIEW: ADMIN PORTAL */}
            {route === "/admin" && isAdmin && (
              <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                {/* PLATFORM METRICS */}
                <div className="stats-grid">
                  <div className="stat-card">
                    <span className="stat-label">Students</span>
                    <span className="stat-value">{adminStats?.total_students || 0}</span>
                    <span className="stat-meta">Registered candidates</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-label">Employers</span>
                    <span className="stat-value">{adminStats?.total_recruiters || 0}</span>
                    <span className="stat-meta">Registered hiring partners</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-label">Active Gigs</span>
                    <span className="stat-value">{adminStats?.active_jobs || 0}</span>
                    <span className="stat-meta">Active public listings</span>
                  </div>
                  <div className="stat-card" style={{ borderLeft: "4px solid #10b981" }}>
                    <span className="stat-label">Placed Students</span>
                    <span className="stat-value">{adminStats?.total_placed || 0}</span>
                    <span className="stat-meta">Hires & accepted offers</span>
                  </div>
                  <div className="stat-card" style={{ borderLeft: "4px solid #f59e0b" }}>
                    <span className="stat-label">Pending Users</span>
                    <span className="stat-value">{pendingApprovals?.pending_users?.length || adminStats?.pending_user_approvals || 0}</span>
                    <span className="stat-meta">Awaiting admin review</span>
                  </div>
                  <div className="stat-card" style={{ borderLeft: "4px solid var(--coral)" }}>
                    <span className="stat-label">Pending Job Offers</span>
                    <span className="stat-value">{pendingApprovals?.pending_jobs?.length || adminStats?.pending_job_approvals || 0}</span>
                    <span className="stat-meta">Recruiter offers to approve</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-label">Moderation Flags</span>
                    <span className="stat-value">{adminStats?.reported_jobs || 0}</span>
                    <span className="stat-meta">Pending user reports</span>
                  </div>
                </div>

                {/* ADMIN TABS */}
                <div className="tab-bar">
                  <button
                    className={`tab-btn ${adminTab === "pending" ? "active" : ""}`}
                    onClick={() => setAdminTab("pending")}
                  >
                    Pending Approvals Queue <span className="tab-badge" style={{ background: "var(--coral)", color: "white" }}>
                      {(pendingApprovals?.pending_users?.length || 0) + (pendingApprovals?.pending_jobs?.length || 0)}
                    </span>
                  </button>
                  <button
                    className={`tab-btn ${adminTab === "users" ? "active" : ""}`}
                    onClick={() => setAdminTab("users")}
                  >
                    User Management <span className="tab-badge">{adminUsers.length}</span>
                  </button>
                  <button
                    className={`tab-btn ${adminTab === "all-jobs" ? "active" : ""}`}
                    onClick={() => setAdminTab("all-jobs")}
                  >
                    All Platform Gigs <span className="tab-badge">{jobs.length}</span>
                  </button>
                  <button
                    className={`tab-btn ${adminTab === "moderation" ? "active" : ""}`}
                    onClick={() => setAdminTab("moderation")}
                  >
                    Moderation Queue <span className="tab-badge">{adminReports.filter((r) => r.status === "PENDING").length}</span>
                  </button>
                </div>

                {/* TAB 1: PENDING APPROVALS QUEUE */}
                {adminTab === "pending" && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                    {/* SECTION A: PENDING USER REGISTRATIONS */}
                    <div className="card">
                      <div className="card-title">
                        <div>
                          <span>Pending User Registrations (Students & Recruiters)</span>
                          <p style={{ margin: "3px 0 0", fontSize: 13, color: "#64748b", fontWeight: 400 }}>
                            New students & recruiters require admin approval before applying for or posting gigs.
                          </p>
                        </div>
                        <span className="badge" style={{ background: "#fef3c7", color: "#92400e" }}>
                          {pendingApprovals.pending_users?.length || 0} Pending
                        </span>
                      </div>

                      {(!pendingApprovals.pending_users || pendingApprovals.pending_users.length === 0) ? (
                        <div className="empty-state" style={{ padding: "24px 12px" }}>
                          <div className="empty-icon">✓</div>
                          <h4 style={{ margin: "4px 0" }}>All user accounts approved</h4>
                          <p style={{ margin: 0, fontSize: 13 }}>No student or recruiter registration requests currently awaiting approval.</p>
                        </div>
                      ) : (
                        <div className="table-responsive">
                          <table>
                            <thead>
                              <tr>
                                <th>Name & Email</th>
                                <th>Role</th>
                                <th>Details / College / Company</th>
                                <th>Joined</th>
                                <th>Admin Actions</th>
                              </tr>
                            </thead>
                            <tbody>
                              {pendingApprovals.pending_users.map((u) => (
                                <tr key={u.id}>
                                  <td>
                                    <strong>{u.name}</strong>
                                    <div style={{ fontSize: 12, color: "#64748b" }}>{u.email}</div>
                                  </td>
                                  <td>
                                    <span className="badge badge-category">{u.role}</span>
                                  </td>
                                  <td>
                                    {u.role === "STUDENT" ? (
                                      <div style={{ fontSize: 12.5 }}>
                                        {u.student_profile?.college || "College"} • {u.student_profile?.degree || "Degree"}
                                        <div style={{ color: "#64748b" }}>CGPA: {u.student_profile?.cgpa || "N/A"}</div>
                                      </div>
                                    ) : (
                                      <div style={{ fontSize: 12.5 }}>
                                        <strong>{u.recruiter_profile?.company_name || "Company"}</strong>
                                        <div style={{ color: "#64748b" }}>{u.recruiter_profile?.industry || "Industry"}</div>
                                      </div>
                                    )}
                                  </td>
                                  <td style={{ fontSize: 12, color: "#64748b" }}>
                                    {new Date(u.created_at).toLocaleDateString()}
                                  </td>
                                  <td>
                                    <div style={{ display: "flex", gap: 6 }}>
                                      <button
                                        className="btn btn-sm btn-primary"
                                        style={{ background: "#10b981", borderColor: "#10b981", color: "white" }}
                                        onClick={async () => {
                                          const res = await authFetch(`/api/admin/users/${u.id}/approve`, { method: "POST" });
                                          if (res.ok) {
                                            addToast(`✓ Account for ${u.name} (${u.role}) approved!`);
                                            loadUserData();
                                          } else {
                                            addToast("Failed to approve user", "error");
                                          }
                                        }}
                                      >
                                        ✓ Accept & Approve
                                      </button>
                                      <button
                                        className="btn btn-sm btn-outline"
                                        onClick={async () => {
                                          await authFetch(`/api/admin/users/${u.id}`, { method: "DELETE" });
                                          addToast(`Account for ${u.name} rejected`);
                                          loadUserData();
                                        }}
                                      >
                                        ✕ Reject
                                      </button>
                                    </div>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>

                    {/* SECTION B: PENDING JOB OFFERS */}
                    <div className="card">
                      <div className="card-title">
                        <div>
                          <span>Pending Job Offers (From Recruiters)</span>
                          <p style={{ margin: "3px 0 0", fontSize: 13, color: "#64748b", fontWeight: 400 }}>
                            Recruiter job listings require admin approval before becoming visible to students.
                          </p>
                        </div>
                        <span className="badge" style={{ background: "#fee2e2", color: "#991b1b" }}>
                          {pendingApprovals.pending_jobs?.length || 0} Pending Offers
                        </span>
                      </div>

                      {(!pendingApprovals.pending_jobs || pendingApprovals.pending_jobs.length === 0) ? (
                        <div className="empty-state" style={{ padding: "24px 12px" }}>
                          <div className="empty-icon">✓</div>
                          <h4 style={{ margin: "4px 0" }}>All job offers approved</h4>
                          <p style={{ margin: 0, fontSize: 13 }}>No recruiter listings pending moderation or approval.</p>
                        </div>
                      ) : (
                        <div className="table-responsive">
                          <table>
                            <thead>
                              <tr>
                                <th>Job Title</th>
                                <th>Recruiter / Company</th>
                                <th>Category & Pay</th>
                                <th>Details</th>
                                <th>Admin Actions</th>
                              </tr>
                            </thead>
                            <tbody>
                              {pendingApprovals.pending_jobs.map((j) => (
                                <tr key={j.id}>
                                  <td>
                                    <strong>{j.title}</strong>
                                    <div style={{ fontSize: 12, color: "#64748b" }}>{j.job_type} • {j.work_arrangement}</div>
                                  </td>
                                  <td>
                                    <strong>{j.company}</strong>
                                    <div style={{ fontSize: 12, color: "#64748b" }}>📍 {j.location}</div>
                                  </td>
                                  <td>
                                    <span className="badge badge-category">{j.category}</span>
                                    <div style={{ fontSize: 12, fontWeight: 700, color: "var(--coral)", marginTop: 4 }}>
                                      💰 {j.pay_rate || j.salary}
                                    </div>
                                  </td>
                                  <td>
                                    <p style={{ margin: 0, fontSize: 12, maxWidth: 260, color: "#475569" }}>
                                      {j.description?.slice(0, 90)}...
                                    </p>
                                    <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 2 }}>
                                      Vacancies: {j.vacancies || 1} • {j.weekly_hours}
                                    </div>
                                  </td>
                                  <td>
                                    <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                                      <button
                                        className="btn btn-sm btn-primary"
                                        style={{ background: "#4f46e5", borderColor: "#4f46e5", color: "white" }}
                                        onClick={async () => {
                                          const res = await authFetch(`/api/admin/jobs/${j.id}/approve`, { method: "POST" });
                                          if (res.ok) {
                                            addToast(`✓ Job offer '${j.title}' approved! Notifications sent to students.`);
                                            loadUserData();
                                            loadJobs();
                                          } else {
                                            addToast("Failed to approve job", "error");
                                          }
                                        }}
                                      >
                                        ✓ Accept Job Offer (Make Live)
                                      </button>
                                      <button
                                        className="btn btn-sm btn-outline"
                                        onClick={async () => {
                                          await authFetch(`/api/admin/jobs/${j.id}/reject`, { method: "POST" });
                                          addToast(`Job offer '${j.title}' rejected`);
                                          loadUserData();
                                          loadJobs();
                                        }}
                                      >
                                        ✕ Reject
                                      </button>
                                    </div>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* TAB 2: MODERATION & REPORTS */}
                {adminTab === "moderation" && (
                  <div className="card">
                    <div className="card-title">
                      <span>Reported Jobs & Moderation Queue</span>
                    </div>

                    {adminReports.length === 0 ? (
                      <div className="empty-state">
                        <div className="empty-icon">🛡️</div>
                        <h4>No reports pending</h4>
                        <p>All job listings are verified and clear of moderation flags.</p>
                      </div>
                    ) : (
                      <div className="table-responsive">
                        <table>
                          <thead>
                            <tr>
                              <th>Gig</th>
                              <th>Employer</th>
                              <th>Reason</th>
                              <th>Reporter</th>
                              <th>Status</th>
                              <th>Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {adminReports.map((r) => (
                              <tr key={r.id}>
                                <td><strong>{r.job_title}</strong></td>
                                <td>{r.company}</td>
                                <td><span className="badge" style={{ background: "#fee2e2", color: "#991b1b" }}>{r.reason}</span></td>
                                <td>{r.reporter_name}</td>
                                <td>{r.status}</td>
                                <td>
                                  {r.status === "PENDING" ? (
                                    <div style={{ display: "flex", gap: 6 }}>
                                      <button
                                        className="btn btn-sm btn-danger"
                                        onClick={async () => {
                                          await authFetch(`/api/admin/reports/${r.id}?action=ACTION_TAKEN`, { method: "PATCH" });
                                          addToast("Job taken down and report resolved");
                                          loadUserData();
                                          loadJobs();
                                        }}
                                      >
                                        Take Down Job
                                      </button>
                                      <button
                                        className="btn btn-sm btn-outline"
                                        onClick={async () => {
                                          await authFetch(`/api/admin/reports/${r.id}?action=DISMISSED`, { method: "PATCH" });
                                          addToast("Report dismissed", "info");
                                          loadUserData();
                                        }}
                                      >
                                        Dismiss
                                      </button>
                                    </div>
                                  ) : (
                                    <span style={{ fontSize: 12, color: "#64748b" }}>Resolved</span>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}

                {/* TAB 2: USER MANAGEMENT */}
                {adminTab === "users" && (
                  <div className="card">
                    <div className="card-title">
                      <span>Registered User Accounts ({adminUsers.length})</span>
                      <button
                        className="btn btn-sm btn-primary"
                        style={{ background: "#2563eb", display: "inline-flex", alignItems: "center", gap: 5 }}
                        onClick={() => setShowCreateUserModal(true)}
                      >
                        + Add New User
                      </button>
                    </div>

                    <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Search users by name or email..."
                        value={adminUserSearch}
                        onChange={(e) => setAdminUserSearch(e.target.value)}
                        style={{ maxWidth: 300 }}
                      />
                      <select
                        className="form-control"
                        value={adminUserRoleFilter}
                        onChange={(e) => setAdminUserRoleFilter(e.target.value)}
                        style={{ maxWidth: 180 }}
                      >
                        <option value="ALL">All Roles</option>
                        <option value="STUDENT">Students</option>
                        <option value="RECRUITER">Employers</option>
                        <option value="ADMIN">Admins</option>
                      </select>
                    </div>

                    <div className="table-responsive">
                      <table>
                        <thead>
                          <tr>
                            <th>User Name</th>
                            <th>Email Address</th>
                            <th>Role</th>
                            <th>Status</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {adminUsers
                            .filter((u) => {
                              const matchQ = !adminUserSearch || u.name.toLowerCase().includes(adminUserSearch.toLowerCase()) || u.email.toLowerCase().includes(adminUserSearch.toLowerCase());
                              const matchR = adminUserRoleFilter === "ALL" || u.role === adminUserRoleFilter;
                              return matchQ && matchR;
                            })
                            .map((u) => (
                              <tr key={u.id}>
                                <td><strong>{u.name}</strong></td>
                                <td>{u.email}</td>
                                <td>
                                  <span className="badge badge-category">{u.role}</span>
                                </td>
                                <td>
                                  <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                                    <span className="badge" style={{
                                      background: u.is_active ? "#dcfce7" : "#fee2e2",
                                      color: u.is_active ? "#15803d" : "#991b1b"
                                    }}>
                                      {u.is_active ? "Active" : "Suspended"}
                                    </span>
                                    <span className="badge" style={{
                                      background: u.is_approved ? "#eff6ff" : "#fef3c7",
                                      color: u.is_approved ? "#1e40af" : "#92400e",
                                      fontSize: 10
                                    }}>
                                      {u.is_approved ? "✓ Approved" : "⏳ Pending"}
                                    </span>
                                  </div>
                                </td>
                                <td>
                                  {u.id !== user.id ? (
                                    <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                                      {u.role !== "ADMIN" && (
                                        <>
                                          {!u.is_approved && (
                                            <button
                                              className="btn btn-sm btn-primary"
                                              style={{ background: "#16a34a", padding: "4px 8px", fontSize: 11 }}
                                              onClick={async () => {
                                                const res = await authFetch(`/api/admin/users/${u.id}/approve`, { method: "POST" });
                                                if (res.ok) {
                                                  addToast(`Approved user ${u.name}!`);
                                                  loadUserData();
                                                } else {
                                                  const data = await res.json().catch(() => ({}));
                                                  addToast(data.detail || "Failed to approve user", "error");
                                                }
                                              }}
                                            >✓ Approve</button>
                                          )}
                                          <button
                                            className="btn btn-sm btn-outline"
                                            title="Edit User Details"
                                            onClick={() => {
                                              setEditingUser(u);
                                              setEditUserData({ name: u.name, email: u.email, role: u.role, is_active: u.is_active, is_approved: u.is_approved });
                                            }}
                                          >✏️ Edit</button>
                                          <button
                                            className="btn btn-sm btn-outline"
                                            onClick={async () => {
                                              const res = await authFetch(`/api/admin/users/${u.id}/toggle-status`, { method: "POST" });
                                              if (res.ok) {
                                                addToast(`User status updated for ${u.name}`);
                                                loadUserData();
                                              } else {
                                                const data = await res.json().catch(() => ({}));
                                                addToast(data.detail || "Could not update user status", "error");
                                              }
                                            }}
                                          >{u.is_active ? "Suspend" : "Activate"}</button>
                                        </>
                                      )}
                                      <button
                                        className="btn btn-sm btn-danger"
                                        onClick={() => setConfirmDialog({
                                          title: u.role === "ADMIN" ? "Delete Administrator" : "Delete User Account",
                                          message: `Permanently delete ${u.name} (${u.email})? Related profile and activity records may also be removed. This cannot be undone.`,
                                          onConfirm: async () => {
                                            try {
                                              const res = await authFetch(`/api/admin/users/${u.id}`, { method: "DELETE" });
                                              const data = await res.json().catch(() => ({}));
                                              if (!res.ok) throw new Error(data.detail || "User deletion failed");
                                              addToast(`${u.role === "ADMIN" ? "Administrator" : "User"} ${u.name} deleted`);
                                              setConfirmDialog(null);
                                              await loadUserData();
                                            } catch (err) {
                                              addToast(err.message || "Could not delete user", "error");
                                            }
                                          }
                                        })}
                                      >Delete</button>
                                    </div>
                                  ) : <span style={{ color: "#64748b", fontSize: 12 }}>Current account</span>}
                                </td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* TAB 3: ALL PLATFORM GIGS */}
                {adminTab === "all-jobs" && (
                  <div className="card">
                    <div className="card-title">
                      <span>Platform-Wide Job Listings ({jobs.length})</span>
                      <button
                        className="btn btn-sm btn-primary"
                        style={{ background: "#2563eb", display: "inline-flex", alignItems: "center", gap: 5 }}
                        onClick={() => navigate("/post-job")}
                      >
                        + Post New Gig
                      </button>
                    </div>

                    <div className="table-responsive">
                      <table>
                        <thead>
                          <tr>
                            <th>Gig Title</th>
                            <th>Employer</th>
                            <th>Category</th>
                            <th>Pay Rate</th>
                            <th>Status</th>
                            <th>Moderation Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {jobs.map((j) => (
                            <tr key={j.id}>
                              <td><strong>{j.title}</strong></td>
                              <td>{j.company}</td>
                              <td>{j.category}</td>
                              <td><span className="badge badge-pay">{j.pay_rate}</span></td>
                              <td><span className="badge badge-category">{j.status}</span></td>
                              <td>
                                <div style={{ display: "flex", gap: 6 }}>
                                  {j.status !== "PENDING_APPROVAL" && (
                                    <button
                                      className="btn btn-sm btn-outline"
                                      onClick={async () => {
                                        const next = j.status === "ACTIVE" ? "CLOSED" : "ACTIVE";
                                        const res = await authFetch(`/api/jobs/${j.id}/status?status_str=${next}`, { method: "PATCH" });
                                        if (!res.ok) {
                                          const data = await res.json().catch(() => ({}));
                                          addToast(data.detail || "Could not update job status", "error");
                                          return;
                                        }
                                        addToast(`Job status set to ${next}`);
                                        loadJobs();
                                      }}
                                    >
                                      {j.status === "ACTIVE" ? "Close" : "Reopen"}
                                    </button>
                                  )}
                                  <button
                                    className="btn btn-sm btn-danger"
                                    onClick={() => {
                                      setConfirmDialog({
                                        title: "Delete Platform Gig",
                                        message: `Are you sure you want to permanently delete '${j.title}'?`,
                                        onConfirm: async () => {
                                          try {
                                            const res = await authFetch(`/api/admin/jobs/${j.id}`, { method: "DELETE" });
                                            const data = await res.json().catch(() => ({}));
                                            if (!res.ok) throw new Error(data.detail || "Job deletion failed");
                                            addToast(`Job listing '${j.title}' deleted by admin`);
                                            setConfirmDialog(null);
                                            loadJobs();
                                          } catch (err) {
                                            addToast(err.message || "Could not delete job listing", "error");
                                          }
                                        }
                                      });
                                    }}
                                  >
                                    Delete
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* VIEW: NOTIFICATIONS */}
            {route === "/notifications" && (
              <div className="card">
                <div className="card-title">
                  <span>Notifications Center</span>
                  {unreadCount > 0 && (
                    <button
                      className="btn btn-sm btn-outline"
                      onClick={async () => {
                        try {
                          const response = await authFetch("/api/notifications/read-all", { method: "POST" });
                          if (!response.ok) throw new Error(`HTTP ${response.status}`);
                          previousUnreadCount.current = 0;
                          setUnreadCount(0);
                          setNotifications((current) => current.map((item) => ({ ...item, is_read: true })));
                          addToast("All notifications marked as read");
                        } catch (err) {
                          addToast("Could not mark notifications as read. Please try again.", "error");
                        }
                      }}
                    >
                      Mark all as read
                    </button>
                  )}
                </div>

                {notifications.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">🔔</div>
                    <h4>No notifications yet</h4>
                    <p>Alerts for applications, interviews, and shifts will appear here.</p>
                  </div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    {notifications.map((n) => (
                      <div
                        key={n.id}
                        style={{
                          padding: 14, borderRadius: 12,
                          background: n.is_read ? "#ffffff" : "#f0fdf4",
                          border: `1px solid ${n.is_read ? "#e2e8f0" : "#bbf7d0"}`,
                          display: "flex", justifyContent: "space-between", alignItems: "center"
                        }}
                      >
                        <div>
                          <h5 style={{ margin: "0 0 4px", fontSize: 14, color: "#0f172a" }}>{n.title}</h5>
                          <p style={{ margin: 0, fontSize: 13, color: "#475569" }}>{n.message}</p>
                          <span style={{ fontSize: 11, color: "#94a3b8" }}>{new Date(n.created_at).toLocaleString()}</span>
                        </div>

                        {!n.is_read && (
                          <button
                            className="btn btn-sm btn-outline"
                            onClick={async () => {
                              try {
                                const response = await authFetch(`/api/notifications/${n.id}/read`, { method: "PATCH" });
                                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                                setNotifications((current) => current.map((item) => item.id === n.id ? { ...item, is_read: true } : item));
                                setUnreadCount((count) => Math.max(0, count - 1));
                                previousUnreadCount.current = Math.max(0, (previousUnreadCount.current ?? unreadCount) - 1);
                              } catch (err) {
                                addToast("Could not mark notification as read. Please try again.", "error");
                              }
                            }}
                          >
                            Mark read
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* MODAL: JOB DETAILS */}
      {selectedJobDetails && (
        <div className="modal-overlay" onClick={() => setSelectedJobDetails(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3>{selectedJobDetails.title}</h3>
                <p style={{ margin: "4px 0 0", color: "#64748b" }}>
                  🏢 {selectedJobDetails.company} • 📍 {selectedJobDetails.location}
                  {selectedJobDetails.is_employer_verified && " • ✓ Verified Employer"}
                </p>
              </div>
              <button className="close-btn" onClick={() => setSelectedJobDetails(null)}>×</button>
            </div>

            <div className="job-badges" style={{ marginBottom: 16 }}>
              <span className="badge badge-pay">💰 {selectedJobDetails.pay_rate}</span>
              <span className="badge badge-hours">⏱️ {selectedJobDetails.weekly_hours}</span>
              <span className="badge badge-shift">📅 {selectedJobDetails.shift_schedule}</span>
              <span className="badge badge-arrangement">🌐 {selectedJobDetails.work_arrangement}</span>
            </div>

            <div style={{ marginBottom: 16 }}>
              <h4 style={{ margin: "0 0 6px", color: "#0f172a" }}>About the Gig</h4>
              <p style={{ color: "#475569", lineHeight: 1.6 }}>{selectedJobDetails.description}</p>
            </div>

            {selectedJobDetails.responsibilities && (
              <div style={{ marginBottom: 16 }}>
                <h4 style={{ margin: "0 0 6px", color: "#0f172a" }}>Key Responsibilities</h4>
                <p style={{ color: "#475569", lineHeight: 1.6 }}>{selectedJobDetails.responsibilities}</p>
              </div>
            )}

            {selectedJobDetails.benefits && (
              <div style={{ marginBottom: 16 }}>
                <h4 style={{ margin: "0 0 6px", color: "#0f172a" }}>Student Perks & Benefits</h4>
                <p style={{ color: "#475569", lineHeight: 1.6 }}>{selectedJobDetails.benefits}</p>
              </div>
            )}

            <div style={{ marginBottom: 20 }}>
              <h4 style={{ margin: "0 0 8px", color: "#0f172a" }}>Required Skills</h4>
              <div className="skills-pill-group">
                {(selectedJobDetails.skills || []).map((s) => (
                  <span key={s} className="skill-pill matched">✓ {s}</span>
                ))}
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
              <button className="btn btn-outline" onClick={() => setSelectedJobDetails(null)}>Close</button>
              <button
                className="btn btn-primary"
                onClick={() => {
                  const target = selectedJobDetails;
                  setSelectedJobDetails(null);
                  handleApplyClick(target);
                }}
              >
                Apply for this Gig
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: APPLY TO JOB */}
      {applyModalJob && (
        <div className="modal-overlay" onClick={() => setApplyModalJob(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3>Apply for {applyModalJob.title}</h3>
                <p style={{ margin: "4px 0 0", color: "#64748b" }}>
                  🏢 {applyModalJob.company} • 💰 {applyModalJob.pay_rate}
                </p>
              </div>
              <button className="close-btn" onClick={() => setApplyModalJob(null)}>×</button>
            </div>

            <form onSubmit={handleApplySubmit}>
              <div className="form-group">
                <label>Applicant Profile Summary</label>
                <div style={{ background: "#f8fafc", padding: 12, borderRadius: 10, fontSize: 13 }}>
                  <p style={{ margin: "0 0 4px" }}><strong>Student:</strong> {user?.name} ({user?.student_profile?.college})</p>
                  <p style={{ margin: "0 0 4px" }}><strong>Branch:</strong> {user?.student_profile?.branch} (CGPA: {user?.student_profile?.cgpa})</p>
                  <p style={{ margin: 0 }}><strong>Skills:</strong> {(user?.student_profile?.skills || []).join(", ")}</p>
                </div>
              </div>

              <div className="form-group">
                <label>Weekly Availability & Preferred Shifts *</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. Weekday evenings (5-8 PM) and Saturday mornings"
                  value={applyAvailability}
                  onChange={(e) => setApplyAvailability(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>Short Cover Note / Why you're a great fit</label>
                <textarea
                  className="form-control"
                  rows="3"
                  placeholder="Brief note to the employer..."
                  value={applyCoverLetter}
                  onChange={(e) => setApplyCoverLetter(e.target.value)}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
                <button type="button" className="btn btn-outline" onClick={() => setApplyModalJob(null)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Confirm & Submit Application
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: REPORT JOB */}
      {reportModalJob && (
        <div className="modal-overlay" onClick={() => setReportModalJob(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Report Suspicious Listing</h3>
              <button className="close-btn" onClick={() => setReportModalJob(null)}>×</button>
            </div>

            <form onSubmit={handleReportSubmit}>
              <div className="form-group">
                <label>Gig</label>
                <p><strong>{reportModalJob.title}</strong> at {reportModalJob.company}</p>
              </div>

              <div className="form-group">
                <label>Reason for Reporting *</label>
                <select
                  className="form-control"
                  value={reportReason}
                  onChange={(e) => setReportReason(e.target.value)}
                >
                  <option value="Misleading compensation">Misleading compensation</option>
                  <option value="Suspected scam">Suspected scam</option>
                  <option value="Fake employer">Fake employer</option>
                  <option value="Inappropriate content">Inappropriate content</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label>Additional Details</label>
                <textarea
                  className="form-control"
                  rows="3"
                  value={reportDetails}
                  onChange={(e) => setReportDetails(e.target.value)}
                  placeholder="Provide context for our moderators..."
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
                <button type="button" className="btn btn-outline" onClick={() => setReportModalJob(null)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-danger">
                  Submit Report
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: SCHEDULE INTERVIEW */}
      {interviewModalApp && (
        <div className="modal-overlay" onClick={() => setInterviewModalApp(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Schedule Interview Round</h3>
              <button className="close-btn" onClick={() => setInterviewModalApp(null)}>×</button>
            </div>

            <form onSubmit={handleScheduleInterview}>
              <div className="form-group">
                <label>Candidate: {interviewModalApp.student_name}</label>
                <p style={{ margin: "2px 0 0", color: "#64748b" }}>Gig: {interviewModalApp.job_title}</p>
              </div>

              <div className="form-group">
                <label>Interview Date & Time *</label>
                <input
                  type="datetime-local"
                  className="form-control"
                  value={interviewDate}
                  onChange={(e) => setInterviewDate(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>Interview Mode</label>
                <select
                  className="form-control"
                  value={interviewMode}
                  onChange={(e) => setInterviewMode(e.target.value)}
                >
                  <option value="ONLINE">ONLINE (Video Call)</option>
                  <option value="OFFLINE">OFFLINE (Campus/Office)</option>
                  <option value="HYBRID">HYBRID</option>
                </select>
              </div>

              {interviewMode === "ONLINE" && (
                <div className="form-group">
                  <label>Meeting Link (Google Meet / Zoom)</label>
                  <input
                    type="url"
                    className="form-control"
                    placeholder="https://meet.google.com/..."
                    value={interviewLink}
                    onChange={(e) => setInterviewLink(e.target.value)}
                  />
                </div>
              )}

              <div className="form-group">
                <label>Notes & Guidelines for Candidate</label>
                <textarea
                  className="form-control"
                  rows="2"
                  value={interviewNotes}
                  onChange={(e) => setInterviewNotes(e.target.value)}
                  placeholder="e.g. Portfolio walkthrough and schedule discussion."
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
                <button type="button" className="btn btn-outline" onClick={() => setInterviewModalApp(null)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Confirm Schedule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* CONFIRMATION DIALOG */}
      {confirmDialog && (
        <div className="modal-overlay" onClick={() => setConfirmDialog(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 440 }}>
            <div className="modal-header">
              <h3>{confirmDialog.title}</h3>
              <button className="close-btn" onClick={() => setConfirmDialog(null)}>×</button>
            </div>
            <p style={{ color: "#475569", lineHeight: 1.5, margin: "0 0 20px" }}>{confirmDialog.message}</p>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
              <button className="btn btn-outline" onClick={() => setConfirmDialog(null)}>
                Cancel
              </button>
              <button className="btn btn-danger" onClick={confirmDialog.onConfirm}>
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: ADMIN CREATE USER */}
      {showCreateUserModal && (
        <div className="modal-overlay" onClick={() => setShowCreateUserModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 480 }}>
            <div className="modal-header">
              <h3>Create New User Account</h3>
              <button className="close-btn" onClick={() => setShowCreateUserModal(false)}>×</button>
            </div>
            <form onSubmit={handleAdminCreateUser}>
              <div className="form-group" style={{ marginBottom: 14 }}>
                <label style={{ display: "block", marginBottom: 6, fontWeight: 600 }}>Full Name *</label>
                <input
                  type="text"
                  className="form-control"
                  required
                  placeholder="e.g. Alex Johnson"
                  value={createUserData.name}
                  onChange={(e) => setCreateUserData({ ...createUserData, name: e.target.value })}
                />
              </div>
              <div className="form-group" style={{ marginBottom: 14 }}>
                <label style={{ display: "block", marginBottom: 6, fontWeight: 600 }}>Email Address *</label>
                <input
                  type="email"
                  className="form-control"
                  required
                  placeholder="e.g. alex@example.edu"
                  value={createUserData.email}
                  onChange={(e) => setCreateUserData({ ...createUserData, email: e.target.value })}
                />
              </div>
              <div className="form-group" style={{ marginBottom: 14 }}>
                <label style={{ display: "block", marginBottom: 6, fontWeight: 600 }}>Password *</label>
                <input
                  type="password"
                  className="form-control"
                  required
                  placeholder="Min 6 characters"
                  value={createUserData.password}
                  onChange={(e) => setCreateUserData({ ...createUserData, password: e.target.value })}
                />
              </div>
              <div className="form-group" style={{ marginBottom: 14 }}>
                <label style={{ display: "block", marginBottom: 6, fontWeight: 600 }}>Account Role *</label>
                <select
                  className="form-control"
                  value={createUserData.role}
                  onChange={(e) => setCreateUserData({ ...createUserData, role: e.target.value })}
                >
                  <option value="STUDENT">Student</option>
                  <option value="RECRUITER">Employer / Recruiter</option>
                  <option value="ADMIN">Administrator</option>
                </select>
              </div>
              <div style={{ display: "flex", gap: 20, margin: "16px 0", padding: "10px 14px", background: "#f8fafc", borderRadius: 8 }}>
                <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={createUserData.is_active}
                    onChange={(e) => setCreateUserData({ ...createUserData, is_active: e.target.checked })}
                  />
                  Active Account
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={createUserData.is_approved}
                    onChange={(e) => setCreateUserData({ ...createUserData, is_approved: e.target.checked })}
                  />
                  Pre-Approved (Ready to Work)
                </label>
              </div>
              <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 18 }}>
                <button type="button" className="btn btn-outline" onClick={() => setShowCreateUserModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" style={{ background: "#2563eb" }}>
                  Create User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: ADMIN EDIT USER */}
      {editingUser && (
        <div className="modal-overlay" onClick={() => setEditingUser(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 480 }}>
            <div className="modal-header">
              <h3>Edit User: {editingUser.name}</h3>
              <button className="close-btn" onClick={() => setEditingUser(null)}>×</button>
            </div>
            <form onSubmit={handleAdminUpdateUser}>
              <div className="form-group" style={{ marginBottom: 14 }}>
                <label style={{ display: "block", marginBottom: 6, fontWeight: 600 }}>Full Name</label>
                <input
                  type="text"
                  className="form-control"
                  required
                  value={editUserData.name}
                  onChange={(e) => setEditUserData({ ...editUserData, name: e.target.value })}
                />
              </div>
              <div className="form-group" style={{ marginBottom: 14 }}>
                <label style={{ display: "block", marginBottom: 6, fontWeight: 600 }}>Email Address</label>
                <input
                  type="email"
                  className="form-control"
                  required
                  value={editUserData.email}
                  onChange={(e) => setEditUserData({ ...editUserData, email: e.target.value })}
                />
              </div>
              <div className="form-group" style={{ marginBottom: 14 }}>
                <label style={{ display: "block", marginBottom: 6, fontWeight: 600 }}>Account Role</label>
                <select
                  className="form-control"
                  value={editUserData.role}
                  onChange={(e) => setEditUserData({ ...editUserData, role: e.target.value })}
                >
                  <option value="STUDENT">Student</option>
                  <option value="RECRUITER">Employer / Recruiter</option>
                  <option value="ADMIN">Administrator</option>
                </select>
              </div>
              <div style={{ display: "flex", gap: 20, margin: "16px 0", padding: "10px 14px", background: "#f8fafc", borderRadius: 8 }}>
                <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={editUserData.is_active}
                    onChange={(e) => setEditUserData({ ...editUserData, is_active: e.target.checked })}
                  />
                  Active Account
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={editUserData.is_approved}
                    onChange={(e) => setEditUserData({ ...editUserData, is_approved: e.target.checked })}
                  />
                  Approved Status
                </label>
              </div>
              <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 18 }}>
                <button type="button" className="btn btn-outline" onClick={() => setEditingUser(null)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" style={{ background: "#2563eb" }}>
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: AUTHENTICATION */}
      {authModalMode && (
        <div className="modal-overlay" onClick={() => setAuthModalMode(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 440 }}>
            <div className="modal-header">
              <h3>{authModalMode === "login" ? "Sign In to PartTime" : "Create Account"}</h3>
              <button className="close-btn" onClick={() => setAuthModalMode(null)}>×</button>
            </div>

            {authError && (
              <div style={{ padding: "10px 14px", background: "#fee2e2", color: "#b91c1c", borderRadius: 10, fontSize: 13, marginBottom: 14 }}>
                ⚠️ {authError}
              </div>
            )}

            <form onSubmit={authModalMode === "login" ? login : register}>
              {authModalMode === "register" && (
                <>
                  <div className="form-group">
                    <label>Role</label>
                    <select
                      className="form-control"
                      value={authRole}
                      onChange={(e) => setAuthRole(e.target.value)}
                    >
                      <option value="STUDENT">College Student (Looking for Work)</option>
                      <option value="RECRUITER">Employer / Business (Posting Gigs)</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Full Name *</label>
                    <input
                      type="text"
                      className="form-control"
                      value={authName}
                      onChange={(e) => setAuthName(e.target.value)}
                      required
                    />
                  </div>

                  {authRole === "STUDENT" ? (
                    <div className="form-group">
                      <label>College / University</label>
                      <input
                        type="text"
                        className="form-control"
                        value={authCollege}
                        onChange={(e) => setAuthCollege(e.target.value)}
                      />
                    </div>
                  ) : (
                    <div className="form-group">
                      <label>Company / Organization Name *</label>
                      <input
                        type="text"
                        className="form-control"
                        value={authCompany}
                        onChange={(e) => setAuthCompany(e.target.value)}
                        required
                      />
                    </div>
                  )}
                </>
              )}

              <div className="form-group">
                <label>Email Address *</label>
                <input
                  type="email"
                  className="form-control"
                  value={authEmail}
                  onChange={(e) => setAuthEmail(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>Password *</label>
                <input
                  type="password"
                  className="form-control"
                  value={authPassword}
                  onChange={(e) => setAuthPassword(e.target.value)}
                  required
                />
              </div>

              <button type="submit" className="btn btn-primary" style={{ width: "100%", padding: 12, marginBottom: 14 }}>
                {authModalMode === "login" ? "Sign In" : "Register Account"}
              </button>

              <div style={{ textAlign: "center", fontSize: 13, color: "#64748b" }}>
                {authModalMode === "login" ? (
                  <span>
                    Don't have an account?{" "}
                    <a href="#register" onClick={(e) => { e.preventDefault(); setAuthModalMode("register"); }}>
                      Register here
                    </a>
                  </span>
                ) : (
                  <span>
                    Already registered?{" "}
                    <a href="#login" onClick={(e) => { e.preventDefault(); setAuthModalMode("login"); }}>
                      Sign In
                    </a>
                  </span>
                )}
              </div>

              {/* DEMO ACCOUNTS QUICK FILL */}
              <div style={{ marginTop: 20, paddingTop: 14, borderTop: "1px solid #f1f5f9", fontSize: 12, color: "#94a3b8" }}>
                <p style={{ margin: "0 0 8px", fontWeight: 700, color: "var(--text-dark)" }}>Quick Demo Logins:</p>
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  <button
                    type="button"
                    className="btn btn-sm btn-outline"
                    onClick={() => {
                      setAuthEmail("dhanush@college.edu");
                      setAuthPassword("Student@123");
                    }}
                  >
                    Student (Dhanush)
                  </button>
                  <button
                    type="button"
                    className="btn btn-sm btn-outline"
                    onClick={() => {
                      setAuthEmail("recruiter@technova.com");
                      setAuthPassword("Recruiter@123");
                    }}
                  >
                    Employer (TechNova)
                  </button>
                  <button
                    type="button"
                    className="btn btn-sm btn-outline"
                    onClick={() => {
                      setAuthEmail("admin@placement.edu");
                      setAuthPassword("Admin@123");
                    }}
                  >
                    Administrator
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

const root = createRoot(document.getElementById("root"));
root.render(<App />);
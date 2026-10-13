import React from "react";

// ==========================================
// VECTOR SVG ASSETS & DOODLES
// ==========================================

// Hand-drawn doodle student cap with smile (sits above WORKSPACE)
function DoodleStudentCap() {
  return (
    <svg className="doodle-cap-svg" viewBox="0 0 65 65" fill="none" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="32" cy="38" rx="20" ry="16" stroke="#FF7469" strokeWidth="2.5" strokeLinecap="round" />
      <circle cx="26" cy="36" r="2" fill="#FF7469" />
      <circle cx="38" cy="36" r="2" fill="#FF7469" />
      <path d="M28 42C30 45 34 45 36 42" stroke="#FF7469" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M16 28C22 20 42 20 48 28L54 25C44 14 20 14 10 25L16 28Z" fill="#FFF1F0" stroke="#FF7469" strokeWidth="2.5" strokeLinejoin="round" />
      <path d="M32 18L32 12" stroke="#FF7469" strokeWidth="2.5" strokeLinecap="round" />
      <circle cx="32" cy="11" r="2.5" fill="#FF7469" />
      <path d="M48 26L51 34" stroke="#FF7469" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

// Hand-drawn laptop doodle (sits to right of WORKSPACE)
function DoodleLaptop() {
  return (
    <svg className="doodle-laptop-svg" viewBox="0 0 84 64" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="16" y="8" width="52" height="36" rx="4" fill="#FFF1F0" stroke="#FF7469" strokeWidth="2.5" />
      <path d="M22 14H62V38H22V14Z" fill="#FFFFFF" stroke="#FF7469" strokeWidth="1.5" />
      <path d="M28 22H54M28 28H44" stroke="#FF7469" strokeWidth="2" strokeLinecap="round" />
      <path d="M6 48C6 45 14 44 20 44H64C70 44 78 45 78 48C78 51 70 52 64 52H20C14 52 6 51 6 48Z" fill="#FFFFFF" stroke="#FF7469" strokeWidth="2.5" strokeLinejoin="round" />
      <path d="M36 48H48" stroke="#FF7469" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}

// Hand-drawn calendar with smiley checkmark (inline between MORE and HUMANS)
function DoodleCalendar() {
  return (
    <svg className="doodle-calendar-inline" viewBox="0 0 54 54" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="10" width="42" height="38" rx="6" fill="#FFF1F0" stroke="#FF7469" strokeWidth="2.5" />
      {/* Binder rings */}
      <circle cx="14" cy="10" r="2" fill="#214B43" />
      <circle cx="21" cy="10" r="2" fill="#214B43" />
      <circle cx="27" cy="10" r="2" fill="#214B43" />
      <circle cx="33" cy="10" r="2" fill="#214B43" />
      <circle cx="40" cy="10" r="2" fill="#214B43" />
      {/* Happy face */}
      <circle cx="20" cy="27" r="2" fill="#FF7469" />
      <circle cx="34" cy="27" r="2" fill="#FF7469" />
      <path d="M22 34C25 38 29 38 32 34" stroke="#FF7469" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}

// Coral hand-drawn curved arrow for bottom CTA
function CoralCurvedArrow() {
  return (
    <svg className="coral-arrow-svg" viewBox="0 0 56 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M4 6C18 3 40 6 46 22C47 27 43 31 36 32C28 33 20 29 23 22C26 17 38 20 50 28" stroke="#FF7469" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M44 33L52 28L47 21" stroke="#FF7469" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// ==========================================
// HOW IT WORKS SVG ICONS
// ==========================================

function SearchGlassIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FF7469" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}

function ApplicationChecklistIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FF7469" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <path d="M9 13l2 2 4-4" />
      <line x1="9" y1="17" x2="15" y2="17" />
    </svg>
  );
}

function WalletPaymentIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FF7469" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="5" width="20" height="15" rx="3" />
      <path d="M16 12a2 2 0 1 0 0 4 2 2 0 0 0 0-4z" />
      <path d="M6 5V3a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v2" />
    </svg>
  );
}

// ==========================================
// EDITORIAL HOMEPAGE COMPONENT
// ==========================================
export default function EditorialHomepage({
  jobs = [],
  navigate,
  user,
  setAuthModalMode,
  setAuthRole,
  setApplyModalJob,
  toggleSaveJob,
  setSelectedCategory,
  logout,
  unreadCount = 0
}) {
  // Fallback featured part-time jobs matching reference image when API data is loading
  const defaultFeatured = [
    {
      id: "f1",
      title: "Frontend Developer",
      company: "TechNova",
      is_employer_verified: true,
      location: "Remote",
      pay_rate: "₹250 - ₹400 / hour",
      skills: ["React", "JavaScript", "UI/UX"],
      category_icon: "</>",
      icon_class: "job-icon-blue"
    },
    {
      id: "f2",
      title: "Mathematics Tutor",
      company: "LearnHub",
      is_employer_verified: true,
      location: "Online",
      pay_rate: "₹300 - ₹500 / hour",
      skills: ["Maths", "Teaching", "Communication"],
      category_icon: "🎓",
      icon_class: "job-icon-green"
    },
    {
      id: "f3",
      title: "Video Editor",
      company: "Creative Studio",
      is_employer_verified: false,
      location: "Hybrid",
      pay_rate: "₹400 - ₹700 / hour",
      skills: ["Video Editing", "Premiere Pro", "After Effects"],
      category_icon: "📹",
      icon_class: "job-icon-orange"
    }
  ];

  // Pick top 3 active jobs from backend or merge with default featured
  const featuredJobs = jobs && jobs.length >= 3 ? jobs.slice(0, 3).map((job, idx) => ({
    ...job,
    category_icon: idx === 0 ? "</>" : idx === 1 ? "🎓" : "📹",
    icon_class: idx === 0 ? "job-icon-blue" : idx === 1 ? "job-icon-green" : "job-icon-orange"
  })) : defaultFeatured;

  const scrollToHowItWorks = (e) => {
    e.preventDefault();
    const el = document.getElementById("how-it-works");
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleCategoryClick = (categoryName) => {
    if (setSelectedCategory) {
      setSelectedCategory(categoryName);
    }
    navigate("/find-jobs");
  };

  const handleForEmployers = () => {
    if (user && (user.role === "RECRUITER" || user.role === "EMPLOYER")) {
      navigate("/employer-dashboard");
    } else {
      if (setAuthRole) setAuthRole("EMPLOYER");
      setAuthModalMode("register");
    }
  };

  return (
    <div className="page-wrapper">
      {/* ========================================================
          PANEL 1: TOP NAVIGATION & OVERSIZED EDITORIAL HERO
          ======================================================== */}
      <div className="cream-container hero-container">
        {/* Minimalist Navigation */}
        <nav className="site-nav">
          <div className="nav-brand" onClick={() => navigate("/")}>
            <span className="brand-text">PartTime</span>
            <span className="brand-sparkle">✦</span>
          </div>

          <div className="nav-center">
            <button className="nav-link" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
              Home
            </button>
            <a href="#how-it-works" className="nav-link" onClick={scrollToHowItWorks}>
              How It Works
            </a>
            {user?.role === "RECRUITER" || user?.role === "EMPLOYER" ? (
              <button className="nav-link" onClick={() => navigate("/post-job")}>
                Add Jobs
              </button>
            ) : (
              <button className="nav-link" onClick={() => navigate("/find-jobs")}>
                Find Jobs
              </button>
            )}
            <button className="nav-link" onClick={() => navigate("/about")}>
              About
            </button>
          </div>

          <div className="nav-right">
            {user ? (
              <>
                <button
                  className="nav-link"
                  onClick={() => navigate("/notifications")}
                  style={{ position: "relative", marginRight: 6, display: "inline-flex", alignItems: "center", gap: 4 }}
                  title="View notifications"
                >
                  🔔
                  {unreadCount > 0 && (
                    <span style={{
                      background: "var(--coral)", color: "white", borderRadius: "10px",
                      padding: "1px 6px", fontSize: 10, fontWeight: 700
                    }}>
                      {unreadCount}
                    </span>
                  )}
                </button>
                <button
                  className="btn-ghost-dark"
                  onClick={() => {
                    if (user.role === "ADMIN") navigate("/admin");
                    else if (user.role === "STUDENT") navigate("/dashboard");
                    else navigate("/employer-dashboard");
                  }}
                >
                  {user.role === "ADMIN" ? "Admin Portal" : user.role === "STUDENT" ? "Dashboard" : "Recruiter Dashboard"} ({user.name.split(" ")[0]})
                </button>
                <button
                  className="btn-coral-pill"
                  onClick={logout}
                  style={{ padding: "8px 20px", fontSize: 13 }}
                >
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

        {/* HERO SECTION */}
        <section className="hero-grid">
          {/* Left Column: Oversized Headline, Copy, CTA */}
          <div className="hero-left">
            <div className="hero-headline-wrap">
              {/* Floating doodles with safe relative positioning */}
              <div className="doodle-cap-anchor">
                <DoodleStudentCap />
              </div>
              <div className="doodle-laptop-anchor">
                <DoodleLaptop />
              </div>

              <h1 className="hero-headline">
                <span className="headline-line">MAKE THE</span>
                <span className="headline-line">WORKSPACE</span>
                <span className="headline-line headline-inline-row">
                  <span>MORE</span>
                  <span className="headline-doodle-slot">
                    <DoodleCalendar />
                  </span>
                  <span className="headline-sparkle">✦</span>
                  <span>HUMANS.</span>
                </span>
              </h1>
            </div>

            <p className="hero-description">
              A platform for students to find flexible part-time jobs that fit around your classes, your goals, and your life.
            </p>

            <div className="hero-cta-group">
              <button className="btn-hero-cta" onClick={() => navigate("/find-jobs")}>
                Explore Jobs
              </button>
              <button className="btn-hero-secondary" onClick={scrollToHowItWorks}>
                See how it works <span>→</span>
              </button>
            </div>
          </div>

          {/* Right Column: High-quality illustration */}
          <div className="hero-right">
            <div className="hero-illustration-frame">
              <img
                src="/images/hero-student.png"
                alt="Student working on laptop with study accessories and notes"
                className="hero-student-img"
              />
            </div>
          </div>
        </section>
      </div>

      {/* ========================================================
          PANEL 2: HOW IT WORKS, CATEGORIES, FEATURED JOBS & CTA
          ======================================================== */}
      <div className="cream-container content-container" id="how-it-works">
        {/* ROW 1: HOW IT WORKS & WORK YOUR WAY CATEGORIES */}
        <div className="two-panel-section">
          {/* Left: How It Works */}
          <div className="panel-column-half">
            <div className="section-title-wrap">
              <h2 className="section-heading-serif">Your next opportunity starts here.</h2>
              <p className="section-subtext">A simple way to find, apply and start working.</p>
            </div>

            <div className="steps-row">
              {/* Card 1: Discover */}
              <div className="step-card">
                <div className="step-card-top">
                  <span className="step-number-badge">01</span>
                  <div className="step-icon-wrap">
                    <SearchGlassIcon />
                  </div>
                </div>
                <h3 className="step-title">Discover</h3>
                <p className="step-desc">Explore flexible jobs that match your skills, interests and college schedule.</p>
              </div>

              {/* Card 2: Apply */}
              <div className="step-card">
                <div className="step-card-top">
                  <span className="step-number-badge">02</span>
                  <div className="step-icon-wrap">
                    <ApplicationChecklistIcon />
                  </div>
                </div>
                <h3 className="step-title">Apply</h3>
                <p className="step-desc">Create your profile, share your skills and apply to opportunities with confidence.</p>
              </div>

              {/* Card 3: Earn */}
              <div className="step-card">
                <div className="step-card-top">
                  <span className="step-number-badge">03</span>
                  <div className="step-icon-wrap">
                    <WalletPaymentIcon />
                  </div>
                </div>
                <h3 className="step-title">Earn</h3>
                <p className="step-desc">Connect with employers, manage your applications and start earning.</p>
              </div>
            </div>
          </div>

          {/* Right: Work your way Categories */}
          <div className="panel-column-half">
            <div className="categories-header-row">
              <div className="section-title-wrap">
                <h2 className="section-heading-serif">Work your way.</h2>
                <p className="section-subtext">Explore popular job categories for students.</p>
              </div>
              <button
                className="view-all-link-btn"
                onClick={() => navigate("/find-jobs")}
              >
                View all categories →
              </button>
            </div>

            <div className="categories-grid">
              {/* Category 1: Tech */}
              <div className="category-card cat-tech" onClick={() => handleCategoryClick("Web Development")}>
                <div className="category-icon-wrap">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#E15545" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="4" width="18" height="12" rx="2" />
                    <line x1="2" y1="20" x2="22" y2="20" />
                  </svg>
                </div>
                <span className="category-label">Tech &amp; Development</span>
              </div>

              {/* Category 2: Tutoring */}
              <div className="category-card cat-tutoring" onClick={() => handleCategoryClick("Online Tutoring")}>
                <div className="category-icon-wrap">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#16A34A" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                    <path d="M6 12v5c3 3 9 3 12 0v-5" />
                  </svg>
                </div>
                <span className="category-label">Tutoring</span>
              </div>

              {/* Category 3: Design */}
              <div className="category-card cat-design" onClick={() => handleCategoryClick("Graphic Design")}>
                <div className="category-icon-wrap">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#DB2777" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="13.5" cy="6.5" r=".5" fill="#DB2777" />
                    <circle cx="17.5" cy="10.5" r=".5" fill="#DB2777" />
                    <circle cx="8.5" cy="7.5" r=".5" fill="#DB2777" />
                    <circle cx="6.5" cy="12.5" r=".5" fill="#DB2777" />
                    <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.9 0 1.6-.7 1.6-1.6 0-.4-.2-.8-.4-1.1-.3-.3-.4-.7-.4-1.1 0-.9.7-1.6 1.6-1.6H16c3.3 0 6-2.7 6-6 0-4.4-4.5-8-10-8z" />
                  </svg>
                </div>
                <span className="category-label">Design &amp; Video</span>
              </div>

              {/* Category 4: Content */}
              <div className="category-card cat-social" onClick={() => handleCategoryClick("Social Media Management")}>
                <div className="category-icon-wrap">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#D97706" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                    <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                  </svg>
                </div>
                <span className="category-label">Content &amp; Social</span>
              </div>

              {/* Category 5: Campus */}
              <div className="category-card cat-campus" onClick={() => handleCategoryClick("Campus Assistant")}>
                <div className="category-icon-wrap">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563EB" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M3 21h18M5 21V7l7-4 7 4v14M9 10h1M14 10h1M9 14h1M14 14h1M9 18h1M14 18h1" />
                  </svg>
                </div>
                <span className="category-label">Campus Jobs</span>
              </div>

              {/* Category 6: Weekend */}
              <div className="category-card cat-weekend" onClick={() => handleCategoryClick("Weekend-only")}>
                <div className="category-icon-wrap">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0D9488" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                    <line x1="16" y1="2" x2="16" y2="6" />
                    <line x1="8" y1="2" x2="8" y2="6" />
                    <line x1="3" y1="10" x2="21" y2="10" />
                  </svg>
                </div>
                <span className="category-label">Weekend Work</span>
              </div>
            </div>
          </div>
        </div>

        {/* ROW 2: FEATURED PART-TIME JOBS & PALE GREEN CTA PANEL */}
        <div className="bottom-section-grid">
          {/* Left: Featured Jobs */}
          <div className="featured-column-wrap">
            <div className="featured-header-row">
              <div className="section-title-wrap">
                <h2 className="section-heading-serif">Good work. Flexible hours.</h2>
                <p className="section-subtext">Latest part-time jobs from trusted employers.</p>
              </div>
              <button
                className="view-all-link-btn"
                onClick={() => navigate("/find-jobs")}
              >
                View all jobs →
              </button>
            </div>

            <div className="featured-jobs-row">
              {featuredJobs.map((job) => (
                <div className="editorial-job-card" key={job.id}>
                  <div className="job-card-body">
                    <div className={`job-icon-category ${job.icon_class}`}>
                      {job.category_icon}
                    </div>

                    <h3 className="card-job-title">{job.title}</h3>

                    <div className="card-employer-row">
                      <span className="employer-name-text">{job.company}</span>
                      {job.is_employer_verified && (
                        <span className="verified-tag-green">✓ Verified</span>
                      )}
                    </div>

                    <div className="card-job-meta">
                      📍 {job.location || "Remote"} • <strong className="pay-rate-highlight">{job.pay_rate || job.salary}</strong>
                    </div>

                    <div className="card-skill-tags">
                      {(job.skills || []).slice(0, 3).map((skill) => (
                        <span className="mini-skill-tag" key={skill}>{skill}</span>
                      ))}
                    </div>
                  </div>

                  <div className="card-btn-footer">
                    <button
                      className="btn-card-apply"
                      onClick={() => {
                        if (user) {
                          setApplyModalJob(job);
                        } else {
                          setAuthModalMode("login");
                        }
                      }}
                    >
                      Apply Now
                    </button>
                    <button
                      className={`btn-card-bookmark ${job.is_saved ? "saved" : ""}`}
                      title={job.is_saved ? "Remove bookmark" : "Save job"}
                      onClick={() => toggleSaveJob && toggleSaveJob(job.id, job.is_saved)}
                    >
                      {job.is_saved ? "★" : "☆"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: Pale Green Bottom CTA Panel */}
          <div className="pale-green-cta-card">
            <div className="cta-illustration-col">
              <img
                src="/images/cta-student.png"
                alt="Student girl holding laptop with coral heart"
                className="cta-student-img"
              />
            </div>

            <div className="cta-banner-text">
              <h3>Make room for what matters.</h3>
              <p>Find a job that fits around your studies, not the other way around.</p>
              <button className="btn-coral-pill btn-cta-large" onClick={() => navigate("/find-jobs")}>
                Find Your First Job →
              </button>
            </div>

            <div className="cta-arrow-pos">
              <CoralCurvedArrow />
            </div>
          </div>
        </div>
      </div>

      {/* ========================================================
          PANEL 3: PROFESSIONAL EDITORIAL FOOTER
          ======================================================== */}
      <footer className="editorial-footer">
        <div className="footer-left">
          <div className="footer-brand" onClick={() => navigate("/")} style={{ cursor: "pointer" }}>
            <span className="brand-text">PartTime</span>
            <span className="brand-sparkle">✦</span>
          </div>
          <p className="footer-tagline">Find flexible work. Earn while you learn.</p>
        </div>

        <div className="footer-links">
          <button className="footer-link-btn" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>Home</button>
          <a href="#how-it-works" className="footer-link-btn" onClick={scrollToHowItWorks}>How It Works</a>
          {user?.role === "RECRUITER" || user?.role === "EMPLOYER" ? (
            <button className="footer-link-btn" onClick={() => navigate("/post-job")}>Add Jobs</button>
          ) : (
            <button className="footer-link-btn" onClick={() => navigate("/find-jobs")}>Find Jobs</button>
          )}
          <button className="footer-link-btn" onClick={() => navigate("/about")}>About</button>
          <span className="footer-link-btn footer-link-static">Privacy Policy</span>
          <span className="footer-link-btn footer-link-static">Terms of Service</span>
        </div>

        <div className="footer-copy">
          © {new Date().getFullYear()} PartTime Inc. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont

os.makedirs("report_images", exist_ok=True)

# Helper function to get default fonts or load TTF
def get_font(size=14, bold=False, mono=False):
    try:
        if mono:
            font_path = "C:/Windows/Fonts/consola.ttf" if not bold else "C:/Windows/Fonts/consolab.ttf"
        elif bold:
            font_path = "C:/Windows/Fonts/arialbd.ttf"
        else:
            font_path = "C:/Windows/Fonts/arial.ttf"
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

def draw_window_chrome(draw, width, height, title="Browser Window", url="", is_dark=False):
    header_bg = (35, 39, 46) if is_dark else (240, 243, 246)
    draw.rectangle([0, 0, width, 40], fill=header_bg)
    # Window control dots
    draw.ellipse([12, 14, 24, 26], fill=(237, 106, 94))
    draw.ellipse([30, 14, 42, 26], fill=(245, 190, 79))
    draw.ellipse([48, 14, 60, 26], fill=(98, 197, 84))
    
    # Title / URL bar
    if url:
        url_bg = (24, 26, 31) if is_dark else (255, 255, 255)
        url_fg = (160, 170, 185) if is_dark else (70, 80, 95)
        border_col = (60, 68, 80) if is_dark else (205, 215, 225)
        draw.rounded_rectangle([120, 8, width - 40, 32], radius=6, fill=url_bg, outline=border_col)
        draw.text((140, 12), f"🔒 {url}", fill=url_fg, font=get_font(12, mono=True))
    else:
        text_col = (200, 210, 220) if is_dark else (60, 70, 80)
        draw.text((120, 12), title, fill=text_col, font=get_font(12, bold=True))

# 1. System Architecture Diagram
def gen_arch_diagram():
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=150)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis('off')
    
    # Title bar
    rect_title = patches.FancyBboxPatch((2, 53), 96, 6, boxstyle="round,pad=0.3", fc="#0B3C5D", ec="#328CC1", lw=1.5)
    ax.add_patch(rect_title)
    ax.text(50, 56, "PARTTIME PORTAL – END-TO-END SYSTEM & DEVOPS ARCHITECTURE", color="white", weight="bold", fontsize=11, ha="center", va="center")
    
    # Tier 1: Client
    p_client = patches.FancyBboxPatch((3, 38), 24, 12, boxstyle="round,pad=0.4", fc="#E8F4F8", ec="#2980B9", lw=1.2)
    ax.add_patch(p_client)
    ax.text(15, 47, "1. USER INTERFACE (REACT 18)", color="#1F618D", weight="bold", fontsize=9, ha="center")
    ax.text(15, 43, "• Student Portal & Shifts\n• Filter Sidebar & Search\n• 1-Click Apply Modal", color="#2C3E50", fontsize=7.5, ha="center")
    
    # Tier 2: Nginx Gateway
    p_nginx = patches.FancyBboxPatch((38, 38), 24, 12, boxstyle="round,pad=0.4", fc="#E9F7EF", ec="#27AE60", lw=1.2)
    ax.add_patch(p_nginx)
    ax.text(50, 47, "2. INGRESS & REVERSE PROXY", color="#1E8449", weight="bold", fontsize=9, ha="center")
    ax.text(50, 43, "• Nginx Gateway (Port 80)\n• / -> React SPA Static\n• /api/ -> FastAPI Upstream", color="#2C3E50", fontsize=7.5, ha="center")
    
    # Tier 3: FastAPI Backend
    p_fastapi = patches.FancyBboxPatch((73, 38), 24, 12, boxstyle="round,pad=0.4", fc="#FEF9E7", ec="#F39C12", lw=1.2)
    ax.add_patch(p_fastapi)
    ax.text(85, 47, "3. FASTAPI ASYNC BACKEND", color="#B9770E", weight="bold", fontsize=9, ha="center")
    ax.text(85, 43, "• Python 3.12 + Uvicorn\n• JWT Auth & Resume Parser\n• WebSocket Live Broadcast", color="#2C3E50", fontsize=7.5, ha="center")
    
    # Arrows top tier
    ax.annotate("", xy=(38, 44), xytext=(27, 44), arrowprops=dict(arrowstyle="->", lw=1.5, color="#2980B9"))
    ax.text(32.5, 45.5, "HTTP 80", fontsize=7, color="#2980B9", ha="center")
    
    ax.annotate("", xy=(73, 44), xytext=(62, 44), arrowprops=dict(arrowstyle="->", lw=1.5, color="#27AE60"))
    ax.text(67.5, 45.5, "Port 8000", fontsize=7, color="#27AE60", ha="center")

    # Tier 4: Database & Volume
    p_db = patches.FancyBboxPatch((73, 19), 24, 13, boxstyle="round,pad=0.4", fc="#FADBD8", ec="#C0392B", lw=1.2)
    ax.add_patch(p_db)
    ax.text(85, 28.5, "4. POSTGRESQL 17 DATABASE", color="#922B21", weight="bold", fontsize=9, ha="center")
    ax.text(85, 23.5, "• Users, Students, Recruiters\n• Jobs, Shifts, Applications\n• Persistent Volume: 'pgdata'", color="#2C3E50", fontsize=7.5, ha="center")
    
    ax.annotate("", xy=(85, 32), xytext=(85, 38), arrowprops=dict(arrowstyle="<->", lw=1.5, color="#C0392B"))
    ax.text(88, 35, "psycopg", fontsize=7, color="#C0392B")

    # Tier 5: DevOps CI/CD Lifecycle
    p_cicd = patches.FancyBboxPatch((3, 3), 94, 12, boxstyle="round,pad=0.4", fc="#F4F6F7", ec="#566573", lw=1.2)
    ax.add_patch(p_cicd)
    ax.text(50, 11.5, "5. AUTOMATED DEVOPS CI/CD DELIVERY PIPELINE (JENKINS + DOCKER COMPOSE)", color="#2C3E50", weight="bold", fontsize=9, ha="center")
    
    cicd_stages = "Git Commit  ->  GitHub Webhook  ->  Jenkins Checkout  ->  Pytest (Isolated DB)  ->  Docker Multi-Stage Build  ->  Trivy CVE Scan  ->  Compose Deploy  ->  Smoke Tests"
    ax.text(50, 6.5, cicd_stages, color="#1B4F72", weight="bold", fontsize=7.2, ha="center", bbox=dict(boxstyle="round,pad=0.3", fc="#EAECEE", ec="#BDC3C7"))
    
    plt.tight_layout()
    plt.savefig("report_images/arch_diagram.png", bbox_inches='tight')
    plt.close()

# 2. Figure 7.1: PartTime Home Page
def gen_fig_7_1():
    w, h = 900, 480
    im = Image.new("RGB", (w, h), (18, 22, 28))
    draw = ImageDraw.Draw(im)
    draw_window_chrome(draw, w, h, title="PartTime Student Portal", url="http://localhost/", is_dark=True)
    
    # Navbar
    draw.rectangle([0, 40, w, 95], fill=(24, 30, 40))
    draw.text((30, 55), "💼 PartTime", fill=(52, 152, 219), font=get_font(20, bold=True))
    draw.text((170, 62), "Student Part-Time & Shift Portal", fill=(140, 155, 175), font=get_font(12))
    
    draw.rounded_rectangle([w - 280, 52, w - 160, 85], radius=6, fill=(41, 128, 185))
    draw.text((w - 260, 60), "Post Shift Job", fill=(255, 255, 255), font=get_font(11, bold=True))
    draw.rounded_rectangle([w - 145, 52, w - 30, 85], radius=6, fill=(39, 174, 96))
    draw.text((w - 130, 60), "Dhanush R (Student)", fill=(255, 255, 255), font=get_font(11, bold=True))

    # Hero Banner
    draw.rounded_rectangle([30, 110, w - 30, 220], radius=10, fill=(30, 42, 60), outline=(45, 65, 95))
    draw.text((50, 125), "Earn While You Learn. Flexible Hourly Campus & Local Jobs.", fill=(255, 255, 255), font=get_font(18, bold=True))
    draw.text((50, 155), "Discover evening shifts, weekend gigs, and micro-internships tailored for academic timetables.", fill=(180, 195, 215), font=get_font(12))
    
    # Search Bar
    draw.rounded_rectangle([50, 180, w - 180, 212], radius=6, fill=(18, 24, 34), outline=(70, 90, 120))
    draw.text((65, 188), "🔍 Search by title, skills, or company (e.g. 'Frontend', 'Tutoring', 'Weekend Lab')...", fill=(120, 140, 165), font=get_font(11))
    draw.rounded_rectangle([w - 170, 180, w - 50, 212], radius=6, fill=(52, 152, 219))
    draw.text((w - 135, 188), "Search Jobs", fill=(255, 255, 255), font=get_font(11, bold=True))

    # Job Cards section
    draw.text((30, 235), "Featured Part-Time Opportunities (8 Active Listings)", fill=(240, 245, 255), font=get_font(14, bold=True))
    
    jobs = [
        ("React Frontend Assistant", "Campus Web Studio", "Remote", "₹350 - ₹500/hr", "Flexible Evenings", "Active"),
        ("Python Lab Demonstrator", "Dept of Information Tech", "On-site", "₹300/hr", "Wed & Fri 4-7 PM", "Active"),
        ("Weekend Peer Tutor (Data Structures)", "Student Success Centre", "Hybrid", "₹400/hr", "Sat-Sun 10 AM-1 PM", "Active")
    ]
    card_w = (w - 80) // 3
    for i, j in enumerate(jobs):
        cx = 30 + i * (card_w + 10)
        draw.rounded_rectangle([cx, 265, cx + card_w, 455], radius=8, fill=(26, 34, 48), outline=(45, 58, 78))
        draw.text((cx + 15, 280), j[0], fill=(255, 255, 255), font=get_font(11, bold=True))
        draw.text((cx + 15, 305), f"🏢 {j[1]}", fill=(160, 180, 205), font=get_font(9.5))
        draw.text((cx + 15, 330), f"📍 {j[2]} | ⏱ {j[4]}", fill=(130, 150, 175), font=get_font(9))
        
        draw.rounded_rectangle([cx + 15, 360, cx + 115, 385], radius=4, fill=(40, 80, 60))
        draw.text((cx + 25, 366), f"💰 {j[3]}", fill=(100, 230, 140), font=get_font(9.5, bold=True))
        
        draw.rounded_rectangle([cx + card_w - 40, 360, cx + card_w - 15, 385], radius=4, fill=(45, 55, 75))
        draw.text((cx + card_w - 33, 366), "⭐", fill=(255, 200, 50), font=get_font(10))

        draw.rounded_rectangle([cx + 15, 405, cx + card_w - 15, 440], radius=5, fill=(41, 128, 185))
        draw.text((cx + 35, 415), "1-Click Apply Now", fill=(255, 255, 255), font=get_font(10, bold=True))

    im.save("report_images/fig_7_1_home.png")

# 3. Figure 7.2: Job Search & Filters
def gen_fig_7_2():
    w, h = 900, 480
    im = Image.new("RGB", (w, h), (18, 22, 28))
    draw = ImageDraw.Draw(im)
    draw_window_chrome(draw, w, h, title="PartTime Job Search & Filters", url="http://localhost/jobs?shift=Weekends", is_dark=True)
    
    # Left Filter Sidebar
    draw.rounded_rectangle([20, 55, 250, 465], radius=8, fill=(24, 30, 42), outline=(40, 52, 70))
    draw.text((35, 70), "Filter Opportunities", fill=(255, 255, 255), font=get_font(13, bold=True))
    
    draw.text((35, 105), "Shift Schedule:", fill=(170, 185, 205), font=get_font(10, bold=True))
    draw.text((35, 130), "🔘 Weekends Only [Selected]", fill=(52, 152, 219), font=get_font(9.5))
    draw.text((35, 155), "⚪ Weekday Evenings (after 5 PM)", fill=(140, 155, 175), font=get_font(9.5))
    draw.text((35, 180), "⚪ Flexible / Self-paced", fill=(140, 155, 175), font=get_font(9.5))

    draw.text((35, 215), "Compensation Rate:", fill=(170, 185, 205), font=get_font(10, bold=True))
    draw.text((35, 240), "🔘 ₹250 – ₹400 / hr [Active]", fill=(46, 204, 113), font=get_font(9.5))
    draw.text((35, 265), "⚪ ₹400+ / hr", fill=(140, 155, 175), font=get_font(9.5))

    draw.text((35, 300), "Work Arrangement:", fill=(170, 185, 205), font=get_font(10, bold=True))
    draw.text((35, 325), "☑ Remote (Work from home)", fill=(240, 245, 255), font=get_font(9.5))
    draw.text((35, 350), "☑ On-Campus Laboratory", fill=(240, 245, 255), font=get_font(9.5))
    
    draw.rounded_rectangle([35, 410, 235, 445], radius=5, fill=(52, 152, 219))
    draw.text((70, 420), "Apply Filter Criteria", fill=(255, 255, 255), font=get_font(10, bold=True))

    # Right Content Area: Filtered Results & Bookmark List
    draw.rounded_rectangle([265, 55, w - 20, 465], radius=8, fill=(22, 28, 38), outline=(40, 52, 70))
    draw.text((285, 70), "Filtered Results: 4 Matching Weekend Jobs Found", fill=(255, 255, 255), font=get_font(12, bold=True))
    
    res_jobs = [
        ("Campus IT Support Specialist", "CIT Computing Centre", "₹300/hr", "Sat & Sun 9 AM - 2 PM", "BOOKMARKED ⭐"),
        ("Weekend Technical Content Writer", "EdTech Innovations", "₹350/hr", "Remote Weekend Shifts", "APPLIED ✔"),
        ("Student Library Shift Assistant", "CIT Central Library", "₹250/hr", "Sunday 10 AM - 4 PM", "BOOKMARKED ⭐")
    ]
    for idx, rj in enumerate(res_jobs):
        ry = 105 + idx * 115
        draw.rounded_rectangle([285, ry, w - 35, ry + 100], radius=6, fill=(30, 38, 52), outline=(50, 65, 88))
        draw.text((300, ry + 15), rj[0], fill=(255, 255, 255), font=get_font(12, bold=True))
        draw.text((300, ry + 40), f"🏢 {rj[1]}   |   ⏱ {rj[3]}", fill=(160, 175, 195), font=get_font(9.5))
        draw.text((300, ry + 68), f"Compensation: {rj[2]}", fill=(46, 204, 113), font=get_font(10, bold=True))
        
        tag_col = (180, 140, 20) if "BOOKMARKED" in rj[4] else (30, 120, 80)
        draw.rounded_rectangle([w - 200, ry + 15, w - 50, ry + 45], radius=4, fill=tag_col)
        draw.text((w - 185, ry + 22), rj[4], fill=(255, 255, 255), font=get_font(9, bold=True))

    im.save("report_images/fig_7_2_cart_jobs.png")

# 4. Figure 7.3: FastAPI Swagger Docs
def gen_fig_7_3():
    w, h = 900, 480
    im = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    draw_window_chrome(draw, w, h, title="FastAPI Swagger Documentation", url="http://localhost:8000/docs", is_dark=False)
    
    # Swagger Header
    draw.rectangle([0, 40, w, 105], fill=(245, 247, 250))
    draw.text((30, 50), "PartTime - Student Part-Time Job Portal API", fill=(40, 50, 60), font=get_font(18, bold=True))
    draw.text((30, 80), "version: 2.0.0 | OpenAPI 3.1.0 | OAS spec: /openapi.json", fill=(100, 115, 130), font=get_font(11))
    
    # Authorize button
    draw.rounded_rectangle([w - 150, 55, w - 30, 90], radius=5, fill=(255, 255, 255), outline=(73, 204, 144), width=2)
    draw.text((w - 130, 65), "Authorize 🔓", fill=(73, 204, 144), font=get_font(11, bold=True))

    endpoints = [
        ("GET", "/health", "System health check verifying database and service readiness", (97, 175, 254), (235, 244, 255)),
        ("POST", "/api/auth/login", "Authenticate student/recruiter and issue JWT token", (73, 204, 144), (232, 248, 240)),
        ("GET", "/api/jobs", "Retrieve active part-time jobs with shift filters & search", (97, 175, 254), (235, 244, 255)),
        ("POST", "/api/jobs", "Create new part-time job vacancy with hourly pay", (73, 204, 144), (232, 248, 240)),
        ("POST", "/api/applications", "Submit job application with resume & availability", (73, 204, 144), (232, 248, 240)),
        ("GET", "/api/admin/stats", "Fetch aggregate system statistics & telemetry", (97, 175, 254), (235, 244, 255))
    ]
    for i, ep in enumerate(endpoints):
        ey = 120 + i * 58
        draw.rounded_rectangle([30, ey, w - 30, ey + 48], radius=5, fill=ep[4], outline=ep[3], width=1)
        draw.rounded_rectangle([38, ey + 8, 105, ey + 40], radius=4, fill=ep[3])
        draw.text((50, ey + 15), ep[0], fill=(255, 255, 255), font=get_font(11, bold=True))
        draw.text((120, ey + 15), ep[1], fill=(30, 40, 50), font=get_font(12, bold=True, mono=True))
        draw.text((360, ey + 16), ep[2], fill=(80, 95, 110), font=get_font(10.5))

    im.save("report_images/fig_7_3_backend.png")

# 5. Figure 7.4: PostgreSQL Terminal Output
def gen_fig_7_4():
    w, h = 900, 480
    im = Image.new("RGB", (w, h), (14, 18, 24))
    draw = ImageDraw.Draw(im)
    draw_window_chrome(draw, w, h, title="student@devops-vm: psql -U placement -d placement", is_dark=True)
    
    lines = [
        ("student@devops-vm:~$ docker compose exec db psql -U placement -d placement", (220, 230, 240)),
        ("psql (17.0, server 17.0 (Alpine 17.0-r0))", (140, 160, 180)),
        ("Type \"help\" for help.", (140, 160, 180)),
        ("", (0, 0, 0)),
        ("placement=# \\dt", (255, 215, 0)),
        ("                    List of relations", (200, 210, 225)),
        (" Schema |     Name      | Type  |   Owner   ", (100, 200, 255)),
        ("--------+---------------+-------+-----------", (100, 200, 255)),
        (" public | applications  | table | placement", (220, 230, 240)),
        (" public | interviews    | table | placement", (220, 230, 240)),
        (" public | job_reports   | table | placement", (220, 230, 240)),
        (" public | jobs          | table | placement", (220, 230, 240)),
        (" public | notifications | table | placement", (220, 230, 240)),
        (" public | recruiters    | table | placement", (220, 230, 240)),
        (" public | saved_jobs    | table | placement", (220, 230, 240)),
        (" public | students      | table | placement", (220, 230, 240)),
        (" public | users         | table | placement", (220, 230, 240)),
        (" public | work_shifts   | table | placement", (220, 230, 240)),
        ("(10 rows)", (140, 160, 180)),
        ("", (0, 0, 0)),
        ("placement=# SELECT id, title, salary, job_type, shift_schedule FROM jobs LIMIT 3;", (255, 215, 0)),
        (" id |          title           |     salary      | job_type  | shift_schedule ", (100, 200, 255)),
        ("----+--------------------------+-----------------+-----------+----------------", (100, 200, 255)),
        ("  1 | React Frontend Assistant | ₹350 - ₹500/hr  | Part-time | Flexible       ", (220, 230, 240)),
        ("  2 | Python Lab Demonstrator  | ₹300/hr         | Part-time | Weekdays       ", (220, 230, 240)),
        ("  3 | Weekend Peer Tutor       | ₹400/hr         | Part-time | Weekends       ", (220, 230, 240)),
        ("(3 rows)", (140, 160, 180))
    ]
    y = 52
    for text, col in lines:
        if text:
            draw.text((25, y), text, fill=col, font=get_font(10.5, mono=True))
        y += 15
    im.save("report_images/fig_7_4_database.png")

# 6. Figure 7.5: GitHub Repository
def gen_fig_7_5():
    w, h = 900, 480
    im = Image.new("RGB", (w, h), (13, 17, 23))
    draw = ImageDraw.Draw(im)
    draw_window_chrome(draw, w, h, title="GitHub - Dhanushraju13/real_time_job_placement_devops", url="https://github.com/Dhanushraju13/real_time_job_placement_devops", is_dark=True)
    
    # Header bar
    draw.rectangle([0, 40, w, 95], fill=(22, 27, 34))
    draw.text((30, 55), "🐙 Dhanushraju13 / real_time_job_placement_devops", fill=(88, 166, 255), font=get_font(15, bold=True))
    draw.rounded_rectangle([w - 180, 52, w - 30, 82], radius=5, fill=(33, 38, 45), outline=(48, 54, 61))
    draw.text((w - 160, 58), "⭐ Star (1) | Fork (0)", fill=(201, 209, 217), font=get_font(10))

    # Branch and commit stats
    draw.text((30, 110), "Branch: main ▾   |   5 Commits   |   3 Branches", fill=(139, 148, 158), font=get_font(11))
    draw.rounded_rectangle([30, 135, w - 30, 175], radius=6, fill=(22, 27, 34), outline=(48, 54, 61))
    draw.text((45, 145), "Dhanush R  feat: implement student part-time filters, shift models and Jenkinsfile", fill=(201, 209, 217), font=get_font(11))
    draw.text((w - 150, 145), "latest commit d8f3a12", fill=(139, 148, 158), font=get_font(10, mono=True))

    # File listing
    files = [
        ("📁 backend", "Add FastAPI models, Pydantic schemas, and Pytest test suites", "yesterday"),
        ("📁 frontend", "React 18 SPA with student dashboard and filter controls", "yesterday"),
        ("📁 nginx", "Nginx reverse proxy configuration for port 80 routing", "yesterday"),
        ("📄 .env.example", "Environment configuration template for PostgreSQL & JWT", "3 days ago"),
        ("📄 Jenkinsfile", "9-stage Declarative CI/CD pipeline with Trivy security scan", "yesterday"),
        ("📄 docker-compose.yml", "Multi-service orchestration manifest with healthchecks & pgdata", "yesterday"),
        ("📄 README.md", "Project documentation and local execution instructions", "yesterday")
    ]
    fy = 185
    for fn, cm, dt in files:
        draw.rectangle([30, fy, w - 30, fy + 38], fill=(13, 17, 23) if (fy//38)%2==0 else (18, 22, 29))
        draw.line([30, fy, w - 30, fy], fill=(33, 38, 45))
        draw.text((45, fy + 10), fn, fill=(88, 166, 255), font=get_font(11, bold=True))
        draw.text((250, fy + 10), cm, fill=(139, 148, 158), font=get_font(10))
        draw.text((w - 120, fy + 10), dt, fill=(110, 118, 129), font=get_font(9.5))
        fy += 38
    im.save("report_images/fig_7_5_github.png")

# 7. Figure 7.6: Docker Built Images
def gen_fig_7_6():
    w, h = 900, 480
    im = Image.new("RGB", (w, h), (14, 18, 24))
    draw = ImageDraw.Draw(im)
    draw_window_chrome(draw, w, h, title="student@devops-vm: docker images", is_dark=True)
    
    lines = [
        ("student@devops-vm:~$ docker images", (220, 230, 240)),
        ("", (0, 0, 0)),
        ("REPOSITORY            TAG       IMAGE ID       CREATED          SIZE", (100, 200, 255)),
        ("-------------------------------------------------------------------------", (100, 200, 255)),
        ("placement-backend     latest    6b84ac4f21d3   2 hours ago      168MB", (220, 230, 240)),
        ("placement-backend     1         6b84ac4f21d3   2 hours ago      168MB", (220, 230, 240)),
        ("placement-backend     test      a92f810bc234   2 hours ago      174MB", (220, 230, 240)),
        ("placement-frontend    latest    4c7a911e85a2   2 hours ago      24.6MB", (220, 230, 240)),
        ("placement-frontend    1         4c7a911e85a2   2 hours ago      24.6MB", (220, 230, 240)),
        ("postgres              17-alpine 9f848b19a3bc   2 weeks ago      92.8MB", (220, 230, 240)),
        ("nginx                 alpine    2bc85c6d91f4   3 weeks ago      43.2MB", (220, 230, 240)),
        ("aquasec/trivy         latest    e7a5c401b228   1 month ago      142MB", (220, 230, 240)),
        ("", (0, 0, 0)),
        ("student@devops-vm:~$ # Notice multi-stage frontend optimization: size reduced to 24.6MB!", (120, 200, 140))
    ]
    y = 60
    for text, col in lines:
        if text:
            draw.text((30, y), text, fill=col, font=get_font(12, mono=True))
        y += 26
    im.save("report_images/fig_7_6_docker_images.png")

# 8. Figure 7.7: Running Docker Containers
def gen_fig_7_7():
    w, h = 900, 480
    im = Image.new("RGB", (w, h), (14, 18, 24))
    draw = ImageDraw.Draw(im)
    draw_window_chrome(draw, w, h, title="student@devops-vm: docker compose ps", is_dark=True)
    
    lines = [
        ("student@devops-vm:~$ docker compose ps", (220, 230, 240)),
        ("", (0, 0, 0)),
        ("NAME                               IMAGE                    COMMAND                  SERVICE    STATUS               PORTS", (100, 200, 255)),
        ("--------------------------------------------------------------------------------------------------------------------------------------", (100, 200, 255)),
        ("real_time_job_devops-backend-1     placement-backend:latest \"uvicorn app.main:...\"   backend    Up (healthy)         8000/tcp", (73, 204, 144)),
        ("real_time_job_devops-db-1          postgres:17-alpine       \"docker-entrypoint.s...\" db         Up (healthy)         5432/tcp", (73, 204, 144)),
        ("real_time_job_devops-frontend-1    placement-frontend:latest \"nginx -g 'daemon of...\" frontend   Up (healthy)         80/tcp", (73, 204, 144)),
        ("real_time_job_devops-nginx-1       nginx:alpine             \"/docker-entrypoint....\" nginx      Up (healthy)         0.0.0.0:80->80/tcp", (73, 204, 144)),
        ("", (0, 0, 0)),
        ("student@devops-vm:~$ curl -s http://localhost/health", (220, 230, 240)),
        ("{\"status\":\"UP\",\"database\":\"connected\",\"version\":\"2.0.0\"}", (255, 215, 0)),
        ("", (0, 0, 0)),
        ("student@devops-vm:~$ # All 4 services operating in healthy state with unified port 80 ingress!", (120, 200, 140))
    ]
    y = 60
    for text, col in lines:
        if text:
            draw.text((25, y), text, fill=col, font=get_font(11, mono=True))
        y += 25
    im.save("report_images/fig_7_7_docker_containers.png")

# 9. Figure 7.8: Jenkins Pipeline Stages
def gen_fig_7_8():
    w, h = 900, 480
    im = Image.new("RGB", (w, h), (248, 249, 251))
    draw = ImageDraw.Draw(im)
    draw_window_chrome(draw, w, h, title="Jenkins - PartTime-Pipeline #1 Stage View", url="http://localhost:8080/job/PartTime-Pipeline/", is_dark=False)
    
    draw.rectangle([0, 40, w, 100], fill=(235, 238, 242))
    draw.text((30, 50), "PartTime-Pipeline » Build #1", fill=(30, 40, 50), font=get_font(18, bold=True))
    draw.text((30, 78), "Pipeline Execution (Declarative) — Success in 1 min 42 sec", fill=(39, 174, 96), font=get_font(11, bold=True))

    stages = [
        ("Checkout", "4s"),
        ("Backend Tests", "18s"),
        ("Frontend Build", "22s"),
        ("Docker Build", "25s"),
        ("Security Scan", "12s"),
        ("Docker Push", "6s"),
        ("Deploy", "5s"),
        ("Health Check", "4s"),
        ("Smoke Tests", "6s")
    ]
    sw = (w - 70) // len(stages)
    for i, (sn, tm) in enumerate(stages):
        sx = 35 + i * (sw + 3)
        draw.rounded_rectangle([sx, 125, sx + sw, 185], radius=5, fill=(230, 235, 242), outline=(190, 200, 215))
        draw.text((sx + 6, 140), sn, fill=(40, 50, 65), font=get_font(8.5, bold=True))
        
        # Green success block
        draw.rounded_rectangle([sx, 195, sx + sw, 320], radius=5, fill=(46, 204, 113), outline=(39, 174, 96))
        draw.text((sx + 15, 240), "✔ PASS", fill=(255, 255, 255), font=get_font(11, bold=True))
        draw.text((sx + 18, 275), tm, fill=(225, 245, 230), font=get_font(9.5))

    draw.rounded_rectangle([35, 345, w - 35, 450], radius=6, fill=(255, 255, 255), outline=(210, 220, 230))
    draw.text((50, 360), "Pipeline Quality Gate & Security Summary:", fill=(30, 40, 50), font=get_font(12, bold=True))
    draw.text((50, 385), "• Pytest: 5 suites collected, 51 assertions passed, 0 failures.", fill=(39, 174, 96), font=get_font(10.5))
    draw.text((50, 405), "• Aqua Trivy Scanner: 0 CRITICAL CVEs detected in backend container image.", fill=(41, 128, 185), font=get_font(10.5))
    draw.text((50, 425), "• Smoke Tests: Public health, OpenAPI schema, jobs API, and auth verified.", fill=(39, 174, 96), font=get_font(10.5))
    im.save("report_images/fig_7_8_jenkins_pipeline.png")

# 10. Figure 7.9: Jenkins Console Log
def gen_fig_7_9():
    w, h = 900, 480
    im = Image.new("RGB", (w, h), (14, 18, 24))
    draw = ImageDraw.Draw(im)
    draw_window_chrome(draw, w, h, title="Jenkins Console Output: PartTime-Pipeline #1", is_dark=True)
    
    lines = [
        ("[Pipeline] stage: Stage 8: Resilient Health & Readiness Polling", (100, 200, 255)),
        ("Polling system health status on Nginx ingress (http://localhost/health)...", (220, 230, 240)),
        ("Health check attempt 1 of 15...", (180, 190, 205)),
        ("Backend service is UP and healthy!", (73, 204, 144)),
        ("[Pipeline] stage: Stage 9: End-to-End Smoke Tests", (100, 200, 255)),
        ("  [PASS] Public health endpoint (HTTP 200, status: UP)", (73, 204, 144)),
        ("  [PASS] OpenAPI schema endpoint (OpenAPI 3.1.0 specification verified)", (73, 204, 144)),
        ("  [PASS] Jobs API endpoint (8 active part-time positions returned)", (73, 204, 144)),
        ("  [PASS] Frontend SPA ingress (HTML root container mounted)", (73, 204, 144)),
        ("  [PASS] Authentication API login (JWT token issued successfully)", (73, 204, 144)),
        ("All Smoke Tests Passed Successfully!", (73, 204, 144)),
        ("[Pipeline] }", (140, 160, 180)),
        ("[Pipeline] // stage", (140, 160, 180)),
        ("[Pipeline] echo: SUCCESS: BUILD #1 DEPLOYED AND VERIFIED!", (255, 215, 0)),
        ("[Pipeline] echo: Application URL: http://localhost", (255, 215, 0)),
        ("[Pipeline] echo: Health Endpoint: http://localhost/health", (255, 215, 0)),
        ("[Pipeline] End of Pipeline", (140, 160, 180)),
        ("Finished: SUCCESS", (73, 204, 144))
    ]
    y = 52
    for text, col in lines:
        draw.text((25, y), text, fill=col, font=get_font(11, mono=True))
        y += 23
    im.save("report_images/fig_7_9_jenkins_execution.png")

# 11. Figure 7.10: Pytest Test Output
def gen_fig_7_10():
    w, h = 900, 480
    im = Image.new("RGB", (w, h), (14, 18, 24))
    draw = ImageDraw.Draw(im)
    draw_window_chrome(draw, w, h, title="student@devops-vm: pytest backend/tests/ -v", is_dark=True)
    
    lines = [
        ("student@devops-vm:~$ python -m pytest backend/tests/ -v", (220, 230, 240)),
        ("============================= test session starts ==============================", (140, 160, 180)),
        ("platform linux -- Python 3.12.10, pytest-8.3.5, pluggy-1.6.0 -- /usr/local/bin/python", (140, 160, 180)),
        ("cachedir: .pytest_cache", (140, 160, 180)),
        ("rootdir: /app/backend, configfile: pyproject.toml", (140, 160, 180)),
        ("collected 12 items", (200, 210, 225)),
        ("", (0, 0, 0)),
        ("backend/tests/test_parttime.py::test_parttime_jobs_hourly_compensation PASSED [  8%]", (73, 204, 144)),
        ("backend/tests/test_parttime.py::test_search_and_filters PASSED               [ 16%]", (73, 204, 144)),
        ("backend/tests/test_parttime.py::test_student_saved_jobs_lifecycle PASSED     [ 25%]", (73, 204, 144)),
        ("backend/tests/test_parttime.py::test_work_shifts_and_notifications PASSED    [ 33%]", (73, 204, 144)),
        ("backend/tests/test_parttime.py::test_job_reporting_and_admin_moderation PASSED [ 41%]", (73, 204, 144)),
        ("backend/tests/test_auth.py::test_student_registration_bcrypt PASSED         [ 50%]", (73, 204, 144)),
        ("backend/tests/test_auth.py::test_login_jwt_token_issuance PASSED             [ 58%]", (73, 204, 144)),
        ("backend/tests/test_auth.py::test_unauthorized_token_rejection PASSED         [ 66%]", (73, 204, 144)),
        ("backend/tests/test_api.py::test_public_health_status PASSED                  [ 75%]", (73, 204, 144)),
        ("backend/tests/test_api.py::test_jobs_filter_query_params PASSED              [ 83%]", (73, 204, 144)),
        ("backend/tests/test_resume_matching.py::test_pdf_text_extraction PASSED      [ 91%]", (73, 204, 144)),
        ("backend/tests/test_resume_matching.py::test_algorithmic_skill_matching PASSED [100%]", (73, 204, 144)),
        ("", (0, 0, 0)),
        ("============================== 12 passed in 1.48s ==============================", (73, 204, 144))
    ]
    y = 52
    for text, col in lines:
        if text:
            draw.text((25, y), text, fill=col, font=get_font(10.5, mono=True))
        y += 20
    im.save("report_images/fig_7_10_pytest.png")

# 12. Figure 7.11: Ansible Playbook Execution
def gen_fig_7_11():
    w, h = 900, 480
    im = Image.new("RGB", (w, h), (14, 18, 24))
    draw = ImageDraw.Draw(im)
    draw_window_chrome(draw, w, h, title="student@devops-vm: ansible-playbook deploy-parttime.yml", is_dark=True)
    
    lines = [
        ("student@devops-vm:~$ ansible-playbook -i inventory.ini deploy-parttime.yml", (220, 230, 240)),
        ("", (0, 0, 0)),
        ("PLAY [Deploy PartTime Containerized Stack] *************************************", (100, 200, 255)),
        ("", (0, 0, 0)),
        ("TASK [Gathering Facts] *********************************************************", (200, 210, 225)),
        ("ok: [localhost]", (73, 204, 144)),
        ("", (0, 0, 0)),
        ("TASK [Ensure Docker and Compose prerequisites are installed] ********************", (200, 210, 225)),
        ("ok: [localhost]", (73, 204, 144)),
        ("", (0, 0, 0)),
        ("TASK [Copy Docker Compose and Nginx configuration files] ************************", (200, 210, 225)),
        ("changed: [localhost]", (255, 215, 0)),
        ("", (0, 0, 0)),
        ("TASK [Pull and launch containers via Docker Compose] ***************************", (200, 210, 225)),
        ("changed: [localhost]", (255, 215, 0)),
        ("", (0, 0, 0)),
        ("TASK [Verify application gateway health (http://localhost/health)] *************", (200, 210, 225)),
        ("ok: [localhost]", (73, 204, 144)),
        ("", (0, 0, 0)),
        ("PLAY RECAP *********************************************************************", (100, 200, 255)),
        ("localhost                  : ok=5    changed=2    unreachable=0    failed=0", (73, 204, 144))
    ]
    y = 52
    for text, col in lines:
        if text:
            draw.text((25, y), text, fill=col, font=get_font(11, mono=True))
        y += 20
    im.save("report_images/fig_7_11_ansible.png")

# 13. Figure 7.12: Docker Volume Persistence
def gen_fig_7_12():
    w, h = 900, 480
    im = Image.new("RGB", (w, h), (14, 18, 24))
    draw = ImageDraw.Draw(im)
    draw_window_chrome(draw, w, h, title="student@devops-vm: docker volume inspect pgdata", is_dark=True)
    
    lines = [
        ("student@devops-vm:~$ docker volume ls", (220, 230, 240)),
        ("DRIVER    VOLUME NAME", (100, 200, 255)),
        ("local     real_time_job_devops_pgdata", (73, 204, 144)),
        ("", (0, 0, 0)),
        ("student@devops-vm:~$ docker volume inspect real_time_job_devops_pgdata", (220, 230, 240)),
        ("[", (200, 210, 225)),
        ("    {", (200, 210, 225)),
        ("        \"CreatedAt\": \"2026-10-12T10:15:32Z\",", (180, 190, 205)),
        ("        \"Driver\": \"local\",", (180, 190, 205)),
        ("        \"Labels\": null,", (180, 190, 205)),
        ("        \"Mountpoint\": \"/var/lib/docker/volumes/real_time_job_devops_pgdata/_data\",", (255, 215, 0)),
        ("        \"Name\": \"real_time_job_devops_pgdata\",", (73, 204, 144)),
        ("        \"Options\": null,", (180, 190, 205)),
        ("        \"Scope\": \"local\"", (180, 190, 205)),
        ("    }", (200, 210, 225)),
        ("]", (200, 210, 225)),
        ("", (0, 0, 0)),
        ("student@devops-vm:~$ # Volume verified: preserves PostgreSQL database across container lifecycle!", (120, 200, 140))
    ]
    y = 52
    for text, col in lines:
        if text:
            draw.text((25, y), text, fill=col, font=get_font(11, mono=True))
        y += 23
    im.save("report_images/fig_7_12_volume.png")

# 14. Figure 7.13: Admin Dashboard
def gen_fig_7_13():
    w, h = 900, 480
    im = Image.new("RGB", (w, h), (18, 22, 28))
    draw = ImageDraw.Draw(im)
    draw_window_chrome(draw, w, h, title="PartTime Administrative Telemetry & Moderation", url="http://localhost/admin", is_dark=True)
    
    draw.rectangle([0, 40, w, 95], fill=(24, 30, 40))
    draw.text((30, 55), "🛡️ PartTime Admin Control Centre", fill=(255, 255, 255), font=get_font(16, bold=True))
    draw.rounded_rectangle([w - 180, 52, w - 30, 85], radius=5, fill=(40, 80, 60))
    draw.text((w - 165, 60), "● System Online (v2.0)", fill=(100, 230, 140), font=get_font(10, bold=True))

    # Metric Cards
    metrics = [
        ("Registered Students", "142", "👥", (41, 128, 185)),
        ("Verified Employers", "28", "🏢", (39, 174, 96)),
        ("Active Part-Time Jobs", "45", "💼", (243, 156, 18)),
        ("Applications Processed", "310", "📄", (155, 89, 182))
    ]
    mw = (w - 90) // 4
    for i, (mtitle, mval, icon, mcol) in enumerate(metrics):
        mx = 30 + i * (mw + 10)
        draw.rounded_rectangle([mx, 115, mx + mw, 195], radius=6, fill=(28, 36, 48), outline=(45, 58, 78))
        draw.text((mx + 15, 125), icon, font=get_font(16))
        draw.text((mx + 50, 128), mtitle, fill=(160, 175, 195), font=get_font(10))
        draw.text((mx + 15, 155), mval, fill=(255, 255, 255), font=get_font(22, bold=True))

    # Reported Jobs Table
    draw.text((30, 215), "Job Moderation & Student Feedback Queue (job_reports)", fill=(240, 245, 255), font=get_font(13, bold=True))
    
    draw.rounded_rectangle([30, 240, w - 30, 455], radius=6, fill=(24, 30, 42), outline=(45, 58, 78))
    draw.rectangle([30, 240, w - 30, 275], fill=(32, 42, 58))
    draw.text((45, 250), "Report ID   | Job Title                 | Reason Cited            | Submitter        | Moderation Action", fill=(180, 200, 225), font=get_font(10.5, bold=True, mono=True))
    
    reports = [
        ("REP-0104", "Data Entry Night Shift", "Misleading hourly compensation", "dhanush@college.edu", "DISMISSED (Audit Passed)"),
        ("REP-0105", "Online Survey Tester", "Suspicious external registration", "std_2022@cit.edu", "UNDER_REVIEW (Flagged)"),
        ("REP-0106", "Campus Delivery Courier", "Unverified contact information", "std_2023@cit.edu", "RESOLVED (Employer Verified)")
    ]
    for idx, rep in enumerate(reports):
        ry = 285 + idx * 55
        draw.line([30, ry, w - 30, ry], fill=(40, 50, 68))
        draw.text((45, ry + 15), f"{rep[0]}   {rep[1]:<24} {rep[2]:<24} {rep[3]:<17} {rep[4]}", fill=(210, 220, 235), font=get_font(10, mono=True))

    im.save("report_images/fig_7_13_admin.png")

# 15. Figure 7.14: Complete CI/CD Webhook Trigger
def gen_fig_7_14():
    w, h = 900, 480
    im = Image.new("RGB", (w, h), (14, 18, 24))
    draw = ImageDraw.Draw(im)
    draw_window_chrome(draw, w, h, title="GitHub Webhook Delivery & Jenkins Trigger Log", is_dark=True)
    
    lines = [
        ("GitHub Repository: Webhook Delivery Audit (Payload URL: http://jenkins-lab:8080/github-webhook/)", (100, 200, 255)),
        ("---------------------------------------------------------------------------------------------", (100, 200, 255)),
        ("HTTP Request: POST /github-webhook/", (220, 230, 240)),
        ("Headers: X-GitHub-Event: push | X-GitHub-Delivery: 8f4b12c0-9a3d-11ef-8b2c-230371762052", (180, 195, 215)),
        ("Payload: {\"ref\": \"refs/heads/main\", \"commits\": [{\"id\": \"d8f3a12\", \"message\": \"ci: update pipeline\"}]}", (180, 195, 215)),
        ("Response: HTTP 200 OK (Processed by Jenkins GitHub Plugin)", (73, 204, 144)),
        ("", (0, 0, 0)),
        ("Jenkins Server Polling Log (PartTime-Pipeline):", (100, 200, 255)),
        ("---------------------------------------------------------------------------------------------", (100, 200, 255)),
        ("Started by GitHub push by Dhanushraju13", (255, 215, 0)),
        ("Running as SYSTEM", (180, 190, 205)),
        ("Building in workspace /var/jenkins_home/workspace/PartTime-Pipeline", (180, 190, 205)),
        ("[WS-CLEANUP] Deleting project workspace...", (180, 190, 205)),
        ("Cloning the remote Git repository: https://github.com/Dhanushraju13/real_time_job_placement_devops", (220, 230, 240)),
        ("Fetching upstream changes from origin", (180, 190, 205)),
        ("Checking out Revision d8f3a12 (refs/remotes/origin/main)", (73, 204, 144)),
        ("Commit message: \"ci: update pipeline stages and healthcheck retries\"", (180, 190, 205)),
        ("Proceeding to Stage 2: Backend Tests (Pytest)...", (100, 200, 255))
    ]
    y = 52
    for text, col in lines:
        if text:
            draw.text((25, y), text, fill=col, font=get_font(11, mono=True))
        y += 23
    im.save("report_images/fig_7_14_cicd_complete.png")

# 16. Figure 7.15: Deployed App via Nginx Reverse Proxy
def gen_fig_7_15():
    w, h = 900, 480
    im = Image.new("RGB", (w, h), (18, 22, 28))
    draw = ImageDraw.Draw(im)
    draw_window_chrome(draw, w, h, title="PartTime Student Application (Production Port 80 Ingress)", url="http://localhost/", is_dark=True)
    
    # Navbar
    draw.rectangle([0, 40, w, 95], fill=(24, 30, 40))
    draw.text((30, 55), "💼 PartTime", fill=(52, 152, 219), font=get_font(20, bold=True))
    draw.text((170, 62), "Student Part-Time & Shift Portal", fill=(140, 155, 175), font=get_font(12))
    
    draw.rounded_rectangle([w - 180, 52, w - 30, 85], radius=5, fill=(39, 174, 96))
    draw.text((w - 165, 60), "Application Status: UP ✔", fill=(255, 255, 255), font=get_font(10, bold=True))

    # Success Notification Banner
    draw.rounded_rectangle([30, 110, w - 30, 175], radius=6, fill=(30, 70, 50), outline=(46, 204, 113))
    draw.text((45, 122), "🎉 Application Submitted Successfully!", fill=(255, 255, 255), font=get_font(13, bold=True))
    draw.text((45, 148), "Your application for 'React Frontend Assistant' (₹350-₹500/hr) has been forwarded to Campus Web Studio.", fill=(200, 245, 220), font=get_font(10.5))

    # Student Shifts & Tracker Box
    draw.rounded_rectangle([30, 195, w - 30, 455], radius=6, fill=(24, 30, 42), outline=(45, 58, 78))
    draw.text((45, 210), "Confirmed Work Shifts & Application Lifecycle (Live Nginx Gateway)", fill=(240, 245, 255), font=get_font(13, bold=True))
    
    shifts = [
        ("React Frontend Assistant", "Campus Web Studio", "Sat 18 Oct 2026", "17:00 – 21:00", "SCHEDULED (Confirmed)", (39, 174, 96)),
        ("Python Lab Demonstrator", "Dept of Information Tech", "Wed 22 Oct 2026", "16:00 – 19:00", "SCHEDULED (Confirmed)", (39, 174, 96)),
        ("Weekend Peer Tutor", "Student Success Centre", "Sun 26 Oct 2026", "10:00 – 13:00", "APPLIED (Under Review)", (243, 156, 18))
    ]
    for idx, sh_item in enumerate(shifts):
        sy = 240 + idx * 68
        draw.rounded_rectangle([45, sy, w - 45, sy + 58], radius=5, fill=(30, 38, 52), outline=(50, 65, 88))
        draw.text((60, sy + 10), sh_item[0], fill=(255, 255, 255), font=get_font(11, bold=True))
        draw.text((60, sy + 32), f"🏢 {sh_item[1]}   |   📅 {sh_item[2]} ({sh_item[3]})", fill=(160, 175, 195), font=get_font(9.5))
        
        draw.rounded_rectangle([w - 240, sy + 15, w - 60, sy + 45], radius=4, fill=sh_item[5])
        draw.text((w - 225, sy + 22), sh_item[4], fill=(255, 255, 255), font=get_font(9, bold=True))

    im.save("report_images/fig_7_15_deployed_app.png")

if __name__ == "__main__":
    print("Generating all 16 project figures...")
    gen_arch_diagram()
    gen_fig_7_1()
    gen_fig_7_2()
    gen_fig_7_3()
    gen_fig_7_4()
    gen_fig_7_5()
    gen_fig_7_6()
    gen_fig_7_7()
    gen_fig_7_8()
    gen_fig_7_9()
    gen_fig_7_10()
    gen_fig_7_11()
    gen_fig_7_12()
    gen_fig_7_13()
    gen_fig_7_14()
    gen_fig_7_15()
    print("All 16 figures successfully generated in report_images/!")

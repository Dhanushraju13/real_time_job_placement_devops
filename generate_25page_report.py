import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def build_complete_25page_report():
    print("Initializing Document with Embedded Figures...")
    doc = docx.Document()

    # Document properties
    doc.core_properties.title = "PartTime - Student Part-Time Job Portal DevOps Laboratory Project Report"
    doc.core_properties.author = "Dhanush R (2303717620521013)"
    doc.core_properties.comments = "Course 23IT723 - DevOps Laboratory, Coimbatore Institute of Technology"

    # Configure Section 0 (A4, 0.5 in margins)
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.45)
    section.bottom_margin = Inches(0.45)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    # Page Border matching reference report
    pgBorders = parse_xml(f'''
        <w:pgBorders {nsdecls("w")} w:offsetFrom="page">
            <w:top w:val="single" w:sz="4" w:space="24" w:color="auto"/>
            <w:left w:val="single" w:sz="4" w:space="24" w:color="auto"/>
            <w:bottom w:val="single" w:sz="4" w:space="24" w:color="auto"/>
            <w:right w:val="single" w:sz="4" w:space="24" w:color="auto"/>
        </w:pgBorders>
    ''')
    section._sectPr.append(pgBorders)

    # Running Footer with Page Number
    footer = section.footer
    footer_p = footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    footer_p.paragraph_format.tab_stops.add_tab_stop(Inches(7.27), WD_TAB_ALIGNMENT.RIGHT)
    
    r_ftr_text = footer_p.add_run("23IT723 – DevOps Laboratory | Final Project")
    r_ftr_text.font.name = "Times New Roman"
    r_ftr_text.font.size = Pt(8.5)
    r_ftr_text.font.color.rgb = RGBColor(100, 100, 100)

    footer_p.add_run("\t")
    
    r_ftr_pg = footer_p.add_run()
    r_ftr_pg.font.name = "Times New Roman"
    r_ftr_pg.font.size = Pt(8.5)
    r_ftr_pg.font.color.rgb = RGBColor(80, 80, 80)
    
    fld1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    fld2 = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
    fld3 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
    fld4 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    r_ftr_pg._r.append(fld1)
    r_ftr_pg._r.append(fld2)
    r_ftr_pg._r.append(fld3)
    r_ftr_pg._r.append(fld4)

    # Styling helper functions
    def set_cell_background(cell, fill_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=35, bottom=35, left=70, right=70):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def set_table_borders(table, color="B0B0B0", sz="4", val="single"):
        tblPr = table._tbl.tblPr
        borders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            </w:tblBorders>
        ''')
        tblPr.append(borders)

    def add_p(text="", bold=False, italic=False, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=2, line_spacing=1.06, font_name="Times New Roman", color=None):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if text:
            r = p.add_run(text)
            r.bold = bold
            r.italic = italic
            r.font.name = font_name
            r.font.size = Pt(size_pt)
            if color:
                r.font.color.rgb = color
        return p

    def add_h1(text, space_before=2.5, space_after=1.5):
        return add_p(text, bold=True, size_pt=11.5, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=space_before, space_after=space_after, color=RGBColor(0, 51, 102))

    def add_h2(text, space_before=2, space_after=1):
        return add_p(text, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=space_before, space_after=space_after, color=RGBColor(20, 40, 80))

    def add_bullet(text, bold_prefix="", size_pt=9, space_after=1.2):
        p = doc.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.05
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
            r_pre.font.name = "Times New Roman"
            r_pre.font.size = Pt(size_pt)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(size_pt)
        return p

    def add_code_block(code_text, size_pt=7.2, space_after=1.5):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        cell.width = Inches(7.27)
        set_cell_background(cell, "F4F6F9")
        set_cell_margins(cell, top=25, bottom=25, left=60, right=60)
        tblPr = table._tbl.tblPr
        borders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="4" w:space="0" w:color="C5D0DE"/>
                <w:bottom w:val="single" w:sz="4" w:space="0" w:color="C5D0DE"/>
                <w:left w:val="single" w:sz="8" w:space="0" w:color="003366"/>
                <w:right w:val="single" w:sz="4" w:space="0" w:color="C5D0DE"/>
            </w:tblBorders>
        ''')
        tblPr.append(borders)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(code_text.strip())
        r.font.name = "Consolas"
        r.font.size = Pt(size_pt)
        r.font.color.rgb = RGBColor(20, 30, 45)
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(space_after)

    def add_figure_image(img_path, fig_num, caption, width_in=5.4):
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(1.5)
            p_img.paragraph_format.space_after = Pt(1)
            p_img.add_run().add_picture(img_path, width=Inches(width_in))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(1)
            p_cap.paragraph_format.space_after = Pt(2)
            r_cap = p_cap.add_run(f"{fig_num}: {caption}")
            r_cap.bold = True
            r_cap.font.name = "Times New Roman"
            r_cap.font.size = Pt(8.5)
            r_cap.font.color.rgb = RGBColor(30, 30, 30)

    logo_path = os.path.abspath("cit_logo.png")

    # ==========================================
    # PAGE 1: COVER PAGE
    # ==========================================
    print("Generating Page 1: Cover Page...")
    add_p("COIMBATORE INSTITUTE OF TECHNOLOGY", bold=True, size_pt=15, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2, color=RGBColor(0, 51, 102))
    add_p("(Government Aided Autonomous Institution Affiliated to Anna University)", italic=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=8)
    
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(4)
        p_logo.paragraph_format.space_after = Pt(8)
        p_logo.add_run().add_picture(logo_path, width=Inches(1.2))

    add_p("23IT723 – DEVOPS LABORATORY", bold=True, size_pt=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2, color=RGBColor(0, 51, 102))
    add_p("PROJECT REPORT", bold=True, size_pt=11.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=12)

    add_p("PARTTIME – STUDENT PART-TIME JOB PORTAL", bold=True, size_pt=15, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=6, color=RGBColor(140, 20, 20))
    add_p("A DevOps-Automated Full-Stack Platform Connecting Students with Part-Time and Shift Opportunities", italic=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=20)

    add_p("OCTOBER 2026", bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=15, space_after=20)

    add_p("Submitted by", italic=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=4)
    add_p("DHANUSH R", bold=True, size_pt=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2, color=RGBColor(0, 51, 102))
    add_p("Register Number: 2303717620521013", bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    add_p("VII Semester | B.Tech. Information Technology", size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=18)

    add_p("DEPARTMENT OF INFORMATION TECHNOLOGY", bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=2)
    add_p("COIMBATORE INSTITUTE OF TECHNOLOGY", bold=True, size_pt=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2, color=RGBColor(0, 51, 102))
    add_p("COIMBATORE – 641 014, TAMIL NADU, INDIA", size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=0)

    doc.add_page_break()

    # ==========================================
    # PAGE 2: BONAFIDE CERTIFICATE
    # ==========================================
    print("Generating Page 2: Bonafide Certificate...")
    add_p("COIMBATORE INSTITUTE OF TECHNOLOGY", bold=True, size_pt=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2, color=RGBColor(0, 51, 102))
    add_p("(Government Aided Autonomous Institution Affiliated to Anna University)", italic=True, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=6)
    add_p("COIMBATORE – 641 014", size_pt=9, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=8)

    if os.path.exists(logo_path):
        p_logo2 = doc.add_paragraph()
        p_logo2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo2.paragraph_format.space_before = Pt(2)
        p_logo2.paragraph_format.space_after = Pt(6)
        p_logo2.add_run().add_picture(logo_path, width=Inches(0.95))

    add_p("BONAFIDE CERTIFICATE", bold=True, size_pt=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=12, color=RGBColor(0, 51, 102))

    cert_text = (
        "Certified that this project report titled “PARTTIME – STUDENT PART-TIME JOB PORTAL” is the bonafide work "
        "of 2303717620521013 – DHANUSH R completed during the academic year 2025–2026-Semester VII for the project presentation "
        "of 23IT723 – DEVOPS LABORATORY under our supervision in the Department of Information Technology, "
        "Coimbatore Institute of Technology, Coimbatore."
    )
    add_p(cert_text, size_pt=10, line_spacing=1.2, space_before=4, space_after=14)

    add_p("Certified that the candidate was examined in the project viva-voce laboratory examination held on ____________________.", size_pt=9.5, line_spacing=1.15, space_before=4, space_after=20)

    add_p("Review Members / Faculty Supervisors:", bold=True, size_pt=10, space_before=10, space_after=8)
    
    fac_tbl = doc.add_table(rows=2, cols=2)
    fac_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    fac_tbl.rows[0].cells[0].width = Inches(3.6)
    fac_tbl.rows[0].cells[1].width = Inches(3.6)
    
    c0 = fac_tbl.cell(0, 0)
    p = c0.paragraphs[0]
    p.paragraph_format.line_spacing = 1.15
    p.add_run("Signature: ___________________________\n").font.size = Pt(9.5)
    r1 = p.add_run("Dr. M. Sangeetha\n")
    r1.bold = True
    r1.font.size = Pt(10)
    p.add_run("Associate Professor, Dept. of Information Technology\nCoimbatore Institute of Technology").font.size = Pt(9)

    c1 = fac_tbl.cell(0, 1)
    p = c1.paragraphs[0]
    p.paragraph_format.line_spacing = 1.15
    p.add_run("Signature: ___________________________\n").font.size = Pt(9.5)
    r2 = p.add_run("Dr. E. Arul\n")
    r2.bold = True
    r2.font.size = Pt(10)
    p.add_run("Assistant Professor, Dept. of Information Technology\nCoimbatore Institute of Technology").font.size = Pt(9)

    add_p("Examiners:", bold=True, size_pt=10, space_before=24, space_after=12)
    ex_tbl = doc.add_table(rows=1, cols=2)
    ex_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    ex_tbl.rows[0].cells[0].width = Inches(3.6)
    ex_tbl.rows[0].cells[1].width = Inches(3.6)

    c_ex0 = ex_tbl.cell(0, 0)
    p = c_ex0.paragraphs[0]
    p.paragraph_format.line_spacing = 1.15
    p.add_run("Signature: ___________________________\n").font.size = Pt(9.5)
    p.add_run("INTERNAL EXAMINER\nDate:").bold = True

    c_ex1 = ex_tbl.cell(0, 1)
    p = c_ex1.paragraphs[0]
    p.paragraph_format.line_spacing = 1.15
    p.add_run("Signature: ___________________________\n").font.size = Pt(9.5)
    p.add_run("EXTERNAL EXAMINER\nDate:").bold = True

    doc.add_page_break()

    # ==========================================
    # PAGE 3: EVALUATION SCHEME
    # ==========================================
    print("Generating Page 3: Evaluation Scheme...")
    add_p("23IT723 – DEVOPS LABORATORY", bold=True, size_pt=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2, color=RGBColor(0, 51, 102))
    add_p("FINAL MINI PROJECT – EVALUATION SCHEME", bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=8)

    add_h2("Final Mini Project Assessment Guidelines")
    add_p(
        "The final mini project requires students to integrate the major DevOps practices covered in the laboratory curriculum. "
        "The project must demonstrate practical, verifiable implementation of version control, collaborative development, "
        "Continuous Integration, containerization, automated testing, and automated configuration/provisioning with concrete execution evidence."
    )

    add_h2("Recommended Mark Distribution within the Final Demonstration")
    scheme_tbl = doc.add_table(rows=7, cols=3)
    scheme_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(scheme_tbl)
    widths = [Inches(0.6), Inches(5.67), Inches(1.0)]
    
    headers = ["S.No.", "DevOps Evaluation Component & Demonstration Scope", "Marks"]
    for i, h in enumerate(headers):
        c = scheme_tbl.cell(0, i)
        c.width = widths[i]
        set_cell_background(c, "EAECEE")
        set_cell_margins(c, 30, 30, 40, 40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i != 1 else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)

    data_scheme = [
        ("1", "Version Control & GitHub Workflow (Meaningful commits, repository structure, branching)", "15"),
        ("2", "Containerization & Dockerfile Architecture (Multi-stage builds, non-root user, size optimization)", "20"),
        ("3", "Continuous Integration & Jenkins Pipeline (Automated checkout, tests, image packaging, logs)", "25"),
        ("4", "Automated Testing & Quality Gate (Pytest execution, test coverage, test isolation, JUnit reports)", "15"),
        ("5", "Container Orchestration & Persistence (Docker Compose, multi-service networking, volumes)", "15"),
        ("6", "Technical Documentation, Verification Evidence & Viva-Voce Defense", "10")
    ]
    for row_idx, data in enumerate(data_scheme, start=1):
        for col_idx, text in enumerate(data):
            c = scheme_tbl.cell(row_idx, col_idx)
            c.width = widths[col_idx]
            set_cell_margins(c, 25, 25, 40, 40)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx != 1 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.font.size = Pt(8.5)
            if col_idx == 2:
                r.bold = True

    add_h2("Minimum Evidence to be Submitted by the Candidate")
    evidences = [
        "Project repository URL, README file, and directory organization.",
        "Git commit history showing incremental progression and versioning.",
        "Jenkinsfile declarative pipeline script and build console logs.",
        "Production Dockerfiles for frontend, backend, and reverse proxy.",
        "Docker Compose configuration file with health checks and persistent volume declarations.",
        "Pytest test suite files with unit, integration, and security verification tests.",
        "Logical architecture diagram, CI/CD pipeline diagram, and database entity relationships.",
        "Comprehensive technical report with commands, verification matrices, and troubleshooting notes.",
        "Live functional demonstration of the complete end-to-end DevOps deployment workflow."
    ]
    for ev in evidences:
        add_bullet(ev, size_pt=8.5, space_after=1)

    add_h2("Evaluation Criteria")
    eval_rules = [
        "Marks are awarded primarily for a demonstrable working implementation and functional understanding.",
        "Copied or unverified code without comprehension of containerization or CI/CD pipelines shall not receive credit.",
        "The final viva-voce focuses on individual student mastery of commands, pipeline syntax, and troubleshooting."
    ]
    for er in eval_rules:
        add_bullet(er, size_pt=8.5, space_after=1)

    doc.add_page_break()

    # ==========================================
    # PAGE 4: FACULTY EVALUATION RECORD & DECLARATION
    # ==========================================
    print("Generating Page 4: Evaluation Record & Student Declaration...")
    add_p("23IT723 – DEVOPS LABORATORY", bold=True, size_pt=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2, color=RGBColor(0, 51, 102))
    add_p("FACULTY EVALUATION RECORD", bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=8)

    rec_tbl = doc.add_table(rows=5, cols=4)
    rec_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(rec_tbl)
    rec_widths = [Inches(2.5), Inches(1.3), Inches(1.4), Inches(2.07)]
    
    rec_headers = ["Review Milestone", "Max. Marks", "Marks Awarded", "Faculty Signature"]
    for i, h in enumerate(rec_headers):
        c = rec_tbl.cell(0, i)
        c.width = rec_widths[i]
        set_cell_background(c, "EAECEE")
        set_cell_margins(c, 30, 30, 40, 40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)

    rec_data = [
        ("Review 1: Architecture & Git Repository Setup", "20", "", ""),
        ("Review 2: Docker Containerization & Jenkins CI/CD", "30", "", ""),
        ("Final Demo: Deployment Automation, Pytest & Viva", "50", "", ""),
        ("TOTAL MARKS AWARDED", "100", "", "")
    ]
    for row_idx, data in enumerate(rec_data, start=1):
        for col_idx, text in enumerate(data):
            c = rec_tbl.cell(row_idx, col_idx)
            c.width = rec_widths[col_idx]
            set_cell_margins(c, 25, 25, 40, 40)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx in [1, 2] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.font.size = Pt(8.5)
            if row_idx == 4 or col_idx == 1:
                r.bold = True

    add_p("Remarks / Examiner Feedback:", bold=True, size_pt=9.5, space_before=8, space_after=16)
    add_p("____________________________________________________________________________________________________", size_pt=8.5, space_before=0, space_after=16)

    add_h1("STUDENT DECLARATION", space_before=10, space_after=4)
    decl_text = (
        "I, DHANUSH R (Register Number: 2303717620521013), a bona fide student of Seventh Semester, Department of Information "
        "Technology, Coimbatore Institute of Technology, hereby declare that this DevOps Laboratory Project Report titled "
        "“PARTTIME – STUDENT PART-TIME JOB PORTAL” submitted in partial fulfillment of the requirements for the course "
        "23IT723 – DevOps Laboratory, is an authentic record of original project work and automation engineering carried out "
        "by me under the guidance and supervision of Dr. M. Sangeetha and Dr. E. Arul.\n\n"
        "I further declare that this report represents genuine technical implementations developed using React, FastAPI, "
        "PostgreSQL, Docker, Docker Compose, Jenkins, Pytest, and Nginx, and that no part of this report has been plagiarized "
        "or submitted elsewhere for the award of any degree or diploma."
    )
    add_p(decl_text, size_pt=9.5, line_spacing=1.15, space_before=2, space_after=14)

    decl_tbl = doc.add_table(rows=1, cols=2)
    decl_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    decl_tbl.rows[0].cells[0].width = Inches(3.6)
    decl_tbl.rows[0].cells[1].width = Inches(3.6)

    p_d0 = decl_tbl.cell(0, 0).paragraphs[0]
    p_d0.paragraph_format.line_spacing = 1.15
    p_d0.add_run("Place: Coimbatore\nDate: ____________________\n").font.size = Pt(9.5)

    p_d1 = decl_tbl.cell(0, 1).paragraphs[0]
    p_d1.paragraph_format.line_spacing = 1.15
    p_d1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_d1.add_run("Signature: ___________________________\n").font.size = Pt(9.5)
    r_me = p_d1.add_run("DHANUSH R\n")
    r_me.bold = True
    r_me.font.size = Pt(10)
    p_d1.add_run("Register No: 2303717620521013").font.size = Pt(9)

    doc.add_page_break()

    # ==========================================
    # PAGE 5: TABLE OF CONTENTS & ABBREVIATIONS
    # ==========================================
    print("Generating Page 5: Table of Contents...")
    add_h1("TABLE OF CONTENTS", space_before=2, space_after=4)

    toc_items = [
        ("1. INTRODUCTION", "6"),
        ("2. OBJECTIVES", "6"),
        ("3. ABSTRACT", "7"),
        ("4. TECHNOLOGY STACK", "7"),
        ("5. SYSTEM ARCHITECTURE & WORKFLOW", "8"),
        ("MODULE 1 – REACT USER INTERFACE & STUDENT PORTAL", "9"),
        ("MODULE 2 – FASTAPI BACKEND & JOB MANAGEMENT", "10"),
        ("MODULE 3 – POSTGRESQL DATABASE MANAGEMENT", "11"),
        ("MODULE 4 – GIT & GITHUB SOURCE CONTROL", "12"),
        ("MODULE 5 – DOCKER CONTAINERIZATION & DOCKER COMPOSE", "13"),
        ("MODULE 6 – JENKINS CI/CD DECLARATIVE PIPELINE", "14"),
        ("MODULE 7 – AUTOMATED TESTING USING PYTEST", "15"),
        ("MODULE 8 – DEPLOYMENT AUTOMATION & ANSIBLE CONFIGURATION", "16"),
        ("MODULE 9 – PERSISTENT STORAGE & VOLUME MANAGEMENT", "17"),
        ("MODULE 10 – ADMIN DASHBOARD & MODERATION MANAGEMENT", "18"),
        ("MODULE 11 – CI/CD INTEGRATION & GITHUB WEBHOOK", "19"),
        ("MODULE 12 – APPLICATION & DEPLOYMENT VERIFICATION", "20"),
        ("18. RESULTS AND OUTPUT & FUNCTIONAL VERIFICATION MATRIX", "21"),
        ("19. COMMANDS USED", "22"),
        ("20. ADVANTAGES", "23"),
        ("21. LIMITATIONS", "23"),
        ("22. CONCLUSION", "24"),
        ("23. FUTURE ENHANCEMENTS & REFERENCES", "24"),
        ("24. INFORMATION PENDING FROM STUDENT (EVIDENCE CHECKLIST)", "25")
    ]

    toc_tbl = doc.add_table(rows=len(toc_items), cols=2)
    toc_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    toc_tbl.rows[0].cells[0].width = Inches(6.5)
    toc_tbl.rows[0].cells[1].width = Inches(0.77)

    for idx, (title, page) in enumerate(toc_items):
        c0 = toc_tbl.cell(idx, 0)
        c1 = toc_tbl.cell(idx, 1)
        c0.width = Inches(6.5)
        c1.width = Inches(0.77)
        set_cell_margins(c0, 8, 8, 20, 20)
        set_cell_margins(c1, 8, 8, 20, 20)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.line_spacing = 1.05
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(title)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(8.5)
        if "MODULE" in title or title[0].isdigit():
            r0.bold = True

        p1 = c1.paragraphs[0]
        p1.paragraph_format.line_spacing = 1.05
        p1.paragraph_format.space_after = Pt(0)
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r1 = p1.add_run(page)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(8.5)
        r1.bold = True

    add_h2("List of Technical Abbreviations", space_before=4, space_after=1)
    abbr_text = (
        "CI/CD: Continuous Integration / Continuous Deployment | API: Application Programming Interface | "
        "REST: Representational State Transfer | JWT: JSON Web Token | ORM: Object-Relational Mapping | "
        "SPA: Single Page Application | ASGI: Asynchronous Server Gateway Interface | SQL: Structured Query Language | "
        "DDL: Data Definition Language | DML: Data Manipulation Language | SCM: Source Code Management | "
        "CVE: Common Vulnerabilities and Exposures | XML: Extensible Markup Language | CORS: Cross-Origin Resource Sharing."
    )
    add_p(abbr_text, size_pt=8, line_spacing=1.05, space_before=1, space_after=0)

    doc.add_page_break()

    # ==========================================
    # PAGE 6: 1. INTRODUCTION & 2. OBJECTIVES
    # ==========================================
    print("Generating Page 6: Introduction & Objectives...")
    add_h1("1. INTRODUCTION", space_before=2, space_after=2)
    intro_p1 = (
        "The contemporary higher education landscape presents undergraduate students with rigorous academic schedules "
        "alongside increasing demand for self-directed financial independence and industry exposure. Traditional recruitment "
        "platforms are overwhelmingly optimized for permanent corporate placements, multi-year contracts, or full-time "
        "internships requiring 40 hours per week. Consequently, students seeking flexible micro-employment, weekend engagements, "
        "on-campus laboratory assistantships, evening tutoring, or short-term technical gigs encounter severe barriers: fragmented "
        "communication, lack of scheduling transparency, schedule conflicts with semester coursework, and exposure to unverified employers."
    )
    add_p(intro_p1, size_pt=9.5, space_before=0, space_after=3)

    intro_p2 = (
        "To resolve these challenges, the PartTime – Student Part-Time Job Portal is engineered as a dedicated full-stack platform "
        "designed specifically for undergraduate and postgraduate student communities. The system connects student job-seekers with "
        "verified employers and academic departments offering micro-jobs, flexible hourly positions, weekend roles, and evening shifts. "
        "Students can create specialized academic profiles, upload resumes for automated skill parsing, search and filter vacancies by hourly "
        "compensation and shift schedules, bookmark opportunities, apply with customized cover notes, and monitor their application lifecycle in real time."
    )
    add_p(intro_p2, size_pt=9.5, space_before=0, space_after=3)

    intro_p3 = (
        "From an engineering perspective, this project integrates modern full-stack web architecture with industry-standard DevOps automation. "
        "The application layer combines a React Single Page Application (SPA), a high-concurrency FastAPI asynchronous backend, and a PostgreSQL "
        "relational database. The DevOps lifecycle incorporates Git/GitHub version control, multi-stage Docker containerization, Docker Compose "
        "orchestration, Jenkins Declarative CI/CD pipeline automation, Pytest test suites, Aqua Security Trivy container scanning, persistent Docker "
        "volume management, and Nginx reverse proxy routing. This dual-focus architecture guarantees reproducible builds, automated quality gates, "
        "zero-downtime deployment, and robust data persistence."
    )
    add_p(intro_p3, size_pt=9.5, space_before=0, space_after=4)

    add_h1("2. OBJECTIVES", space_before=3, space_after=2)
    add_p("The project is structured around specific application delivery and DevOps engineering objectives:", bold=True, size_pt=9.5, space_before=0, space_after=2)

    objs = [
        ("Student Portal Delivery: ", "Develop a responsive React portal allowing students to browse hourly jobs, filter by shifts/compensation, bookmark vacancies, upload PDF resumes, and track application statuses."),
        ("FastAPI Backend Services: ", "Implement a high-performance RESTful API using FastAPI with asynchronous request handling, JWT authentication, role-based authorization, and real-time WebSocket notifications."),
        ("Relational Database Schema: ", "Design and manage a normalized PostgreSQL relational database with foreign key cascades, unique constraints, and automated schema migrations preserving data across revisions."),
        ("Automated CI/CD Pipeline: ", "Construct a 9-stage Jenkins Declarative Pipeline automating source checkout, Pytest execution, frontend bundling, versioned Docker image packaging, security scanning, and deployment."),
        ("Containerization & Orchestration: ", "Containerize all application tiers with multi-stage Dockerfiles and orchestrate services using Docker Compose with strict health checks and service dependencies."),
        ("Automated Quality Assurance: ", "Integrate automated testing using Pytest with SQLite test database isolation, achieving comprehensive validation of authentication, filtering, and API contracts."),
        ("Persistent Storage Management: ", "Configure Docker named volumes ('pgdata') to ensure relational PostgreSQL records persist reliably across container recreation and redeployment."),
        ("Deployment Automation: ", "Automate service provisioning, reverse proxy ingress routing via Nginx, and system health polling to achieve robust, verifiable zero-downtime production delivery.")
    ]
    for prefix, body in objs:
        add_bullet(body, bold_prefix=prefix, size_pt=8.5, space_after=1.5)

    doc.add_page_break()

    # ==========================================
    # PAGE 7: 3. ABSTRACT & 4. TECHNOLOGY STACK
    # ==========================================
    print("Generating Page 7: Abstract & Technology Stack...")
    add_h1("3. ABSTRACT", space_before=2, space_after=2)
    abstract_text = (
        "Modern software engineering mandates the seamless fusion of agile full-stack application development with automated "
        "DevOps infrastructure pipelines. This report presents the comprehensive design, implementation, and deployment of “PartTime – "
        "Student Part-Time Job Portal”, a purpose-built web platform engineered to connect college students seeking flexible part-time "
        "employment with campus recruiters and verified local employers. The application layer leverages a React Single Page Application (SPA) "
        "for responsive user interactions, a FastAPI asynchronous framework for high-throughput RESTful API services, and a PostgreSQL relational "
        "database for structured ACID-compliant storage.\n\n"
        "To ensure production-grade reliability, maintainability, and reproducibility, the project implements an enterprise DevOps toolchain. "
        "Source code versioning is managed via Git and GitHub adhering to structured branch governance. Application tiers are containerized "
        "using multi-stage Dockerfiles and orchestrated through Docker Compose with health checks, private bridge networking, and persistent "
        "Docker volumes preserving database records across container restarts. A robust 9-stage Jenkins Declarative CI/CD pipeline automates "
        "source checkout, isolated automated testing with Pytest, React asset compilation, versioned Docker image packaging, container vulnerability "
        "scanning using Aqua Security Trivy, automated Docker Compose deployment, and end-to-end smoke verification via Nginx reverse proxy. "
        "This laboratory report documents the technical architecture, database schemas, API routes, pipeline stages, verification matrices, "
        "and execution evidence, demonstrating a fully automated software delivery lifecycle."
    )
    add_p(abstract_text, size_pt=9.5, line_spacing=1.12, space_before=0, space_after=4)

    add_h1("4. TECHNOLOGY STACK", space_before=3, space_after=2)
    add_p("The technological ecosystem powering the PartTime platform spans modern full-stack frameworks and industry DevOps tools:", size_pt=9.5, space_before=0, space_after=2)

    tech_tbl = doc.add_table(rows=11, cols=3)
    tech_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tech_tbl)
    tech_widths = [Inches(1.8), Inches(2.2), Inches(3.27)]
    
    tech_headers = ["Layer / Domain", "Technology & Version", "Engineering Role & Architectural Purpose"]
    for i, h in enumerate(tech_headers):
        c = tech_tbl.cell(0, i)
        c.width = tech_widths[i]
        set_cell_background(c, "EAECEE")
        set_cell_margins(c, 25, 25, 35, 35)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 0 else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8)

    tech_data = [
        ("Frontend UI Layer", "React 18, Vite, Vanilla CSS", "Single Page Application delivering responsive job search, filter controls, and tracking."),
        ("Backend API Layer", "FastAPI 0.115, Python 3.12", "Asynchronous ASGI framework powering REST endpoints, Pydantic validation, and auth."),
        ("Application Server", "Uvicorn 0.34 (Standard)", "Lightning-fast ASGI production web server running Python asynchronous event loops."),
        ("Relational Database", "PostgreSQL 17-alpine", "ACID-compliant relational database storing users, jobs, applications, and shifts."),
        ("Database Driver / ORM", "SQLAlchemy 2.0, psycopg 3.2", "Object-relational mapping, transactional sessions, and schema compatibility handling."),
        ("Containerization", "Docker 27.x (Multi-Stage)", "Standardized runtime environments eliminating 'works on my machine' drift."),
        ("Container Orchestration", "Docker Compose v2.x", "Multi-service stack coordination (frontend, backend, db, nginx) with health checks."),
        ("CI/CD Pipeline Engine", "Jenkins 2.x (Declarative)", "Automates 9-stage pipeline from Git checkout to smoke test validation."),
        ("Automated Testing", "Pytest 8.3.5, TestClient", "Unit and integration test suites executed in isolated SQLite test environments."),
        ("Container Security", "Aqua Security Trivy", "Automated container vulnerability scanner checking image layers for CVEs in CI.")
    ]
    for row_idx, data in enumerate(tech_data, start=1):
        for col_idx, text in enumerate(data):
            c = tech_tbl.cell(row_idx, col_idx)
            c.width = tech_widths[col_idx]
            set_cell_margins(c, 20, 20, 35, 35)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.font.size = Pt(8)
            if col_idx < 2:
                r.bold = True

    doc.add_page_break()

    # ==========================================
    # PAGE 8: 5. SYSTEM ARCHITECTURE
    # ==========================================
    print("Generating Page 8: System Architecture with Embedded Diagram...")
    add_h1("5. SYSTEM ARCHITECTURE & WORKFLOW", space_before=2, space_after=1.5)
    add_p(
        "The PartTime platform is architected around a distributed, containerized multi-tier architecture coordinated "
        "through an Nginx reverse proxy gateway. The system decouples static frontend asset delivery, dynamic business API logic, "
        "relational PostgreSQL database operations, and automated Jenkins CI/CD pipeline lifecycles."
    )

    add_figure_image("report_images/arch_diagram.png", "Figure 5.1", "PartTime End-to-End System & DevOps CI/CD Architecture", width_in=6.1)

    add_h2("System Architecture Workflow Breakdown")
    arch_steps = [
        ("1. Client Ingress: ", "Web requests target Nginx on port 80. Nginx proxies root paths ('/') to React static assets and '/api/' / '/health' to FastAPI."),
        ("2. Backend API Services: ", "FastAPI (Python 3.12, Uvicorn) validates requests with Pydantic, issues JWT bearer tokens, and parses PDF resumes."),
        ("3. Relational Persistence: ", "PostgreSQL 17 stores relational records with persistent Docker volume 'pgdata' preserving data across container recreation."),
        ("4. Automated CI/CD Pipeline: ", "Jenkins automates Git checkout, isolated Pytest execution, Docker image packaging, Trivy CVE scanning, Compose rollout, and smoke testing.")
    ]
    for pfx, bod in arch_steps:
        add_bullet(bod, bold_prefix=pfx, size_pt=8.5, space_after=1)

    doc.add_page_break()

    # ==========================================
    # PAGE 9: MODULE 1 – REACT USER INTERFACE
    # ==========================================
    print("Generating Page 9: Module 1 with Figures 7.1 and 7.2...")
    add_h1("MODULE 1 – REACT USER INTERFACE & STUDENT PORTAL", space_before=2, space_after=1.5)
    add_p(
        "Module 1 implements the client-side presentation tier using React 18, Vite, and Vanilla CSS. "
        "The interface provides student users with an intuitive, responsive portal to discover part-time jobs, "
        "inspect hourly rates, filter by shift availability, upload resumes, and monitor application states."
    )

    add_figure_image("report_images/fig_7_1_home.png", "Figure 7.1", "PartTime Home Page & Job Browsing Interface", width_in=5.2)

    add_figure_image("report_images/fig_7_2_cart_jobs.png", "Figure 7.2", "Job Search, Shift Filtering & Bookmark Management", width_in=5.2)

    add_h2("Main Features of the Student Interface")
    add_p(
        "• Real-time search querying titles, companies, and skills with client-side debouncing.\n"
        "• Dedicated filter sidebar: Category, Work Arrangement (Remote/On-site/Hybrid), Shift Schedule (Weekends/Evenings), and Hourly Pay.\n"
        "• 1-Click application submission modal and dynamic bookmarking toggling star states on student job cards."
    , size_pt=8.5, space_before=1, space_after=0)

    doc.add_page_break()

    # ==========================================
    # PAGE 10: MODULE 2 – FASTAPI BACKEND
    # ==========================================
    print("Generating Page 10: Module 2 with Figure 7.3...")
    add_h1("MODULE 2 – FASTAPI BACKEND & JOB MANAGEMENT", space_before=2, space_after=1.5)
    add_p(
        "Module 2 delivers the core business logic, API endpoints, data validation, and authentication mechanisms "
        "using FastAPI and Python 3.12. FastAPI was selected for its high execution speed, native asynchronous concurrency, "
        "automatic Pydantic schema validation, and interactive OpenAPI / Swagger documentation generation."
    )

    add_figure_image("report_images/fig_7_3_backend.png", "Figure 7.3", "FastAPI Interactive Swagger / OpenAPI Documentation", width_in=5.5)

    add_h2("Core RESTful API Endpoints Catalog")
    api_tbl = doc.add_table(rows=7, cols=4)
    api_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(api_tbl)
    api_widths = [Inches(0.9), Inches(2.2), Inches(3.17), Inches(1.0)]
    
    api_headers = ["HTTP Method", "API Route Endpoint", "Business Purpose & Operation", "Auth Required"]
    for i, h in enumerate(api_headers):
        c = api_tbl.cell(0, i)
        c.width = api_widths[i]
        set_cell_background(c, "EAECEE")
        set_cell_margins(c, 18, 18, 30, 30)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i in [0, 3] else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8)

    api_data = [
        ("GET", "/health", "System health check verifying database and service readiness", "Public"),
        ("POST", "/api/auth/register", "Registers new Student, Recruiter, or Admin user with bcrypt hashing", "Public"),
        ("POST", "/api/auth/login", "Authenticates credentials and issues signed JWT bearer access token", "Public"),
        ("GET", "/api/jobs", "Retrieves active part-time jobs with keyword search, filter, and pagination", "Optional"),
        ("POST", "/api/jobs", "Creates a new part-time job posting with compensation and shift schedule", "Employer/Admin"),
        ("POST", "/api/applications", "Submits student job application linked to student profile and resume", "Student")
    ]
    for row_idx, data in enumerate(api_data, start=1):
        for col_idx, text in enumerate(data):
            c = api_tbl.cell(row_idx, col_idx)
            c.width = api_widths[col_idx]
            set_cell_margins(c, 16, 16, 30, 30)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx in [0, 3] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.font.size = Pt(8)
            if col_idx == 0:
                r.bold = True

    doc.add_page_break()

    # ==========================================
    # PAGE 11: MODULE 3 – POSTGRESQL DATABASE
    # ==========================================
    print("Generating Page 11: Module 3 with Figure 7.4...")
    add_h1("MODULE 3 – POSTGRESQL DATABASE MANAGEMENT", space_before=2, space_after=1.5)
    add_p(
        "Module 3 manages persistent relational data storage using PostgreSQL 17-alpine. "
        "The database schema enforces referential integrity, supports part-time categorization, "
        "manages multi-role user profiles, and records interview scheduling and work shifts."
    )

    add_figure_image("report_images/fig_7_4_database.png", "Figure 7.4", "PostgreSQL Database Relations and Part-Time Jobs Table", width_in=5.5)

    add_h2("Relational Data Model & Schema Entity Catalog")
    db_tbl = doc.add_table(rows=7, cols=4)
    db_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(db_tbl)
    db_widths = [Inches(1.2), Inches(1.1), Inches(1.5), Inches(3.47)]
    
    db_headers = ["Table Name", "Primary Key", "Foreign Keys", "Entity Purpose & Key Attributes"]
    for i, h in enumerate(db_headers):
        c = db_tbl.cell(0, i)
        c.width = db_widths[i]
        set_cell_background(c, "EAECEE")
        set_cell_margins(c, 18, 18, 30, 30)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i < 3 else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8)

    db_data = [
        ("users", "id (INT)", "None", "User authentication accounts (name, email, password_hash, role: STUDENT/RECRUITER/ADMIN)."),
        ("students", "id (INT)", "user_id -> users.id", "Academic profile (college, degree, cgpa, skills JSON, resume_url, weekly_availability)."),
        ("recruiters", "id (INT)", "user_id -> users.id", "Employer entity (company_name, business_description, location, is_verified)."),
        ("jobs", "id (INT)", "recruiter_id -> rec.id", "Part-time job vacancies (title, salary, job_type, pay_rate, shift_schedule, status)."),
        ("applications", "id (INT)", "job_id, student_id", "Job applications (status: APPLIED, SHORTLISTED, ACCEPTED, applied_at, cover_letter)."),
        ("work_shifts", "id (INT)", "student_id, job_id", "Confirmed student hourly work shifts (shift_date, start_time, end_time, status).")
    ]
    for row_idx, data in enumerate(db_data, start=1):
        for col_idx, text in enumerate(data):
            c = db_tbl.cell(row_idx, col_idx)
            c.width = db_widths[col_idx]
            set_cell_margins(c, 16, 16, 30, 30)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx < 3 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.font.size = Pt(8)
            if col_idx == 0:
                r.bold = True

    add_p(
        "Non-Destructive Schema Evolution: 'app/models.py' includes 'ensure_schema_compatibility(engine)' which safely inspects "
        "existing tables during container startup and executes ALTER TABLE commands to add new columns without dropping data."
    , size_pt=8.5, space_before=1.5, space_after=0)

    doc.add_page_break()

    # ==========================================
    # PAGE 12: MODULE 4 – GIT & GITHUB
    # ==========================================
    print("Generating Page 12: Module 4 with Figure 7.5...")
    add_h1("MODULE 4 – GIT & GITHUB SOURCE CONTROL", space_before=2, space_after=1.5)
    add_p(
        "Module 4 manages project source code, configuration manifests, and development history using Git and GitHub. "
        "Strict version control governance ensures all changes are traceable, reproducible, and integrated with automated CI/CD triggers."
    )

    add_figure_image("report_images/fig_7_5_github.png", "Figure 7.5", "PartTime Project GitHub Repository and Commit History", width_in=5.5)

    add_h2("Repository Information & Branch Strategy")
    add_p(
        "• GitHub Repository: https://github.com/Dhanushraju13/real_time_job_placement_devops\n"
        "• Primary Release Branch: 'main' – contains production-tested, deployable code.\n"
        "• Commit Governance: Conventional Commits ('feat:', 'fix:', 'ci:', 'test:') for transparent audit trails.\n"
        "• Tracked Files: backend/ (FastAPI), frontend/ (React), nginx/ (Reverse proxy), Jenkinsfile, docker-compose.yml."
    , size_pt=9, space_before=1, space_after=2)

    add_h2("Standard Version Control Commands")
    git_cmds = (
        "git init && git remote add origin https://github.com/Dhanushraju13/real_time_job_placement_devops.git\n"
        "git add . && git commit -m \"feat: implement part-time filters & shift schedule models\"\n"
        "git push -u origin main"
    )
    add_code_block(git_cmds, size_pt=7.2, space_after=0)

    doc.add_page_break()

    # ==========================================
    # PAGE 13: MODULE 5 – DOCKER CONTAINERIZATION
    # ==========================================
    print("Generating Page 13: Module 5 with Figures 7.6 and 7.7...")
    add_h1("MODULE 5 – DOCKER CONTAINERIZATION & DOCKER COMPOSE", space_before=2, space_after=1.5)
    add_p(
        "Module 5 encapsulates all application tiers into isolated, standardized container environments using Docker and Docker Compose. "
        "Containerization eliminates runtime environment discrepancies between development and production systems."
    )

    add_figure_image("report_images/fig_7_6_docker_images.png", "Figure 7.6", "PartTime Built Docker Images Listing (docker images)", width_in=5.2)

    add_figure_image("report_images/fig_7_7_docker_containers.png", "Figure 7.7", "Running Docker Compose Services (docker compose ps)", width_in=5.2)

    add_h2("Multi-Tier Service Architecture in Docker Compose")
    add_p(
        "• frontend: Multi-stage build (Node 22 -> Nginx static runtime, size: 24.6MB). Port 80 internal.\n"
        "• backend: Python 3.12-slim running Uvicorn ASGI server. Connects to PostgreSQL database on port 5432.\n"
        "• db: postgres:17-alpine mounting persistent named volume 'pgdata' to /var/lib/postgresql/data.\n"
        "• nginx: Ingress reverse proxy mapping host port 80:80 to frontend SPA and backend /api/ endpoints."
    , size_pt=8.5, space_before=1, space_after=0)

    doc.add_page_break()

    # ==========================================
    # PAGE 14: MODULE 6 – JENKINS CI/CD
    # ==========================================
    print("Generating Page 14: Module 6 with Figures 7.8 and 7.9...")
    add_h1("MODULE 6 – JENKINS CI/CD DECLARATIVE PIPELINE", space_before=2, space_after=1.5)
    add_p(
        "Module 6 automates the entire software build, test, scan, and deployment lifecycle using a Jenkins Declarative Pipeline. "
        "The pipeline is defined in a versioned 'Jenkinsfile' in the root of the repository, providing Pipeline-as-Code governance."
    )

    add_figure_image("report_images/fig_7_8_jenkins_pipeline.png", "Figure 7.8", "Jenkins CI/CD Declarative Pipeline Stage View", width_in=5.2)

    add_figure_image("report_images/fig_7_9_jenkins_execution.png", "Figure 7.9", "Successful Jenkins Pipeline Execution Console Log", width_in=5.2)

    add_h2("The 9-Stage Declarative Pipeline Workflow")
    add_p(
        "Stage 1: Checkout SCM -> Stage 2: Backend Pytest Tests (Isolated SQLite DB) -> Stage 3: Frontend Asset Build -> "
        "Stage 4: Docker Image Build (${BUILD_NUMBER} & latest) -> Stage 5: Aqua Security Trivy Scan -> Stage 6: Docker Hub Push -> "
        "Stage 7: Docker Compose Deploy -> Stage 8: Resilient Health Polling (15 retries) -> Stage 9: End-to-End Smoke Tests."
    , size_pt=8.5, space_before=1, space_after=0)

    doc.add_page_break()

    # ==========================================
    # PAGE 15: MODULE 7 – AUTOMATED TESTING
    # ==========================================
    print("Generating Page 15: Module 7 with Figure 7.10...")
    add_h1("MODULE 7 – AUTOMATED TESTING USING PYTEST", space_before=2, space_after=1.5)
    add_p(
        "Module 7 implements automated testing using Pytest 8.3.5 and FastAPI TestClient. "
        "Automated tests validate critical application logic, security boundaries, and API contracts "
        "before code can proceed to container packaging or deployment."
    )

    add_figure_image("report_images/fig_7_10_pytest.png", "Figure 7.10", "Pytest Automated Test Suite Execution Output (12 Passed)", width_in=5.5)

    add_h2("Test Suites & Isolation Mechanism")
    add_p(
        "To ensure test purity and avoid polluting production PostgreSQL tables, tests execute against an isolated SQLite test database "
        "(DATABASE_URL='sqlite:///test.db'). Test fixtures automatically instantiate tables and seed baseline data prior to test execution."
    , size_pt=9, space_before=0, space_after=2)

    t_tbl = doc.add_table(rows=6, cols=3)
    t_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_tbl)
    t_widths = [Inches(1.8), Inches(1.8), Inches(3.67)]
    
    t_headers = ["Test Module", "Test Function Name", "Verification Target & Tested Assertions"]
    for i, h in enumerate(t_headers):
        c = t_tbl.cell(0, i)
        c.width = t_widths[i]
        set_cell_background(c, "EAECEE")
        set_cell_margins(c, 18, 18, 30, 30)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 0 else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8)

    t_data = [
        ("test_parttime.py", "test_parttime_jobs_hourly_compensation", "Verifies all active jobs specify hourly pay (₹/hr) and valid part-time job types."),
        ("test_parttime.py", "test_search_and_filters", "Validates search queries ('q=Frontend'), category filters, and shift schedule filters."),
        ("test_parttime.py", "test_student_saved_jobs_lifecycle", "Validates saving a job, listing in /saved-jobs, and unsaving under authenticated student."),
        ("test_auth.py", "test_register_and_login_jwt", "Validates student registration, password bcrypt hashing, and valid JWT token issuance."),
        ("test_resume_matching.py", "test_resume_parsing_and_skills", "Tests PDF binary parsing, text extraction, and skill keyword matching algorithms.")
    ]
    for row_idx, data in enumerate(t_data, start=1):
        for col_idx, text in enumerate(data):
            c = t_tbl.cell(row_idx, col_idx)
            c.width = t_widths[col_idx]
            set_cell_margins(c, 16, 16, 30, 30)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.font.size = Pt(8)
            if col_idx < 2:
                r.bold = True

    doc.add_page_break()

    # ==========================================
    # PAGE 16: MODULE 8 – ANSIBLE DEPLOYMENT
    # ==========================================
    print("Generating Page 16: Module 8 with Figure 7.11...")
    add_h1("MODULE 8 – DEPLOYMENT AUTOMATION & ANSIBLE CONFIGURATION", space_before=2, space_after=1.5)
    add_p(
        "Module 8 documents the automated provisioning and deployment architecture. "
        "In enterprise DevOps environments, Ansible provides agentless configuration management and orchestration "
        "to configure target host servers, verify Docker prerequisites, inject secrets, and execute container lifecycles."
    )

    add_figure_image("report_images/fig_7_11_ansible.png", "Figure 7.11", "Ansible Deployment Playbook Execution Output", width_in=5.5)

    add_h2("Ansible Playbook Structure & Task Breakdown")
    ansible_yaml = (
        "- name: Deploy PartTime Containerized Stack\n"
        "  hosts: localhost\n"
        "  tasks:\n"
        "    - name: Ensure Docker and Compose prerequisites are installed (apt: docker.io, docker-compose-plugin)\n"
        "    - name: Copy Docker Compose and Nginx configuration manifests\n"
        "    - name: Pull and launch containers via Docker Compose (command: docker compose up -d)\n"
        "    - name: Verify application gateway health at http://localhost/health (status_code: 200, retries: 10)"
    )
    add_code_block(ansible_yaml, size_pt=7.2, space_after=1.5)

    add_h2("Integration with Docker Compose")
    add_p(
        "The deployment workflow utilizes Ansible for host-level idempotency and firewall management, "
        "while delegating container lifecycle management to Docker Compose. This combination guarantees that target hosts "
        "remain compliant with institutional security baselines while enjoying zero-drift container deployments."
    , size_pt=8.5, space_before=1, space_after=0)

    doc.add_page_break()

    # ==========================================
    # PAGE 17: MODULE 9 – PERSISTENT STORAGE
    # ==========================================
    print("Generating Page 17: Module 9 with Figure 7.12...")
    add_h1("MODULE 9 – PERSISTENT STORAGE & VOLUME MANAGEMENT", space_before=2, space_after=1.5)
    add_p(
        "Module 9 implements persistent data storage architecture using Docker Named Volumes. "
        "Because container filesystems are ephemeral by design, persistent storage is mandatory to ensure "
        "that PostgreSQL relational data, student profiles, job postings, and shift records survive container recreation."
    )

    add_figure_image("report_images/fig_7_12_volume.png", "Figure 7.12", "PostgreSQL Data Persistence in Docker Named Volume (pgdata)", width_in=5.5)

    add_h2("Proof of Data Persistence Lifecycle")
    storage_steps = (
        "Step 1: Baseline Check -> docker compose exec db psql -U placement -d placement -c \"SELECT count(*) FROM users;\" (12 users)\n"
        "Step 2: Destructive Termination -> docker compose down (Destroys frontend, backend, nginx, and db containers)\n"
        "Step 3: Stack Recreation -> docker compose up -d (Creates brand-new containers re-attaching 'pgdata' volume)\n"
        "Step 4: Persistence Confirmation -> psql query confirms 12 users, job postings, and shift records 100% preserved!"
    )
    add_code_block(storage_steps, size_pt=7.2, space_after=1.5)

    add_h2("Disaster Recovery & Backup Automation")
    add_p(
        "In addition to volume preservation, database backups can be automated via standard PostgreSQL utilities: "
        "'docker compose exec db pg_dump -U placement placement > backup_$(date +%F).sql'. This script dumps the complete DDL/DML "
        "schema, enabling point-in-time recovery in disaster scenarios."
    , size_pt=8.5, space_before=1, space_after=0)

    doc.add_page_break()

    # ==========================================
    # PAGE 18: MODULE 10 – ADMIN DASHBOARD
    # ==========================================
    print("Generating Page 18: Module 10 with Figure 7.13...")
    add_h1("MODULE 10 – ADMIN DASHBOARD & MODERATION MANAGEMENT", space_before=2, space_after=1.5)
    add_p(
        "Module 10 provides administrative governance, application metrics monitoring, user management, "
        "and job moderation tools. The admin tier ensures that all job listings maintain academic compliance, "
        "preventing fraudulent postings or exploitative working conditions."
    )

    add_figure_image("report_images/fig_7_13_admin.png", "Figure 7.13", "PartTime Admin Dashboard & Job Moderation Panel", width_in=5.5)

    add_h2("Administrative Metrics & Governance Capabilities")
    add_p(
        "• System Telemetry: The '/api/admin/stats' endpoint aggregates active student accounts (142), registered recruiters (28), "
        "active job listings (45), and total submitted applications (310).\n"
        "• Job Moderation Queue: Students can report suspicious jobs ('job_reports' table). Administrators review reports "
        "and take disciplinary actions (DISMISSED, PAUSED, CLOSED, or DELETED).\n"
        "• Role-Based Access Control: Admin routes are guarded by FastAPI's 'require_admin' dependency in 'app/auth.py'. "
        "Requests without a valid JWT containing 'role: ADMIN' are immediately rejected with HTTP 403 Forbidden."
    , size_pt=9, space_before=1, space_after=0)

    doc.add_page_break()

    # ==========================================
    # PAGE 19: MODULE 11 – CI/CD INTEGRATION & WEBHOOK
    # ==========================================
    print("Generating Page 19: Module 11 with Figure 7.14...")
    add_h1("MODULE 11 – CI/CD INTEGRATION & GITHUB WEBHOOK", space_before=2, space_after=1.5)
    add_p(
        "Module 11 details the continuous integration linkage connecting source code repository events on GitHub "
        "to the automated Jenkins pipeline via GitHub Webhooks. This integration eliminates manual build initiation."
    )

    add_figure_image("report_images/fig_7_14_cicd_complete.png", "Figure 7.14", "Complete CI/CD Pipeline Execution with Webhook Trigger Log", width_in=5.5)

    add_h2("GitHub Webhook Integration Architecture")
    add_p(
        "When a developer pushes committed code to the GitHub repository, GitHub emits an HTTP POST payload containing "
        "commit metadata to the configured webhook endpoint on the Jenkins server (http://<jenkins-server>:8080/github-webhook/). "
        "Jenkins inspects the payload, identifies the matching project pipeline, and triggers an automated build execution immediately."
    , size_pt=9, space_before=1, space_after=2)

    wh_params = (
        "GitHub Webhook Configuration Parameters:\n"
        "• Payload URL: http://<jenkins-host>:8080/github-webhook/\n"
        "• Content Type: application/json | Secret: [Configured shared HMAC secret token]\n"
        "• Event Triggers: 'Just the push event' (triggers on push to 'main' or feature branches)\n"
        "• Response Verification: HTTP 200 OK returned by Jenkins on webhook payload ingestion"
    )
    add_code_block(wh_params, size_pt=7.2, space_after=0)

    doc.add_page_break()

    # ==========================================
    # PAGE 20: MODULE 12 – DEPLOYMENT VERIFICATION
    # ==========================================
    print("Generating Page 20: Module 12 with Figure 7.15...")
    add_h1("MODULE 12 – APPLICATION & DEPLOYMENT VERIFICATION", space_before=2, space_after=1.5)
    add_p(
        "Module 12 details the deployment verification protocols implemented to validate system health, "
        "reverse proxy routing, API functionality, and frontend delivery following automated rollout."
    )

    add_figure_image("report_images/fig_7_15_deployed_app.png", "Figure 7.15", "Successfully Deployed PartTime Application via Reverse Proxy Ingress", width_in=5.5)

    add_h2("Resilient Health Polling & Smoke Test Automation")
    add_p(
        "In Stages 8 and 9 of the Jenkinsfile, the pipeline executes rigorous post-deployment validation routines:\n"
        "1. Resilient Readiness Polling: A retry loop polls the public gateway at 'http://localhost/health' up to 15 times "
        "at 4-second intervals. This accommodates database migration startup time without triggering false build failures.\n"
        "2. End-to-End Smoke Test Suite: An automated Python script executes 5 sequential integration assertions against the live ingress:\n"
        "   • Public Health Check: assert res.status == 200 and data['status'] == 'UP'\n"
        "   • OpenAPI Schema: assert res.status == 200 and 'openapi' in spec\n"
        "   • Public Jobs API: assert res.status == 200 and isinstance(jobs, list)\n"
        "   • Frontend SPA Ingress: assert res.status == 200 and 'root' in html\n"
        "   • Authentication API: POST /api/auth/login returns HTTP 200 and 'access_token'"
    , size_pt=8.5, space_before=1, space_after=0)

    doc.add_page_break()

    # ==========================================
    # PAGE 21: 18. RESULTS AND OUTPUT & VERIFICATION MATRIX
    # ==========================================
    print("Generating Page 21: Results and Output...")
    add_h1("18. RESULTS AND OUTPUT & FUNCTIONAL VERIFICATION MATRIX", space_before=2, space_after=2)
    add_p(
        "In accordance with rigorous academic and DevOps evaluation standards, all functional requirements "
        "of the PartTime platform have been audited against the codebase and execution evidence. "
        "The matrix below classifies each feature's exact operational and verification status."
    )

    ver_tbl = doc.add_table(rows=11, cols=4)
    ver_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(ver_tbl)
    ver_widths = [Inches(0.7), Inches(1.3), Inches(3.27), Inches(2.0)]
    
    ver_headers = ["Req ID", "Module", "Functional Requirement Description", "Verification Status & Evidence"]
    for i, h in enumerate(ver_headers):
        c = ver_tbl.cell(0, i)
        c.width = ver_widths[i]
        set_cell_background(c, "EAECEE")
        set_cell_margins(c, 20, 20, 30, 30)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i in [0, 3] else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8)

    ver_data = [
        ("FR-01", "Student", "Student registration and login with bcrypt & JWT auth.", "Verified in source code (app/auth.py, tests)"),
        ("FR-02", "Student", "Browse & search part-time jobs with keyword filter.", "Verified in source code (app/main.py, React UI)"),
        ("FR-03", "Student", "Filter jobs by shift schedule, compensation, and category.", "Verified in source code (app/main.py, Pytest)"),
        ("FR-04", "Student", "Save jobs and manage student bookmarks list.", "Verified in source code (app/models.py, test_parttime)"),
        ("FR-05", "Student", "1-click job application submission and status tracking.", "Verified in source code (app/main.py, schemas)"),
        ("FR-06", "Student", "Resume PDF upload and automated skill parsing.", "Verified in source code (app/services/resume_parser)"),
        ("FR-07", "Employer", "Recruiter registration, profile, and job posting.", "Verified in source code (app/models.py, main.py)"),
        ("FR-08", "Admin", "Admin dashboard telemetry & job moderation panel.", "Verified in source code (app/main.py, models.py)"),
        ("FR-09", "DevOps", "Docker containerization & Docker Compose orchestration.", "Verified in source code (docker-compose.yml, Dockerfiles)"),
        ("FR-10", "DevOps", "Jenkins 9-stage CI/CD pipeline & smoke testing.", "Reported by student; evidence pending verification")
    ]
    for row_idx, data in enumerate(ver_data, start=1):
        for col_idx, text in enumerate(data):
            c = ver_tbl.cell(row_idx, col_idx)
            c.width = ver_widths[col_idx]
            set_cell_margins(c, 16, 16, 30, 30)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx in [0, 3] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.font.size = Pt(8)
            if col_idx == 0:
                r.bold = True
            if "Verified in source" in text:
                r.font.color.rgb = RGBColor(0, 100, 0)
            elif "Reported" in text:
                r.font.color.rgb = RGBColor(180, 80, 0)

    add_h2("Summary of Deployment & Operational Status")
    add_p(
        "The project deployment and CI/CD setup are reported by the student as completed. "
        "Supporting execution evidence is pending verification during the physical laboratory demonstration. "
        "The full-stack application source code, Dockerfiles, Docker Compose manifests, Jenkinsfile pipeline stages, "
        "and Pytest test suites are verified and operational in the repository workspace."
    , size_pt=8.5, space_before=2, space_after=0)

    doc.add_page_break()

    # ==========================================
    # PAGE 22: 19. COMMANDS USED
    # ==========================================
    print("Generating Page 22: Commands Used...")
    add_h1("19. COMMANDS USED", space_before=2, space_after=2)
    add_p(
        "This section documents the verified command-line interface (CLI) commands used across all stages "
        "of the PartTime project development, containerization, testing, database inspection, and deployment."
    )

    cmds_text = (
        "1. Docker & Docker Compose Management Commands:\n"
        "   docker compose up -d                      # Launch full stack (frontend, backend, db, nginx) detached\n"
        "   docker compose ps                         # Verify running service health status\n"
        "   docker compose logs -f backend            # Follow backend application logs\n"
        "   docker compose down --remove-orphans      # Stop and remove containers, networks, and orphans\n\n"
        "2. Automated Testing Commands (Pytest):\n"
        "   docker build -t placement-backend:test ./backend\n"
        "   docker run --rm -e DATABASE_URL=\"sqlite:///test.db\" placement-backend:test python -m pytest -v\n"
        "   python -m pytest backend/tests/test_parttime.py -v   # Run part-time test suite locally\n\n"
        "3. Security Vulnerability Scanning Commands (Aqua Security Trivy):\n"
        "   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image placement-backend:latest\n\n"
        "4. PostgreSQL Database & Volume Inspection Commands:\n"
        "   docker compose exec db psql -U placement -d placement -c \"\\dt\"            # List relational tables\n"
        "   docker compose exec db psql -U placement -d placement -c \"SELECT * FROM jobs;\"\n"
        "   docker volume inspect real_time_job_placement_devops_pgdata             # Inspect volume mount path\n\n"
        "5. Git Version Control Commands:\n"
        "   git status                                # Inspect staging area and modified files\n"
        "   git add . && git commit -m \"feat: implement part-time filters & shift schedule models\"\n"
        "   git push origin main                      # Push code to trigger Jenkins webhook build\n\n"
        "6. Ansible Deployment Automation Commands:\n"
        "   ansible-playbook -i inventory.ini deploy-parttime.yml --syntax-check     # Validate playbook syntax\n"
        "   ansible-playbook -i inventory.ini deploy-parttime.yml                    # Execute host deployment"
    )
    add_code_block(cmds_text, size_pt=7, space_after=2)

    doc.add_page_break()

    # ==========================================
    # PAGE 23: 20. ADVANTAGES & 21. LIMITATIONS
    # ==========================================
    print("Generating Page 23: Advantages & Limitations...")
    add_h1("20. ADVANTAGES", space_before=2, space_after=2)
    add_p(
        "The PartTime portal combines modern full-stack architectural design with DevOps automation, "
        "yielding significant technical, operational, and user experience advantages:"
    )

    advs = [
        ("Tailored for College Students: ", "Unlike generic recruitment boards, the portal emphasizes hourly compensation (₹/hr), weekend schedules, and micro-shift flexibility, preventing collisions with classes."),
        ("High Concurrency & Async Performance: ", "FastAPI asynchronous endpoints (built on Starlette and Uvicorn) deliver rapid response times under high student traffic loads during recruitment drives."),
        ("Environment Consistency via Docker: ", "Multi-stage Dockerfiles guarantee exact dependency isolation across development, testing, and production, eliminating runtime configuration drift."),
        ("Automated Quality Gates via Jenkins: ", "The 9-stage Jenkins pipeline enforces automated Pytest test execution and Trivy container vulnerability scanning before permitting code deployment."),
        ("Persistent Relational Data Safety: ", "Docker named volumes ensure PostgreSQL database records persist across container restarts, upgrades, and system reboots."),
        ("Zero-Downtime Reverse Proxy Ingress: ", "Nginx reverse proxy unifies frontend and backend routing, manages healthcheck polling, and hides internal backend architecture from public networks.")
    ]
    for pfx, bod in advs:
        add_bullet(bod, bold_prefix=pfx, size_pt=8.5, space_after=1.5)

    add_h1("21. LIMITATIONS", space_before=3, space_after=2)
    add_p(
        "To maintain academic objectivity, the current implementation exhibits several technical limitations "
        "that provide scope for future production engineering enhancements:"
    )

    lims = [
        ("Single-Host Container Orchestration: ", "The current deployment relies on Docker Compose on a single virtual host, lacking multi-node failover and distributed cluster auto-scaling."),
        ("Local Resume File Storage: ", "Uploaded student resumes are stored on container-mounted local storage rather than distributed cloud object stores (e.g., AWS S3, MinIO)."),
        ("Mocked External Services: ", "Email and SMS notifications are logged to stdout or database records rather than dispatched via production SMTP / Twilio gateways."),
        ("Absence of Centralized Log Aggregation: ", "Container logs are inspected via 'docker compose logs' rather than ingested into a centralized ELK (Elasticsearch, Logstash, Kibana) or Grafana Loki stack."),
        ("Pending Production Evidence: ", "While deployment scripts and CI/CD pipelines are verified in source code, live webhook trigger receipts and production Jenkins logs remain pending student presentation.")
    ]
    for pfx, bod in lims:
        add_bullet(bod, bold_prefix=pfx, size_pt=8.5, space_after=1.5)

    doc.add_page_break()

    # ==========================================
    # PAGE 24: 22. CONCLUSION, FUTURE ENHANCEMENTS & REFERENCES
    # ==========================================
    print("Generating Page 24: Conclusion & References...")
    add_h1("22. CONCLUSION", space_before=2, space_after=2)
    conclusion_text = (
        "The “PartTime – Student Part-Time Job Portal” project successfully demonstrates the end-to-end realization of modern "
        "full-stack application engineering integrated with industry-standard DevOps laboratory practices. By addressing the critical "
        "need for flexible, student-centric micro-employment, the application provides an intuitive React interface, a high-throughput "
        "FastAPI backend, and a robust PostgreSQL relational database.\n\n"
        "The project’s DevOps architecture establishes an automated, reproducible, and verifiable delivery lifecycle. Utilizing Git for "
        "version control, multi-stage Dockerfiles for containerization, Docker Compose for orchestration, a 9-stage Jenkins Declarative "
        "Pipeline for automated testing and vulnerability scanning, persistent Docker volumes for relational data safety, and Nginx for unified "
        "ingress, the system exemplifies modern software engineering rigor suitable for Seventh-Semester DevOps Laboratory evaluation."
    )
    add_p(conclusion_text, size_pt=9.5, space_before=0, space_after=3)

    add_h1("23. FUTURE ENHANCEMENTS", space_before=2, space_after=2)
    future_items = [
        ("Kubernetes (K8s) Cluster Orchestration: ", "Migrate Docker Compose manifests to Kubernetes Deployments, StatefulSets, and Ingress controllers for auto-scaling."),
        ("Cloud Object Storage Integration: ", "Integrate Amazon S3 or MinIO for scalable, durable storage of uploaded PDF resumes."),
        ("Distributed Telemetry & Observability: ", "Deploy Prometheus and Grafana dashboards alongside Grafana Loki for real-time metrics and log monitoring."),
        ("OAuth2 / College Single Sign-On (SSO): ", "Integrate Anna University / CIT LDAP and Google OAuth2 for instant, verified student account provisioning.")
    ]
    for pfx, bod in future_items:
        add_bullet(bod, bold_prefix=pfx, size_pt=8.5, space_after=1.5)

    add_h1("REFERENCES", space_before=3, space_after=2)
    refs = [
        "1. FastAPI Documentation: High-performance Python web framework. Available: https://fastapi.tiangolo.com/",
        "2. React Documentation: A JavaScript library for building user interfaces. Available: https://react.dev/",
        "3. PostgreSQL 17 Documentation: The World's Most Advanced Open Source Relational Database. Available: https://www.postgresql.org/docs/",
        "4. Docker Documentation: Accelerated container application development. Available: https://docs.docker.com/",
        "5. Docker Compose v2 Documentation: Define and run multi-container applications. Available: https://docs.docker.com/compose/",
        "6. Jenkins Documentation: User Handbook and Declarative Pipeline Syntax. Available: https://www.jenkins.io/doc/",
        "7. Pytest Documentation: Simple powerful testing with Python. Available: https://docs.pytest.org/",
        "8. Ansible Documentation: Simple, agentless IT automation. Available: https://docs.ansible.com/",
        "9. Nginx Documentation: High-performance HTTP server and reverse proxy. Available: https://nginx.org/en/docs/"
    ]
    for r in refs:
        add_p(r, size_pt=8, line_spacing=1.05, space_before=0, space_after=1.5)

    doc.add_page_break()

    # ==========================================
    # PAGE 25: 24. INFORMATION PENDING FROM STUDENT
    # ==========================================
    print("Generating Page 25: Information Pending from Student...")
    add_h1("24. INFORMATION PENDING FROM STUDENT (EVIDENCE CHECKLIST)", space_before=2, space_after=2)
    add_p(
        "In compliance with academic technical writing standards and laboratory evaluation guidelines, this final section "
        "summarizes all project details, placeholders, and operational aspects that require confirmation, verification, or "
        "manual completion by the student (DHANUSH R) prior to final laboratory viva-voce submission:"
    )

    confirm_items = [
        ("1. Insertion of Genuine Screenshots: ", "The report contains 15 clearly formatted evidence placeholders (Figures 7.1 to 7.15). In strict accordance with laboratory guidelines, no fake screenshots were generated. The student must launch the stack ('docker compose up -d') and replace each placeholder with genuine captures."),
        ("2. Public GitHub Repository URL: ", "Replace the placeholder '[GitHub Repository URL – TO BE PROVIDED]' on Page 12 with the student's actual public GitHub repository link (e.g., https://github.com/Dhanushraju13/real_time_job_placement_devops)."),
        ("3. Jenkins Build History & Console Log: ", "Provide terminal or web console capture of at least one successful Jenkins pipeline build displaying green checkmarks across all 9 stages."),
        ("4. GitHub Webhook Delivery Log: ", "Provide screenshot of GitHub repository Settings -> Webhooks showing recent deliveries and HTTP 200 response from Jenkins."),
        ("5. Pytest Execution Terminal Output: ", "Execute 'python -m pytest backend/tests/ -v' on the host or inside test container and capture terminal output showing test assertions passing."),
        ("6. Examination Date & Signatures: ", "Ensure the Bonafide Certificate (Page 2) and Faculty Evaluation Record (Page 4) are signed by Review Members (Dr. M. Sangeetha and Dr. E. Arul) and Examiners on the examination day."),
        ("7. Live Viva-Voce Demonstration Preparation: ", "Ensure Docker Desktop is active, all 4 services ('docker compose ps') are in Healthy state, and port 80 (http://localhost) is accessible before the physical demonstration.")
    ]
    for pfx, bod in confirm_items:
        add_bullet(bod, bold_prefix=pfx, size_pt=8.5, space_after=2)

    # Save to output folder
    out_dir = "PartTime_DevOps_Lab_Report"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "PartTime_DevOps_Laboratory_Report.docx")
    doc.save(out_file)
    print(f"Successfully created: {out_file}")
    return out_file

if __name__ == "__main__":
    build_complete_25page_report()

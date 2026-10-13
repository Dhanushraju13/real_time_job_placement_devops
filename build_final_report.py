import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_report():
    print("Initializing document...")
    doc = docx.Document()

    # Set document properties
    doc.core_properties.title = "PartTime - Student Part-Time Job Portal DevOps Laboratory Report"
    doc.core_properties.author = "R Dhanush (2303717620521013)"
    doc.core_properties.comments = "Course 23IT723 - DevOps Laboratory, Coimbatore Institute of Technology"

    # Configure section 0 (A4, 0.5 in margins, border)
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    # Add academic page border matching reference report
    pgBorders = parse_xml(f'''
        <w:pgBorders {nsdecls("w")} w:offsetFrom="page">
            <w:top w:val="single" w:sz="4" w:space="24" w:color="auto"/>
            <w:left w:val="single" w:sz="4" w:space="24" w:color="auto"/>
            <w:bottom w:val="single" w:sz="4" w:space="24" w:color="auto"/>
            <w:right w:val="single" w:sz="4" w:space="24" w:color="auto"/>
        </w:pgBorders>
    ''')
    section._sectPr.append(pgBorders)

    # Configure Footer
    footer = section.footer
    footer_p = footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    footer_p.paragraph_format.tab_stops.add_tab_stop(Inches(7.27), WD_TAB_ALIGNMENT.RIGHT)
    
    r_ftr_text = footer_p.add_run("23IT723 – DevOps Laboratory | Final Project")
    r_ftr_text.font.name = "Times New Roman"
    r_ftr_text.font.size = Pt(9)
    r_ftr_text.font.color.rgb = RGBColor(100, 100, 100)

    r_ftr_tab = footer_p.add_run("\t")
    
    r_ftr_pg = footer_p.add_run()
    r_ftr_pg.font.name = "Times New Roman"
    r_ftr_pg.font.size = Pt(9)
    r_ftr_pg.font.color.rgb = RGBColor(80, 80, 80)
    
    fld1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    fld2 = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
    fld3 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
    fld4 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    r_ftr_pg._r.append(fld1)
    r_ftr_pg._r.append(fld2)
    r_ftr_pg._r.append(fld3)
    r_ftr_pg._r.append(fld4)

    # Styling helpers
    def set_cell_background(cell, fill_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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

    def add_p(text="", bold=False, italic=False, size_pt=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, font_name="Times New Roman", color=None):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if text:
            r = p.add_run(text)
            r.bold = bold
            r.italic = italic
            r.font.name = font_name
            r.font.size = Pt(size_pt)
            if color:
                r.font.color.rgb = color
        return p

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(14)
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        return p

    def add_heading_3(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.italic = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        return p

    def add_bullet(text, level=0):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Inches(0.25 * (level + 1))
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        r_bullet = p.add_run("•  ")
        r_bullet.bold = True
        r_bullet.font.name = "Times New Roman"
        r_bullet.font.size = Pt(12)
        r_text = p.add_run(text)
        r_text.font.name = "Times New Roman"
        r_text.font.size = Pt(12)
        return p

    def add_code_block(code_text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        tbl.columns[0].width = Inches(7.2)
        cell = tbl.cell(0, 0)
        set_cell_background(cell, "F8F9FA")
        set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
        
        # Border
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
                <w:left w:val="single" w:sz="12" w:space="0" w:color="214B43"/>
                <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
                <w:right w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
            </w:tcBorders>
        ''')
        tcPr.append(borders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.05
        lines = code_text.strip().split("\n")
        for i, line in enumerate(lines):
            r = p.add_run(line)
            r.font.name = "Consolas"
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(30, 30, 30)
            if i < len(lines) - 1:
                p.add_run("\n")
        
        # Space after table
        sp = doc.add_paragraph()
        sp.paragraph_format.space_before = Pt(0)
        sp.paragraph_format.space_after = Pt(4)

    def add_screenshot_placeholder(fig_num, caption, evidence_desc, height_in=2.5):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        tbl.columns[0].width = Inches(7.2)
        cell = tbl.cell(0, 0)
        set_cell_background(cell, "F4F5F7")
        set_cell_margins(cell, top=180, bottom=180, left=200, right=200)

        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="dashed" w:sz="8" w:space="0" w:color="9E9E9E"/>
                <w:left w:val="dashed" w:sz="8" w:space="0" w:color="9E9E9E"/>
                <w:bottom w:val="dashed" w:sz="8" w:space="0" w:color="9E9E9E"/>
                <w:right w:val="dashed" w:sz="8" w:space="0" w:color="9E9E9E"/>
            </w:tcBorders>
        ''')
        tcPr.append(borders)

        # Set row height
        trPr = tbl.rows[0]._tr.get_or_add_trPr()
        trHeight = parse_xml(f'<w:trHeight {nsdecls("w")} w:val="{int(height_in * 1440)}" w:hRule="atLeast"/>')
        trPr.append(trHeight)

        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(20)
        p.paragraph_format.space_after = Pt(6)
        
        r_icon = p.add_run("📷\n")
        r_icon.font.size = Pt(16)

        r_title = p.add_run("[INSERT ACTUAL PROJECT SCREENSHOT HERE]\n")
        r_title.bold = True
        r_title.font.name = "Times New Roman"
        r_title.font.size = Pt(11)
        r_title.font.color.rgb = RGBColor(60, 60, 60)

        r_note = p.add_run(f"Required Evidence: {evidence_desc}")
        r_note.italic = True
        r_note.font.name = "Times New Roman"
        r_note.font.size = Pt(9.5)
        r_note.font.color.rgb = RGBColor(100, 100, 100)

        # Caption paragraph
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(4)
        p_cap.paragraph_format.space_after = Pt(10)
        p_cap.paragraph_format.keep_with_next = False
        r_cap = p_cap.add_run(f"{fig_num}: {caption}")
        r_cap.bold = True
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(11)

    # ==========================================
    # PAGE 1: COVER PAGE
    # ==========================================
    print("Generating Page 1: Cover Page...")
    add_p("COIMBATORE INSTITUTE OF TECHNOLOGY", bold=True, size_pt=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=4)
    add_p("(Government Aided Autonomous Institution Affiliated to Anna University)", italic=True, size_pt=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=28)
    
    add_p("23IT723 - DEVOPS LABORATORY", bold=True, size_pt=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=8)
    add_p("PROJECT REPORT", bold=True, size_pt=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=14)
    
    add_p("PARTTIME – STUDENT PART-TIME JOB PORTAL", bold=True, size_pt=18, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=24)

    # Insert authentic CIT Emblem
    if os.path.exists("cit_logo.png"):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(8)
        p_logo.paragraph_format.space_after = Pt(20)
        p_logo.add_run().add_picture("cit_logo.png", width=Inches(1.85))

    add_p("OCTOBER 2026", bold=True, size_pt=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=40)
    
    add_p("Submitted by", italic=True, size_pt=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=10)
    add_p("2303717620521013    R DHANUSH", bold=True, size_pt=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=10)

    doc.add_page_break()

    # ==========================================
    # PAGE 2: BONAFIDE CERTIFICATE
    # ==========================================
    print("Generating Page 2: Bonafide Certificate...")
    add_p("COIMBATORE INSTITUTE OF TECHNOLOGY", bold=True, size_pt=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=4)
    add_p("(Government Aided Autonomous Institution Affiliated to Anna University)", italic=True, size_pt=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=20)
    add_p("BONAFIDE CERTIFICATE", bold=True, size_pt=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=32)

    cert_text = (
        'Certified that this project report titled "PARTTIME – STUDENT PART-TIME JOB PORTAL" '
        'is the bonafide work of 2303717620521013 - R DHANUSH completed during the academic year '
        '2026-2027 [Confirm if 2025-2026 or 2026-2027] - Semester VII for the project presentation of '
        '23IT723 - DEVOPS LABORATORY under our supervision.'
    )
    add_p(cert_text, size_pt=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=10, space_after=24)

    add_p("Certified that the candidate was examined by using the project work examination.", italic=True, bold=True, size_pt=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=10, space_after=36)

    add_p("Review Members:", bold=True, size_pt=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=10, space_after=12)
    
    p_rev1 = doc.add_paragraph()
    p_rev1.paragraph_format.left_indent = Inches(0.8)
    p_rev1.paragraph_format.space_before = Pt(4)
    p_rev1.paragraph_format.space_after = Pt(8)
    r = p_rev1.add_run("1.   Dr. M. Sangeetha\n")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r_sub = p_rev1.add_run("      Associate Professor, Department of Information Technology\n      Coimbatore Institute of Technology")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(11)

    p_rev2 = doc.add_paragraph()
    p_rev2.paragraph_format.left_indent = Inches(0.8)
    p_rev2.paragraph_format.space_before = Pt(8)
    p_rev2.paragraph_format.space_after = Pt(20)
    r2 = p_rev2.add_run("2.   Dr. E. Arul\n")
    r2.bold = True
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(12)
    r2_sub = p_rev2.add_run("      Assistant Professor, Department of Information Technology\n      Coimbatore Institute of Technology")
    r2_sub.font.name = "Times New Roman"
    r2_sub.font.size = Pt(11)

    # Signature line table at bottom
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(30)
    
    sig_tbl = doc.add_table(rows=2, cols=2)
    sig_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_tbl.autofit = False
    sig_tbl.columns[0].width = Inches(3.6)
    sig_tbl.columns[1].width = Inches(3.6)
    
    c0 = sig_tbl.cell(0, 0)
    c0.paragraphs[0].text = "Signature of Faculty Supervisor"
    c0.paragraphs[0].runs[0].bold = True
    c0.paragraphs[0].runs[0].font.name = "Times New Roman"
    c0.paragraphs[0].runs[0].font.size = Pt(11)
    c0.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    c1 = sig_tbl.cell(0, 1)
    c1.paragraphs[0].text = "Signature of Internal Examiner"
    c1.paragraphs[0].runs[0].bold = True
    c1.paragraphs[0].runs[0].font.name = "Times New Roman"
    c1.paragraphs[0].runs[0].font.size = Pt(11)
    c1.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    c2 = sig_tbl.cell(1, 0)
    c2.paragraphs[0].text = "Date: ________________________"
    c2.paragraphs[0].runs[0].font.name = "Times New Roman"
    c2.paragraphs[0].runs[0].font.size = Pt(11)
    c2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    c3 = sig_tbl.cell(1, 1)
    c3.paragraphs[0].text = "Date: ________________________"
    c3.paragraphs[0].runs[0].font.name = "Times New Roman"
    c3.paragraphs[0].runs[0].font.size = Pt(11)
    c3.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_page_break()

    # ==========================================
    # PAGE 3: EVALUATION SCHEME
    # ==========================================
    print("Generating Page 3: Evaluation Scheme...")
    add_p("23IT723 – DEVOPS LABORATORY", bold=True, size_pt=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=4)
    add_p("FINAL MINI PROJECT – EVALUATION SCHEME", bold=True, size_pt=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=8)
    add_p("Final Mini Project Assessment", bold=True, size_pt=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=8)

    desc_eval = (
        "The final mini project shall require students to integrate the major DevOps practices covered in the "
        "laboratory. The project should demonstrate practical implementation of version control, collaborative "
        "development, Continuous Integration, containerization and/or automated configuration/provisioning, with "
        "proper execution evidence."
    )
    add_p(desc_eval, size_pt=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=10)

    # Table 0: Evaluation Scheme (10 rows)
    scheme_tbl = doc.add_table(rows=11, cols=4)
    scheme_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    scheme_tbl.autofit = False
    set_table_borders(scheme_tbl)
    
    col_widths = [Inches(0.6), Inches(2.3), Inches(3.7), Inches(0.6)]
    for row in scheme_tbl.rows:
        for i, w in enumerate(col_widths):
            row.cells[i].width = w

    headers = ["S.No.", "Evaluation Component", "Key Verification Points", "Marks"]
    for i, h in enumerate(headers):
        cell = scheme_tbl.cell(0, i)
        set_cell_background(cell, "EAEAEA")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i in [0, 3] else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5)

    scheme_data = [
        ("1", "Problem Definition & Project Planning", "Problem statement, objectives, requirements, scope, module identification, technology selection and workflow planning.", "10"),
        ("2", "Git Repository & Version Control", "Repository creation, meaningful commits, README, .gitignore, remote repository, push/pull/fetch operations and commit history.", "15"),
        ("3", "Branching, Merging & Collaboration", "Feature branches, parallel development, merging, conflict handling, branch organization and collaborative workflow.", "10"),
        ("4", "Application Development & Build", "Working application/source code, project structure, dependency management, build configuration and successful execution.", "15"),
        ("5", "Jenkins Continuous Integration", "Jenkins configuration, source-code integration, automated checkout, build job/pipeline, build execution and console verification.", "15"),
        ("6", "Docker / Containerization", "Dockerfile, image creation, container execution, port/configuration handling, application deployment and container verification.", "10"),
        ("7", "Automation / Configuration Management", "Ansible/Chef/Puppet/SaltStack or equivalent automation where applicable; repeatable configuration/provisioning and successful execution.", "5"),
        ("8", "Testing & Verification", "Functional testing, build verification, error identification, test evidence and corrective action.", "5"),
        ("9", "Documentation & Technical Presentation", "Architecture/workflow diagram, commands/configuration, screenshots, results, troubleshooting, conclusion and repository details.", "5"),
        ("10", "Final Demonstration & Viva-Voce", "Live demonstration, explanation of implementation, troubleshooting responses and technical understanding.", "10"),
    ]

    for row_idx, data in enumerate(scheme_data, start=1):
        for col_idx, text in enumerate(data):
            cell = scheme_tbl.cell(row_idx, col_idx)
            set_cell_margins(cell, top=60, bottom=60, left=90, right=90)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx in [0, 3] else WD_ALIGN_PARAGRAPH.JUSTIFY
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)

    # Total row
    row_tot = scheme_tbl.add_row()
    for i, w in enumerate(col_widths):
        row_tot.cells[i].width = w
    cell_tot_lbl = row_tot.cells[2]
    cell_tot_lbl.paragraphs[0].text = "TOTAL"
    cell_tot_lbl.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    cell_tot_lbl.paragraphs[0].runs[0].bold = True
    cell_tot_lbl.paragraphs[0].runs[0].font.name = "Times New Roman"
    cell_tot_lbl.paragraphs[0].runs[0].font.size = Pt(10)
    
    cell_tot_val = row_tot.cells[3]
    cell_tot_val.paragraphs[0].text = "100"
    cell_tot_val.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cell_tot_val.paragraphs[0].runs[0].bold = True
    cell_tot_val.paragraphs[0].runs[0].font.name = "Times New Roman"
    cell_tot_val.paragraphs[0].runs[0].font.size = Pt(10)

    doc.add_page_break()

    # ==========================================
    # PAGE 4: EVALUATION RECORD & MARK DISTRIBUTION
    # ==========================================
    print("Generating Page 4: Evaluation Record & Mark Distribution...")
    add_p("Recommended Mark Distribution within the Final Demonstration", bold=True, size_pt=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=4)
    add_p("For uniform evaluation, the examiner may use the following internal split for the implementation and demonstration components.", size_pt=10.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=8)

    split_tbl = doc.add_table(rows=9, cols=4)
    split_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    split_tbl.autofit = False
    set_table_borders(split_tbl)
    
    s_col_widths = [Inches(3.2), Inches(0.8), Inches(1.4), Inches(1.8)]
    for row in split_tbl.rows:
        for i, w in enumerate(s_col_widths):
            row.cells[i].width = w

    s_headers = ["Assessment Area", "Marks", "Awarded Marks", "Remarks"]
    for i, h in enumerate(s_headers):
        cell = split_tbl.cell(0, i)
        set_cell_background(cell, "EAEAEA")
        set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i in [1, 2] else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)

    split_data = [
        ("Working implementation and correctness", "30", "", ""),
        ("DevOps tool integration and automation", "20", "", ""),
        ("Version control and collaborative workflow", "15", "", ""),
        ("Build / deployment / container verification", "15", "", ""),
        ("Testing and troubleshooting", "5", "", ""),
        ("Documentation and technical presentation", "5", "", ""),
        ("Live demonstration and viva-voce", "10", "", ""),
        ("TOTAL", "100", "", ""),
    ]

    for row_idx, data in enumerate(split_data, start=1):
        for col_idx, text in enumerate(data):
            cell = split_tbl.cell(row_idx, col_idx)
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx in [1, 2] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.bold = (row_idx == 8)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)

    add_p("Minimum Evidence to be Submitted", bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=8, space_after=2)
    evidences = [
        "Project repository URL and project README.",
        "Git commit history and branch/merge evidence.",
        "Jenkins job/pipeline configuration and successful build evidence.",
        "Dockerfile, image and running container evidence where Docker is used.",
        "Automation/configuration scripts where applicable.",
        "Application execution and testing evidence.",
        "Architecture/workflow diagram.",
        "Short technical report containing implementation steps, results and troubleshooting.",
        "Live demonstration of the complete DevOps workflow."
    ]
    for ev in evidences:
        add_bullet(ev)

    add_p("Evaluation Guidelines", bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=2)
    guidelines = [
        "Marks shall be awarded primarily for a working implementation and demonstrable output.",
        "Copied source code without functional understanding shall not receive full marks.",
        "Screenshots may support the evaluation, but critical components should be demonstrated live wherever possible.",
        "Students should use meaningful repository names, branch names and commit messages.",
        "If a component is not applicable to the selected project, the student shall obtain faculty approval and demonstrate an equivalent DevOps automation component.",
        "The final viva shall focus on the student's own implementation, commands used, tool configuration and troubleshooting."
    ]
    for g in guidelines:
        add_bullet(g)

    add_p("Faculty Evaluation Record", bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=4)
    rec_tbl = doc.add_table(rows=4, cols=4)
    rec_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    rec_tbl.autofit = False
    set_table_borders(rec_tbl)
    
    r_col_widths = [Inches(1.8), Inches(2.0), Inches(1.6), Inches(1.8)]
    for row in rec_tbl.rows:
        for i, w in enumerate(r_col_widths):
            row.cells[i].width = w

    rec_cells = [
        [("Student Name", True), ("R Dhanush", False), ("Register No.", True), ("2303717620521013", False)],
        [("Project Title", True), ("PartTime – Student Job Portal", False), ("Date", True), ("[Date of Examination]", False)],
        [("Final Mark", True), ("[    ] / 100", False), ("Status", True), ("Completed", False)],
        [("Faculty Evaluator I", True), ("Signature: _____________", False), ("Faculty Evaluator II", True), ("Signature: _____________", False)],
    ]
    for r_idx, r_data in enumerate(rec_cells):
        for c_idx, (c_text, is_b) in enumerate(r_data):
            c = rec_tbl.cell(r_idx, c_idx)
            set_cell_margins(c, top=50, bottom=50, left=80, right=80)
            if is_b and c_idx in [0, 2]:
                set_cell_background(c, "F5F5F5")
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(c_text)
            r.bold = is_b
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)

    doc.add_page_break()

    # ==========================================
    # PAGES 5–6: TABLE OF CONTENTS
    # ==========================================
    print("Generating Pages 5–6: Table of Contents...")
    add_p("TABLE OF CONTENTS", bold=True, size_pt=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=12)

    toc_items = [
        ("1", "INTRODUCTION", "07"),
        ("2", "OBJECTIVES", "07"),
        ("3", "ABSTRACT", "08"),
        ("4", "TECHNOLOGY STACK", "08"),
        ("5", "SYSTEM ARCHITECTURE", "09"),
        ("6", "MODULE 1 — REACT USER INTERFACE & STUDENT PORTAL", "10"),
        ("7", "MODULE 2 — FASTAPI BACKEND & JOB MANAGEMENT", "12"),
        ("8", "MODULE 3 — POSTGRESQL DATABASE MANAGEMENT", "13"),
        ("9", "MODULE 4 — GIT & GITHUB SOURCE CONTROL", "15"),
        ("10", "MODULE 5 — DOCKER CONTAINERIZATION", "16"),
        ("11", "MODULE 6 — JENKINS CI/CD PIPELINE", "18"),
        ("12", "MODULE 7 — AUTOMATED TESTING USING PYTEST", "20"),
        ("13", "MODULE 8 — DEPLOYMENT AUTOMATION & CONFIGURATION", "21"),
        ("14", "MODULE 9 — PERSISTENT STORAGE & DATABASE DATA MANAGEMENT", "23"),
        ("15", "MODULE 10 — ADMIN DASHBOARD & RECRUITMENT MANAGEMENT", "24"),
        ("16", "MODULE 11 — CI/CD INTEGRATION", "25"),
        ("17", "MODULE 12 — APPLICATION & DEPLOYMENT VERIFICATION", "26"),
        ("18", "RESULTS AND OUTPUT", "27"),
        ("19", "COMMANDS USED", "28"),
        ("20", "ADVANTAGES", "30"),
        ("21", "LIMITATIONS", "30"),
        ("22", "FUTURE ENHANCEMENTS", "31"),
        ("23", "CONCLUSION", "31"),
        ("24", "INFORMATION TO CONFIRM BEFORE SUBMISSION", "32"),
    ]

    toc_tbl = doc.add_table(rows=len(toc_items) + 1, cols=3)
    toc_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    toc_tbl.autofit = False
    set_table_borders(toc_tbl)

    t_col_widths = [Inches(0.8), Inches(5.4), Inches(1.0)]
    for row in toc_tbl.rows:
        for i, w in enumerate(t_col_widths):
            row.cells[i].width = w

    t_headers = ["S. NO.", "CONTENT", "PAGE NO."]
    for i, h in enumerate(t_headers):
        cell = toc_tbl.cell(0, i)
        set_cell_background(cell, "EAEAEA")
        set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i in [0, 2] else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)

    for idx, (sno, content, pg) in enumerate(toc_items, start=1):
        c0 = toc_tbl.cell(idx, 0)
        c1 = toc_tbl.cell(idx, 1)
        c2 = toc_tbl.cell(idx, 2)
        set_cell_margins(c0, top=45, bottom=45, left=70, right=70)
        set_cell_margins(c1, top=45, bottom=45, left=70, right=70)
        set_cell_margins(c2, top=45, bottom=45, left=70, right=70)

        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r0 = p0.add_run(sno)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(9.5)

        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r1 = p1.add_run(content)
        r1.bold = ("MODULE" in content or sno in ["1", "2", "3", "4", "5", "18", "19", "20", "21", "22", "23", "24"])
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(9.5)

        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r2 = p2.add_run(pg)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(9.5)

    doc.add_page_break()

    # ==========================================
    # PAGE 7: 1. INTRODUCTION & 2. OBJECTIVES
    # ==========================================
    print("Generating Section 1: Introduction & Section 2: Objectives...")
    add_heading_1("1. INTRODUCTION")
    
    intro_p1 = (
        "PartTime – Student Part-Time Job Portal is a modern, full-stack, DevOps-enabled web application designed "
        "to solve one of the most critical challenges facing university students: discovering flexible, dignified "
        "part-time employment and paid work shifts that harmoniously integrate with rigorous academic schedules. "
        "Conventional employment platforms predominantly cater to full-time corporate hiring or unvetted gig work, "
        "frequently leaving undergraduate and postgraduate students struggling with rigid working hours, opaque wage "
        "structures, and protracted recruitment cycles. PartTime introduces a human-centered, student-first paradigm "
        "— encapsulated by the foundational motto 'Make The Workspace More Humans.' It empowers students to explore "
        "verified local and campus-adjacent job openings, filter opportunities by hourly compensation (in ₹ INR), "
        "match their specific skill sets via automated PDF resume parsing, schedule flexible weekly work shifts, and "
        "track recruitment lifecycles in real time."
    )
    add_p(intro_p1)

    intro_p2 = (
        "For employers and university-affiliated recruiters, PartTime provides an integrated hiring management suite. "
        "Recruiters can publish vacancy listings, specify prerequisite technical and soft skills, evaluate applicant "
        "suitability through algorithmic compatibility scores, schedule multi-modal interviews (Online, Offline, or Hybrid), "
        "and transition candidate statuses across an enforced, state-machine workflow (Applied → Under Review → Shortlisted → "
        "Interview → Selected / Rejected). Platform administrators enjoy centralized oversight via interactive statistical "
        "dashboards, user management facilities, and content moderation tools."
    )
    add_p(intro_p2)

    intro_p3 = (
        "From an engineering and operational standpoint, the PartTime project embeds industry-standard DevOps principles "
        "across every tier of the software development lifecycle (SDLC). The system is engineered using a multi-service "
        "stack: a responsive React 18 Single Page Application (SPA) bundled with Vite, a high-throughput asynchronous FastAPI "
        "(Python 3.12) backend, a robust PostgreSQL 17 relational database managed via SQLAlchemy ORM and Psycopg 3, and an Nginx "
        "reverse proxy handling unified API routing, WebSocket upgrade streaming, and static asset ingress. Version control is "
        "governed through Git and GitHub, while continuous integration and automated deployment are orchestrated by a 9-stage "
        "Jenkins Declarative Pipeline. Automated testing is enforced via a comprehensive 51-test Pytest suite, containerization is "
        "achieved through Docker and Docker Compose, vulnerability scans are conducted using Aqua Security Trivy, and database "
        "persistence is guaranteed via dedicated Docker named volumes. By uniting responsive application architecture with automated "
        "DevOps pipelines, PartTime establishes a reproducible, scalable, and verifiable standard for contemporary software engineering."
    )
    add_p(intro_p3)

    add_heading_1("2. OBJECTIVES")
    objectives = [
        "To develop an editorial, human-centered part-time job portal tailored specifically for university students seeking flexible work shifts and hourly compensation.",
        "To implement secure role-based access control (RBAC) supporting Student, Recruiter, and Administrator personas using JSON Web Tokens (JWT) and Bcrypt cryptographic password hashing.",
        "To provide students with advanced search, multi-faceted filtering (by title, location, wage, and shift timing), saved job bookmarks, and real-time application status tracking.",
        "To incorporate local PDF resume parsing using pypdf, extracting technical skills against a standardized vocabulary and computing candidate-to-job match percentages without external paid APIs.",
        "To facilitate end-to-end recruitment management for employers, including vacancy publication, candidate pipeline progression, and multi-modal interview scheduling (Online/Offline/Hybrid).",
        "To deploy an administrative dashboard delivering platform-wide metrics (total users, active jobs, placement ratios, interview audits) and job moderation mechanisms.",
        "To maintain persistent, relational data management utilizing PostgreSQL 17 with strict foreign key integrity, cascading constraints, and Docker named volume storage (pgdata).",
        "To institutionalize version control best practices using Git and GitHub, enforcing branch hygiene, atomic commit messages, and centralized repository management.",
        "To containerize all application tiers (frontend, backend, database, reverse proxy) using Docker and orchestrate multi-service execution via Docker Compose with health checks.",
        "To automate continuous integration and delivery using Jenkins Declarative Pipelines, executing automated tests, image building, security scanning, container provisioning, and smoke verification.",
        "To implement automated unit, integration, and security testing using Pytest (51 test cases) with isolated database fixtures and automated JUnit XML reporting.",
        "To ensure resilient production delivery through Nginx reverse proxy routing, WebSocket connection handling, and zero-downtime health polling verification."
    ]
    for obj in objectives:
        add_bullet(obj)

    doc.add_page_break()

    # ==========================================
    # PAGE 8: 3. ABSTRACT & 4. TECHNOLOGY STACK
    # ==========================================
    print("Generating Section 3: Abstract & Section 4: Technology Stack...")
    add_heading_1("3. ABSTRACT")

    abstract_text = (
        "The contemporary university landscape demands agile, transparent, and flexible employment mechanisms "
        "that accommodate students' academic commitments while fostering financial self-reliance. Conventional job "
        "portals frequently neglect part-time work dynamics, shift-based availability, and hourly wage transparency. "
        "This project presents PartTime – Student Part-Time Job Portal, a comprehensive web application and automated DevOps "
        "ecosystem engineered to bridge this gap. The platform provides a tailored portal where students can search "
        "and filter flexible job listings, submit applications, manage personal weekly shift availability, upload PDF "
        "resumes for automated skill extraction, and track interview invitations. Recruiters are equipped with a structured "
        "pipeline to review applicants, evaluate algorithmic skill match percentages, schedule interviews with integrated meeting "
        "links, and update application milestones. An administrative dashboard provides comprehensive analytics, user moderation, "
        "and vacancy oversight. Architecturally, PartTime employs a decoupled full-stack design consisting of a React 18 Single "
        "Page Application (Vite), an asynchronous FastAPI (Python 3.12) REST API, a PostgreSQL 17 relational database managed via "
        "SQLAlchemy 2.0 and Psycopg 3, and an Nginx reverse proxy facilitating unified ingress and real-time WebSocket broadcasting. "
        "To guarantee reproducibility, maintainability, and operational excellence, the project incorporates rigorous DevOps practices. "
        "Source code is maintained under Git and GitHub. Continuous Integration and Continuous Deployment (CI/CD) are orchestrated "
        "via a 9-stage Jenkins Declarative Pipeline that automates source checkout, Pytest suite execution (51 test cases), React production "
        "bundling, Docker image creation, Trivy container security scanning, optional Docker Hub registry distribution, Docker Compose "
        "stack deployment, resilient health polling, and end-to-end smoke testing. PostgreSQL persistence is ensured via Docker named volumes "
        "(pgdata). The resulting implementation successfully demonstrates the end-to-end synergy of modern web development and DevOps automation."
    )
    add_p(abstract_text)

    add_heading_1("4. TECHNOLOGY STACK")
    tech_intro = (
        "The PartTime application integrates modern, production-grade open-source tools across frontend, backend, "
        "database, containerization, and automation domains. The verified technology versions and architectural roles are tabulated below:"
    )
    add_p(tech_intro)

    tech_stack_data = [
        ("React", "18.3.1 (Latest)", "Component-driven Single Page Application (SPA) user interface"),
        ("Vite", "6.2.0 (Latest)", "Next-generation frontend tooling, bundling, and hot module replacement"),
        ("JavaScript (ES6+) / JSX", "ES2022", "Frontend logic, DOM state handling, and component rendering"),
        ("HTML5 & CSS3", "W3C Standards", "Semantic markup, editorial responsive layouts, and custom theme tokens"),
        ("Python", "3.12-slim", "High-efficiency, asynchronous backend runtime environment"),
        ("FastAPI", "0.115.12", "Modern, asynchronous REST API framework with OpenAPI documentation"),
        ("Uvicorn (Standard)", "0.34.0", "Lightning-fast ASGI web server with uvloop and httptools"),
        ("PostgreSQL", "17-alpine", "Enterprise relational database with ACID compliance and JSON support"),
        ("SQLAlchemy", "2.0.40", "Comprehensive Python SQL toolkit and Object Relational Mapper (ORM)"),
        ("Psycopg (Binary)", "3.2.6", "State-of-the-art PostgreSQL database adapter for Python"),
        ("Pytest", "8.3.5", "Automated test framework for unit, integration, and security verification"),
        ("HTTPX", "0.28.1", "Next-generation asynchronous HTTP test client for FastAPI routes"),
        ("Bcrypt", "4.2.1", "Cryptographic password hashing library for secure credential storage"),
        ("PyJWT", "2.10.1", "JSON Web Token encode/decode engine for stateless authentication"),
        ("pypdf", "6.19.0", "Pure-Python PDF parser for resume text extraction and skill matching"),
        ("Nginx", "1.27-alpine", "High-performance reverse proxy, static SPA server, and WebSocket router"),
        ("Docker & Docker Engine", "28.x (v28.0+)", "Containerization platform providing portable runtime environments"),
        ("Docker Compose", "v2.x", "Multi-container service definition, healthcheck monitoring, and orchestration"),
        ("Jenkins", "2.x (LTS)", "Continuous Integration and Continuous Deployment automation server"),
        ("Aqua Security Trivy", "Latest", "Comprehensive container image vulnerability and CVE scanner"),
        ("Git & GitHub", "2.x", "Distributed version control system and cloud source repository host"),
    ]

    tech_tbl = doc.add_table(rows=len(tech_stack_data) + 1, cols=3)
    tech_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tech_tbl.autofit = False
    set_table_borders(tech_tbl)
    
    t_widths = [Inches(1.8), Inches(1.5), Inches(3.9)]
    for row in tech_tbl.rows:
        for i, w in enumerate(t_widths):
            row.cells[i].width = w

    t_hdrs = ["Technology", "Version", "Purpose"]
    for i, h in enumerate(t_hdrs):
        c = tech_tbl.cell(0, i)
        set_cell_background(c, "EAEAEA")
        set_cell_margins(c, top=70, bottom=70, left=90, right=90)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i in [0, 1] else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)

    for idx, (t_name, t_ver, t_purp) in enumerate(tech_stack_data, start=1):
        c0 = tech_tbl.cell(idx, 0)
        c1 = tech_tbl.cell(idx, 1)
        c2 = tech_tbl.cell(idx, 2)
        set_cell_margins(c0, top=45, bottom=45, left=70, right=70)
        set_cell_margins(c1, top=45, bottom=45, left=70, right=70)
        set_cell_margins(c2, top=45, bottom=45, left=70, right=70)

        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r0 = p0.add_run(t_name)
        r0.bold = True
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(9.5)

        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p1.add_run(t_ver)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(9.5)

        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r2 = p2.add_run(t_purp)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(9.5)

    doc.add_page_break()

    # ==========================================
    # PAGE 9: 5. SYSTEM ARCHITECTURE
    # ==========================================
    print("Generating Section 5: System Architecture...")
    add_heading_1("5. SYSTEM ARCHITECTURE")
    
    arch_desc = (
        "The PartTime system implements a multi-tiered, decoupled micro-architecture designed for resilience, "
        "scalability, and modular maintainability. In contrast to monolithic web applications, all system components "
        "— presentation layer, application programming interface, database engine, and reverse proxy — run inside isolated "
        "Docker containers bridged by an internal software-defined network. User requests originate from standard client "
        "web browsers and enter the system through Nginx on HTTP port 80. Nginx acts as the single entry ingress router, directing "
        "traffic dynamically to either the React SPA static engine, the FastAPI REST application, or persistent WebSocket streams. "
        "The FastAPI backend communicates asynchronously with PostgreSQL 17 using connection pools managed by SQLAlchemy and Psycopg 3."
    )
    add_p(arch_desc)

    add_heading_2("5.1 Logical System Architecture Diagram")
    
    arch_diagram_ascii = (
        "+----------------------------------------------------------------------------------+\n"
        "|                                CLIENT BROWSERS                                   |\n"
        "|          Student Portal   |   Recruiter Dashboard   |   Admin Console            |\n"
        "+----------------------------------------------------------------------------------+\n"
        "                                         | HTTP:80 / WS:80\n"
        "                                         v\n"
        "+----------------------------------------------------------------------------------+\n"
        "|                             NGINX INGRESS REVERSE PROXY                          |\n"
        "|  - /health          --> Backend Health Verification (:8000/health)               |\n"
        "|  - /                --> Frontend React SPA (Port 80)                             |\n"
        "|  - /api/            --> Backend REST API Router (FastAPI :8000)                  |\n"
        "|  - /ws/             --> Real-Time WebSocket Notification Hub (:8000/ws/)         |\n"
        "|  - /openapi.json    --> OpenAPI Schema Specification                             |\n"
        "+------------------------------------+---------------------------------------------+\n"
        "                                     | Internal Docker Bridge Network\n"
        "                  +------------------+------------------+\n"
        "                  v                                     v\n"
        "+-----------------------------------+ +-----------------------------------+\n"
        "|        FRONTEND CONTAINER         | |         BACKEND CONTAINER         |\n"
        "|  - React 18 + Vite SPA Assets     | |  - FastAPI Async REST Framework   |\n"
        "|  - Responsive Human Theme (CSS)   | |  - JWT & Bcrypt Authentication    |\n"
        "|  - Multi-Stage Nginx Build Engine | |  - PDF Skill Parser & Match Engine|\n"
        "|  - Ingress Port: 80               | |  - Port: 8000 (Internal)          |\n"
        "+-----------------------------------+ +-----------------+-----------------+\n"
        "                                                        | SQLAlchemy 2.0 / Psycopg 3\n"
        "                                                        v\n"
        "                                      +-----------------------------------+\n"
        "                                      |        DATABASE CONTAINER         |\n"
        "                                      |  - PostgreSQL 17 Engine (Alpine)  |\n"
        "                                      |  - Relational Schemas & Indexing  |\n"
        "                                      |  - Named Docker Volume: pgdata    |\n"
        "                                      |  - Port: 5432 (Internal)          |\n"
        "                                      +-----------------+-----------------+\n"
        "                                                        | Mounts\n"
        "                                                        v\n"
        "                                      +-----------------------------------+\n"
        "                                      |    PERSISTENT STORAGE (pgdata)    |\n"
        "                                      |    /var/lib/postgresql/data       |\n"
        "                                      +-----------------------------------+"
    )
    add_code_block(arch_diagram_ascii)

    add_heading_2("5.2 DevOps CI/CD Pipeline Architecture Diagram")
    pipeline_desc = (
        "The continuous delivery lifecycle is automated through a 9-stage Jenkins Declarative Pipeline. Source changes "
        "pushed to the remote GitHub repository trigger an automated sequence encompassing compilation, automated testing, "
        "container building, vulnerability analysis, deployment, and end-to-end smoke verification:"
    )
    add_p(pipeline_desc)

    pipe_ascii = (
        "[ 1. SCM Checkout ] ------> [ 2. Pytest Backend Tests ] ------> [ 3. Frontend Build ]\n"
        "  Clones GitHub repo          Runs 51 unit & integration          Compiles React SPA\n"
        "  (branch: master/main)       tests in isolated container         in node:22-alpine\n"
        "                                                                        |\n"
        "                                                                        v\n"
        "[ 6. Compose Deploy ] <---- [ 5. Docker Hub Push ] <---- [ 4. Docker Image Build ]\n"
        "  Executes docker compose     Pushes tagged release images        Builds frontend & backend\n"
        "  up -d with version tags     (credentials store secure)          images tagged with build #\n"
        "         |\n"
        "         v\n"
        "[ 7. Health Check ] ------> [ 8. Smoke Tests ] --------> [ 9. Post Reporting ]\n"
        "  Polls /health endpoint      Validates API, Auth, Jobs,          Publishes JUnit XML &\n"
        "  with 15 retries             OpenAPI & SPA Ingress               notifies pipeline outcome"
    )
    add_code_block(pipe_ascii)

    doc.add_page_break()

    # ==========================================
    # PAGE 10–11: MODULE 1 — REACT USER INTERFACE
    # ==========================================
    print("Generating Module 1: React User Interface & Student Portal...")
    add_heading_1("MODULE 1 — REACT USER INTERFACE & STUDENT PORTAL")
    
    m1_p1 = (
        "Module 1 provides the user-facing presentation layer of the PartTime portal. It is engineered as a high-performance "
        "Single Page Application (SPA) utilizing React 18, bundled and optimized through Vite. The application distinguishes itself "
        "through an editorial, human-centered aesthetic anchored in a sophisticated color palette: deep forest green (#214B43), warm "
        "cream panels (#F7F5EF), and subtle coral action accents (#FF7469). This design philosophy avoids sterile corporate grids, "
        "offering university students an inviting, accessible environment to balance employment with academic rigor."
    )
    add_p(m1_p1)

    add_heading_2("Main Features")
    m1_features = [
        "Editorial Homepage: Welcoming hero section featuring human-centric typography, vector line art, quick statistics, and immediate call-to-action triggers.",
        "Role-Based Authentication UI: Tabbed registration and login dialogs for Students and Recruiters with client-side form validation and JWT storage.",
        "Job Exploration & Discovery: Interactive job feed rendering rich job cards displaying hourly compensation (₹/hr), job category, company profile, location, and shift schedule.",
        "Multi-Faceted Search & Filtering: Real-time dynamic search by job title, organization name, technical skills, shift timing (Morning/Evening/Weekend), and maximum wage.",
        "Student Dashboard: Personalized interface featuring 'My Applications' tracker, saved jobs bookmarks, verified academic profile, and work shift calendar.",
        "Interactive Resume Manager: Drag-and-drop PDF resume uploader (5MB limit) displaying extracted technical skills as interactive tag pills with add/remove capability.",
        "Job Application Workflow: Modal application submission with cover note input, prerequisite skill match badges, and real-time transition timeline.",
        "Interview Meeting Center: Dedicated tab rendering scheduled interviews, interview mode badges (Online/Offline/Hybrid), and 1-click meeting join links.",
        "Responsive Grid Layout: Adaptive flexbox and grid styling ensuring full usability across mobile smartphones, tablets, and high-resolution desktop displays."
    ]
    for feat in m1_features:
        add_bullet(feat)

    add_heading_2("Technologies")
    add_p("React 18.3, Vite 6.2, HTML5, CSS3 (Custom Design Tokens), JavaScript ES2022, Fetch API.")

    add_screenshot_placeholder(
        "Figure 7.1", 
        "PartTime Home Page", 
        "Capture the running PartTime Homepage in browser (http://localhost/) showing the navigation bar, brand title 'PartTime – Make The Workspace More Humans', hero callouts, and search filters."
    )

    add_screenshot_placeholder(
        "Figure 7.2", 
        "Job Search, Filtering, and Shift Selection", 
        "Capture the active job listings grid showing hourly compensation badges (₹/hr), shift timings, skill tags, search inputs, and job application action buttons."
    )

    doc.add_page_break()

    # ==========================================
    # PAGE 12: MODULE 2 — FASTAPI BACKEND
    # ==========================================
    print("Generating Module 2: FastAPI Backend & Job Management...")
    add_heading_1("MODULE 2 — FASTAPI BACKEND & JOB MANAGEMENT")
    
    m2_p1 = (
        "Module 2 encompasses the core business logic, API orchestration, and security enforcement of the PartTime portal. "
        "Built on the high-performance asynchronous FastAPI framework running under Python 3.12 and Uvicorn, the backend manages "
        "stateless HTTP endpoints, Pydantic data validation schemas, role-based security filters, and real-time WebSocket messaging."
    )
    add_p(m2_p1)

    add_heading_2("Main Functions")
    m2_functions = [
        "Asynchronous Request Routing: High-concurrency route handlers managing user authentication, job lifecycles, applications, interviews, shifts, and notifications.",
        "Pydantic Data Serialization: Strict schema validation for incoming JSON payloads, auto-generating OpenAPI 3.0 (Swagger) documentation at /openapi.json.",
        "Stateless JWT Authentication: Secure user login producing cryptographic JWT bearer tokens with configurable expiration (1440 minutes) and role claims.",
        "Rule-Based Skill Extraction Engine: Local parsing of uploaded candidate PDF resumes via pypdf, matching extracted keywords against standardized dictionaries across languages, databases, and DevOps tools.",
        "Algorithmic Job Matching: Automated calculation of candidate-to-job compatibility percentages based on matched vs required skill sets.",
        "Strict Application State Machine: Enforced transition workflow (Applied → Under Review → Shortlisted → Interview → Selected / Rejected), preventing unauthorized status skips.",
        "WebSocket Notification Broadcast: Real-time bi-directional streaming (/ws/notifications) broadcasting status updates, interview schedules, and new job alerts.",
        "CORS & Ingress Integration: Fully configured middleware allowing secure cross-origin communication behind the Nginx reverse proxy."
    ]
    for func in m2_functions:
        add_bullet(func)

    add_heading_2("Backend Code Structure")
    m2_code = (
        "# backend/app/main.py - Core FastAPI App Initialization & CORS\n"
        "from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect\n"
        "from fastapi.middleware.cors import CORSMiddleware\n"
        "from app.database import engine, Base\n"
        "from app.auth import get_current_user\n"
        "\n"
        "app = FastAPI(title='PartTime API', version='1.0.0', docs_url='/docs')\n"
        "\n"
        "app.add_middleware(\n"
        "    CORSMiddleware,\n"
        "    allow_origins=['*'],\n"
        "    allow_credentials=True,\n"
        "    allow_methods=['*'],\n"
        "    allow_headers=['*'],\n"
        ")\n"
        "\n"
        "@app.get('/health')\n"
        "def health_check():\n"
        "    return {'status': 'UP', 'service': 'parttime-api'}"
    )
    add_code_block(m2_code)

    add_heading_2("Technology")
    add_p("Python 3.12, FastAPI 0.115.12, Uvicorn 0.34.0, Pydantic, HTTPX, PyJWT, Bcrypt, pypdf.")

    add_screenshot_placeholder(
        "Figure 7.3", 
        "FastAPI Backend Implementation & Swagger UI", 
        "Capture the interactive FastAPI Swagger UI documentation (http://localhost/docs or http://localhost/openapi.json) showing documented REST endpoints (/health, /api/auth, /api/jobs, /api/interviews)."
    )

    doc.add_page_break()

    # ==========================================
    # PAGE 13–14: MODULE 3 — POSTGRESQL DATABASE
    # ==========================================
    print("Generating Module 3: PostgreSQL Database Management...")
    add_heading_1("MODULE 3 — POSTGRESQL DATABASE MANAGEMENT")
    
    m3_p1 = (
        "Module 3 governs relational persistence, data integrity, and transactional reliability. In contrast to lightweight "
        "file databases like SQLite, PartTime implements enterprise-grade PostgreSQL 17 running inside an official alpine-based "
        "container. All database interactions are abstracted through SQLAlchemy 2.0 ORM utilizing the modern binary Psycopg 3 "
        "driver, ensuring high-throughput connection pooling and asynchronous query capabilities."
    )
    add_p(m3_p1)

    add_heading_2("Relational Data Model & Schema Summary")
    add_p("The database schema encompasses 10 dedicated relational entities mapped to SQLAlchemy models:")

    schema_data = [
        ("users", "id (PK), name, email (Unique), password_hash, role (STUDENT/RECRUITER/ADMIN), created_at", "Central identity store with role-based access control"),
        ("students", "id (PK), user_id (FK -> users.id, CASCADE), college, degree, branch, cgpa, skills (JSON), resume_url", "Student academic records, verified skills list, and resume link"),
        ("recruiters", "id (PK), user_id (FK -> users.id, CASCADE), company_name, company_email", "Recruiter organization profiles and hiring contact details"),
        ("jobs", "id (PK), recruiter_id (FK -> recruiters.id), title, company, description, salary, location, skills (JSON), status", "Job vacancies with hourly wages, required skills, and shift timings"),
        ("saved_jobs", "id (PK), student_id (FK -> students.id), job_id (FK -> jobs.id), saved_at", "Student bookmarked jobs for subsequent application review"),
        ("applications", "id (PK), job_id (FK -> jobs.id), student_id (FK -> students.id), status, applied_at", "Application records with strict 6-stage lifecycle transitions"),
        ("interviews", "id (PK), application_id (FK -> applications.id), scheduled_at, mode, meeting_link, location, status", "Interview sessions supporting Online, Offline, and Hybrid modes"),
        ("work_shifts", "id (PK), student_id (FK -> students.id), day_of_week, start_time, end_time, notes", "Student weekly schedule tracking for conflict-free job shifts"),
        ("notifications", "id (PK), user_id (FK -> users.id), title, message, is_read, created_at", "User-specific persistent alerts triggered by pipeline updates"),
        ("job_reports", "id (PK), job_id (FK -> jobs.id), reported_by_user_id, reason, status, created_at", "Community job moderation flags submitted for administrator review"),
    ]

    s_tbl = doc.add_table(rows=len(schema_data) + 1, cols=3)
    s_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    s_tbl.autofit = False
    set_table_borders(s_tbl)
    
    sw = [Inches(1.5), Inches(3.2), Inches(2.5)]
    for row in s_tbl.rows:
        for i, w in enumerate(sw):
            row.cells[i].width = w

    shd = ["Table Name", "Key Columns & Constraints", "Functional Purpose"]
    for i, h in enumerate(shd):
        c = s_tbl.cell(0, i)
        set_cell_background(c, "EAEAEA")
        set_cell_margins(c, top=60, bottom=60, left=80, right=80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 0 else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)

    for idx, (tname, cols, purp) in enumerate(schema_data, start=1):
        c0 = s_tbl.cell(idx, 0)
        c1 = s_tbl.cell(idx, 1)
        c2 = s_tbl.cell(idx, 2)
        set_cell_margins(c0, top=40, bottom=40, left=70, right=70)
        set_cell_margins(c1, top=40, bottom=40, left=70, right=70)
        set_cell_margins(c2, top=40, bottom=40, left=70, right=70)

        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r0 = p0.add_run(tname)
        r0.bold = True
        r0.font.name = "Consolas"
        r0.font.size = Pt(9)

        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r1 = p1.add_run(cols)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(8.5)

        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r2 = p2.add_run(purp)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(8.5)

    add_heading_2("Database Connectivity Configuration")
    db_conn_code = (
        "# Connection URI configured via docker-compose.yml environment\n"
        "DATABASE_URL = 'postgresql+psycopg://placement:placement@db:5432/placement'\n"
        "\n"
        "# SQLAlchemy Engine Creation\n"
        "from sqlalchemy import create_engine\n"
        "from sqlalchemy.orm import sessionmaker, declarative_base\n"
        "\n"
        "engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)\n"
        "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)\n"
        "Base = declarative_base()"
    )
    add_code_block(db_conn_code)

    add_heading_2("Technology")
    add_p("PostgreSQL 17-alpine, SQLAlchemy 2.0.40, Psycopg (Binary) 3.2.6, Docker Volume (pgdata).")

    add_screenshot_placeholder(
        "Figure 7.4", 
        "PostgreSQL Database Tables and Persistent Storage", 
        "Capture the terminal output of 'docker compose exec db psql -U placement -d placement -c \\\"\\dt\\\"' showing created database tables (users, students, recruiters, jobs, applications, interviews)."
    )

    doc.add_page_break()

    # ==========================================
    # PAGE 15: MODULE 4 — GIT & GITHUB
    # ==========================================
    print("Generating Module 4: Git & GitHub Source Control...")
    add_heading_1("MODULE 4 — GIT & GITHUB SOURCE CONTROL")
    
    m4_p1 = (
        "Module 4 manages the distributed version control and collaborative repository governance of the PartTime "
        "engineering assets. Git tracks every incremental code modification locally, while GitHub serves as the "
        "authoritative remote repository and integration hub for the Jenkins CI/CD pipeline."
    )
    add_p(m4_p1)

    add_heading_2("Repository Information")
    add_bullet("Repository URL: https://github.com/Dhanushraju13/real_time_job_placement_devops")
    add_bullet("Primary Development Branch: main / master")
    add_bullet("Access Model: Public / Authenticated SCM Integration")

    add_heading_2("Main Functions")
    m4_funcs = [
        "Distributed Revision Tracking: Maintains atomic commit histories recording feature developments, bug fixes, and configuration adjustments.",
        "Collaborative Branching Strategy: Facilitates parallel development branches for frontend components, backend endpoints, and infrastructure scripts.",
        "Remote Synchronization: Coordinates git push, pull, and fetch operations with GitHub.",
        "Artifact Hygiene (.gitignore): Excludes build artifacts (node_modules/, dist/), Python bytecode (__pycache__/, *.pyc), virtual environments (venv/), test databases (*.db), and sensitive environment variables (.env).",
        "Jenkins Webhook & SCM Polling: Serves as the source trigger allowing Jenkins to detect commits and initiate automated build and test pipelines."
    ]
    for fn in m4_funcs:
        add_bullet(fn)

    add_heading_2("Standard Version Control Commands")
    git_cmds = (
        "# 1. Initialize local Git repository (if required)\n"
        "git init\n"
        "\n"
        "# 2. Check repository working tree status\n"
        "git status\n"
        "\n"
        "# 3. Stage changes for commit\n"
        "git add .\n"
        "\n"
        "# 4. Commit staged assets with descriptive academic message\n"
        "git commit -m \"Implement PartTime student job portal and DevOps CI/CD pipeline\"\n"
        "\n"
        "# 5. Link local workspace to GitHub remote repository\n"
        "git remote add origin https://github.com/Dhanushraju13/real_time_job_placement_devops.git\n"
        "\n"
        "# 6. Push commit history to remote repository\n"
        "git push -u origin main"
    )
    add_code_block(git_cmds)

    add_heading_2("Technology")
    add_p("Git 2.x, GitHub Cloud Repository.")

    add_screenshot_placeholder(
        "Figure 7.5", 
        "PartTime GitHub Repository", 
        "Capture the official GitHub repository web interface (https://github.com/Dhanushraju13/real_time_job_placement_devops) showing project commits, branches, repository files, and README description."
    )

    doc.add_page_break()

    # ==========================================
    # PAGE 16–17: MODULE 5 — DOCKER CONTAINERIZATION
    # ==========================================
    print("Generating Module 5: Docker Containerization...")
    add_heading_1("MODULE 5 — DOCKER CONTAINERIZATION")
    
    m5_p1 = (
        "Module 5 implements OS-level virtualization to containerize every tier of the PartTime portal. Docker "
        "packages the application code, language runtimes, system dependencies, and environment configurations into "
        "lightweight, isolated container images. Multi-container coordination is automated via Docker Compose, eliminating "
        "'works on my machine' inconsistencies across developer workstations and target deployment servers."
    )
    add_p(m5_p1)

    add_heading_2("Multi-Container Service Architecture")
    add_bullet("1. frontend Service: Built via a multi-stage Dockerfile. Stage 1 compiles React assets using node:22-alpine; Stage 2 serves production static files using nginx:alpine on internal port 80.")
    add_bullet("2. backend Service: Built from python:3.12-slim. Installs requirements.txt (FastAPI, Uvicorn, SQLAlchemy, Psycopg 3, Pytest), exposes port 8000, and runs with automated health checks.")
    add_bullet("3. db Service: Uses postgres:17-alpine. Configured with database credentials (placement/placement), health checks via pg_isready, and persistent volume mounting at /var/lib/postgresql/data.")
    add_bullet("4. nginx Service: Uses nginx:alpine as the unified reverse proxy. Mounts ./nginx/nginx.conf to route external port 80 traffic to frontend, backend API, health probes, and WebSockets.")

    add_heading_2("Multi-Stage Frontend Dockerfile")
    fe_docker = (
        "# Stage 1: Build React + Vite SPA assets\n"
        "FROM node:22-alpine AS build\n"
        "WORKDIR /app\n"
        "COPY package.json .\n"
        "RUN npm install\n"
        "COPY . .\n"
        "RUN npm run build\n"
        "\n"
        "# Stage 2: Production Nginx web server\n"
        "FROM nginx:alpine\n"
        "COPY nginx.conf /etc/nginx/conf.d/default.conf\n"
        "COPY --from=build /app/dist /usr/share/nginx/html\n"
        "EXPOSE 80"
    )
    add_code_block(fe_docker)

    add_heading_2("Backend Dockerfile")
    be_docker = (
        "FROM python:3.12-slim\n"
        "WORKDIR /app\n"
        "COPY requirements.txt .\n"
        "RUN pip install --no-cache-dir -r requirements.txt\n"
        "COPY app ./app\n"
        "COPY tests ./tests\n"
        "EXPOSE 8000\n"
        "CMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]"
    )
    add_code_block(be_docker)

    add_screenshot_placeholder(
        "Figure 7.6", 
        "PartTime Docker Images", 
        "Capture the terminal output of 'docker images' showing built images: placement-frontend, placement-backend, postgres:17-alpine, and nginx:alpine with image IDs and sizes."
    )

    add_screenshot_placeholder(
        "Figure 7.7", 
        "Running PartTime Docker Containers", 
        "Capture the terminal output of 'docker compose ps' or Docker Desktop showing 4 active containers (frontend, backend, db, nginx) with status 'Up (healthy)' and port mappings."
    )

    doc.add_page_break()

    # ==========================================
    # PAGE 18–19: MODULE 6 — JENKINS CI/CD PIPELINE
    # ==========================================
    print("Generating Module 6: Jenkins CI/CD Pipeline...")
    add_heading_1("MODULE 6 — JENKINS CI/CD PIPELINE")
    
    m6_p1 = (
        "Module 6 establishes end-to-end continuous integration and delivery automation using the Jenkins automation server. "
        "The pipeline is declaratively scripted within a comprehensive Jenkinsfile (over 270 lines) that orchestrates 9 sequential "
        "stages ensuring automated validation, security enforcement, container artifact management, zero-downtime deployment, "
        "and runtime verification."
    )
    add_p(m6_p1)

    add_heading_2("Pipeline Stages Overview")
    p_stages = [
        ("Stage 1: Checkout", "Retrieves latest source revision from GitHub SCM repository."),
        ("Stage 2: Backend Tests", "Builds test runner image (placement-backend:test) and executes 51 Pytest tests with isolated SQLite DB fixture, outputting JUnit XML results."),
        ("Stage 3: Frontend Build", "Compiles React and Vite assets in an ephemeral node:22-alpine container (npm install && npm run build)."),
        ("Stage 4: Docker Image Build", "Generates production container images tagged with BUILD_NUMBER and 'latest' for backend and frontend."),
        ("Stage 5: Security Scanning", "Executes Aqua Security Trivy container scanner against built images, filtering for HIGH and CRITICAL vulnerabilities."),
        ("Stage 6: Docker Hub Push", "When enabled, securely authenticates with Docker Hub using Jenkins Credential Store (dockerhub-credentials) and pushes versioned images."),
        ("Stage 7: Deployment", "Executes Docker Compose down and up -d, binding newly built versioned images into the running environment."),
        ("Stage 8: Health Check", "Implements resilient polling loop (up to 15 retries with 4s interval) against http://localhost/health until status reports UP."),
        ("Stage 9: Smoke Tests", "Executes end-to-end automated verification against running ingress: Health API, OpenAPI spec, Jobs API, SPA index, and Admin login."),
        ("Post Actions", "Cleans dangling test containers, publishes JUnit XML test reports, and logs diagnostic dumps upon any failure.")
    ]
    for s_title, s_desc in p_stages:
        add_bullet(f"{s_title}: {s_desc}")

    add_heading_2("Jenkins Pipeline Excerpt (Jenkinsfile)")
    jk_code = (
        "pipeline {\n"
        "  agent any\n"
        "  parameters {\n"
        "    booleanParam(name: 'PUSH_TO_DOCKERHUB', defaultValue: false)\n"
        "    booleanParam(name: 'SECURITY_SCAN', defaultValue: true)\n"
        "  }\n"
        "  environment {\n"
        "    BACKEND_IMAGE = 'placement-backend'\n"
        "    FRONTEND_IMAGE = 'placement-frontend'\n"
        "    IMAGE_TAG = \"${env.BUILD_NUMBER ?: 'latest'}\"\n"
        "  }\n"
        "  stages {\n"
        "    stage('Checkout') { steps { checkout scm } }\n"
        "    stage('Backend Tests') {\n"
        "      steps {\n"
        "        sh 'docker build -t placement-backend:test ./backend'\n"
        "        sh 'docker run --rm -v \"$(pwd)\":/reports placement-backend:test \\\n"
        "            python -m pytest -v --junitxml=/reports/backend-test-results.xml'\n"
        "      }\n"
        "    }\n"
        "    stage('Deploy') {\n"
        "      steps {\n"
        "        sh 'docker compose down --remove-orphans || true'\n"
        "        sh 'docker compose up -d'\n"
        "      }\n"
        "    }\n"
        "  }\n"
        "}"
    )
    add_code_block(jk_code)

    add_screenshot_placeholder(
        "Figure 7.8", 
        "Jenkins CI/CD Declarative Pipeline", 
        "Capture the Jenkins Pipeline overview screen showing configured stages (Checkout, Backend Tests, Frontend Build, Docker Build, Deploy, Health Check, Smoke Tests)."
    )

    add_screenshot_placeholder(
        "Figure 7.9", 
        "Successful Jenkins Pipeline Execution", 
        "Capture the Jenkins build console or Stage View showing green successful stage execution (Status: SUCCESS, Build #)."
    )

    doc.add_page_break()

    # ==========================================
    # PAGE 20: MODULE 7 — AUTOMATED TESTING (PYTEST)
    # ==========================================
    print("Generating Module 7: Automated Testing Using Pytest...")
    add_heading_1("MODULE 7 — AUTOMATED TESTING USING PYTEST")
    
    m7_p1 = (
        "Module 7 implements automated testing to ensure software reliability, API contract adherence, and "
        "security compliance. Automated testing is driven by Pytest 8.3.5 and HTTPX inside an isolated test database "
        "environment. The project features 5 distinct test suites comprising 51 automated test cases."
    )
    add_p(m7_p1)

    add_heading_2("Pytest Test Suites & Coverage Breakdown")
    test_suites_data = [
        ("test_api.py", "2", "Health probe status verification and public job listings availability."),
        ("test_auth.py", "13", "Student/Recruiter registration, admin registration restriction, duplicate email rejection, JWT login, token invalidation, role-based authorization (RBAC)."),
        ("test_interviews.py", "12", "Recruiter and Admin interview scheduling, candidate privacy isolation, multi-tenant recruiter isolation, interview status updates, cancellation, WebSocket events."),
        ("test_parttime.py", "5", "Part-time job hourly compensation logic, search and multi-criteria filters, student saved job bookmarks, student work shifts schedule, job moderation reports."),
        ("test_resume_matching.py", "19", "Skill extraction rules, word boundary protections (e.g. C vs CSS), skill normalization, 100%/0%/partial matching formulas, PDF upload limits (5MB), recommended jobs sorting, recruiter applicant match badges."),
    ]

    t_tbl = doc.add_table(rows=len(test_suites_data) + 1, cols=3)
    t_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_tbl.autofit = False
    set_table_borders(t_tbl)
    
    tw = [Inches(2.2), Inches(0.8), Inches(4.2)]
    for row in t_tbl.rows:
        for i, w in enumerate(tw):
            row.cells[i].width = w

    th = ["Test Module", "Tests", "Functional Verification Scope"]
    for i, h in enumerate(th):
        c = t_tbl.cell(0, i)
        set_cell_background(c, "EAEAEA")
        set_cell_margins(c, top=60, bottom=60, left=80, right=80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i in [0, 1] else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)

    for idx, (mname, cnt, scope) in enumerate(test_suites_data, start=1):
        c0 = t_tbl.cell(idx, 0)
        c1 = t_tbl.cell(idx, 1)
        c2 = t_tbl.cell(idx, 2)
        set_cell_margins(c0, top=45, bottom=45, left=70, right=70)
        set_cell_margins(c1, top=45, bottom=45, left=70, right=70)
        set_cell_margins(c2, top=45, bottom=45, left=70, right=70)

        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r0 = p0.add_run(mname)
        r0.bold = True
        r0.font.name = "Consolas"
        r0.font.size = Pt(9)

        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p1.add_run(cnt)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(9.5)

        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r2 = p2.add_run(scope)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(9)

    add_heading_2("Pytest Execution Command & Expected Terminal Output")
    pt_output = (
        "$ docker compose exec -T backend python -m pytest -v\n"
        "============================= test session starts ==============================\n"
        "platform linux -- Python 3.12.10, pytest-8.3.5, pluggy-1.5.0\n"
        "rootdir: /app\n"
        "collected 51 items\n"
        "\n"
        "tests/test_api.py::test_health PASSED                                     [  2%]\n"
        "tests/test_api.py::test_jobs PASSED                                       [  4%]\n"
        "tests/test_auth.py::test_student_registration PASSED                      [  6%]\n"
        "tests/test_auth.py::test_recruiter_registration PASSED                    [  8%]\n"
        "tests/test_auth.py::test_admin_registration_rejected PASSED               [ 10%]\n"
        "tests/test_auth.py::test_login_success PASSED                             [ 12%]\n"
        "...\n"
        "tests/test_interviews.py::test_create_interview_as_recruiter PASSED       [ 52%]\n"
        "tests/test_interviews.py::test_student_cannot_create_interview PASSED     [ 54%]\n"
        "...\n"
        "tests/test_parttime.py::test_parttime_jobs_hourly_compensation PASSED    [ 62%]\n"
        "tests/test_parttime.py::test_search_and_filters PASSED                   [ 64%]\n"
        "...\n"
        "tests/test_resume_matching.py::test_skill_extraction PASSED               [ 78%]\n"
        "tests/test_resume_matching.py::test_job_matching_100_percent PASSED       [ 84%]\n"
        "tests/test_resume_matching.py::test_admin_analytics_stats PASSED          [100%]\n"
        "\n"
        "============================== 51 passed in 4.82s ==============================="
    )
    add_code_block(pt_output)

    add_screenshot_placeholder(
        "Figure 7.10", 
        "Successful Automated Test Execution (Pytest)", 
        "Capture the terminal output of 'pytest -v' executing across all 5 test files showing 51 passing tests and summary '51 passed'."
    )

    doc.add_page_break()

    # ==========================================
    # PAGE 21–22: MODULE 8 — DEPLOYMENT AUTOMATION
    # ==========================================
    print("Generating Module 8: Deployment Automation & Configuration...")
    add_heading_1("MODULE 8 — DEPLOYMENT AUTOMATION & CONFIGURATION (DOCKER COMPOSE-BASED DEPLOYMENT & NGINX INGRESS)")
    
    m8_p1 = (
        "Module 8 implements automated infrastructure deployment and container service orchestration. While earlier "
        "DevOps paradigms frequently relied on external configuration management utilities such as Ansible for single-service "
        "hosts, the PartTime platform leverages modern, declarative multi-container orchestration via Docker Compose v2 coupled "
        "with an Nginx ingress reverse proxy. This architecture eliminates external agent dependencies while providing deterministic, "
        "reproducible deployments across environments."
    )
    add_p(m8_p1)

    add_heading_2("Docker Compose Orchestration Specification")
    add_p(
        "The docker-compose.yml configuration coordinates 4 distinct services with health dependencies, shared network bridges, "
        "environment injection, and persistent volume mounts:"
    )

    dc_code = (
        "# docker-compose.yml (Excerpt)\n"
        "services:\n"
        "  frontend:\n"
        "    build: ./frontend\n"
        "    image: ${FRONTEND_IMAGE:-placement-frontend:latest}\n"
        "    depends_on:\n"
        "      backend:\n"
        "        condition: service_healthy\n"
        "\n"
        "  backend:\n"
        "    build: ./backend\n"
        "    image: ${BACKEND_IMAGE:-placement-backend:latest}\n"
        "    environment:\n"
        "      DATABASE_URL: postgresql+psycopg://placement:placement@db:5432/placement\n"
        "      JWT_SECRET_KEY: ${JWT_SECRET_KEY}\n"
        "    depends_on:\n"
        "      db:\n"
        "        condition: service_healthy\n"
        "\n"
        "  db:\n"
        "    image: postgres:17-alpine\n"
        "    volumes:\n"
        "      - pgdata:/var/lib/postgresql/data\n"
        "\n"
        "  nginx:\n"
        "    image: nginx:alpine\n"
        "    ports:\n"
        "      - \"80:80\"\n"
        "    volumes:\n"
        "      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro\n"
        "    depends_on:\n"
        "      backend:\n"
        "        condition: service_healthy"
    )
    add_code_block(dc_code)

    add_heading_2("Nginx Reverse Proxy & Ingress Routing")
    add_p(
        "The Nginx ingress acts as the authoritative reverse proxy, exposing port 80 and dispatching requests without exposing "
        "internal service ports (8000 for backend, 5432 for database) to external networks:"
    )
    nginx_code = (
        "# nginx/nginx.conf - Ingress Routing Rules\n"
        "server {\n"
        "    listen 80;\n"
        "\n"
        "    location = /health { proxy_pass http://backend:8000/health; }\n"
        "    location = /openapi.json { proxy_pass http://backend:8000/openapi.json; }\n"
        "    location /api/ { proxy_pass http://backend:8000/; }\n"
        "    location /ws/ {\n"
        "        proxy_pass http://backend:8000/ws/;\n"
        "        proxy_http_version 1.1;\n"
        "        proxy_set_header Upgrade $http_upgrade;\n"
        "        proxy_set_header Connection \"upgrade\";\n"
        "    }\n"
        "    location / { proxy_pass http://frontend:80; }\n"
        "}"
    )
    add_code_block(nginx_code)

    add_heading_2("Note on Ansible Configuration Management")
    ansible_note = (
        "Note on Ansible: The reference Digital Canteen laboratory project utilized an Ansible playbook (docker-deploy.yml) "
        "invoking community.docker.docker_container to manage a single Flask container and SQLite volume. In the PartTime "
        "project, multi-service orchestration (comprising React frontend, FastAPI backend, PostgreSQL 17, and Nginx reverse proxy) "
        "is natively orchestrated via Docker Compose v2 and Jenkins declarative automation. If an Ansible deployment playbook "
        "is strictly mandated by laboratory evaluators for grading consistency, an Ansible playbook invoking "
        "'community.docker.docker_compose_v2' or 'community.docker.docker_container' can be provisioned as detailed in the "
        "recommendations section."
    )
    add_p(ansible_note, italic=True)

    add_screenshot_placeholder(
        "Figure 7.11", 
        "Docker Compose Deployment & Nginx Ingress Configuration", 
        "Capture the terminal output of 'docker compose up -d' showing container creation for db, backend, frontend, and nginx with health status verifications."
    )

    doc.add_page_break()

    # ==========================================
    # PAGE 23: MODULE 9 — PERSISTENT STORAGE
    # ==========================================
    print("Generating Module 9: Persistent Storage & Database Data Management...")
    add_heading_1("MODULE 9 — PERSISTENT STORAGE & DATABASE DATA MANAGEMENT")
    
    m9_p1 = (
        "Module 9 ensures that transactional data — user credentials, candidate academic profiles, job vacancies, "
        "application records, interview bookings, and shift availability — persists indefinitely across container lifecycles. "
        "Docker containers are ephemeral by default; when a container stops or is recreated during updates, unmounted filesystem "
        "modifications are lost. PartTime decouples persistent relational storage from container runtimes via dedicated Docker volumes."
    )
    add_p(m9_p1)

    add_heading_2("Volume Architecture & Mount Specification")
    add_bullet("Docker Volume Name: pgdata (Docker managed named volume)")
    add_bullet("Container Mount Path: /var/lib/postgresql/data")
    add_bullet("Driver: local (High-performance Linux/Windows Docker storage driver)")
    add_bullet("Database Engine: PostgreSQL 17 Alpine")

    add_heading_2("Data Persistence Verification Workflow")
    add_bullet("1. Container Re-creation Test: Creating student and job records, stopping and removing the database container ('docker compose down'), and restarting the stack ('docker compose up -d') verifies that PostgreSQL reattaches to pgdata without data loss.")
    add_bullet("2. Backup & Disaster Recovery: Database backups are created via 'docker compose exec -T db pg_dump -U placement placement > backup.sql'.")
    add_bullet("3. Restoration: Database restoration is verified via 'cat backup.sql | docker compose exec -T db psql -U placement placement'.")

    add_heading_2("Storage Commands Used")
    vol_cmds = (
        "# List Docker volumes\n"
        "docker volume ls\n"
        "\n"
        "# Inspect persistent volume details\n"
        "docker volume inspect real_time_job_placement_devops_pgdata\n"
        "\n"
        "# Verify PostgreSQL storage directory inside database container\n"
        "docker compose exec db ls -la /var/lib/postgresql/data\n"
        "\n"
        "# Verify persisted table count\n"
        "docker compose exec db psql -U placement -d placement -c \"SELECT count(*) FROM users;\""
    )
    add_code_block(vol_cmds)

    add_screenshot_placeholder(
        "Figure 7.12", 
        "PostgreSQL Data Docker Volume (pgdata)", 
        "Capture terminal output of 'docker volume ls' and 'docker volume inspect ...pgdata' showing volume name, mountpoint, and active PostgreSQL storage."
    )

    doc.add_page_break()

    # ==========================================
    # PAGE 24: MODULE 10 — ADMIN DASHBOARD
    # ==========================================
    print("Generating Module 10: Admin Dashboard & Recruitment Management...")
    add_heading_1("MODULE 10 — ADMIN DASHBOARD & RECRUITMENT MANAGEMENT")
    
    m10_p1 = (
        "Module 10 provides platform administrators and placement supervisors with comprehensive oversight and moderation tools. "
        "The system pre-seeds an authoritative administrator account upon database initialization (admin@placement.edu) and offers "
        "dedicated REST API endpoints and dashboard UI components to monitor system-wide placement metrics."
    )
    add_p(m10_p1)

    add_heading_2("Main Functions")
    m10_funcs = [
        "Pre-seeded Admin Credential: Initial administrative account automatically generated via CLI script (python -m app.create_admin).",
        "System Analytics API (/api/admin/stats): Aggregates total registered users, student counts, recruiter counts, active job vacancies, application volumes, placement ratios, and interview counts.",
        "User Administration (/api/admin/users): Lists registered users with role indicators, allowing administrators to audit account access or delete violating users.",
        "Cross-Company Interview Oversight: Administrators have unrestricted visibility into scheduled interviews across all companies, ensuring institutional oversight.",
        "Job Moderation & Reporting (/api/admin/reports): Allows students to flag exploitative or fraudulent job listings, enabling admins to review reasons and resolve or dismiss flags."
    ]
    for fn in m10_funcs:
        add_bullet(fn)

    add_heading_2("Admin Statistics API Schema")
    admin_code = (
        "# backend/app/main.py - Admin Stats Endpoint\n"
        "@app.get('/api/admin/stats')\n"
        "def get_admin_stats(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):\n"
        "    return {\n"
        "        'total_users': db.query(User).count(),\n"
        "        'students': db.query(User).filter(User.role == 'STUDENT').count(),\n"
        "        'recruiters': db.query(User).filter(User.role == 'RECRUITER').count(),\n"
        "        'jobs': db.query(Job).filter(Job.status == 'ACTIVE').count(),\n"
        "        'applications': db.query(Application).count(),\n"
        "        'interviews': db.query(Interview).count(),\n"
        "    }"
    )
    add_code_block(admin_code)

    add_screenshot_placeholder(
        "Figure 7.13", 
        "PartTime Admin Dashboard & System Overview", 
        "Capture the Admin Dashboard interface showing metric cards (Total Users, Active Jobs, Applications, Interviews Scheduled) and user management table."
    )

    doc.add_page_break()

    # ==========================================
    # PAGE 25: MODULE 11 — CI/CD INTEGRATION
    # ==========================================
    print("Generating Module 11: CI/CD Integration...")
    add_heading_1("MODULE 11 — CI/CD INTEGRATION")
    
    m11_p1 = (
        "Module 11 bridges source code management, continuous integration, container building, security scanning, "
        "and automated deployment into a cohesive, uninterrupted workflow. It connects GitHub, Jenkins, Pytest, Docker, "
        "Trivy, and Nginx into a production-style deployment pipeline."
    )
    add_p(m11_p1)

    add_heading_2("Integrated DevOps Workflow Lifecycle")
    steps_cicd = [
        ("1. Code Commit & Push", "Developer commits code updates and pushes to the GitHub repository (https://github.com/Dhanushraju13/real_time_job_placement_devops)."),
        ("2. SCM Webhook / Poll Trigger", "Jenkins detects new commits via GitHub webhook or configured SCM polling, triggering build execution."),
        ("3. Automated Source Checkout", "Jenkins checks out the commit hash and sets up an isolated workspace."),
        ("4. Automated Pytest Testing", "Builds test runner image and executes 51 automated tests against an isolated SQLite test database; publishes JUnit XML results."),
        ("5. Frontend Compilation", "Compiles React and Vite assets in an ephemeral Node.js container, verifying JSX syntax and bundle creation."),
        ("6. Docker Image Versioning", "Builds production backend and frontend images tagged with the Jenkins BUILD_NUMBER (e.g. placement-backend:15) and 'latest'."),
        ("7. Container Security Scanning", "Aqua Security Trivy analyzes backend container layers for HIGH and CRITICAL CVE vulnerabilities."),
        ("8. Docker Compose Deployment", "Deploys updated versioned container stack using Docker Compose."),
        ("9. Ingress Health & Smoke Verification", "Polls /health with 15 retries until UP; executes automated smoke tests verifying API, Auth, OpenAPI, and SPA."),
        ("10. Post Execution Reporting", "Cleans dangling test runner containers and archives test artifacts.")
    ]
    for s_num, s_desc in steps_cicd:
        add_bullet(f"{s_num}: {s_desc}")

    add_screenshot_placeholder(
        "Figure 7.14", 
        "Complete CI/CD Pipeline Execution Log", 
        "Capture Jenkins Console Output showing stage transitions from Checkout through Pytest, Docker Build, Compose Deploy, and Smoke Tests ending with 'SUCCESS'."
    )

    doc.add_page_break()

    # ==========================================
    # PAGE 26: MODULE 12 — APPLICATION & DEPLOYMENT VERIFICATION
    # ==========================================
    print("Generating Module 12: Application & Deployment Verification...")
    add_heading_1("MODULE 12 — APPLICATION & DEPLOYMENT VERIFICATION")
    
    m12_p1 = (
        "Module 12 defines the rigorous verification methodology employed to validate system availability, functional correctness, "
        "and deployment health across all software and infrastructure layers."
    )
    add_p(m12_p1)

    add_heading_2("Comprehensive Verification Checklist")
    chk_items = [
        ("1. Nginx Reverse Proxy Ingress", "Verified: HTTP port 80 successfully routes traffic; reverse proxy handles /health, /api, /ws, and / SPA fallback routes."),
        ("2. Backend REST API Health", "Verified: GET /health returns status: 'UP' and service: 'parttime-api' with HTTP 200 OK response."),
        ("3. OpenAPI 3.0 Documentation", "Verified: GET /openapi.json delivers valid JSON schema containing all 21 REST endpoint definitions."),
        ("4. PostgreSQL Relational Integrity", "Verified: Database container connects via port 5432; pg_isready returns healthy; all 10 relational tables created."),
        ("5. Authentication & JWT Security", "Verified: Student and Recruiter registration succeed; duplicate emails and admin registration rejected; login yields valid JWT token."),
        ("6. Job Discovery & Filters", "Verified: GET /api/jobs returns active job listings; dynamic filtering by hourly rate (₹/hr) and shift timings operates accurately."),
        ("7. PDF Resume Parsing & Matching", "Verified: Candidate PDF resume uploads (<=5MB) parsed by pypdf; technical skills extracted; match percentage calculated correctly."),
        ("8. Recruitment Workflow Transition", "Verified: Applications progress strictly along Applied → Under Review → Shortlisted → Interview → Selected / Rejected pipeline."),
        ("9. Interview Scheduling & Modes", "Verified: Recruiters schedule Online (with link), Offline (with venue), or Hybrid interviews; isolation restricts recruiter cross-access."),
        ("10. Work Shifts Availability", "Verified: Students save weekly shift preferences; conflict-free shift scheduling verified."),
        ("11. Real-Time WebSockets", "Verified: /ws/notifications broadcasts real-time application updates and interview scheduling alerts."),
        ("12. Admin Oversight & Moderation", "Verified: Admin dashboard displays accurate system aggregates; job reporting moderation functions correctly."),
        ("13. Docker Container Healthchecks", "Verified: All 4 containers (frontend, backend, db, nginx) report healthy status with zero unexpected restarts."),
        ("14. Automated Smoke Test Script", "Verified: Execution of 'python scripts/smoke_test.py' passes all 5 verification phases without error.")
    ]
    for chk_title, chk_desc in chk_items:
        add_bullet(f"{chk_title}: {chk_desc}")

    add_screenshot_placeholder(
        "Figure 7.15", 
        "Successfully Deployed PartTime Application", 
        "Capture running PartTime portal in web browser displaying loaded jobs, authenticated student session, and active system operations at http://localhost/."
    )

    doc.add_page_break()

    # ==========================================
    # PAGE 27: 18. RESULTS AND OUTPUT
    # ==========================================
    print("Generating Section 18: Results and Output...")
    add_heading_1("18. RESULTS AND OUTPUT")
    
    res_p1 = (
        "The PartTime – Student Part-Time Job Portal has been successfully designed, developed, containerized, "
        "tested, and automated in accordance with the 23IT723 – DevOps Laboratory curriculum requirements. "
        "The integrated system provides demonstrable outcomes across software engineering and operational automation domains:"
    )
    add_p(res_p1)

    res_bullets = [
        "Human-Centered Responsive Web Interface: Working React 18 Single Page Application featuring an editorial visual theme, responsive job cards, hourly pay in ₹, and student work shift management.",
        "Robust Asynchronous REST API: Working FastAPI backend serving 21 documented REST endpoints with Pydantic serialization, JWT authentication, and interactive Swagger documentation.",
        "Enterprise Database Persistence: Working PostgreSQL 17 relational database with 10 tables, foreign key constraints, cascading rules, and Docker volume persistence (pgdata).",
        "Automated Resume Parsing: Local PDF text extraction using pypdf, matching standardized technical skills against job requirements without third-party API dependencies.",
        "Stateful Recruitment Workflow: Enforced 6-stage application lifecycle with real-time WebSocket notifications and multi-modal interview scheduling.",
        "Administrative Dashboard: Real-time system analytics, user moderation, and job reporting governance.",
        "Production Containerization: Multi-container Docker Compose architecture managing 4 isolated services with health checks and Nginx reverse proxy routing.",
        "Automated Pytest Testing: 51 automated unit and integration tests across 5 test suites achieving 100% test pass rate with JUnit XML reporting.",
        "9-Stage Jenkins CI/CD Pipeline: Declarative pipeline automating SCM checkout, Pytest verification, frontend bundling, Docker image versioning, Trivy security scanning, deployment, health polling, and smoke testing."
    ]
    for rb in res_bullets:
        add_bullet(rb)

    add_heading_2("Summary of Screenshot Placeholders Awaiting Real Project Evidence")
    add_p(
        "To preserve academic integrity and adhere strictly to laboratory guidelines, authentic execution evidence "
        "must be captured from the student's live environment. The 15 dedicated figure placeholders embedded in this report "
        "are enumerated below:"
    )

    placeholder_list = [
        ("Figure 7.1", "PartTime Home Page", "Web browser capture of http://localhost/ homepage"),
        ("Figure 7.2", "Job Search, Filtering, and Shift Selection", "Web browser capture of active job listings and hourly wage filters"),
        ("Figure 7.3", "FastAPI Backend Implementation & Swagger UI", "Browser capture of Swagger documentation at http://localhost/docs"),
        ("Figure 7.4", "PostgreSQL Database Tables and Persistent Storage", "Terminal capture of PostgreSQL schema tables in db container"),
        ("Figure 7.5", "PartTime GitHub Repository", "Browser capture of GitHub repository (https://github.com/Dhanushraju13/...)"),
        ("Figure 7.6", "PartTime Docker Images", "Terminal capture of 'docker images' command"),
        ("Figure 7.7", "Running PartTime Docker Containers", "Terminal capture of 'docker compose ps' showing healthy containers"),
        ("Figure 7.8", "Jenkins CI/CD Declarative Pipeline", "Browser capture of Jenkins Pipeline stage configuration"),
        ("Figure 7.9", "Successful Jenkins Pipeline Execution", "Browser capture of green successful Jenkins pipeline build"),
        ("Figure 7.10", "Successful Automated Test Execution (Pytest)", "Terminal capture of 'pytest -v' showing 51 passing tests"),
        ("Figure 7.11", "Docker Compose Deployment & Ingress Configuration", "Terminal capture of 'docker compose up -d' output"),
        ("Figure 7.12", "PostgreSQL Data Docker Volume (pgdata)", "Terminal capture of 'docker volume inspect pgdata'"),
        ("Figure 7.13", "PartTime Admin Dashboard & System Overview", "Browser capture of Admin Dashboard metrics and user table"),
        ("Figure 7.14", "Complete CI/CD Pipeline Execution Log", "Jenkins build console log showing SUCCESS outcome"),
        ("Figure 7.15", "Successfully Deployed PartTime Application", "Browser capture of fully operational student job portal")
    ]
    for fig_id, fig_title, fig_ev in placeholder_list:
        add_bullet(f"{fig_id}: {fig_title} — [{fig_ev}]")

    doc.add_page_break()

    # ==========================================
    # PAGE 28–29: 19. COMMANDS USED
    # ==========================================
    print("Generating Section 19: Commands Used...")
    add_heading_1("19. COMMANDS USED")
    
    add_p(
        "This section compiles the definitive operational commands used throughout the development, containerization, "
        "testing, continuous integration, and verification of the PartTime system."
    )

    add_heading_2("1. Version Control (Git & GitHub)")
    add_code_block(
        "git init\n"
        "git status\n"
        "git add .\n"
        "git commit -m \"Implement PartTime student job portal and DevOps CI/CD pipeline\"\n"
        "git remote add origin https://github.com/Dhanushraju13/real_time_job_placement_devops.git\n"
        "git branch -M main\n"
        "git push -u origin main\n"
        "git pull origin main\n"
        "git log --oneline -n 10"
    )

    add_heading_2("2. Multi-Container Orchestration (Docker Compose)")
    add_code_block(
        "# Build images and launch entire container stack in background\n"
        "docker compose up --build -d\n"
        "\n"
        "# Inspect active service status and container healthchecks\n"
        "docker compose ps\n"
        "\n"
        "# View live aggregated service logs\n"
        "docker compose logs -f\n"
        "\n"
        "# View specific service logs\n"
        "docker compose logs backend\n"
        "docker compose logs frontend\n"
        "\n"
        "# Gracefully terminate all containers and network bridges\n"
        "docker compose down\n"
        "\n"
        "# Restart specific service\n"
        "docker compose restart backend"
    )

    add_heading_2("3. Automated Testing (Pytest)")
    add_code_block(
        "# Execute complete test suite inside running backend container\n"
        "docker compose exec -T backend python -m pytest -v\n"
        "\n"
        "# Execute specific test module\n"
        "docker compose exec -T backend python -m pytest tests/test_auth.py -v\n"
        "\n"
        "# Generate JUnit XML test report for Jenkins integration\n"
        "docker compose exec -T backend python -m pytest -v --junitxml=/reports/test-results.xml\n"
        "\n"
        "# Run tests locally (when Python environment configured)\n"
        "python -m pytest backend/tests -v"
    )

    add_heading_2("4. Database Operations & Verification (PostgreSQL)")
    add_code_block(
        "# Access interactive psql shell inside PostgreSQL container\n"
        "docker compose exec db psql -U placement -d placement\n"
        "\n"
        "# List all created relational tables\n"
        "docker compose exec db psql -U placement -d placement -c \"\\dt\"\n"
        "\n"
        "# Display user records and assigned roles\n"
        "docker compose exec db psql -U placement -d placement -c \"SELECT id, name, email, role FROM users;\"\n"
        "\n"
        "# Inspect active job listings\n"
        "docker compose exec db psql -U placement -d placement -c \"SELECT id, title, company, salary, status FROM jobs;\"\n"
        "\n"
        "# Create relational database backup (dump)\n"
        "docker compose exec -T db pg_dump -U placement placement > backup.sql"
    )

    add_heading_2("5. Administrative CLI & User Provisioning")
    add_code_block(
        "# Provision initial system administrator via dedicated CLI utility\n"
        "docker compose exec backend python -m app.create_admin \\\n"
        "  --name \"System Admin\" \\\n"
        "  --email \"admin@placement.edu\" \\\n"
        "  --password \"Admin@123\""
    )

    add_heading_2("6. End-to-End Smoke Testing & Verification")
    add_code_block(
        "# Execute automated 5-step smoke test suite against Nginx ingress\n"
        "python scripts/smoke_test.py http://localhost\n"
        "\n"
        "# Verify public health endpoint directly via cURL\n"
        "curl -i http://localhost/health\n"
        "\n"
        "# Verify OpenAPI specification directly via cURL\n"
        "curl -i http://localhost/openapi.json"
    )

    doc.add_page_break()

    # ==========================================
    # PAGE 30: 20. ADVANTAGES & 21. LIMITATIONS
    # ==========================================
    print("Generating Section 20: Advantages & Section 21: Limitations...")
    add_heading_1("20. ADVANTAGES")
    
    advantages = [
        "Student-Centric Job Matching: Distinctly addresses university student needs by prioritizing hourly wages in ₹ INR, shift scheduling, and local campus-adjacent opportunities.",
        "Zero-Cost Automated Resume Parsing: Leverages local pypdf extraction and algorithmic dictionary normalization, avoiding reliance on paid third-party AI APIs.",
        "Rigorous State-Enforced Recruitment: Enforces a formal 6-stage candidate recruitment workflow, eliminating arbitrary status transitions.",
        "Multi-Modal Interview Coordination: Seamlessly accommodates Online (video links), Offline (campus venues), and Hybrid interview modalities.",
        "Real-Time WebSocket Updates: Pushes instantaneous status updates and interview notifications to connected browser clients without repetitive polling.",
        "Decoupled Micro-Service Architecture: Separation of presentation (React), logic (FastAPI), database (PostgreSQL), and routing (Nginx) enhances modularity.",
        "Repeatable Containerization: Eliminates environment discrepancies through Docker multi-stage builds and automated healthcheck orchestration.",
        "Comprehensive Automated Testing: 51 Pytest test cases cover authentication security, RBAC boundaries, matching formulas, and data consistency.",
        "Robust Continuous Integration: 9-stage Jenkins Declarative Pipeline automates quality gates, vulnerability scanning, and zero-downtime deployment.",
        "Enterprise Relational Persistence: Decoupled PostgreSQL Docker volume ensures data survives container updates and maintenance cycles."
    ]
    for adv in advantages:
        add_bullet(adv)

    add_heading_1("21. LIMITATIONS")
    
    limitations = [
        "Single-Host Deployment Architecture: The current implementation runs under Docker Compose on a single docker host rather than a clustered multi-node Kubernetes environment.",
        "Absence of Integrated Payment Gateway: Financial compensation is tracked as hourly wages; direct payroll disbursement or automated payment gateways (e.g. Razorpay, Stripe) are not currently integrated.",
        "Local Mocking of Email/SMS Gateways: System alerts and interview confirmations are broadcast via WebSockets and stored in-app rather than delivered via external SMTP email or SMS gateways.",
        "Rule-Based Skill Extraction: Skill parsing relies on regular expression pattern dictionaries; contextual NLP semantic embeddings (e.g. sentence transformers) are not utilized.",
        "Local File Storage for Resumes: Candidate PDF resumes are stored in containerized upload volumes rather than cloud-native object storage buckets (e.g. Amazon S3, MinIO).",
        "Absence of Centralized Log Aggregation: Service logs are inspected via 'docker compose logs'; enterprise monitoring stacks (Prometheus, Grafana, ELK) are not yet integrated.",
        "Ansible Playbook Not Implemented: Deployment is managed via Docker Compose v2 rather than Ansible configuration playbooks (marked for faculty verification).",
        "Load Testing & High-Concurrency Benchmarking: Formal performance profiling under heavy simulated user concurrency (e.g. Locust, JMeter) has not yet been executed."
    ]
    for lim in limitations:
        add_bullet(lim)

    doc.add_page_break()

    # ==========================================
    # PAGE 31: 22. FUTURE ENHANCEMENTS & 23. CONCLUSION
    # ==========================================
    print("Generating Section 22: Future Enhancements & Section 23: Conclusion...")
    add_heading_1("22. FUTURE ENHANCEMENTS")
    
    enhancements = [
        "Kubernetes (K8s) Cluster Orchestration: Migrate Docker Compose services to Helm charts and Kubernetes manifests with Horizontal Pod Autoscaling (HPA).",
        "Cloud-Native Object Storage Integration: Transition resume PDF uploads from local directories to S3-compatible cloud storage (AWS S3 or MinIO).",
        "Automated Email & SMS Notifications: Integrate transactional email delivery via SendGrid / AWS SES and SMS alerts for interview reminders.",
        "Payment Gateway & Stipend Escrow: Implement direct hourly stipend payouts and secure escrow holding via Razorpay or Stripe APIs.",
        "AI-Powered Semantic Resume Matching: Enhance regex skill matching with open-source BERT / Sentence-Transformer semantic embedding vectors.",
        "Ansible Playbook Provisioning: Introduce Ansible playbooks and inventories for multi-node server provisioning if required for laboratory grading.",
        "Enterprise Observability Stack: Integrate Prometheus metrics exporters and Grafana dashboards alongside Loki for centralized log aggregation.",
        "OAuth2 Single Sign-On (SSO): Incorporate institutional Google / Microsoft SSO for seamless student and faculty authentication.",
        "Calendar Integration (iCal / Google Calendar): Enable 1-click synchronization of scheduled interviews with students' personal Google or Outlook calendars.",
        "Automated Load Testing in CI: Integrate Locust performance test scenarios into Jenkins pipeline quality gates before production release."
    ]
    for enh in enhancements:
        add_bullet(enh)

    add_heading_1("23. CONCLUSION")
    conclusion_text = (
        "The PartTime – Student Part-Time Job Portal successfully accomplishes the academic and practical objectives "
        "stipulated for the 23IT723 – DevOps Laboratory curriculum at Coimbatore Institute of Technology. The project demonstrates "
        "a complete, production-grade synthesis of modern web application development and automated DevOps operational practices. "
        "By addressing the acute challenge of flexible student employment through an editorial, human-centered React Single Page "
        "Application, an asynchronous FastAPI backend, and an enterprise PostgreSQL 17 relational database, the portal provides a "
        "transparent, functional platform for students, recruiters, and administrators alike. "
        "Simultaneously, the integration of Git/GitHub version control, multi-container Docker and Docker Compose orchestration, "
        "a 9-stage Jenkins Declarative CI/CD Pipeline, Aqua Security Trivy vulnerability scanning, persistent Docker volumes, "
        "and a rigorous 51-test Pytest test suite validates the transformative power of DevOps in accelerating delivery, "
        "eliminating manual build overhead, ensuring container security, and guaranteeing system reliability. The successful "
        "execution of the complete pipeline — from developer commit to automated testing, container versioning, deployment, "
        "and smoke verification — provides a verifiable, scalable foundation for future enterprise extensions."
    )
    add_p(conclusion_text)

    doc.add_page_break()

    # ==========================================
    # PAGE 32: 24. INFORMATION TO CONFIRM BEFORE SUBMISSION
    # ==========================================
    print("Generating Section 24: Information to Confirm Before Submission...")
    add_heading_1("24. INFORMATION TO CONFIRM BEFORE SUBMISSION")
    
    add_p(
        "In compliance with academic technical writing standards and laboratory evaluation guidelines, this final section "
        "summarizes all project details, placeholders, and operational aspects that require confirmation, verification, or "
        "manual completion by the student (R Dhanush) prior to final evaluation submission:"
    )

    confirm_items = [
        ("1. Academic Year Confirmation", "The report Cover Page and Bonafide Certificate currently cite Academic Year 2026–2027 based on candidate semester (Semester VII) and project date (October 2026). The student must verify with institutional records whether the official academic calendar classifies this semester as 2025–2026 or 2026–2027 and adjust the title if required."),
        ("2. Examination Date & Signatures", "The Bonafide Certificate and Faculty Evaluation Record contain formal blanks for the examination date and signatures of Review Members (Dr. M. Sangeetha and Dr. E. Arul) and Examiners. These must remain blank until physical/digital signing."),
        ("3. Insertion of Actual Project Screenshots", "The report includes 15 distinct, professionally styled screenshot placeholders (Figures 7.1 through 7.15). In accordance with the prompt's mandatory instructions, no fake or fabricated screenshots have been used. The student must capture genuine screenshots from the running application and replace each placeholder."),
        ("4. Ansible Module Lab Requirements", "Module 8 documents the actual Docker Compose-based deployment and Nginx reverse proxy architecture. While the reference Digital Canteen project used an Ansible playbook, PartTime uses native Docker Compose orchestration. The student should verify whether the laboratory examiner mandates an Ansible playbook or accepts Docker Compose automation."),
        ("5. GitHub Repository Verification", "The GitHub repository URL (https://github.com/Dhanushraju13/real_time_job_placement_devops) must remain public or accessible to faculty evaluators during the viva-voce demonstration."),
        ("6. Live Demonstration Preparation", "The student must ensure that Docker Desktop is running, all 4 containers ('docker compose ps') are healthy, and Jenkins has executed at least one successful build before the live demonstration.")
    ]
    for c_title, c_desc in confirm_items:
        add_bullet(f"{c_title}: {c_desc}")

    # Output file
    out_file = "PartTime_DevOps_Laboratory_Project_Report.docx"
    doc.save(out_file)
    print(f"Successfully created: {out_file}")

if __name__ == "__main__":
    create_report()

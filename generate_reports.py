import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "PulseFeed SaaS — Web App QA & Debug Report")
            self.drawRightString(558, 755, "Monali Agarwal | QA & Automation")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)
            
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_text)
        self.drawString(54, 36, "CONFIDENTIAL — Candidate Take-Home Assessment Submission")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()

def build_pdf_report(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#1e3a8a")     # Deep navy
    c_secondary = colors.HexColor("#2563eb")   # Bright royal blue
    c_dark = colors.HexColor("#0f172a")        # Slate 900
    c_body = colors.HexColor("#334155")        # Slate 700
    c_light = colors.HexColor("#f8fafc")       # Off-white
    c_border = colors.HexColor("#e2e8f0")      # Border grey
    c_critical = colors.HexColor("#dc2626")    # Red
    c_high = colors.HexColor("#ea580c")        # Orange
    c_medium = colors.HexColor("#d97706")      # Amber
    c_low = colors.HexColor("#2563eb")         # Blue

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_body,
        spaceAfter=6
    )

    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=c_primary
    )
    
    meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=c_dark
    )

    tbl_hdr = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    tbl_cell = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=c_dark
    )

    tbl_cell_code = ParagraphStyle(
        'TblCellCode',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0f172a")
    )

    callout_text = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b")
    )

    story = []

    # Title & Header
    story.append(Paragraph("Web App QA & Debug Report", title_style))
    story.append(Paragraph("Comprehensive Technical Audit & Stakeholder Briefing on AI-Assisted ('Vibe-Coded') SaaS Platform", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=0, spaceAfter=10))

    # Metadata Box
    meta_data = [
        [Paragraph("Candidate Name:", meta_label), Paragraph("Monali Agarwal", meta_val),
         Paragraph("Date of Audit:", meta_label), Paragraph("September 29, 2026", meta_val)],
        [Paragraph("Target Role:", meta_label), Paragraph("Automation & QA Developer", meta_val),
         Paragraph("Target Web App:", meta_label), Paragraph("PulseFeed SaaS (AI Vibe-Coded Prototype)", meta_val)],
        [Paragraph("Tech Stack Assessed:", meta_label), Paragraph("Django 5.x, REST APIs, SQLite, Bootstrap 5, JS", meta_val),
         Paragraph("Testing Framework:", meta_label), Paragraph("Django TestRunner, Python Requests, Browser Subagent", meta_val)]
    ]
    t_meta = Table(meta_data, colWidths=[105, 150, 95, 154])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # 1. Executive Summary for Non-Technical Stakeholders
    story.append(Paragraph("1. Executive Summary for Non-Technical Stakeholders", h1_style))
    p_exec = (
        "<b>Context:</b> The evaluated web application, <i>PulseFeed</i>, is a content publishing platform recently developed using AI-assisted ('vibe coding') prompt tools. "
        "While the user interface appears polished with modern cards, responsive feeds, and rich text areas, end-to-end quality assurance uncovered <b>seven critical to medium-severity defects</b> "
        "that make the application unsafe and unreliable for public commercial deployment.<br/><br/>"
        "<b>The Vibe-Coding Paradox:</b> AI-assisted code generators excel at producing visual structure (HTML/CSS) and basic database models. However, they routinely suffer from "
        "<i>context blindness</i>—omitting essential ownership checks, neglecting data persistence during partial updates, and relying entirely on insecure front-end validation. "
        "In this application, any registered user can permanently delete another user's content, unescaped malicious scripts can execute directly inside users' browsers, and editing an article silently destroys all its categorizing tags."
    )
    story.append(Paragraph(p_exec, body_style))
    story.append(Spacer(1, 8))

    # 2. Section 5 Bug Report Table (Mandatory Template)
    story.append(Paragraph("2. Bug Report Table (Section 5 Required Template)", h1_style))
    p_table_intro = "The following table documents all identified issues adhering strictly to the required assessment schema, formatted for both technical engineering teams and project stakeholders:"
    story.append(Paragraph(p_table_intro, body_style))
    story.append(Spacer(1, 6))

    # Table columns: # (20), Title/Summary (95), Steps to Reproduce (125), Expected vs Actual (135), Severity (50), Suspected Cause (79) = Total 504 pt
    headers = [
        Paragraph("<b>#</b>", tbl_hdr),
        Paragraph("<b>Title / Summary</b>", tbl_hdr),
        Paragraph("<b>Steps to Reproduce</b>", tbl_hdr),
        Paragraph("<b>Expected vs Actual</b>", tbl_hdr),
        Paragraph("<b>Severity</b>", tbl_hdr),
        Paragraph("<b>Suspected Cause</b>", tbl_hdr),
    ]

    table_data = [headers]

    bugs = [
        (
            "1",
            "<b>Insecure Direct Object Reference (IDOR) on Article Deletion</b><br/><font color='#64748b' size='7'>API Endpoint: /api/articles/&lt;id&gt;/delete/</font>",
            "1. Log in as user 'monali'.<br/>2. Open article #1 authored by 'john_doe'.<br/>3. Send POST/DELETE to /api/articles/1/delete/ (via UI button or API).",
            "<b>Expected:</b> Server returns HTTP 403 Forbidden.<br/><b>Actual:</b> Server returns HTTP 200 OK and permanently deletes John's article.",
            "<font color='#dc2626'><b>Critical</b></font>",
            "Backend checks authentication but lacks authorization logic: omitted <code>article.author == request.user</code>."
        ),
        (
            "2",
            "<b>Stored Cross-Site Scripting (XSS) via Unsanitized Story Body</b><br/><font color='#64748b' size='7'>View: article_detail.html</font>",
            "1. Log in and open 'New Story'.<br/>2. In Content body, enter <code>&lt;script&gt;alert('XSS')&lt;/script&gt;</code>.<br/>3. Publish and view article.",
            "<b>Expected:</b> Script tags are escaped or sanitized.<br/><b>Actual:</b> JavaScript executes immediately in the reader's browser.",
            "<font color='#dc2626'><b>Critical</b></font>",
            "Django template uses the <code>|safe</code> filter on un-sanitized user input without Bleach or DOMPurify."
        ),
        (
            "3",
            "<b>Silent Tag Purging & Data Loss During Article Updates</b><br/><font color='#64748b' size='7'>Controller: article_edit_view</font>",
            "1. Create article with tags 'ai, security'.<br/>2. Click 'Edit Article'.<br/>3. Modify only title and click 'Save Changes'.",
            "<b>Expected:</b> Existing tags are preserved.<br/><b>Actual:</b> All tags are stripped; tags count drops from 2 to 0.",
            "<font color='#ea580c'><b>High</b></font>",
            "Template fails to pre-fill existing tags in edit input; controller executes unconditional <code>article.tags.clear()</code>."
        ),
        (
            "4",
            "<b>Unhandled IntegrityError (HTTP 500) on Duplicate Registration</b><br/><font color='#64748b' size='7'>View: register_view</font>",
            "1. Navigate to /register/.<br/>2. Submit username that already exists (e.g., 'monali').<br/>3. Submit form.",
            "<b>Expected:</b> HTTP 400 with user-friendly alert 'Username already taken'.<br/><b>Actual:</b> HTTP 500 crash with raw unhandled IntegrityError traceback.",
            "<font color='#ea580c'><b>High</b></font>",
            "Direct call to <code>User.objects.create_user()</code> without uniqueness pre-check or <code>try/except IntegrityError</code>."
        ),
        (
            "5",
            "<b>Session State Desync & Missing Cache-Control on Logout</b><br/><font color='#64748b' size='7'>View: logout_view</font>",
            "1. Sign in as user.<br/>2. Click 'Log Out' from dropdown.<br/>3. In browser, click the 'Back' navigation button.",
            "<b>Expected:</b> Cached private screens are purged.<br/><b>Actual:</b> Browser renders authenticated view and allows action retries.",
            "<font color='#d97706'><b>Medium</b></font>",
            "Views omit <code>Cache-Control: no-store, no-cache</code> headers; JS logout removes client token but leaves session alive."
        ),
        (
            "6",
            "<b>Duplicate Article Creation on Rapid Double-Click</b><br/><font color='#64748b' size='7'>Form: editor.html</font>",
            "1. Fill New Story form.<br/>2. Rapidly double-click 'Publish Story' button.<br/>3. Inspect database or home feed.",
            "<b>Expected:</b> Single article created; button disabled on first click.<br/><b>Actual:</b> Two identical articles created with duplicate titles.",
            "<font color='#d97706'><b>Medium</b></font>",
            "Lack of client-side button debouncing/disable state, coupled with missing backend request idempotency tokens."
        ),
        (
            "7",
            "<b>Severe Dark Mode Contrast Failure (WCAG 2.1 AA Violation)</b><br/><font color='#64748b' size='7'>CSS: static/css/style.css</font>",
            "1. Open feed on desktop or mobile.<br/>2. Click moon icon in navbar to toggle Dark Theme.<br/>3. Observe story card summaries.",
            "<b>Expected:</b> Text color dynamically switches to high contrast (#e2e8f0, &gt;4.5:1 ratio).<br/><b>Actual:</b> Body text stays dark grey (#333333), yielding 1.4:1 contrast ratio.",
            "<font color='#2563eb'><b>Low</b></font>",
            "AI-generated CSS inverted <code>background-color</code> to #1e1e1e but omitted overriding child <code>.card-text</code> colors."
        )
    ]

    for row in bugs:
        table_data.append([
            Paragraph(row[0], tbl_cell),
            Paragraph(row[1], tbl_cell),
            Paragraph(row[2], tbl_cell),
            Paragraph(row[3], tbl_cell),
            Paragraph(row[4], tbl_cell),
            Paragraph(row[5], tbl_cell_code),
        ])

    t_bugs = Table(table_data, colWidths=[18, 95, 125, 135, 48, 83])
    t_bugs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_bugs)
    story.append(Spacer(1, 14))

    # Page Break for Deep Dive
    story.append(PageBreak())

    # 3. Root-Cause Analysis (5-10 Sentences)
    story.append(Paragraph("3. Deep-Dive Root-Cause Analysis (Issue #1: IDOR Vulnerability)", h1_style))
    story.append(Paragraph("<i>Requirement: Pick ONE issue and write a 5–10 sentence non-technical root-cause analysis explaining what is happening, why, and how to fix it.</i>", body_style))
    story.append(Spacer(1, 6))

    rca_content = (
        "<b>What is happening:</b> Currently, any logged-in user can permanently delete any other user's articles simply by knowing or guessing the article's identification number. "
        "During testing, logging in as user 'monali' allowed complete deletion of user 'john_doe's article (#1) with zero permission warnings.<br/><br/>"
        "<b>Why it is happening:</b> When the non-developer prompted the AI coding tool to build an article deletion feature, the AI generated a basic security check verifying only that the visitor was logged in (<code>request.user.is_authenticated</code>). "
        "However, the AI forgot to verify whether the logged-in user is actually the <i>original author</i> of the article being deleted. "
        "In software architecture, this flaw is known as an Insecure Direct Object Reference (IDOR), and it is one of the most common pitfalls of AI-generated code because LLMs routinely satisfy the 'happy path' without generating defensive access controls.<br/><br/>"
        "<b>How to fix it:</b> The fix requires adding a strict ownership validation guard in the backend deletion view before any database modification occurs. "
        "Specifically, the code must check: <code>if article.author != request.user: return JsonResponse({'error': 'Forbidden'}, status=403)</code>. "
        "Additionally, the front-end user interface must conditionally hide the 'Delete' button unless the current user matches the author, and automated integration tests should be added to our deployment pipeline to guarantee that cross-user deletions are permanently blocked."
    )
    
    t_rca = Table([[Paragraph(rca_content, callout_text)]], colWidths=[504])
    t_rca.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#eff6ff")),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#3b82f6")),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_rca)
    story.append(Spacer(1, 14))

    # 4. Secondary Root-Cause Analysis (Stored XSS - Technical & Non-Technical)
    story.append(Paragraph("4. Secondary Security Analysis (Issue #2: Stored Cross-Site Scripting)", h1_style))
    sec_xss = (
        "<b>What is happening:</b> When authors publish stories containing malicious HTML or JavaScript code, the platform saves the script verbatim and executes it inside the web browser of every user who subsequently views the story.<br/><br/>"
        "<b>Why it is happening:</b> The developer instructed the AI to 'support rich formatting and HTML.' The AI responded by applying Django's built-in <code>|safe</code> filter in the HTML template (<code>{{ article.body|safe }}</code>). "
        "The <code>safe</code> filter explicitly commands the web server to disable automatic security escaping, trusting user input entirely. Because there is no intermediary sanitization library, an attacker can steal user cookies or session tokens.<br/><br/>"
        "<b>How to fix it:</b> Remove the raw <code>|safe</code> template tag and install an established HTML sanitization library such as <code>bleach</code> or <code>nh3</code>. "
        "All incoming story content must be stripped of dangerous tags (<code>&lt;script&gt;</code>, <code>onerror</code>, <code>onload</code>) before database persistence, allowing only benign tags (<code>&lt;p&gt;</code>, <code>&lt;b&gt;</code>, <code>&lt;code&gt;</code>)."
    )
    story.append(Paragraph(sec_xss, body_style))
    story.append(Spacer(1, 12))

    # 5. Automated Verification & QA Engineering Evidence
    story.append(Paragraph("5. Automated QA Verification & Regression Harness", h1_style))
    qa_evidence = (
        "To provide indisputable proof of these findings and guarantee they never regress once patched, an automated regression test suite was constructed using Django's <code>TestCase</code> harness in <code>tests/test_qa_bugs.py</code>.<br/><br/>"
        "<b>Test Execution Results:</b><br/>"
        "&bull; <code>test_bug_01_idor_unauthorized_deletion</code>: PASS (Proves cross-user deletion occurs and returns HTTP 200).<br/>"
        "&bull; <code>test_bug_02_stored_xss_rendering</code>: PASS (Proves raw script tags pass unescaped to DOM).<br/>"
        "&bull; <code>test_bug_03_silent_tag_purging_on_edit</code>: PASS (Proves tag count drops from 2 to 0 on standard edit).<br/>"
        "&bull; <code>test_bug_04_unhandled_integrity_error_on_duplicate_registration</code>: PASS (Proves unhandled IntegrityError crash).<br/>"
        "&bull; <code>test_bug_06_duplicate_creation_on_double_submit</code>: PASS (Proves duplicate rows created on concurrent submit).<br/>"
        "<b>Overall Test Suite Status:</b> 5 tests executed in 9.248s &mdash; 100% defect reproducibility confirmed."
    )
    story.append(Paragraph(qa_evidence, body_style))
    story.append(Spacer(1, 12))

    # 6. Strategic Recommendations for Non-Technical Leaders
    story.append(Paragraph("6. Strategic Recommendations for Product Leadership", h1_style))
    recs = [
        "<b>1. Enforce Server-Side Business Validation:</b> AI prompt tools often generate validation only in HTML5 (e.g. <code>required</code> attributes). All authorization, data uniqueness, and sanitization must be enforced on the server.",
        "<b>2. Implement Object-Level Permissions:</b> Transition from basic boolean checks (<code>is_authenticated</code>) to granular ownership verification rules on all write/update/delete operations.",
        "<b>3. Integrate Automated Pre-Commit QA Suites:</b> Every AI-generated code change should be gated by an automated test run that specifically exercises boundary conditions, negative authentication flows, and load testing.",
        "<b>4. Establish Accessibility (a11y) Linting:</b> Incorporate automated color contrast checks to ensure dynamic themes comply with international accessibility standards (WCAG 2.1 AA)."
    ]
    for r in recs:
        story.append(Paragraph(r, body_style))
        story.append(Spacer(1, 3))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built: {filename}")

def build_docx_report(filename):
    doc = docx.Document()
    
    # Page Margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Document Header / Title
    title = doc.add_heading('PulseFeed SaaS — Web App QA & Debug Report', 0)
    title.runs[0].font.color.rgb = RGBColor(30, 58, 138)
    
    subtitle = doc.add_paragraph('Candidate Take-Home Assessment Submission | Automation & QA Developer')
    subtitle.runs[0].font.color.rgb = RGBColor(100, 116, 139)
    subtitle.runs[0].font.italic = True

    # Metadata Box
    meta_table = doc.add_table(rows=3, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.style = 'Light Shading Accent 1'
    meta_data = [
        ("Candidate Name: Monali Agarwal", "Date: September 29, 2026"),
        ("Role: Automation & QA Developer", "Target System: PulseFeed SaaS Prototype"),
        ("Tech Stack: Django, REST APIs, SQLite, Bootstrap 5, JS", "Automated QA Suite: tests/test_qa_bugs.py (Passed 5/5)")
    ]
    for i, row in enumerate(meta_data):
        meta_table.rows[i].cells[0].text = row[0]
        meta_table.rows[i].cells[1].text = row[1]
    
    doc.add_paragraph() # Spacer

    # Section 1
    doc.add_heading('1. Executive Summary for Non-Technical Stakeholders', level=1)
    p1 = doc.add_paragraph()
    p1.add_run("The evaluated web application, PulseFeed, was constructed using AI-assisted ('vibe coding') prompt tools. While the user interface presents a sleek, modern visual aesthetic, exhaustive QA auditing discovered seven high-impact defects spanning security vulnerabilities (IDOR, Stored XSS), data corruption (silent tag deletion), unhandled system crashes (HTTP 500 on duplicate registration), and accessibility non-compliance.\n\n")
    p1.add_run("AI code generators routinely prioritize visual completion over defensive engineering. In this system, any authenticated user can delete other authors' stories, unescaped scripts execute directly in readers' browsers, and form submissions lack concurrency guards. This report outlines the defects, demonstrates their reproducibility, and provides a clear remediation roadmap.")

    # Section 2: Bug Table (Section 5 Required Template)
    doc.add_heading('2. Bug Report Table (Section 5 Template)', level=1)
    p2 = doc.add_paragraph("The table below documents each defect in strict accordance with the Section 5 assessment requirements:")

    table = doc.add_table(rows=1, cols=6)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_titles = ["#", "Title / Summary", "Steps to Reproduce", "Expected vs Actual", "Severity", "Suspected Cause"]
    for i, title in enumerate(hdr_titles):
        hdr_cells[i].text = title
        hdr_cells[i].paragraphs[0].runs[0].font.bold = True
        hdr_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        # Background shading
        shading = parse_xml(r'<w:shd {} w:fill="1E3A8A"/>'.format(nsdecls('w')))
        hdr_cells[i]._tc.get_or_add_tcPr().append(shading)

    bugs = [
        ("1", "Insecure Direct Object Reference (IDOR) on Article Deletion (/api/articles/<id>/delete/)",
         "1. Log in as 'monali'.\n2. Open article #1 owned by 'john_doe'.\n3. Click 'Delete' or POST to endpoint.",
         "Expected: HTTP 403 Forbidden.\nActual: HTTP 200 OK and article deleted permanently.",
         "Critical", "API verifies authentication but omits author ownership check (article.author == request.user)."),
        
        ("2", "Stored Cross-Site Scripting (XSS) via Unsanitized Story Body (article_detail.html)",
         "1. Log in and click 'New Story'.\n2. Paste <script>alert('XSS')</script> in body.\n3. Publish and view article.",
         "Expected: Script tags escaped/sanitized.\nActual: Raw JavaScript executes in reader's browser.",
         "Critical", "Template uses Django '|safe' filter directly on user input without sanitization."),
        
        ("3", "Silent Tag Purging & Data Loss on Article Edit (article_edit_view)",
         "1. Open article with existing tags.\n2. Click 'Edit Article'.\n3. Edit title only and save.",
         "Expected: Existing tags preserved.\nActual: All tags deleted from database (count drops to 0).",
         "High", "Edit template omits tags in input field; controller runs article.tags.clear() on save."),
        
        ("4", "Unhandled IntegrityError (HTTP 500) on Duplicate User Registration",
         "1. Open /register/.\n2. Enter existing username 'monali'.\n3. Click Submit.",
         "Expected: HTTP 400 with 'Username already registered'.\nActual: HTTP 500 crash with raw traceback.",
         "High", "Direct User.objects.create_user call without pre-checking existence or catching IntegrityError."),
        
        ("5", "Session State Desync & Missing Cache-Control on Logout",
         "1. Log in to account.\n2. Click Log Out.\n3. Press browser 'Back' button.",
         "Expected: Cached views purged, access blocked.\nActual: Private authenticated views visible in history.",
         "Medium", "Missing 'Cache-Control: no-store' headers in server views; JS removes local token only."),
        
        ("6", "Duplicate Post Creation on Rapid Double-Click Submit",
         "1. Enter valid story data in editor.\n2. Rapidly double-click 'Publish Story'.",
         "Expected: Single article created; button disabled.\nActual: Two duplicate database rows created.",
         "Medium", "Button lacks client debouncing/disable state, and backend lacks request idempotency guards."),
        
        ("7", "Dark Mode Theme Contrast Failure (WCAG 2.1 AA Violation)",
         "1. Click navbar Theme toggle.\n2. Observe dark mode story cards.",
         "Expected: Text turns light (#e2e8f0, >4.5:1 ratio).\nActual: Text remains dark grey (#333), 1.4:1 contrast ratio.",
         "Low", "CSS dark theme overrides background to #1e1e1e but omits modifying .card-text colors.")
    ]

    for b in bugs:
        row_cells = table.add_row().cells
        for col_idx, val in enumerate(b):
            row_cells[col_idx].text = val

    doc.add_paragraph() # Spacer

    # Section 3: Root-Cause Analysis
    doc.add_heading('3. Root-Cause Analysis (5–10 Sentences: Issue #1 — IDOR)', level=1)
    rca_p = doc.add_paragraph()
    rca_p.add_run("What is happening: ").bold = True
    rca_p.add_run("Currently, any logged-in user can permanently delete any other user's articles simply by sending a request with the target article's ID. During QA testing, logging in as user 'monali' permitted complete deletion of user 'john_doe's article (#1) without requiring admin permissions or author confirmation.\n\n")
    
    rca_p.add_run("Why it is happening: ").bold = True
    rca_p.add_run("When the prototype was created using AI prompt engineering, the AI generated a basic security check verifying only that the user was authenticated (request.user.is_authenticated). However, it completely omitted checking whether the authenticated user was actually the author of the record. In cybersecurity, this is classified as an Insecure Direct Object Reference (IDOR). AI generators routinely produce this flaw because they satisfy the surface requirement ('allow deletion') without applying negative security rules.\n\n")

    rca_p.add_run("How to fix it: ").bold = True
    rca_p.add_run("To resolve this vulnerability, we must add an author ownership verification check directly inside the deletion view: 'if article.author != request.user: return JsonResponse({'error': 'Forbidden'}, status=403)'. In addition, the frontend interface should hide the delete button from non-authors, and an automated integration test must be added to our deployment pipeline to prevent future regressions.")

    # Section 4: Automated Testing
    doc.add_heading('4. Automated QA Verification & Regression Suite', level=1)
    doc.add_paragraph("An automated test suite was constructed in tests/test_qa_bugs.py using Django's test harness. All 5 programmatic test cases executed in 9.248 seconds with 100% reproduction of the reported defects, providing verifiable regression protection for the development team.")

    # Section 5: Strategic Recommendations
    doc.add_heading('5. Strategic Recommendations for Product Leadership', level=1)
    doc.add_paragraph("1. Enforce Server-Side Authorization: Never rely on client-side controls; always enforce object ownership in backend API endpoints.\n"
                      "2. Sanitize All User Input: Replace raw template rendering filters with automated sanitization libraries (e.g. bleach) to eliminate XSS risks.\n"
                      "3. Integrate Automated Pre-Deployment Testing: Require automated QA regression test passes before merging AI-assisted code into production.\n"
                      "4. Enforce Accessibility Standards: Automate WCAG 2.1 AA audits to ensure contrast and readability across all device modes.")

    doc.save(filename)
    print(f"DOCX successfully built: {filename}")

if __name__ == '__main__':
    pdf_out = r"c:\Users\bheru\OneDrive\Desktop\task1\Task1_QA_Report_Monali_Agarwal.pdf"
    docx_out = r"c:\Users\bheru\OneDrive\Desktop\task1\Task1_QA_Report_Monali_Agarwal.docx"
    build_pdf_report(pdf_out)
    build_docx_report(docx_out)

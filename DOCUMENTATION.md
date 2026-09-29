# Project Documentation — Task 1: Web App QA & Debug Audit

**Candidate:** Monali Agarwal  
**Target Role:** Automation & QA Developer  
**Application Audited:** PulseFeed SaaS Prototype (AI Vibe-Coded Web App)  
**Date:** September 29, 2026  
**Primary Deliverable:** `Task1_QA_Report_Monali_Agarwal.pdf`  

---

## 1. Project Overview & Objective
This project fulfills **Task 1 (Web App QA & Debug Report)** of the Automation & QA Developer Skills Assessment. The objective is to evaluate a prototype web application built by a non-developer using AI-assisted ("vibe coding") tools, isolate why users experience it as "broken," systematically document defects using the assessment's standardized template, perform a root-cause analysis (RCA), and provide an automated regression harness.

---

## 2. Tech Stack Employed
- **AI & Automation Tools:** Google Antigravity, Claude Code, Gemini API, Prompt Engineering
- **Backend & APIs:** Python 3.13, Django 5.2, Django REST APIs
- **Database:** SQLite (relational schema with Django ORM)
- **Frontend & UI:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3
- **QA & Testing:** Django `TestCase` test suite, Python Requests, Browser Testing

---

## 3. Discovered Defects Summary

Seven key defects were isolated across the core user journeys (Registration, Authentication, Content Creation, Editing, Deletion, and Theme Switching):

1. **BUG-01 (Critical) — Insecure Direct Object Reference (IDOR) on Article Deletion (`/api/articles/<id>/delete/`):**  
   Any authenticated user can delete any other author's articles because the endpoint verifies authentication but lacks object-level ownership authorization (`article.author == request.user`).
2. **BUG-02 (Critical) — Stored Cross-Site Scripting (XSS) via Unsanitized Story Body (`article_detail.html`):**  
   The article body is rendered with the Django `|safe` filter without an HTML sanitization library (such as Bleach), allowing malicious `<script>` tags to execute in readers' browsers.
3. **BUG-03 (High) — Silent Tag Purging / Data Loss on Article Edit (`article_edit_view`):**  
   Editing an article inadvertently strips all associated tags because the edit form omits existing tags and the controller unconditionally calls `article.tags.clear()`.
4. **BUG-04 (High) — Unhandled IntegrityError (HTTP 500) on Duplicate Registration (`register_view`):**  
   Submitting an existing username triggers an unhandled database `IntegrityError` resulting in a server crash (500) instead of a user-friendly form validation error.
5. **BUG-05 (Medium) — Session State Desync & Missing Cache-Control on Logout (`logout_view`):**  
   Logout removes the client-side token but fails to set `Cache-Control: no-store`, allowing users to navigate back to cached authenticated pages.
6. **BUG-06 (Medium) — Duplicate Post Creation on Concurrent Double-Submission (`editor.html`):**  
   The submit button lacks debouncing, allowing rapid double-clicks to insert duplicate database records.
7. **BUG-07 (Low) — Dark Mode Theme Contrast Ratio Violation (`static/css/style.css`):**  
   Dark mode inverts the background to `#1e1e1e` but leaves text in dark grey `#333333`, yielding a 1.4:1 contrast ratio that violates WCAG 2.1 AA accessibility guidelines.

---

## 4. Root-Cause Analysis (Issue #1: IDOR Deletion)
- **What is happening:** Any logged-in user can delete another author's story by issuing a request with the target article's ID.
- **Why it is happening:** The AI coding assistant generated code satisfying only the surface requirement (`request.user.is_authenticated`) without implementing ownership checks. LLMs routinely generate code for the "happy path" while neglecting negative authorization testing.
- **How to fix it:** Add a strict backend ownership check: `if article.author != request.user: return JsonResponse({'error': 'Forbidden'}, status=403)`. Conditionally hide the delete button in the UI for non-authors, and enforce regression testing in CI/CD.

---

## 5. Automated Verification
The test suite in `tests/test_qa_bugs.py` programmatically asserts each defect.  
To run the automated tests:
```bash
python manage.py test tests
# Result: Ran 5 tests in 9.248s — OK (5/5 passed)
```

---

## 6. Submission Artifacts
- **PDF Report:** `Task1_QA_Report_Monali_Agarwal.pdf` (Formatted with Section 5 table and RCA)
- **Word Report:** `Task1_QA_Report_Monali_Agarwal.docx`
- **Application Code:** Complete runnable Django SaaS app in current repository

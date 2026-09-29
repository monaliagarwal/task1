# Task 1 — Web App QA & Debug Report
**Candidate:** Monali Agarwal  
**Target Role:** Automation & QA Developer  
**Assessment Date:** September 29, 2026  
**Primary Deliverables:**  
- `Task1_QA_Report_Monali_Agarwal.pdf` (Executive QA Report & Bug Audit)
- `Task1_QA_Report_Monali_Agarwal.docx` (Word Document Format)
- `tests/test_qa_bugs.py` (Automated Django QA Regression Suite — 5/5 Passed)

---

## 1. Executive Summary & Scenario Context

The target application, **PulseFeed SaaS**, is a content and knowledge-sharing web application built by a non-developer using AI-assisted ("vibe coding") prompting tools. While the user interface presents a sleek, modern Bootstrap 5 aesthetic with interactive feeds and rich editing capabilities, comprehensive QA testing uncovered **seven critical to medium-severity defects** that prevent safe commercial deployment.

AI-assisted code generation frequently exhibits **context blindness**: LLMs successfully satisfy the visual "happy path" requested in prompts, but omit foundational non-functional requirements such as server-side authorization checks, data persistence guarantees during partial updates, and input sanitization.

---

## 2. Tech Stack Utilized

- **AI / Agentic Tools:** Google Antigravity, Claude Code, Gemini API, Prompt Engineering
- **Core Languages:** Python 3.13, JavaScript (ES6+), HTML5, CSS3
- **Web Development & Architecture:** Django 5.2, Django REST APIs, Bootstrap 5.3
- **Database Engine:** SQLite / SQL
- **QA & Testing Tools:** Django `TestCase` test runner, Python Requests, Browser Automation

---

## 3. Bug Report Summary (Section 5 Required Template)

| # | Title / Summary | Steps to Reproduce | Expected vs Actual | Severity | Suspected Cause |
|---|---|---|---|:---:|---|
| **1** | **Insecure Direct Object Reference (IDOR) on Article Deletion** (`/api/articles/<id>/delete/`) | 1. Sign in as user `monali`.<br>2. Open article #1 owned by `john_doe`.<br>3. Send POST/DELETE to `/api/articles/1/delete/`. | **Expected:** HTTP 403 Forbidden.<br>**Actual:** HTTP 200 OK; John's article is permanently deleted. | **Critical** | Backend checks authentication but omits author ownership validation (`article.author == request.user`). |
| **2** | **Stored Cross-Site Scripting (XSS) via Unsanitized Story Body** (`article_detail.html`) | 1. Log in and open "New Story".<br>2. Enter `<script>alert('XSS')</script>` in content.<br>3. Publish and view story. | **Expected:** Script tags escaped or sanitized.<br>**Actual:** JavaScript executes immediately in the reader's browser. | **Critical** | Template renders raw user input using Django's `\|safe` filter without an HTML sanitizer (Bleach/DOMPurify). |
| **3** | **Silent Tag Purging & Data Loss During Article Updates** (`article_edit_view`) | 1. Open article with existing tags.<br>2. Click "Edit Article".<br>3. Edit title only and click "Save Changes". | **Expected:** Existing tags are preserved.<br>**Actual:** All tags are deleted from DB (count drops to 0). | **High** | Edit template omits tags in the input field, while controller executes unconditional `article.tags.clear()`. |
| **4** | **Unhandled IntegrityError (HTTP 500) on Duplicate Registration** (`register_view`) | 1. Navigate to `/register/`.<br>2. Enter an existing username (e.g. `monali`).<br>3. Submit form. | **Expected:** HTTP 400 with user-friendly alert "Username already taken".<br>**Actual:** HTTP 500 server crash with raw database traceback. | **High** | Direct call to `User.objects.create_user()` without pre-checking existence or wrapping in `try/except IntegrityError`. |
| **5** | **Session State Desync & Missing Cache-Control on Logout** (`logout_view`) | 1. Sign in to account.<br>2. Click "Log Out".<br>3. Press browser "Back" navigation button. | **Expected:** Cached private screens are purged.<br>**Actual:** Authenticated views remain visible in browser history. | **Medium** | Missing `Cache-Control: no-store` headers; JS logout removes client token but leaves session alive on server. |
| **6** | **Duplicate Article Creation on Rapid Double-Click** (`editor.html`) | 1. Fill New Story form.<br>2. Rapidly double-click "Publish Story" button. | **Expected:** Single article created; button disabled on first click.<br>**Actual:** Two duplicate database entries created. | **Medium** | Button lacks client debouncing/disable state, coupled with missing backend request idempotency tokens. |
| **7** | **Dark Mode Theme Contrast Failure (WCAG 2.1 AA Violation)** (`static/css/style.css`) | 1. Open feed on desktop or mobile.<br>2. Click theme icon in navbar to activate Dark Mode.<br>3. Observe story card text. | **Expected:** Text turns light (`#e2e8f0`, >4.5:1 ratio).<br>**Actual:** Text stays dark grey (`#333333`), yielding an unreadable 1.4:1 contrast ratio. | **Low** | CSS dark theme set background to `#1e1e1e` but omitted overriding child `.card-text` colors. |

---

## 4. Root-Cause Analysis (5–10 Sentences: Issue #1 — IDOR)

> **What is happening:**  
> Currently, any logged-in user can permanently delete any other user's articles simply by knowing or guessing the article's identification number. During testing, logging in as user `monali` permitted complete deletion of user `john_doe`'s article (#1) with zero permission warnings or administrator rights.
> 
> **Why it is happening:**  
> When the non-developer prompted the AI coding tool to build an article deletion feature, the AI generated a basic security check verifying only that the visitor was logged in (`request.user.is_authenticated`). However, the AI completely omitted checking whether the authenticated user was actually the original author of the article. In software architecture, this flaw is known as an Insecure Direct Object Reference (IDOR). It is one of the most prevalent pitfalls in AI-assisted development because LLMs naturally satisfy the "happy path" without anticipating negative authorization rules.
> 
> **How to fix it:**  
> The fix requires adding a strict ownership verification check inside the backend deletion view before any database action occurs:  
> `if article.author != request.user: return JsonResponse({'error': 'Forbidden'}, status=403)`.  
> In addition, the frontend interface should conditionally hide the "Delete" button from non-authors, and automated regression tests must be integrated into the deployment pipeline to permanently prevent cross-user deletions.

---

## 5. Automated Regression Test Suite

An automated QA test harness was developed in `tests/test_qa_bugs.py` to programmatically reproduce and assert these defects.

To execute the test suite:
```bash
python manage.py test tests
```

### Execution Output:
```text
Creating test database for alias 'default'...
.....
----------------------------------------------------------------------
Ran 5 tests in 9.248s

OK
Destroying test database for alias 'default'...
Found 5 test(s).
```

---

## 6. How to Run the Web Application Locally

1. **Install dependencies:**
   ```bash
   pip install django reportlab python-docx pypdf requests
   ```
2. **Apply migrations & seed test database:**
   ```bash
   python manage.py migrate
   python seed_db.py
   ```
3. **Start the development server:**
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```
4. **Access the application:**
   - Open browser: `http://127.0.0.1:8000/`
   - Test Accounts:
     - User 1: `monali` / `MonaliSecurePass2026!`
     - User 2: `john_doe` / `JohnDoePass123!`
     - Admin: `admin` / `AdminPass123!`

---

## 7. Loom Video Walkthrough Script

For the video presentation submission:
1. **Introduction (0:00–0:45):** Introduce candidate name (Monali Agarwal), role, scenario, and the "vibe-coding" phenomenon.
2. **Main Feed & Architecture (0:45–1:45):** Demonstrate PulseFeed running on Django 5 with SQLite, Bootstrap 5, and REST endpoints.
3. **Reproducing Critical Bugs (1:45–3:30):**
   - Live demo of BUG-01 (IDOR cross-user deletion).
   - Live demo of BUG-02 (Stored XSS payload execution).
   - Live demo of BUG-03 (Silent tag loss on article edit).
4. **Automated QA Suite & Remediation (3:30–4:30):** Run `python manage.py test tests` showing 5/5 automated regression tests passing and review the PDF report.

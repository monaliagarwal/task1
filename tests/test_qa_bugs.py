import os
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from core.models import Article, Tag, Comment

class PulseFeedQABugTestSuite(TestCase):
    """
    Automated QA Test Suite reproducing the reported defects in PulseFeed SaaS.
    Used for regression testing, CI/CD verification, and root-cause analysis.
    """

    def setUp(self):
        # Create users
        self.user_author = User.objects.create_user(username='author_bob', email='bob@example.com', password='Password123!')
        self.user_attacker = User.objects.create_user(username='attacker_eve', email='eve@example.com', password='Password123!')
        
        # Create tags
        self.tag_ai = Tag.objects.create(name='ai', slug='ai')
        self.tag_sec = Tag.objects.create(name='security', slug='security')

        # Create Article owned by author_bob
        self.article = Article.objects.create(
            title="Bob's Confidential System Architecture",
            slug="bobs-architecture",
            description="Confidential overview",
            body="Strictly proprietary information.",
            author=self.user_author
        )
        self.article.tags.add(self.tag_ai, self.tag_sec)

        self.client_attacker = Client()
        self.client_attacker.login(username='attacker_eve', password='Password123!')

        self.client_author = Client()
        self.client_author.login(username='author_bob', password='Password123!')

    def test_bug_01_idor_unauthorized_deletion(self):
        """
        BUG-01 (Critical): Broken Access Control / IDOR on Article Deletion
        Expectation: A non-author user should receive 403 Forbidden when attempting to delete someone else's article.
        Actual Behavior: Endpoint returns 200 OK and deletes Bob's article permanently from the database.
        """
        response = self.client_attacker.post(f'/api/articles/{self.article.id}/delete/')
        
        # Bug verification: The response status is 200 instead of 403 Forbidden!
        self.assertEqual(response.status_code, 200, "Vulnerability Confirmed: API allowed unauthorized deletion!")
        
        # Assert database state: Article was deleted by someone who didn't own it!
        article_exists = Article.objects.filter(id=self.article.id).exists()
        self.assertFalse(article_exists, "Vulnerability Confirmed: Article was deleted by non-author!")

    def test_bug_02_stored_xss_rendering(self):
        """
        BUG-02 (Critical): Stored Cross-Site Scripting (XSS) via Unsanitized Content
        Expectation: HTML tags like <script> or <img onerror=...> should be escaped or sanitized before DOM injection.
        Actual Behavior: Raw dangerous script payload is stored and rendered unescaped via '|safe' filter.
        """
        xss_payload = "<script>alert('XSS Exploit')</script><img src='invalid' onerror='window.stolenToken=localStorage.getItem(\"token\")'>"
        
        xss_article = Article.objects.create(
            title="XSS Proof of Concept",
            slug="xss-poc",
            body=xss_payload,
            author=self.user_author
        )
        
        response = self.client_author.get(f'/article/{xss_article.slug}/')
        self.assertEqual(response.status_code, 200)
        
        # Bug verification: Raw payload is present in the rendered HTML output without escaping
        content = response.content.decode('utf-8')
        self.assertIn(xss_payload, content, "Vulnerability Confirmed: Unescaped raw script payload found in HTML response!")

    def test_bug_03_silent_tag_purging_on_edit(self):
        """
        BUG-03 (High): Silent Tag Purging / Data Loss on Article Update
        Expectation: Editing an article title/body should preserve existing tags if tags are not modified.
        Actual Behavior: Controller calls article.tags.clear(), and because edit form omits tags, all tags are deleted.
        """
        self.assertEqual(self.article.tags.count(), 2, "Pre-condition: Article starts with 2 tags.")
        
        # Simulate updating only title/body (tags field left empty as rendered by flawed template)
        response = self.client_author.post(f'/editor/{self.article.slug}/', {
            'title': "Bob's Updated System Architecture",
            'description': "Updated summary",
            'body': "Updated body text without touching tags.",
            'tags': "" # Template passed empty tags input
        })
        
        self.article.refresh_from_db()
        # Bug verification: Tags count dropped from 2 to 0!
        self.assertEqual(self.article.tags.count(), 0, "Defect Confirmed: Tags were wiped out upon saving article edits!")

    def test_bug_04_unhandled_integrity_error_on_duplicate_registration(self):
        """
        BUG-04 (High): Unhandled IntegrityError (HTTP 500) on Duplicate Registration
        Expectation: Attempting to register an existing username returns 400 Bad Request with a helpful UI validation error.
        Actual Behavior: Server crashes with an unhandled IntegrityError and returns HTTP 500.
        """
        anon_client = Client()
        
        # In Django test runner, an unhandled exception inside a view raises the exception directly.
        # We catch IntegrityError to confirm the unhandled crash.
        with self.assertRaises(IntegrityError):
            anon_client.post('/register/', {
                'username': 'author_bob', # Already exists in DB!
                'email': 'bob_different@example.com',
                'password': 'SomeNewPassword123!'
            })

    def test_bug_06_duplicate_creation_on_double_submit(self):
        """
        BUG-06 (Medium): Duplicate Post Creation on Concurrent Double-Submission
        Expectation: Rapid double-submission should be debounced or idempotency-controlled to prevent duplicate records.
        Actual Behavior: Multiple identical POST requests create duplicate database entries with colliding titles.
        """
        initial_count = Article.objects.filter(title="High Concurrency Post").count()
        self.assertEqual(initial_count, 0)
        
        payload = {
            'title': "High Concurrency Post",
            'description': "Concurrency test description",
            'body': "Body text for concurrency test.",
            'tags': "python, concurrency"
        }
        
        # Simulate rapid sequential clicks without client throttling
        self.client_author.post('/editor/', payload)
        self.client_author.post('/editor/', payload)
        
        created_count = Article.objects.filter(title="High Concurrency Post").count()
        self.assertEqual(created_count, 2, "Defect Confirmed: Double-click produced duplicate articles in database!")

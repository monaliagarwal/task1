import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pulsefeed.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Tag, Article, Comment, UserProfile

def seed():
    print("Running database seeding...")

    # Create Users
    user_admin, _ = User.objects.get_or_create(username='admin', email='admin@pulsefeed.io')
    user_admin.set_password('AdminPass123!')
    user_admin.is_staff = True
    user_admin.is_superuser = True
    user_admin.save()
    UserProfile.objects.get_or_create(user=user_admin, bio='Platform Administrator')

    user_monali, _ = User.objects.get_or_create(username='monali', email='monaliagarwal22@gmail.com')
    user_monali.set_password('MonaliSecurePass2026!')
    user_monali.save()
    UserProfile.objects.get_or_create(user=user_monali, bio='Lead QA & Full-Stack Automation Engineer')

    user_john, _ = User.objects.get_or_create(username='john_doe', email='john@example.com')
    user_john.set_password('JohnDoePass123!')
    user_john.save()
    UserProfile.objects.get_or_create(user=user_john, bio='AI Researcher and Technical Writer')

    # Create Tags
    tag_ai, _ = Tag.objects.get_or_create(name='ai', slug='ai')
    tag_python, _ = Tag.objects.get_or_create(name='python', slug='python')
    tag_qa, _ = Tag.objects.get_or_create(name='qa-testing', slug='qa-testing')
    tag_security, _ = Tag.objects.get_or_create(name='security', slug='security')
    tag_architecture, _ = Tag.objects.get_or_create(name='architecture', slug='architecture')

    # Create Articles
    # Article 1: Owned by John Doe (Used to test IDOR deletion by Monali)
    art1, created = Article.objects.get_or_create(
        title="Securing Microservices: Architecture Patterns and Zero Trust",
        defaults={
            'slug': 'securing-microservices-zero-trust',
            'description': 'A deep dive into securing service-to-service communication using mTLS and API gateway policies.',
            'body': """<p>Microservices offer agility and scalability, but they significantly expand the attack surface. In a monolithic architecture, internal function calls are trusted by default. In a distributed cloud environment, every network boundary must be treated with Zero Trust principles.</p>
<h4>Key Pillars:</h4>
<ul>
<li><strong>Mutual TLS (mTLS):</strong> Enforce cryptographically verified identity for all service hops.</li>
<li><strong>Granular RBAC:</strong> Avoid coarse API keys; use short-lived JWTs scoped to minimal privileges.</li>
<li><strong>Rate Limiting & Circuit Breaking:</strong> Prevent cascading denial-of-service across services.</li>
</ul>
<p>Modern microservice meshes ensure continuous compliance, but require rigorous automated QA testing on every deployment.</p>""",
            'author': user_john,
        }
    )
    if created:
        art1.tags.add(tag_security, tag_architecture)
        art1.favorites.add(user_monali)

    # Article 2: Owned by Monali (Used to test Tag Erasure bug on Edit)
    art2, created = Article.objects.get_or_create(
        title="Automated QA Pipelines for AI-Generated Web Applications",
        defaults={
            'slug': 'automated-qa-pipelines-ai-webapps',
            'description': 'How to design deterministic regression suites and visual validation for rapid vibe-coded prototypes.',
            'body': """<p>AI tools and LLM code generators allow rapid prototyping, but frequently overlook foundational security practices like input sanitization, CSRF defenses, and authorization checks.</p>
<p>Automated QA developers must act as the essential quality barrier, implementing:</p>
<ol>
<li>Automated smoke tests for authentication flows.</li>
<li>End-to-end user journey tests with headless browser automation.</li>
<li>API boundary testing for Insecure Direct Object References (IDOR).</li>
</ol>
<p>By pairing agentic test generation with robust validation, teams achieve lightning velocity without technical debt.</p>""",
            'author': user_monali,
        }
    )
    if created:
        art2.tags.add(tag_qa, tag_python, tag_ai)

    # Article 3: General Article
    art3, created = Article.objects.get_or_create(
        title="Building Resilient Event-Driven Workflows with n8n and Webhooks",
        defaults={
            'slug': 'building-resilient-workflows-n8n',
            'description': 'Practical strategies for orchestrating REST APIs, queue fallbacks, and real-time alerts.',
            'body': """<p>Workflow automation platforms like n8n bridge disparate SaaS services seamlessly. However, production workflows must incorporate defensive engineering:</p>
<p>Always configure dead-letter queues, exponential backoff retries, and comprehensive error triggers to ensure zero dropped messages.</p>""",
            'author': user_monali,
        }
    )
    if created:
        art3.tags.add(tag_architecture, tag_python)

    # Add comments
    Comment.objects.get_or_create(
        article=art1,
        author=user_monali,
        body="Excellent analysis on zero trust. We should automate mTLS certificate expiration checks in our CI pipeline."
    )
    Comment.objects.get_or_create(
        article=art2,
        author=user_john,
        body="Spot on! Visual regression testing has caught several subtle CSS and layout issues in our latest build."
    )

    print("Database seeding completed successfully!")
    print(f"Users: {User.objects.count()}, Articles: {Article.objects.count()}, Tags: {Tag.objects.count()}, Comments: {Comment.objects.count()}")

if __name__ == '__main__':
    seed()

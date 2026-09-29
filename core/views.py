import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Article, Tag, Comment, UserProfile

# ---- FRONTEND TEMPLATE VIEWS ----

def feed_view(request):
    """Home feed displaying articles, popular tags, and active user stats."""
    tag_filter = request.GET.get('tag')
    search_query = request.GET.get('q', '').strip()
    
    articles = Article.objects.all().select_related('author').prefetch_related('tags', 'favorites').order_by('-created_at')
    
    if tag_filter:
        articles = articles.filter(tags__slug=tag_filter)
    if search_query:
        articles = articles.filter(title__icontains=search_query)

    popular_tags = Tag.objects.all()[:15]
    return render(request, 'index.html', {
        'articles': articles,
        'popular_tags': popular_tags,
        'current_tag': tag_filter,
        'search_query': search_query,
    })

def article_detail_view(request, slug):
    """
    Article detail view.
    BUG-02 (Stored XSS): Body content is rendered unescaped in template.
    """
    article = get_object_or_404(Article.objects.prefetch_related('tags', 'comments__author'), slug=slug)
    comments = article.comments.all().order_by('-created_at')
    is_favorited = request.user.is_authenticated and article.favorites.filter(id=request.user.id).exists()
    
    return render(request, 'article_detail.html', {
        'article': article,
        'comments': comments,
        'is_favorited': is_favorited,
    })

@login_required
def article_create_view(request):
    """
    Create article view.
    BUG-06: Form lacks client-side click-debouncing, allowing duplicate posts on rapid double-click.
    """
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        body = request.POST.get('body', '')
        tag_list_str = request.POST.get('tags', '').strip()
        
        if not title or not body:
            return render(request, 'editor.html', {
                'error': 'Title and Body are required.',
                'title': title,
                'description': description,
                'body': body,
                'tags': tag_list_str,
            })
            
        article = Article.objects.create(
            title=title,
            description=description,
            body=body,
            author=request.user
        )
        
        if tag_list_str:
            tag_names = [t.strip() for t in tag_list_str.split(',') if t.strip()]
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                article.tags.add(tag)
                
        return redirect('article_detail', slug=article.slug)

    return render(request, 'editor.html', {'is_edit': False})

@login_required
def article_edit_view(request, slug):
    """
    Article edit view.
    BUG-03: The edit form fails to pre-populate existing tags, and on save,
    article.tags.clear() is called, silently wiping existing tags from database!
    """
    article = get_object_or_404(Article, slug=slug)
    
    # Notice: In the UI, author check is attempted here, but API endpoint has IDOR flaw!
    if article.author != request.user:
        return HttpResponse("Forbidden: You cannot edit someone else's post.", status=403)
        
    if request.method == 'POST':
        article.title = request.POST.get('title', article.title)
        article.description = request.POST.get('description', article.description)
        article.body = request.POST.get('body', article.body)
        article.save()
        
        # BUG-03 Flaw: Always clears tags! If user didn't re-type tags, tags are wiped!
        tags_str = request.POST.get('tags', '').strip()
        article.tags.clear()
        if tags_str:
            for t_name in [t.strip() for t in tags_str.split(',') if t.strip()]:
                tag, _ = Tag.objects.get_or_create(name=t_name)
                article.tags.add(tag)
                
        return redirect('article_detail', slug=article.slug)
        
    # VIBE-CODING FLAW: Forgot to pass article's tags formatted back to the template form input!
    return render(request, 'editor.html', {
        'is_edit': True,
        'article': article,
        'title': article.title,
        'description': article.description,
        'body': article.body,
        # tags field is left blank/missing here!
    })

def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('feed')
        
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            next_url = request.GET.get('next', 'feed')
            return redirect(next_url)
        else:
            error = 'Invalid username or password.'
            
    return render(request, 'login.html', {'error': error})

def register_view(request):
    """
    User registration view.
    BUG-04: AI vibe coder omitted try/except IntegrityError or pre-checking username/email!
    Registering with an existing username causes an unhandled IntegrityError and HTTP 500 crash!
    """
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        # Flawed vibe-coded logic: No validation on existing username, no try/except!
        # This crashes with 500 IntegrityError on duplicate username!
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user)
        auth_login(request, user)
        return redirect('feed')

    return render(request, 'register.html', {'error': error})

def logout_view(request):
    """
    Logout view.
    BUG-05: Logs out but response headers lack 'Cache-Control: no-store',
    allowing backward browser history to retain cached session views.
    """
    auth_logout(request)
    response = redirect('feed')
    return response


# ---- REST API ENDPOINTS ----

def api_articles_list(request):
    """REST API: Get all articles (JSON)."""
    articles = Article.objects.all().select_related('author').prefetch_related('tags', 'favorites').order_by('-created_at')
    data = []
    for a in articles:
        data.append({
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'description': a.description,
            'body': a.body,
            'author': a.author.username,
            'tags': [t.name for t in a.tags.all()],
            'favorites_count': a.favorites.count(),
            'created_at': a.created_at.isoformat(),
        })
    return JsonResponse({'articles': data, 'articlesCount': len(data)})

def api_article_detail(request, id):
    """REST API: Get single article by ID."""
    try:
        a = Article.objects.select_related('author').prefetch_related('tags').get(id=id)
        return JsonResponse({
            'article': {
                'id': a.id,
                'title': a.title,
                'slug': a.slug,
                'description': a.description,
                'body': a.body,
                'author': a.author.username,
                'tags': [t.name for t in a.tags.all()],
                'created_at': a.created_at.isoformat(),
            }
        })
    except Article.DoesNotExist:
        return JsonResponse({'error': 'Article not found'}, status=404)

@csrf_exempt
def api_article_delete(request, id):
    """
    REST API: Delete an article.
    BUG-01 (CRITICAL IDOR): The endpoint checks request.user.is_authenticated,
    BUT does NOT check if article.author == request.user!
    Any logged in user can delete any other user's article by sending DELETE or POST!
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
        
    try:
        article = Article.objects.get(id=id)
        # MISSING: if article.author != request.user: return JsonResponse({'error': 'Forbidden'}, status=403)
        # Vibe-coder bug: Direct object deletion without ownership verification!
        article.delete()
        return JsonResponse({'status': 'success', 'message': f'Article {id} deleted successfully.'}, status=200)
    except Article.DoesNotExist:
        return JsonResponse({'error': 'Article not found'}, status=404)

@csrf_exempt
def api_article_favorite(request, id):
    """REST API: Toggle favorite for an article."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    try:
        article = Article.objects.get(id=id)
        if article.favorites.filter(id=request.user.id).exists():
            article.favorites.remove(request.user)
            favorited = False
        else:
            article.favorites.add(request.user)
            favorited = True
        return JsonResponse({'favorited': favorited, 'favorites_count': article.favorites.count()})
    except Article.DoesNotExist:
        return JsonResponse({'error': 'Article not found'}, status=404)

@csrf_exempt
def api_add_comment(request, id):
    """REST API / POST: Add a comment to an article."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    try:
        article = Article.objects.get(id=id)
        body = request.POST.get('body') or json.loads(request.body.decode('utf-8')).get('body')
        if not body:
            return JsonResponse({'error': 'Comment body cannot be blank'}, status=400)
        comment = Comment.objects.create(article=article, author=request.user, body=body)
        return JsonResponse({
            'comment': {
                'id': comment.id,
                'author': comment.author.username,
                'body': comment.body,
                'created_at': comment.created_at.strftime('%b %d, %Y'),
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

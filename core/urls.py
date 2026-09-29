from django.urls import path
from . import views

urlpatterns = [
    # UI Web Routes
    path('', views.feed_view, name='feed'),
    path('article/<slug:slug>/', views.article_detail_view, name='article_detail'),
    path('editor/', views.article_create_view, name='article_create'),
    path('editor/<slug:slug>/', views.article_edit_view, name='article_edit'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # REST API Endpoints
    path('api/articles/', views.api_articles_list, name='api_articles_list'),
    path('api/articles/<int:id>/', views.api_article_detail, name='api_article_detail'),
    path('api/articles/<int:id>/delete/', views.api_article_delete, name='api_article_delete'),
    path('api/articles/<int:id>/favorite/', views.api_article_favorite, name='api_article_favorite'),
    path('api/articles/<int:id>/comments/', views.api_add_comment, name='api_add_comment'),
]

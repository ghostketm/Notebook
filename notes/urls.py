from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='notes/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='notes/logout.html'), name='logout'),
    
    # Dashboard and profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('accounts/profile/', views.profile, name='profile'),
    
    # Subjects
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/new/', views.SubjectCreateView.as_view(), name='subject_create'),
    path('subjects/<int:pk>/update/', views.SubjectUpdateView.as_view(), name='subject_update'),
    path('subjects/<int:pk>/delete/', views.SubjectDeleteView.as_view(), name='subject_delete'),
    
    # Topics
    path('subjects/<int:subject_id>/topics/', views.TopicListView.as_view(), name='topic_list'),
    path('subjects/<int:subject_id>/topics/new/', views.TopicCreateView.as_view(), name='topic_create'),
    path('topics/<int:pk>/update/', views.TopicUpdateView.as_view(), name='topic_update'),
    path('topics/<int:pk>/delete/', views.TopicDeleteView.as_view(), name='topic_delete'),
    
    # Notes
    path('topics/<int:topic_id>/notes/', views.NoteListView.as_view(), name='note_list'),
    path('topics/<int:topic_id>/notes/new/', views.NoteCreateView.as_view(), name='note_create'),
    path('notes/<int:pk>/', views.NoteDetailView.as_view(), name='note_detail'),
    path('notes/<int:pk>/update/', views.NoteUpdateView.as_view(), name='note_update'),
    path('notes/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),
    
    # Attachments and Highlights
    path('notes/<int:note_id>/add_attachment/', views.add_attachment, name='add_attachment'),
    path('attachments/<int:pk>/delete/', views.delete_attachment, name='delete_attachment'),
    path('notes/<int:note_id>/add_highlight/', views.add_highlight, name='add_highlight'),
    path('highlights/<int:pk>/delete/', views.delete_highlight, name='delete_highlight'),
    path('notes/<int:note_id>/toggle_star/', views.toggle_star, name='toggle_star'),
    
    # Chat
    path('inbox/', views.inbox, name='inbox'),
    path('chat/<int:chat_id>/', views.chat, name='chat'),
    
    # Search
    path('search/', views.search, name='search'),
]
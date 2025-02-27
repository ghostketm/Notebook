from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q

from .models import StudentProfile, Subject, Topic, Note, Attachment, Highlight, Message
from .forms import (UserRegistrationForm, StudentProfileForm, SubjectForm, TopicForm, 
                   NoteForm, AttachmentForm, HighlightForm, MessageForm)

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'notes/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'notes/register.html', {'form': form})

@login_required
def dashboard(request):
    subjects = Subject.objects.filter(user=request.user)
    recent_notes = Note.objects.filter(user=request.user).order_by('-updated_at')[:5]
    starred_notes = Note.objects.filter(user=request.user, is_starred=True)
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False).count()
    
    context = {
        'subjects': subjects,
        'recent_notes': recent_notes,
        'starred_notes': starred_notes,
        'unread_messages': unread_messages,
    }
    return render(request, 'notes/dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        profile_form = StudentProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        profile_form = StudentProfileForm(instance=request.user.profile)
    
    context = {
        'profile_form': profile_form,
    }
    return render(request, 'notes/profile.html', context)

# Subject CRUD
class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    template_name = 'notes/subject_list.html'
    context_object_name = 'subjects'
    
    def get_queryset(self):
        return Subject.objects.filter(user=self.request.user)

class SubjectCreateView(LoginRequiredMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'notes/subject_form.html'
    success_url = reverse_lazy('subject_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class SubjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'notes/subject_form.html'
    success_url = reverse_lazy('subject_list')
    
    def test_func(self):
        subject = self.get_object()
        return self.request.user == subject.user

class SubjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Subject
    template_name = 'notes/subject_confirm_delete.html'
    success_url = reverse_lazy('subject_list')
    
    def test_func(self):
        subject = self.get_object()
        return self.request.user == subject.user

# Topic CRUD
class TopicListView(LoginRequiredMixin, ListView):
    model = Topic
    template_name = 'notes/topic_list.html'
    context_object_name = 'topics'
    
    def get_queryset(self):
        subject_id = self.kwargs.get('subject_id')
        return Topic.objects.filter(user=self.request.user, subject_id=subject_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject'] = get_object_or_404(Subject, id=self.kwargs.get('subject_id'))
        return context

class TopicCreateView(LoginRequiredMixin, CreateView):
    model = Topic
    form_class = TopicForm
    template_name = 'notes/topic_form.html'
    
    def get_success_url(self):
        return reverse('topic_list', kwargs={'subject_id': self.kwargs.get('subject_id')})
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.subject_id = self.kwargs.get('subject_id')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject'] = get_object_or_404(Subject, id=self.kwargs.get('subject_id'))
        return context

class TopicUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Topic
    form_class = TopicForm
    template_name = 'notes/topic_form.html'
    
    def get_success_url(self):
        return reverse('topic_list', kwargs={'subject_id': self.object.subject.id})
    
    def test_func(self):
        topic = self.get_object()
        return self.request.user == topic.user

class TopicDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Topic
    template_name = 'notes/topic_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('topic_list', kwargs={'subject_id': self.object.subject.id})
    
    def test_func(self):
        topic = self.get_object()
        return self.request.user == topic.user

# Note CRUD
class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'notes/note_list.html'
    context_object_name = 'notes'
    
    def get_queryset(self):
        topic_id = self.kwargs.get('topic_id')
        return Note.objects.filter(user=self.request.user, topic_id=topic_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = get_object_or_404(Topic, id=self.kwargs.get('topic_id'))
        context['topic'] = topic
        context['subject'] = topic.subject
        return context

class NoteDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Note
    template_name = 'notes/note_detail.html'
    
    def test_func(self):
        note = self.get_object()
        return self.request.user == note.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['highlight_form'] = HighlightForm()
        context['attachment_form'] = AttachmentForm()
        return context

class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    
    def get_success_url(self):
        return reverse('note_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.topic_id = self.kwargs.get('topic_id')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = get_object_or_404(Topic, id=self.kwargs.get('topic_id'))
        context['topic'] = topic
        context['subject'] = topic.subject
        return context

class NoteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    
    def get_success_url(self):
        return reverse('note_detail', kwargs={'pk': self.object.pk})
    
    def test_func(self):
        note = self.get_object()
        return self.request.user == note.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topic'] = self.object.topic
        context['subject'] = self.object.topic.subject
        return context

class NoteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Note
    template_name = 'notes/note_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('note_list', kwargs={'topic_id': self.object.topic.id})
    
    def test_func(self):
        note = self.get_object()
        return self.request.user == note.user

# Attachment and Highlight functionality
@login_required
def add_attachment(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    
    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.note = note
            attachment.save()
            return redirect('note_detail', pk=note.id)
    
    return redirect('note_detail', pk=note.id)

@login_required
def delete_attachment(request, attachment_id):
    attachment = get_object_or_404(Attachment, id=attachment_id, note__user=request.user)
    note_id = attachment.note.id
    attachment.delete()
    return redirect('note_detail', pk=note_id)

@login_required
def add_highlight(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    
    if request.method == 'POST':
        form = HighlightForm(request.POST)
        if form.is_valid():
            highlight = form.save(commit=False)
            highlight.note = note
            highlight.save()
            return redirect('note_detail', pk=note.id)
    
    return redirect('note_detail', pk=note.id)

@login_required
def delete_highlight(request, highlight_id):
    highlight = get_object_or_404(Highlight, id=highlight_id, note__user=request.user)
    note_id = highlight.note.id
    highlight.delete()
    return redirect('note_detail', pk=note_id)

@login_required
def toggle_star(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.is_starred = not note.is_starred
    note.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'is_starred': note.is_starred})
    
    return redirect('note_detail', pk=note.id)

# Chat functionality
@login_required
def inbox(request):
    messages_received = Message.objects.filter(receiver=request.user)
    messages_sent = Message.objects.filter(sender=request.user)
    
    users = set()
    for message in messages_received:
        users.add(message.sender)
    for message in messages_sent:
        users.add(message.receiver)
    
    context = {
        'users': users,
    }
    return render(request, 'notes/inbox.html', context)

@login_required
def chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Mark messages as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    
    # Get conversation
    messages_sent = Message.objects.filter(sender=request.user, receiver=other_user)
    messages_received = Message.objects.filter(sender=other_user, receiver=request.user)
    conversation = sorted(
        list(messages_sent) + list(messages_received),
        key=lambda x: x.created_at
    )
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = other_user
            message.save()
            return redirect('chat', user_id=user_id)
    else:
        form = MessageForm()
    
    context = {
        'other_user': other_user,
        'conversation': conversation,
        'form': form,
    }
    return render(request, 'notes/chat.html', context)

@login_required
def search(request):
    query = request.GET.get('q', '')
    
    if query:
        notes = Note.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            user=request.user
        )
        subjects = Subject.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            user=request.user
        )
        topics = Topic.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            user=request.user
        )
    else:
        notes = []
        subjects = []
        topics = []
    
    context = {
        'notes': notes,
        'subjects': subjects,
        'topics': topics,
        'query': query,
    }
    return render(request, 'notes/search_results.html', context)

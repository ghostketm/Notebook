from django import forms
from .models import StudentProfile, Subject, Topic, Note, Attachment, Highlight, Message
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['nickname', 'institution', 'course', 'profile_picture', 'bio']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description', 'color']

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name', 'description']

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'tags']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'notes-editor'}),
        }

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file', 'name']

class HighlightForm(forms.ModelForm):
    class Meta:
        model = Highlight
        fields = ['text', 'color']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }
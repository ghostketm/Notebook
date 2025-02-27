from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.urls import reverse

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=50, blank=True)
    institution = models.CharField(max_length=100, blank=True)
    course = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#007bff")  # Hex color code
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        unique_together = ['name', 'user']

class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.subject.name} - {self.name}"
    
    class Meta:
        unique_together = ['name', 'subject', 'user']

class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='notes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    is_starred = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('note_detail', kwargs={'pk': self.pk})

class Attachment(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    name = models.CharField(max_length=100)
    is_image = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Check if the file is an image
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg']
        file_extension = self.file.name.split('.')[-1].lower()
        if '.' + file_extension in image_extensions:
            self.is_image = True
        super().save(*args, **kwargs)

class Highlight(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='highlights')
    text = models.TextField()
    color = models.CharField(max_length=7, default="#ffff00")  # Yellow by default
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Highlight in {self.note.title}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"
    
    class Meta:
        ordering = ['-created_at']
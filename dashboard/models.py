from django.db import models
from django.contrib.auth.models import User

class QuickNote(models.Model):
    note_id = models.CharField(max_length=255, unique=True, db_index=True)
    content = models.TextField(blank=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quick_notes'
        ordering = ['-updated_at']

    def __str__(self):
        return self.note_id

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'dashboard_notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message[:30]}"

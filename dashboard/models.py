from django.db import models

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

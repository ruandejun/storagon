from django.db import models
from django.contrib.auth.models import User

class Card(models.Model):
    STATUS_CHOICES = [
        ('Chưa sử dụng', 'Chưa sử dụng'),
        ('Đang sử dụng', 'Đang sử dụng'),
        ('Thẻ chết', 'Thẻ chết'),
        ('Thẻ sống', 'Thẻ sống'),
        ('Thẻ tốt', 'Thẻ tốt'),
        ('Thẻ lỗi', 'Thẻ lỗi'),
        ('Sub OK', 'Sub OK'),
        ('Sub lỗi', 'Sub lỗi'),
    ]
    card_number = models.CharField(max_length=255, unique=True)
    expiry_date = models.CharField(max_length=50, blank=True, null=True)
    cvv = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Chưa sử dụng')
    extra_info = models.TextField(blank=True, null=True)
    used_count = models.IntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_cards')
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='used_cards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company_cards'
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f"{self.card_number} ({self.status})"

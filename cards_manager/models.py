from django.db import models

class Card(models.Model):
    STATUS_CHOICES = [
        ('Chưa sử dụng', 'Chưa sử dụng'),
        ('Đang sử dụng', 'Đang sử dụng'),
        ('Đã sử dụng', 'Đã sử dụng'),
        ('Thẻ chết', 'Thẻ chết'),
        ('Thẻ sống', 'Thẻ sống'),
        ('Thẻ tốt', 'Thẻ tốt'),
    ]
    card_number = models.CharField(max_length=255, unique=True)
    expiry_date = models.CharField(max_length=50, blank=True, null=True)
    cvv = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Chưa sử dụng')
    extra_info = models.TextField(blank=True, null=True)
    used_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company_cards'
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f"{self.card_number} ({self.status})"

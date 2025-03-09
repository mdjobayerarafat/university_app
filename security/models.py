from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Report(models.Model):
    REPORT_TYPES = [
        ('LOST', 'Lost Item'),
        ('FOUND', 'Found Item'),
        ('SECURITY', 'Security Concern'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date_occurred = models.DateTimeField()
    date_reported = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    image = models.ImageField(upload_to='report_images/', blank=True, null=True)
    is_urgent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_reported']

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.title}"
from django.db import models
from repos.models import SourceFile
from django.contrib.auth.models import User

class CheckLog(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('done','Done'),
        ('error','Error'),
    ]
    source_file = models.ForeignKey(SourceFile, related_name='check_logs', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    result = models.TextField(blank=True)  # flake8 output
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

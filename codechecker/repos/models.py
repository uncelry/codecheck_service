from django.db import models
from users.models import User

def user_upload_path(instance, filename):
    return f'user_{instance.owner.id}/{filename}'

class SourceFile(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('checked', 'Checked'),
        ('error', 'Error'),
        ('deleted', 'Deleted'),
    ]

    owner = models.ForeignKey(User, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_upload_path)
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    last_check = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    # version or replace tracking
    replaced = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']

    def mark_deleted(self):
        self.deleted = True
        self.status = 'deleted'
        self.save()

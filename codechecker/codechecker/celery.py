import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codechecker.settings')

app = Celery('codechecker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

import subprocess
import os
from celery import shared_task
from django.utils import timezone
from .models import CheckLog
from repos.models import SourceFile
from django.core.mail import send_mail
from django.conf import settings

@shared_task(bind=True, max_retries=3)
def run_flake8_check(self, source_file_id, check_log_id):
    """
    Task that runs flake8 against the uploaded file and saves results to CheckLog.
    """
    try:
        sf = SourceFile.objects.get(id=source_file_id)
        check = CheckLog.objects.get(id=check_log_id)
        # Ensure file path accessible
        file_path = sf.file.path
        # Run flake8 via subprocess, capture output
        # Note: in docker container flake8 must be installed and in PATH
        proc = subprocess.run(['flake8', file_path, '--max-line-length', '120'],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)

        output = proc.stdout.strip()
        if proc.returncode == 0:
            check.status = 'done'
            check.result = 'No issues found' if not output else output
        else:
            check.status = 'done'
            # flake8 returns non-zero if issues; put stdout into result
            check.result = output or proc.stderr
        check.save()
        sf.last_check = timezone.now()
        sf.status = 'checked'
        sf.save()
        # schedule email send
        send_check_email.delay(check.id)
    except Exception as exc:
        # Save error to check log
        try:
            check.status = 'error'
            check.result = f'Exception: {str(exc)}'
            check.save()
        except:
            pass
        raise self.retry(exc=exc, countdown=10)

@shared_task
def trigger_check_for_file(source_file_id):
    """
    Create CheckLog and dispatch run_flake8_check
    """
    sf = SourceFile.objects.get(id=source_file_id)
    check = CheckLog.objects.create(source_file=sf, status='pending')
    # offload to run_flake8_check
    run_flake8_check.delay(sf.id, check.id)

@shared_task
def scan_and_check_new_files():
    """
    Periodic: finds files marked new/replaced and triggers checks.
    """
    from repos.models import SourceFile
    new_files = SourceFile.objects.filter(status='new', deleted=False)
    for f in new_files:
        trigger_check_for_file.delay(f.id)

@shared_task
def send_check_email(check_log_id):
    """
    Send email about check results and mark CheckLog.email_sent = True
    """
    try:
        check = CheckLog.objects.get(id=check_log_id)
        sf = check.source_file
        owner = sf.owner
        subject = f'Code check result for {sf.filename}'
        body = (
            f'Hello {owner.username},\n\n'
            f'Your file "{sf.filename}" was checked at {check.created_at}.\n\n'
            f'Result:\n{check.result}\n\n'
            'Best regards,\nCodeChecker'
        )
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [owner.email],
            fail_silently=False
        )
        check.email_sent = True
        check.email_sent_at = timezone.now()
        check.save()
    except Exception as exc:
        # Optionally retry or log
        raise

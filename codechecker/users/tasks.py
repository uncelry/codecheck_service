from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta

from django.utils.timezone import now

from users.models import User


@shared_task
def send_verification_email(email, verification_url):
    subject = "Email verification"
    message = f"Check the link to verify your email:\n\n{verification_url}"

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )


def delete_expired_unverified_users():
    users = User.objects.filter(email_verified=False, date_joined__lte=now() - timedelta(hours=1))
    users.delete()
    print("deleted expired users")

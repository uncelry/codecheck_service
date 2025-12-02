from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from users.tasks import delete_expired_unverified_users


def start():
    scheduler = BackgroundScheduler()

    # Раз в 60 секунд
    scheduler.add_job(delete_expired_unverified_users, "interval", seconds=5)

    scheduler.start()

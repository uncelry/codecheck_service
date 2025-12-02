import os

from django.apps import AppConfig

class UsersConfig(AppConfig):
    name = "users"

    def ready(self):
        # Запускать APScheduler только если явно разрешено
        if os.environ.get("ENABLE_APSCHEDULER") != "true":
            return

        from users.scheduler import start
        start()

import pytest

from checks.models import CheckLog
from checks.tasks import run_flake8_check
from repos.models import SourceFile
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_celery_check_task():
    owner = User.objects.create(username="some@email.com", email="some@email.com", password="faf3f23f3")

    file = SourceFile.objects.create(
        filename="x.py",
        file="dummy.py",
        owner=owner,
        status="new"
    )
    check = CheckLog.objects.create(source_file=file, status='pending')

    # вызываем задачу синхронно
    run_flake8_check(file.id, check.id)

    file.refresh_from_db()

    assert file.status in ["checked", "error"]
    assert file.last_check is not None

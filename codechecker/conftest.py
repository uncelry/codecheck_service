import os
import django


def pytest_addoption(parser):
    """
    Регистрируем custom ini-опцию allowed_apps.
    """
    parser.addini(
        "allowed_apps",
        "Comma-separated list of Django apps for which the tests should run",
        default="",
    )


def pytest_configure(config):
    """
    Настраиваем Django и читаем список приложений из pytest.ini
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codechecker.settings")
    django.setup()

    allowed_apps = config.getini("allowed_apps")
    config.allowed_apps = [
        app.strip() for app in allowed_apps.split(",") if app.strip()
    ]


def pytest_collection_modifyitems(config, items):
    """
    Фильтруем тесты: запускаем только те, что лежат в apps из allowed_apps.
    """
    allowed_apps = config.allowed_apps

    # если список пустой — запускаем все тесты
    if not allowed_apps:
        return

    selected = []
    deselected = []

    for item in items:
        path = str(item.fspath).replace("\\", "/")  # для Windows

        # допускаем тесты только из разрешённых приложений
        if any(f"/{app}/" in path for app in allowed_apps):
            selected.append(item)
        else:
            deselected.append(item)

    # заменяем тесты списком выбранных
    items[:] = selected

    if deselected:
        config.hook.pytest_deselected(items=deselected)

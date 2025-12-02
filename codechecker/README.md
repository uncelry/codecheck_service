## Запуск проекта
1. Заполните .env
2. `docker-compose up --build` (первые миграции можно запускать вручную: `docker-compose run web python manage.py migrate`).
3. Создайте суперпользователя: `docker-compose run web python manage.py createsuperuser`.
4. Celery worker/beat запускаются как сервисы (celery и celery-beat в compose).
5. Откройте http://localhost:8000/ — UI; API по http://localhost:8000/api/files/.

Запуск тестов: `docker-compose exec web pytest -vv`

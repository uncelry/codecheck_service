#!/bin/bash
set -e

echo "Waiting for Postgres..."

# Ждём пока база поднимется
while ! nc -z db 5432; do
  sleep 1
done

echo "Postgres is ready!"

# Выполняем миграции
echo "Running migrations..."
python manage.py migrate --noinput

# Собираем статику
echo "Collecting static..."
python manage.py collectstatic --noinput

# Запускаем Gunicorn
echo "Starting Gunicorn..."
exec gunicorn codechecker.wsgi:application --bind 0.0.0.0:8000

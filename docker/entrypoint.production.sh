python manage.py migrate --noinput
python manage.py collectstatic --noinput
python -m gunicorn --reload --bind 0.0.0.0:8000 --workers 3 BagualesPOS.wsgi:application

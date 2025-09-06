source $UV_PROJECT_ENVIRONMENT/bin/activate
cd /app
python manage.py makemigrations
python manage.py migrate
# python manage.py collectstatic --noinput
python manage.py livereload &
python manage.py runserver 0.0.0.0:8000

uv run manage.py migrate --noinput
uv run manage.py collectstatic --noinput
uv run manage.py livereload && uv run manage.py runserver 0.0.0.0:8000

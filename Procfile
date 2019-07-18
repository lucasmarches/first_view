release: python manage.py makemigrations
release: python manage.py migrate
web: gunicorn first_view.wsgi --log-file -

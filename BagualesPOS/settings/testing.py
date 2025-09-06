from .base import *

DEBUG = False

SECRET_KEY = 'testing-secret-key'

# Usar SQLite en memoria para tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Simplificá middleware si querés
MIDDLEWARE = MIDDLEWARE.copy()

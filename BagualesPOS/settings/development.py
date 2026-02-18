from .base import *


TEMPLATES[0].get('DIRS').append(BASE_DIR/"templates_dev")


SECURE_CROSS_ORIGIN_OPENER_POLICY = None

# Configuración temporal para usar SQLite si PostgreSQL no está disponible
import os
if not env.str('DB_HOST') or env.str('DB_HOST') == '':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

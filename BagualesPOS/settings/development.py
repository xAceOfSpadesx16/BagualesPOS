from .base import *


TEMPLATES[0].get('DIRS').append(BASE_DIR/"templates_dev")


# Livereload settings
indice_statics = INSTALLED_APPS.index('django.contrib.staticfiles')

INSTALLED_APPS.insert(indice_statics, 'livereload')

MIDDLEWARE += [
    'livereload.middleware.LiveReloadScript',
]
LIVERELOAD_HOST= env.str('LIVERELOAD_HOST')
LIVERELOAD_PORT= env.int('LIVERELOAD_PORT')

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

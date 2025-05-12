from .base import *


TEMPLATES[0].get('DIRS').append(BASE_DIR/"templates_dev")
print(BASE_DIR)
# LIVERELOAD 

INSTALLED_APPS += [
    'livereload',
]
MIDDLEWARE += [
    'livereload.middleware.LiveReloadScript',
]
LIVERELOAD_HOST= env.str('LIVERELOAD_HOST')
LIVERELOAD_PORT= env.int('LIVERELOAD_PORT')


SECURE_CROSS_ORIGIN_OPENER_POLICY = None

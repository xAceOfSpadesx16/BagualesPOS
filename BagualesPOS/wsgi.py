"""
WSGI config for BagualesPOS project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from environ import Env
from django.core.wsgi import get_wsgi_application
env=Env()
Env.read_env()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'BagualesPOS.settings.{env.str("SETTINGS_MODULE")}')

application = get_wsgi_application()

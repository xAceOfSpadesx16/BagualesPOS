from django.conf import settings

def django_debug(request):
    return {
        'django_debug': settings.DEBUG,
    }
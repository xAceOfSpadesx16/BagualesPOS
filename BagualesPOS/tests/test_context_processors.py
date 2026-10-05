from django.test import SimpleTestCase
from django.test.utils import override_settings
from django.http import HttpRequest
from BagualesPOS.context_processors import django_debug

class ContextProcessorsTestCase(SimpleTestCase):
    @override_settings(DEBUG=True)
    def test_django_debug_true(self):
        request = HttpRequest()
        context = django_debug(request)
        self.assertTrue(context['django_debug'])

    @override_settings(DEBUG=False)
    def test_django_debug_false(self):
        request = HttpRequest()
        context = django_debug(request)
        self.assertFalse(context['django_debug'])

from django.test import TestCase
from unittest.mock import patch
from locale import Error
from utils.formats import formatted_integer

class FormatsTestCase(TestCase):
    def test_formatted_integer(self):
        # Test with locale (mocking if necessary or assuming available)
        # In this env it might work or fail, but the function has a try-except.
        # Let's test basic functionality.
        self.assertEqual(formatted_integer(1000), "1.000")
        self.assertEqual(formatted_integer(100), "100")

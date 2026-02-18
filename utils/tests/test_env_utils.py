from django.test import TestCase
from utils.env_utils import SETTING_MODULE

class EnvUtilsTestCase(TestCase):
    def test_setting_module(self):
        # We just want to ensure it's loaded and is a string
        self.assertIsInstance(SETTING_MODULE, str)
        self.assertTrue(len(SETTING_MODULE) > 0)

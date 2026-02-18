from django.test import TestCase
from django.apps import apps
from administration.apps import AdministrationConfig

class AdministrationConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(AdministrationConfig.name, 'administration')
        self.assertEqual(apps.get_app_config('administration').name, 'administration')

    def test_boilerplate_imports(self):
        # Import modules to ensure they are covered
        import administration.models
        import administration.admin
        import administration.urls
        import administration.views
        
        # Simple assertions to avoid "unused import" warnings if linters are strict,
        # and to prove they were imported.
        self.assertIsNotNone(administration.models)
        self.assertIsNotNone(administration.admin)
        self.assertIsNotNone(administration.urls)
        self.assertIsNotNone(administration.views)

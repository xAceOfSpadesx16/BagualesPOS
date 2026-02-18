from django.test import TestCase
from clients.models import Client

class ClientSoftDeleteTestCase(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            name="Test",
            last_name="User",
            dni="123456789",
            email="test@example.com",
            address="Test Address",
            postal_code="1234"
        )

    def test_soft_delete(self):
        """Test that soft_delete sets is_deleted=True and creates timestamp"""
        self.assertFalse(self.client.is_deleted)
        self.assertIsNone(self.client.deleted_at)

        self.client.soft_delete()
        self.client.refresh_from_db()

        self.assertTrue(self.client.is_deleted)
        self.assertIsNotNone(self.client.deleted_at)

    def test_restore(self):
        """Test that restore reverses soft_delete"""
        self.client.soft_delete()
        self.client.refresh_from_db()
        self.assertTrue(self.client.is_deleted)

        self.client.restore()
        self.client.refresh_from_db()

        self.assertFalse(self.client.is_deleted)
        self.assertIsNone(self.client.deleted_at)

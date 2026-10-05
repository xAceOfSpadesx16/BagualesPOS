from django.test import TestCase
from devices.models import Device, CashRegister
from devices.serializers import DeviceSerializer
from utils.tests import TenantTestCase

class DeviceSerializerTestCase(TenantTestCase, TestCase):
    def setUp(self):
        super().setUp()
        self.device = CashRegister.objects.create(
            company=self.company,
            code="SER-01",
            name="Serializer Test Device",
            is_active=True
        )
    
    def test_device_serializer(self):
        serializer = DeviceSerializer(self.device)
        data = serializer.data
        self.assertEqual(data['code'], "SER-01")
        self.assertEqual(data['name'], "Serializer Test Device")

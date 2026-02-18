from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from devices.serializers import (
    DeviceAssignSerializer, DeviceConfigUpdateSerializer,
    PolymorphicDeviceSerializer, CashRegisterSerializer
)
from devices.models import CashRegister, PriceChecker, Device

User = get_user_model()

class DeviceSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.cr = CashRegister.objects.create(code='CR-TEST', name='Test Register')

    def test_assign_serializer_validation(self):
        # Valid user
        data = {'user_id': self.user.id}
        serializer = DeviceAssignSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user_id'], self.user.id)
        
        # Invalid user
        data = {'user_id': 9999}
        serializer = DeviceAssignSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('user_id', serializer.errors)

    def test_polymorphic_serializer(self):
        # Create devices
        cr = CashRegister.objects.create(code='CR-01', name='Cash Register')
        pc = PriceChecker.objects.create(code='PC-01', name='Price Checker')
        
        # Serialize list
        devices = Device.objects.filter(code__in=['CR-01', 'PC-01']).order_by('code')
        serializer = PolymorphicDeviceSerializer(devices, many=True)
        data = serializer.data
        
        # Check if correct fields are present
        # CR should have has_open_session
        cr_data = next(d for d in data if d['code'] == 'CR-01')
        self.assertIn('has_open_session', cr_data)
        self.assertEqual(cr_data['resourcetype'], 'CashRegister')
        
        # PC should have display_promotions
        pc_data = next(d for d in data if d['code'] == 'PC-01')
        self.assertIn('display_promotions', pc_data)
        self.assertEqual(pc_data['resourcetype'], 'PriceChecker')

    def test_config_update_serializer(self):
        data = {'key': 'theme', 'value': 'dark'}
        serializer = DeviceConfigUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

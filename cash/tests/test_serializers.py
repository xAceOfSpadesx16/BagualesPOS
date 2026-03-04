from django.test import TestCase
from cash.serializers import OpenCashSessionSerializer, CloseCashSessionSerializer
from utils.tests import TenantTestCase

class SerializerValidationTestCase(TenantTestCase, TestCase):
    """Tests for serializer validations"""
    
    def test_open_session_serializer_negative_balance_validation(self):
        """Test OpenCashSessionSerializer validation"""
        data = {
            'cash_register': 1,
            'opening_balance': '-100.00'
        }
        
        serializer = OpenCashSessionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('opening_balance', serializer.errors)
        
    def test_close_session_serializer_negative_balance_validation(self):
        """Test CloseCashSessionSerializer validation"""
        data = {
            'closing_balance': '-50.00',
            'notes': 'Test'
        }
        
        serializer = CloseCashSessionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('closing_balance', serializer.errors)

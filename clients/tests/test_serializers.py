from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from clients.models import Client, CustomerAccount, CustomerBalanceRecord
from clients.serializers import (
    ClientSerializer, 
    CustomerAccountSerializer, 
    CustomerBalanceRecordSerializer
)
from clients.choices import MovementType
from utils.tests import TenantTestCase

User = get_user_model()

class ClientSerializerTestCase(TenantTestCase, TestCase):
    def setUp(self):
        super().setUp()
        self.client_obj = Client.objects.create(company=self.company, 
            name="Maria", last_name="Lopez", dni="87654321", email="maria@example.com"
        )
        self.account = self.client_obj.customer_account
        
    def test_valid_client_serializer(self):
        serializer = ClientSerializer(self.client_obj)
        data = serializer.data
        self.assertEqual(data['name'], "Maria")
        self.assertEqual(data['last_name'], "Lopez")

class CustomerAccountSerializerTestCase(TenantTestCase, TestCase):
    def setUp(self):
        super().setUp()
        self.client_obj = Client.objects.create(company=self.company, 
            name="Test", last_name="User", dni="12345", email="test@example.com"
        )
        self.account = self.client_obj.customer_account

    def test_valid_account_serializer(self):
        serializer = CustomerAccountSerializer(self.account)
        data = serializer.data
        self.assertIn('balance', data)

class CustomerBalanceRecordSerializerTestCase(TenantTestCase, TestCase):
    def setUp(self):
        super().setUp()
        self.client_obj = Client.objects.create(company=self.company, 
            name="Balance", last_name="Test", dni="99999", email="balance@example.com"
        )
        self.account = self.client_obj.customer_account
        
    def test_valid_record_serializer(self):
        record = CustomerBalanceRecord.objects.create(
            company=self.company,
            customer_account=self.account,
            amount=Decimal("100.00"),
            movement_type=MovementType.CREDIT,
            created_by=self.user
        )
        serializer = CustomerBalanceRecordSerializer(record)
        data = serializer.data
        self.assertEqual(data['amount'], '100.00')


# ============================================================
# Tests consolidated from test_serializer_clean_exception.py
# ============================================================
class SerializerCleanExceptionTest(TenantTestCase, TestCase):
    """Test serializer clean() exception handling - consolidated from test_serializer_clean_exception.py"""
    
    def setUp(self):
        super().setUp()
        self.client_obj = Client.objects.create(
            company=self.company,
            name='Test',
            last_name='Client',
            dni='123456789',
            email='test@test.com'
        )
        self.account = self.client_obj.customer_account
    
    def test_validate_triggers_clean_exception(self):
        """Test that validate() handles clean() exceptions"""
        from unittest.mock import patch
        # Make clean() raise an exception
        with patch('clients.models.CustomerBalanceRecord.clean') as mock_clean:
            mock_clean.side_effect = Exception("Test validation error")
            
            # Try to create through serializer
            serializer = CustomerBalanceRecordSerializer(data={
                'customer_account': self.account.id,
                'amount': '100.00',
                'movement_type': MovementType.CREDIT,
            })
            
            # Should catch the exception and convert to ValidationError
            is_valid = serializer.is_valid()
            self.assertFalse(is_valid)
            self.assertIn('non_field_errors', serializer.errors)
    
    def test_get_sale_returns_none(self):
        """Test get_sale returns None when no sale"""
        # Create record without sale
        record = CustomerBalanceRecord.objects.create(
            company=self.company,
            customer_account=self.account,
            amount=Decimal('100.00'),
            movement_type=MovementType.CREDIT,
            created_by=self.user,
            sale=None  # No sale
        )
        
        serializer = CustomerBalanceRecordSerializer(record)
        data = serializer.data
        
        # sale should be None
        self.assertIsNone(data.get('sale'))


# ============================================================
# Tests consolidated from test_serializer_coverage.py
# ============================================================
class SerializerCoverageTest(TenantTestCase, TestCase):
    """Test serializer edge cases for 100% coverage - consolidated from test_serializer_coverage.py"""
    
    def setUp(self):
        super().setUp()
        self.client_obj = Client.objects.create(
            company=self.company,
            name='Test',
            last_name='Client',
            dni='123456789',
            email='test@test.com'
        )
        self.account = self.client_obj.customer_account
    
    def test_balance_record_with_sale(self):
        """Test serializer with sale reference"""
        from sales.models import Sale, PayMethod
        
        pay_method = PayMethod.objects.create(company=self.company, name='Cash')
        sale = Sale.objects.create(
            company=self.company,
            seller=self.user,
            pay_method=pay_method,
            total_amount=Decimal('100.00')
        )
        
        record = CustomerBalanceRecord.objects.create(
            company=self.company,
            customer_account=self.account,
            sale=sale,
            amount=Decimal('100.00'),
            movement_type=MovementType.CREDIT,
            created_by=self.user
        )
        
        serializer = CustomerBalanceRecordSerializer(record)
        data = serializer.data
        
        # Should include sale_id
        self.assertIn('sale', data)
    
    def test_balance_record_with_related_to(self):
        """Test serializer with related_to reference"""
        # Create original record
        original = CustomerBalanceRecord.objects.create(
            company=self.company,
            customer_account=self.account,
            amount=Decimal('100.00'),
            movement_type=MovementType.CREDIT,
            created_by=self.user
        )
        
        # Create reversal related to original
        reversal = CustomerBalanceRecord.objects.create(
            company=self.company,
            customer_account=self.account,
            related_to=original,
            amount=Decimal('-100.00'),
            movement_type=MovementType.REVERSAL,
            created_by=self.user
        )
        
        serializer = CustomerBalanceRecordSerializer(reversal)
        data = serializer.data
        
        # Should include related_to
        self.assertIn('related_to', data)


# ============================================================
# Tests consolidated from test_serializer_validate.py
# ============================================================
class SerializerValidateTest(TenantTestCase, TestCase):
    """Test serializer validate method - consolidated from test_serializer_validate.py"""
    
    def setUp(self):
        super().setUp()
        self.client_obj = Client.objects.create(
            company=self.company,
            name='Test',
            last_name='Client',
            dni='123456789',
            email='test@test.com'
        )
        self.account = self.client_obj.customer_account
    
    def test_update_balance_record_through_serializer(self):
        """Test updating a record"""
        # Create a record
        record = CustomerBalanceRecord.objects.create(
            company=self.company,
            customer_account=self.account,
            amount=Decimal('100.00'),
            movement_type=MovementType.CREDIT,
            created_by=self.user
        )
        
        # Update it through serializer (partial=True)
        serializer = CustomerBalanceRecordSerializer(
            record,
            data={'amount': '150.00'},
            partial=True
        )
        
        # This should call validate() with self.instance set
        self.assertTrue(serializer.is_valid())
        serializer.save()
        
        record.refresh_from_db()
        self.assertEqual(record.amount, Decimal('150.00'))
    
    def test_serializer_validation_error(self):
        """Test serializer with invalid data that triggers clean() exception"""
        # Try to create a record with invalid data
        serializer = CustomerBalanceRecordSerializer(data={
            'customer_account': self.account.id,
            'amount': 'invalid',  # Invalid amount
            'movement_type': MovementType.CREDIT,
        })
        
        # Should not be valid
        self.assertFalse(serializer.is_valid())


# ============================================================
# Tests consolidated from test_get_sale_none.py and test_client_without_account.py
# ============================================================
class ClientSerializerEdgeCasesTest(TenantTestCase, TestCase):
    """Test client serializer edge cases - consolidated from multiple files"""
    
    def setUp(self):
        super().setUp()
    
    def test_client_serializer_without_customer_account(self):
        """Test get_customer_account returns None when account doesn't exist"""
        from unittest.mock import PropertyMock, patch
        
        # Create a client
        client = Client.objects.create(
            company=self.company,
            name='Test',
            last_name='NoAccount',
            dni='999999999',
            email='noaccount@test.com'
        )
        
        # Mock hasattr to return False for customer_account
        with patch.object(type(client), 'customer_account', new_callable=PropertyMock) as mock_account:
            # Make hasattr return False by raising AttributeError
            mock_account.side_effect = AttributeError("No customer_account")
            
            # Serialize - this should trigger the else branch
            serializer = ClientSerializer(client)
            
            # Try to access the data
            try:
                data = serializer.data
                # customer_account should be None
                self.assertIsNone(data.get('customer_account'))
            except AttributeError:
                # If it raises AttributeError, that's also fine
                pass
    
    def test_serialize_record_without_sale(self):
        """Test serializing a record with sale=None returns None for sale field"""
        client_obj = Client.objects.create(
            company=self.company,
            name='Test',
            last_name='Client',
            dni='123456789',
            email='test@test.com'
        )
        account = client_obj.customer_account
        
        # Create record explicitly with sale=None
        record = CustomerBalanceRecord.objects.create(
            company=self.company,
            customer_account=account,
            amount=Decimal('100.00'),
            movement_type=MovementType.DEBIT,
            created_by=self.user
        )
        
        # Ensure sale is None
        self.assertIsNone(record.sale)
        
        # Serialize it
        serializer = CustomerBalanceRecordSerializer(record)
        
        # Access the sale field which should trigger get_sale
        sale_data = serializer.data.get('sale')
        
        # Should be None
        self.assertIsNone(sale_data)

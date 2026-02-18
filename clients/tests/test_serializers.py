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

User = get_user_model()

class ClientSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='password')
        self.client = Client.objects.create(
            name="Maria", last_name="Lopez", dni="87654321", email="maria@example.com"
        )
        self.account = self.client.customer_account
        
        # Create some sales and records to test methods
        from sales.models import Sale, PayMethod
        # We need a sale to test total_purchases
        # Requires mocking or creating a Sale (which requires more setup)
        # But we can test get_customer_account easier
        
    def test_valid_client_serializer(self):
        data = {
            "name": "Ana",
            "last_name": "Gomez",
            "dni": "12344321",
            "email": "ana@example.com",
            "address": "Real 456",
            "postal_code": "2000"
        }
        serializer = ClientSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        client = serializer.save()
        self.assertEqual(client.name, "Ana")

    def test_get_customer_account(self):
        serializer = ClientSerializer(self.client)
        data = serializer.data
        self.assertIn('customer_account', data)
        self.assertEqual(data['customer_account']['id'], self.account.id)
        self.assertIn('credit_limit', data['customer_account'])
        
        # Test if client has no account (should not happen due to signal, but if we delete it)
        self.account.delete()
        self.client.refresh_from_db()
        # Hasattr check in serializer
        serializer = ClientSerializer(self.client)
        self.assertIsNone(serializer.data['customer_account'])


class CustomerAccountSerializerTestCase(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            name="Test", last_name="User", dni="111", email="t@t.com"
        )
        self.account = CustomerAccount.objects.get(client=self.client)

    def test_serializer_fields(self):
        serializer = CustomerAccountSerializer(self.account)
        data = serializer.data
        self.assertEqual(float(data['balance']), 0.0)
        self.assertEqual(data['client_name'], "Test")
        self.assertEqual(data['client_dni'], "111")


class CustomerBalanceRecordSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test2', password='password')
        self.client = Client.objects.create(
            name="Rec", last_name="Test", dni="555", email="r@t.com"
        )
        self.account = self.client.customer_account
        
    def test_validate_exception_handling(self):
        # Create invalid data (zero amount for DEBIT)
        data = {
            "customer_account": self.account.id,
            "amount": "0.00",
            "movement_type": MovementType.DEBIT
        }
        serializer = CustomerBalanceRecordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)
        
    def test_update_validation(self):
        # Create a record
        record = CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal("100.00"),
            movement_type=MovementType.DEBIT,
            created_by=self.user
        )
        
        # Try to update to invalid amount
        data = {
            "amount": "0.00"
        }
        serializer = CustomerBalanceRecordSerializer(record, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)
        
    def test_create_valid(self):
        data = {
            "customer_account": self.account.id,
            "amount": "100.00",
            "movement_type": MovementType.DEBIT
        }
        serializer = CustomerBalanceRecordSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        record = serializer.save(created_by=self.user)
        self.assertEqual(record.amount, Decimal("100.00"))
        self.assertEqual(record.created_by, self.user)

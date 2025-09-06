from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from clients.models import Client, CustomerBalanceRecord

class CustomerBalanceRecordTestCase(TestCase):

    def setUp(self):
        self.client_obj = Client.objects.create(
            name="Juan",
            last_name="Pérez",
            dni="12345678",
            email="juan@example.com",
            address="Falsa 123",
            postal_code="1000",
            billing_type="C"
        )

    def test_valid_credit(self):
        record = CustomerBalanceRecord(
            client=self.client_obj,
            amount=Decimal("150.00"),
            movement_type=CustomerBalanceRecord.MovementType.CREDIT
        )
        record.full_clean()

    def test_invalid_credit_zero(self):
        record = CustomerBalanceRecord(
            client=self.client_obj,
            amount=Decimal("0.00"),
            movement_type=CustomerBalanceRecord.MovementType.CREDIT
        )
        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_valid_debit(self):
        record = CustomerBalanceRecord(
            client=self.client_obj,
            amount=Decimal("-200.00"),
            movement_type=CustomerBalanceRecord.MovementType.DEBIT
        )
        record.full_clean()

    def test_invalid_debit_positive(self):
        record = CustomerBalanceRecord(
            client=self.client_obj,
            amount=Decimal("80.00"),
            movement_type=CustomerBalanceRecord.MovementType.DEBIT
        )
        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_valid_refund(self):
        original = CustomerBalanceRecord.objects.create(
            client=self.client_obj,
            amount=Decimal("-100.00"),
            movement_type=CustomerBalanceRecord.MovementType.DEBIT
        )
        refund = CustomerBalanceRecord(
            client=self.client_obj,
            amount=Decimal("100.00"),
            movement_type=CustomerBalanceRecord.MovementType.REFUND,
            related_to=original
        )
        refund.full_clean()

    def test_invalid_refund_without_reference(self):
        refund = CustomerBalanceRecord(
            client=self.client_obj,
            amount=Decimal("100.00"),
            movement_type=CustomerBalanceRecord.MovementType.REFUND
        )
        with self.assertRaises(ValidationError):
            refund.full_clean()

    def test_valid_reversal(self):
        original = CustomerBalanceRecord.objects.create(
            client=self.client_obj,
            amount=Decimal("-300.00"),
            movement_type=CustomerBalanceRecord.MovementType.DEBIT
        )
        reversal = CustomerBalanceRecord(
            client=self.client_obj,
            amount=Decimal("300.00"),
            movement_type=CustomerBalanceRecord.MovementType.REVERSAL,
            related_to=original
        )
        reversal.full_clean()

    def test_invalid_duplicate_reversal(self):
        original = CustomerBalanceRecord.objects.create(
            client=self.client_obj,
            amount=Decimal("-400.00"),
            movement_type=CustomerBalanceRecord.MovementType.DEBIT
        )
        CustomerBalanceRecord.objects.create(
            client=self.client_obj,
            amount=Decimal("400.00"),
            movement_type=CustomerBalanceRecord.MovementType.REVERSAL,
            related_to=original
        )
        second_reversal = CustomerBalanceRecord(
            client=self.client_obj,
            amount=Decimal("400.00"),
            movement_type=CustomerBalanceRecord.MovementType.REVERSAL,
            related_to=original
        )
        with self.assertRaises(ValidationError):
            second_reversal.full_clean()

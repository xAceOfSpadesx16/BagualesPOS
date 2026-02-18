from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from clients.models import Client, CustomerBalanceRecord, CustomerAccount
from clients.choices import MovementType

class CustomerBalanceRecordTestCase(TestCase):

    def setUp(self):
        self.client_obj = Client.objects.create(
            name="Juan",
            last_name="Pérez",
            dni="12345678",
            email="juan@example.com",
            address="Falsa 123",
            postal_code="1000"
        )
        self.account = CustomerAccount.objects.get(client=self.client_obj)

    def test_valid_credit(self):
        record = CustomerBalanceRecord(
            customer_account=self.account,
            amount=Decimal("150.00"),
            movement_type=MovementType.CREDIT
        )
        record.full_clean()

    def test_invalid_credit_zero(self):
        record = CustomerBalanceRecord(
            customer_account=self.account,
            amount=Decimal("0.00"),
            movement_type=MovementType.CREDIT
        )
        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_valid_debit(self):
        # Debit validation expects positive amount (represents debt amount)
        record = CustomerBalanceRecord(
            customer_account=self.account,
            amount=Decimal("200.00"),
            movement_type=MovementType.DEBIT
        )
        record.full_clean()

    def test_invalid_debit_zero(self):
        # Test that zero debits are invalid
        record = CustomerBalanceRecord(
            customer_account=self.account,
            amount=Decimal("0.00"),
            movement_type=MovementType.DEBIT
        )
        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_valid_refund(self):
        original = CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal("100.00"),
            movement_type=MovementType.DEBIT
        )
        refund = CustomerBalanceRecord(
            customer_account=self.account,
            amount=Decimal("100.00"),
            movement_type=MovementType.REFUND,
            related_to=original
        )
        refund.full_clean()

    def test_invalid_refund_missing_related(self):
        refund = CustomerBalanceRecord(
            customer_account=self.account,
            amount=Decimal("100.00"),
            movement_type=MovementType.REFUND
            # related_to missing
        )
        with self.assertRaises(ValidationError) as cm:
            refund.full_clean()
        self.assertIn("related_to", cm.exception.message_dict)

    def test_valid_reversal(self):
        original = CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal("300.00"),
            movement_type=MovementType.DEBIT
        )
        reversal = CustomerBalanceRecord(
            customer_account=self.account,
            amount=Decimal("300.00"),
            movement_type=MovementType.REVERSAL,
            related_to=original
        )
        reversal.full_clean()

    def test_invalid_duplicate_reversal(self):
        original = CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal("400.00"),
            movement_type=MovementType.DEBIT
        )
        CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal("400.00"),
            movement_type=MovementType.REVERSAL,
            related_to=original
        )
        second_reversal = CustomerBalanceRecord(
            customer_account=self.account,
            amount=Decimal("400.00"),
            movement_type=MovementType.REVERSAL,
            related_to=original
        )
        with self.assertRaises(ValidationError):
            second_reversal.full_clean()
            
    def test_validate_adjustment(self):
        # Adjustment must have related_to
        record = CustomerBalanceRecord(
            customer_account=self.account,
            amount=Decimal("10.00"),
            movement_type=MovementType.ADJUSTMENT
        )
        with self.assertRaises(ValidationError) as cm:
            record.full_clean()
        self.assertIn('related_to', cm.exception.message_dict)
        
        # Valid adjustment
        original = CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal("100.00"),
            movement_type=MovementType.DEBIT
        )
        record.related_to = original
        record.full_clean()
        
    def test_delta_client_balance(self):
        # Debit -> negative impact (owes money)
        debit = CustomerBalanceRecord(movement_type=MovementType.DEBIT, amount=Decimal('100'))
        self.assertEqual(debit._delta_client_balance(), Decimal('-100'))
        
        # Credit -> positive (pays money)
        credit = CustomerBalanceRecord(movement_type=MovementType.CREDIT, amount=Decimal('100'))
        self.assertEqual(credit._delta_client_balance(), Decimal('100'))
        
        # Refund -> positive (money back to client balance? or reduces debt?)
        # Model says: return Decimal(self.amount)
        refund = CustomerBalanceRecord(movement_type=MovementType.REFUND, amount=Decimal('100'))
        self.assertEqual(refund._delta_client_balance(), Decimal('100'))
        
        # Adjustment on DEBIT -> Positive (fixes debt, thus adds to balance/reduces debt?)
        # Model: if self.related_to.movement_type == MovementType.DEBIT: return Decimal(self.amount)
        # Assuming adjustment amount is positive.
        original_debit = CustomerBalanceRecord(movement_type=MovementType.DEBIT)
        adj_debit = CustomerBalanceRecord(movement_type=MovementType.ADJUSTMENT, amount=Decimal('10'), related_to=original_debit)
        self.assertEqual(adj_debit._delta_client_balance(), Decimal('10'))
        
        # Adjustment on CREDIT -> Negative
        original_credit = CustomerBalanceRecord(movement_type=MovementType.CREDIT)
        adj_credit = CustomerBalanceRecord(movement_type=MovementType.ADJUSTMENT, amount=Decimal('10'), related_to=original_credit)
        self.assertEqual(adj_credit._delta_client_balance(), Decimal('-10'))

    def test_clean_inactive_account(self):
        self.account.active = False
        self.account.save()
        
        record = CustomerBalanceRecord(
            customer_account=self.account,
            amount=Decimal("100.00"),
            movement_type=MovementType.DEBIT
        )
        with self.assertRaises(ValidationError) as cm:
            record.full_clean()
        self.assertIn('inactive', cm.exception.messages[0])

    def test_clean_credit_limit_exceeded(self):
        self.account.credit_limit = Decimal('100.00')
        self.account.save()
        
        # Balance is 0. Limit is 100.
        # Try to debit 150. Future balance -150 < -100. Should fail.
        record = CustomerBalanceRecord(
            customer_account=self.account,
            amount=Decimal("150.00"),
            movement_type=MovementType.DEBIT
        )
        with self.assertRaises(ValidationError) as cm:
            record.full_clean()
        self.assertIn('exceeds credit limit', cm.exception.messages[0])

    def test_clean_edit_record_recalculates_balance(self):
        # Create initial record
        record = CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal("50.00"),
            movement_type=MovementType.DEBIT
        )
        # Current balance: -50.
        
        self.account.credit_limit = Decimal('60.00')
        self.account.save()
        
        # Edit record to increase amount to 100.
        # Old delta: -50. New delta: -100.
        # Current balance: -50.
        # Logic: current (-50) - old_delta (-50) + new_delta (-100) = -100.
        # Limit check: -100 < -60. Fail.
        
        record.amount = Decimal("100.00")
        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_str_method(self):
        record = CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal("100.00"),
            movement_type=MovementType.DEBIT
        )
        self.assertIn(str(record.amount), str(record))
        self.assertIn(record.movement_type, str(record))

    def test_validate_reversal_no_related(self):
        record = CustomerBalanceRecord(
            customer_account=self.account,
            amount=Decimal("10.00"),
            movement_type=MovementType.REVERSAL
        )
        with self.assertRaises(ValidationError) as cm:
            record.full_clean()
        self.assertIn('related_to', cm.exception.message_dict)

    def test_validate_same_account(self):
        # Create another account
        client2 = Client.objects.create(name="Other", last_name="Client", dni="999", email="o@c.com")
        account2 = client2.customer_account
        
        original = CustomerBalanceRecord.objects.create(
            customer_account=account2,
            amount=Decimal("100.00"),
            movement_type=MovementType.DEBIT
        )
        
        # Try to reverse it in self.account
        reversal = CustomerBalanceRecord(
            customer_account=self.account,
            amount=Decimal("100.00"),
            movement_type=MovementType.REVERSAL,
            related_to=original
        )
        with self.assertRaises(ValidationError) as cm:
            reversal.full_clean()
        # The key might be related_to or NON_FIELD_ERRORS depending on implementation
        # implementation says: raise ValidationError({'related_to': ...})
        self.assertIn('related_to', cm.exception.message_dict)

    def test_validate_refund_different_account(self):
        """Test that refund must belong to same account as original"""
        # Create another account
        client2 = Client.objects.create(name="Refund", last_name="Client", dni="888", email="r@c.com")
        account2 = client2.customer_account
        
        original = CustomerBalanceRecord.objects.create(
            customer_account=account2,
            amount=Decimal("100.00"),
            movement_type=MovementType.DEBIT
        )
        
        # Try to refund it in self.account
        refund = CustomerBalanceRecord(
            customer_account=self.account,
            amount=Decimal("100.00"),
            movement_type=MovementType.REFUND,
            related_to=original
        )
        
        with self.assertRaises(ValidationError) as cm:
            refund.full_clean()
        self.assertIn('related_to', cm.exception.message_dict)

    def test_clean_race_condition_simulation(self):
        # Create a record that looks like it's being updated (has pk) but doesn't exist in DB
        record = CustomerBalanceRecord(
            id=99999,
            customer_account=self.account,
            amount=Decimal("100.00"),
            movement_type=MovementType.DEBIT
        )
        # validators logic: if self.pk: try get... except DoesNotExist: pass
        # This should not raise DoesNotExist, just pass silently in the try/except block
        # and then proceed to other checks.
        try:
            record.full_clean()
        except ValidationError:
            # It might fail other validations, but shouldn't crash with DoesNotExist
            pass
        except CustomerBalanceRecord.DoesNotExist:
            self.fail("full_clean raised DoesNotExist")


class ClientModelTestCase(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            name="Test", last_name="User", dni="111", email="test@test.com"
        )

    def test_str(self):
        self.assertEqual(str(self.client), "Test User")

    def test_get_full_name(self):
        self.assertEqual(self.client.get_full_name, "Test User")

    def test_balance_property(self):
        self.assertEqual(self.client.balance, Decimal('0.00'))
        
    def test_soft_delete_restore(self):
        self.assertFalse(self.client.is_deleted)
        self.assertIsNone(self.client.deleted_at)
        
        self.client.soft_delete()
        self.assertTrue(self.client.is_deleted)
        self.assertIsNotNone(self.client.deleted_at)
        
        self.client.restore()
        self.assertFalse(self.client.is_deleted)
        self.assertIsNone(self.client.deleted_at)

    def test_email_validation(self):
        self.client.email = "invalid-email"
        with self.assertRaises(ValidationError):
            self.client.full_clean()


class CustomerAccountTestCase(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            name="Acc", last_name="Test", dni="222", email="acc@test.com"
        )
        self.account = self.client.customer_account

    def test_str(self):
        self.assertIn(self.client.get_full_name, str(self.account))

    def test_is_active_property(self):
        self.assertTrue(self.account.is_active)
        self.account.active = False
        self.assertFalse(self.account.is_active)

    def test_get_balance_property(self):
        self.assertEqual(self.account.get_balance, Decimal('0.00'))

    def test_deactivate(self):
        self.assertTrue(self.account.active)
        self.account.deactivate()
        self.assertFalse(self.account.active)

    def test_get_movements(self):
        # Create some movements
        m1 = CustomerBalanceRecord.objects.create(
            customer_account=self.account, movement_type=MovementType.DEBIT, amount=Decimal('10')
        )
        m2 = CustomerBalanceRecord.objects.create(
            customer_account=self.account, movement_type=MovementType.CREDIT, amount=Decimal('10')
        )
        
        self.assertEqual(self.account.get_movements().count(), 2)
        self.assertEqual(self.account.get_movements(movement_type=MovementType.DEBIT).count(), 1)
        
        # Test date filtering
        # Use a time slightly in the past to ensure created records are included
        start_time = timezone.now() - timezone.timedelta(minutes=1)
        self.assertEqual(self.account.get_movements(start_date=start_time).count(), 2)
        
        # Use a time even further in the past for end_date to exclude them
        past_end_date = start_time - timezone.timedelta(minutes=1)
        self.assertEqual(self.account.get_movements(end_date=past_end_date).count(), 0)

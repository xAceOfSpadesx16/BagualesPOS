from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from clients.models import Client, CustomerAccount, CustomerBalanceRecord
from clients.choices import MovementType

User = get_user_model()

class BalanceRecordsManagerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client.objects.create(
            name='Test', last_name='Client', dni='123456789', email='test@test.com'
        )
        self.account = self.client.customer_account
        
        # Create records
        self.credit = CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal('100.00'),
            movement_type=MovementType.CREDIT,
            created_by=self.user
        )
        self.debit = CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal('50.00'),
            movement_type=MovementType.DEBIT,
            created_by=self.user
        )
        self.adjustment = CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal('10.00'),
            movement_type=MovementType.ADJUSTMENT,
            related_to=self.debit,
            created_by=self.user
        )
        self.refund = CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal('20.00'),
            movement_type=MovementType.REFUND,
            related_to=self.credit,
            created_by=self.user
        )
        
        # Reconciled record
        self.reconciled = CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal('30.00'),
            movement_type=MovementType.DEBIT,
            reconciled=True,
            created_by=self.user
        )

    def test_filters(self):
        self.assertEqual(CustomerBalanceRecord.objects.credit().count(), 1)
        self.assertEqual(CustomerBalanceRecord.objects.debit().count(), 2) # debit + reconciled debit
        self.assertEqual(CustomerBalanceRecord.objects.adjustment().count(), 1)
        self.assertEqual(CustomerBalanceRecord.objects.refund().count(), 1)
        
        # Reversal
        reversal = CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal('50.00'),
            movement_type=MovementType.REVERSAL,
            related_to=self.debit,
            created_by=self.user
        )
        self.assertEqual(CustomerBalanceRecord.objects.reversal().count(), 1)

    def test_reconciled_filters(self):
        self.assertEqual(CustomerBalanceRecord.objects.reconciled().count(), 1)
        self.assertEqual(CustomerBalanceRecord.objects.unreconciled().count(), 4)

    def test_date_filters(self):
        today = timezone.now().date()
        self.assertEqual(CustomerBalanceRecord.objects.from_date(today).count(), 5)
        self.assertEqual(CustomerBalanceRecord.objects.to_date(today).count(), 5)
        
        future = today + timezone.timedelta(days=1)
        self.assertEqual(CustomerBalanceRecord.objects.from_date(future).count(), 0)
        
        with self.assertRaises(ValueError):
            CustomerBalanceRecord.objects.from_date('invalid')
            
        with self.assertRaises(ValueError):
            CustomerBalanceRecord.objects.to_date('invalid')

    def test_search(self):
        self.assertEqual(CustomerBalanceRecord.objects.search('100.00').count(), 1)
        self.assertEqual(CustomerBalanceRecord.objects.search(str(self.credit.id)).count(), 0) # No sale_id yet
        # Test notes search
        self.credit.notes = "Special note"
        self.credit.save()
        self.assertEqual(CustomerBalanceRecord.objects.search("Special").count(), 1)

    def test_aggregates(self):
        self.assertEqual(CustomerBalanceRecord.objects.credit_total(), Decimal('100.00'))
        # Debit total: 50 (debit) + 30 (reconciled) = 80
        self.assertEqual(CustomerBalanceRecord.objects.debit_total(), Decimal('80.00'))
        self.assertEqual(CustomerBalanceRecord.objects.total_amount(), Decimal('210.00'))

    def test_for_client(self):
        self.assertEqual(CustomerBalanceRecord.objects.for_client(self.client.id).count(), 5)
        self.assertEqual(CustomerBalanceRecord.objects.for_client(999).count(), 0)

    def test_ordering(self):
        newest = CustomerBalanceRecord.objects.newest().first()
        oldest = CustomerBalanceRecord.objects.oldest().first()
        self.assertEqual(newest, self.reconciled)
        self.assertEqual(oldest, self.credit)

    def test_effective(self):
        # Create a reversal for the first debit
        CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal('50.00'),
            movement_type=MovementType.REVERSAL,
            related_to=self.debit,
            created_by=self.user
        )
        
        effective_qs = CustomerBalanceRecord.objects.effective()
        
        # The debit should be excluded because it has a reversal
        self.assertFalse(effective_qs.filter(id=self.debit.id).exists())
        # The reversal itself is excluded by .exclude(movement_type=MovementType.REVERSAL)
        # Wait, effective() logic:
        # return self.exclude(movement_type=MovementType.REVERSAL)
        #        .annotate(_has_reversal=Exists(reversals))
        #        .filter(_has_reversal=False)
        
        # So both the Original Record (marked with _has_reversal=True) AND the Reversal Record (excluded by filter) should be gone.
        self.assertTrue(effective_qs.filter(id=self.credit.id).exists())
        self.assertTrue(effective_qs.filter(id=self.adjustment.id).exists())
        self.assertTrue(effective_qs.filter(id=self.refund.id).exists())
        self.assertTrue(effective_qs.filter(id=self.reconciled.id).exists()) # No reversal on this one
        
    def test_client_balance(self):
        # Calculate expected balance
        # Credit (100) -> +100
        # Debit (50) -> -50
        # Adjustment (10) on Debit -> +10 (fixes a debit means we owe less or paid more? 
        # Logic in _delta_client_balance/client_balance:
        # Adjustment on DEBIT -> sum (positive). Logic: If I was charged 50 (Debit), and I adjust 10, it means the charge was wrong?
        # Let's check model logic: 
        # When(Q(movement_type=MovementType.ADJUSTMENT) & Q(related_to__movement_type=MovementType.DEBIT), then=F('amount'))
        # So +10.
        # Refund (20) -> +20
        # Reconciled Debit (30) -> -30
        
        # Total: 100 - 50 + 10 + 20 - 30 = 50.
        
        balance = CustomerBalanceRecord.objects.client_balance()
        self.assertEqual(balance, Decimal('50.00'))

    def test_with_related(self):
        # Just ensure it runs without error
        qs = CustomerBalanceRecord.objects.with_related()
        self.assertTrue(qs.exists())
        
    def test_with_related_records(self):
        # Just ensure it runs without error
        qs = CustomerBalanceRecord.objects.with_related_records()
        self.assertTrue(qs.exists())
        
    def test_date_filters_datetime(self):
        """Test from_date and to_date with datetime objects"""
        now = timezone.now()
        # Create a record right now
        CustomerBalanceRecord.objects.create(
            customer_account=self.account,
            amount=Decimal('5.00'),
            movement_type=MovementType.DEBIT,
            created_by=self.user
        )
        
        # from_date with datetime
        # Just before now
        start = now - timezone.timedelta(seconds=1)
        self.assertTrue(CustomerBalanceRecord.objects.from_date(start).exists())
        
        # to_date with datetime
        end = now + timezone.timedelta(seconds=2)
        self.assertTrue(CustomerBalanceRecord.objects.to_date(end).exists())

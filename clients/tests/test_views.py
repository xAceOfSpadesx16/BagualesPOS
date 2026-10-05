from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from clients.models import Client, CustomerAccount, CustomerBalanceRecord
from clients.choices import MovementType
from utils.tests import TenantTestCase

User = get_user_model()

class ClientViewSetTestCase(TenantTestCase, APITestCase):
    def setUp(self):
        super().setUp()
        # Already have self.user from TenantTestCase # User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.client_obj = Client.objects.create(company=self.company, 
            name="Pedro", last_name="Gomez", dni="222", email="p@g.com", chosen_billing_type="C"
        )
        self.url = reverse('client-list')

    def test_list_clients(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_client(self):
        data = {
            "name": "Ana",
            "last_name": "Diaz",
            "dni": "333",
            "email": "a@d.com",
            "address": "Calle 1",
            "postal_code": "1234",
            "chosen_billing_type": "B"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Client.objects.count(), 2)

    def test_soft_delete_client(self):
        url = reverse('client-detail', args=[self.client_obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.client_obj.refresh_from_db()
        self.assertTrue(self.client_obj.is_deleted)

    def test_restore_client(self):
        self.client_obj.soft_delete()
        url = reverse('client-restore', args=[self.client_obj.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client_obj.refresh_from_db()
        self.assertFalse(self.client_obj.is_deleted)

    def test_filter_clients(self):
        # Create another client with different billing type
        Client.objects.create(company=self.company, 
            name="Juan", last_name="Perez", dni="555", email="j@p.com", chosen_billing_type="A"
        )
        
        # Filter by billing type
        response = self.client.get(self.url, {'chosen_billing_type': 'A'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Juan")

    def test_search_clients(self):
        # Create another client
        Client.objects.create(company=self.company, 
            name="Maria", last_name="Lopez", dni="666", email="m@l.com"
        )

        # Search by name
        response = self.client.get(self.url, {'search': 'Maria'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Maria")

        # Search by dni
        response = self.client.get(self.url, {'search': '666'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Maria")

    def test_ordering_clients(self):
        # Create another client
        Client.objects.create(company=self.company, 
            name="Alberto", last_name="Alvarez", dni="777", email="a@a.com"
        )

        # Order by name ascending
        response = self.client.get(self.url, {'ordering': 'name'})
        self.assertEqual(response.data['results'][0]['name'], "Alberto")
        self.assertEqual(response.data['results'][1]['name'], "Pedro")

        # Order by name descending
        response = self.client.get(self.url, {'ordering': '-name'})
        self.assertEqual(response.data['results'][0]['name'], "Pedro")
        self.assertEqual(response.data['results'][1]['name'], "Alberto")

class CustomerAccountViewSetTestCase(TenantTestCase, APITestCase):
    def setUp(self):
        super().setUp()
        # Already have self.user from TenantTestCase # User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.client_obj = Client.objects.create(company=self.company, 
            name="Luis", last_name="Paz", dni="444", email="l@p.com"
        )
        self.account = CustomerAccount.objects.get(client=self.client_obj)

    def test_deactivate_account(self):
        url = reverse('customeraccount-deactivate', args=[self.account.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account.refresh_from_db()
        self.assertFalse(self.account.is_active)

    def test_summary(self):
        # Setup data for summary
        # Account 1 (active): limit 1000. Balance 0.
        self.account.credit_limit = Decimal('1000.00')
        self.account.save()
        
        # Account 2 (active): limit 500. Balance -200 (Debt)
        client2 = Client.objects.create(company=self.company, name="C2", last_name="L2", dni="999", email="c2@t.com")
        acc2 = client2.customer_account
        acc2.credit_limit = Decimal('500.00')
        acc2.save()
        
        CustomerBalanceRecord.objects.create(company=self.company, customer_account=acc2,
            movement_type=MovementType.DEBIT,
            amount=Decimal('200.00'),
            created_by=self.user
        )
        # acc2 balance is -200.
        
        # Account 3 (active): limit 0. Balance +100 (Credit)
        client3 = Client.objects.create(company=self.company, name="C3", last_name="L3", dni="888", email="c3@t.com")
        acc3 = client3.customer_account
        acc3.save()
        
        CustomerBalanceRecord.objects.create(company=self.company, customer_account=acc3,
            movement_type=MovementType.CREDIT,
            amount=Decimal('100.00'),
            created_by=self.user
        )
        # acc3 balance is +100.
        
        # Inactive account (should be ignored)
        client4 = Client.objects.create(company=self.company, name="C4", last_name="L4", dni="777", email="c4@t.com")
        acc4 = client4.customer_account
        acc4.active = False
        acc4.save()
        
        url = reverse('customeraccount-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Calculations:
        # Total Credit Limit: 1000 + 500 + 0 = 1500
        self.assertEqual(Decimal(response.data['credit_limit']), Decimal('1500.00'))
        
        # Current Balance: 0 + (-200) + 100 = -100
        self.assertEqual(Decimal(response.data['current_balance']), Decimal('-100.00'))
        
        # Available Credit = Total Limit + Current Balance = 1500 + (-100) = 1400.
        # Check logic: 
        # Account 1: 1000 avail.
        # Account 2: 500 limit - 200 debt = 300 avail.
        # Account 3: 0 limit + 100 credit = 100 avail.
        # Total avail: 1000 + 300 + 100 = 1400. Matches.
        self.assertEqual(Decimal(response.data['available_credit']), Decimal('1400.00'))
        
        # Total Debit: 200
        self.assertEqual(Decimal(response.data['total_debit']), Decimal('200.00'))
        
        # Total Credit: 100
        self.assertEqual(Decimal(response.data['total_credit']), Decimal('100.00'))


class CustomerBalanceRecordViewSetTestCase(TenantTestCase, APITestCase):
    def setUp(self):
        super().setUp()
        # Already have self.user from TenantTestCase # User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.client_obj = Client.objects.create(company=self.company, 
            name="Luis", last_name="Paz", dni="444", email="l@p.com"
        )
        self.account = CustomerAccount.objects.get(client=self.client_obj)
        self.url = reverse('customerbalancerecord-list')

    def test_create_record_assigns_user(self):
        data = {
            "customer_account": self.account.id,
            "amount": "100.00",
            "movement_type": MovementType.DEBIT,
            "notes": "Test creation"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        record = CustomerBalanceRecord.objects.get(id=response.data['id'])
        self.assertEqual(record.created_by, self.user)
        self.assertEqual(record.amount, Decimal('100.00'))

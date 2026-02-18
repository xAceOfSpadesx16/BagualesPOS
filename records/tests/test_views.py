from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from sales.models import Sale
from clients.models import Client

User = get_user_model()

class RecordsViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.client_obj = Client.objects.create(name="Juan", last_name="Perez", dni="123")
        self.sale = Sale.objects.create(client=self.client_obj)
        self.url = reverse('records-list')

    def test_list_records(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_record(self):
        url = reverse('records-detail', args=[self.sale.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.sale.id)

    def test_filter_records(self):
        # Create another sale that is closed
        Sale.objects.create(client=self.client_obj, closed=True)
        
        # Filter by closed
        response = self.client.get(self.url, {'closed': 'True'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['closed'])

    def test_search_records(self):
        # Create another sale with different client
        other_client = Client.objects.create(name="Maria", last_name="Lopez", dni="999", email="maria@test.com")
        Sale.objects.create(client=other_client)

        # Search by client name
        response = self.client.get(self.url, {'search': 'Maria'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['client_data']['name'], "Maria")

    def test_ordering_records(self):
        # Create another sale with higher amount
        Sale.objects.create(client=self.client_obj, total_amount=5000)

        # Order by total_amount ascending
        response = self.client.get(self.url, {'ordering': 'total_amount'})
        self.assertEqual(response.data['results'][0]['total_amount'], '0.00') # Default is 0
        self.assertEqual(response.data['results'][1]['total_amount'], '5000.00')

        # Order by total_amount descending
        response = self.client.get(self.url, {'ordering': '-total_amount'})
        self.assertEqual(response.data['results'][0]['total_amount'], '5000.00')
        self.assertEqual(response.data['results'][1]['total_amount'], '0.00')

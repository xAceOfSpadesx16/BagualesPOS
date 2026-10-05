from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from devices.models import Device, CashRegister, PriceChecker, StockTerminal
from utils.tests import TenantTestCase

User = get_user_model()

class DeviceViewSetTestCase(TenantTestCase, APITestCase):
    def setUp(self):
        super().setUp()
        # Already have self.user from TenantTestCase # User.objects.create_user(username='admin', password='password')
        self.client.force_authenticate(user=self.user)
        
        self.cr = CashRegister.objects.create(company=self.company, code='CR-01', name='Cash Register 1', is_active=True, is_online=True)
        self.pc = PriceChecker.objects.create(code='PC-01', name='Price Checker 1', is_active=True, is_online=False)
        self.st = StockTerminal.objects.create(code='ST-01', name='Stock Terminal 1', is_active=False)
        
        self.list_url = reverse('device-list')

    def test_list_polymorphic(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 3)
        
        # Verify types in list serializer
        codes = [d['code'] for d in results]
        self.assertIn('CR-01', codes)
        self.assertIn('PC-01', codes)
        self.assertIn('ST-01', codes)
        
        # Check device_type field
        for d in results:
            if d['code'] == 'CR-01':
                self.assertEqual(d['device_type'], 'CashRegister')
            elif d['code'] == 'PC-01':
                self.assertEqual(d['device_type'], 'PriceChecker')

    def test_retrieve_polymorphic(self):
        # Retrieve CashRegister
        url = reverse('device-detail', args=[self.cr.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should contain specific fields
        self.assertIn('has_open_session', response.data)
        
        # Retrieve PriceChecker
        url = reverse('device-detail', args=[self.pc.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('display_promotions', response.data)

    def test_heartbeat_action(self):
        url = reverse('device-heartbeat', args=[self.pc.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('timestamp', response.data)
        
        self.pc.refresh_from_db()
        self.assertTrue(self.pc.is_online)
        self.assertIsNotNone(self.pc.last_seen)

    def test_assign_unassign_action(self):
        # Assign
        url = reverse('device-assign', args=[self.cr.id])
        response = self.client.post(url, {'user_id': self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.cr.refresh_from_db()
        self.assertEqual(self.cr.assigned_user, self.user)
        
        # Unassign
        url = reverse('device-unassign', args=[self.cr.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.cr.refresh_from_db()
        self.assertIsNone(self.cr.assigned_user)

    def test_assign_invalid_user(self):
        url = reverse('device-assign', args=[self.cr.id])
        response = self.client.post(url, {'user_id': 9999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_filters(self):
        # Filter by specific type endpoints
        
        # Cash Registers
        url = reverse('device-cash-registers')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], 'CR-01')
        
        # Price Checkers
        url = reverse('device-price-checkers')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], 'PC-01')
        
        # Stock Terminals (ST-01 is inactive, view checks is_active=True)
        url = reverse('device-stock-terminals')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 0) # Inactive

    def test_status_filters(self):
        # Online
        url = reverse('device-online')
        response = self.client.get(url)
        # CR-01 is online and active. PC-01 is offline. ST-01 inactive.
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], 'CR-01')
        
        # Offline
        url = reverse('device-offline')
        response = self.client.get(url)
        # PC-01 is offline and active. ST-01 inactive.
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], 'PC-01')

    def test_summary(self):
        url = reverse('device-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data['total'], 3)
        self.assertEqual(data['active'], 2) # CR + PC
        self.assertEqual(data['online'], 1) # CR
        self.assertEqual(data['offline'], 1) # Active (2) - Online (1) = 1 (PC)
        
        self.assertEqual(data['by_type']['cash_registers'], 1)
        self.assertEqual(data['by_type']['price_checkers'], 1)
        self.assertEqual(data['by_type']['stock_terminals'], 1)

class DeviceViewSetCoverageTestCase(TenantTestCase, APITestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)
    
    def test_device_viewset_owner_filter(self):
        from devices.models import CashRegister
        CashRegister.objects.create(company=self.company, name="Dev1", code="DEV-1")
        self.user.owned_company = self.company
        self.user.save()
        response = self.client.get(reverse('device-list'))
        self.assertEqual(len(response.data['results']), 1)
        
        self.user.owned_company = None
        self.user.is_superuser = False
        self.user.save()
        self.user.company = None
        response2 = self.client.get(reverse('device-list'))
        self.assertEqual(len(response2.data['results']), 0)
    
    def test_device_viewset_swagger_fake_view(self):
        """Test line 39: swagger_fake_view in get_queryset"""
        from rest_framework.test import APIRequestFactory
        from devices.views import DeviceViewSet
        
        factory = APIRequestFactory()
        request = factory.get('/api/devices/')
        request.user = self.user
        
        viewset = DeviceViewSet()
        viewset.request = request
        viewset.swagger_fake_view = True  # Simulate swagger
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)
    
    def test_device_viewset_superuser_sees_all(self):
        """Test line 47: superuser sees all devices"""
        from rest_framework.test import APIRequestFactory
        from devices.views import DeviceViewSet
        from devices.models import CashRegister
        
        # Create devices
        CashRegister.objects.create(company=self.company, name="Dev1", code="DEV-1-SUPER")
        
        # Create superuser
        superuser = User.objects.create_superuser(
            username='super_devices',
            password='pass',
            email='super_devices@test.com'
        )
        
        factory = APIRequestFactory()
        request = factory.get('/api/devices/')
        request.user = superuser
        
        viewset = DeviceViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertGreaterEqual(queryset.count(), 1)
    
    def test_device_viewset_user_with_branches(self):
        """Test line 49: user with branches sees only their branch devices"""
        from rest_framework.test import APIRequestFactory
        from devices.views import DeviceViewSet
        from devices.models import CashRegister
        from core.models import Branch
        
        # Create branch and device
        branch = Branch.objects.create(company=self.company, name="DevBranch", code="DEVBR")
        CashRegister.objects.create(company=self.company, branch=branch, name="Dev1", code="DEV-1-BR")
        
        # Create user with branch
        user_with_branch = User.objects.create_user(
            username='withbranch_dev',
            password='pass',
            company=self.company
        )
        user_with_branch.branch.add(branch)
        
        factory = APIRequestFactory()
        request = factory.get('/api/devices/')
        request.user = user_with_branch
        
        viewset = DeviceViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 1)
    
    def test_device_viewset_user_no_branches_fallback(self):
        """Test lines 50-51: user with company but no branches returns company devices"""
        from rest_framework.test import APIRequestFactory
        from devices.views import DeviceViewSet
        from devices.models import CashRegister
        
        # Create device
        CashRegister.objects.create(company=self.company, name="Dev1", code="DEV-1")
        
        # Create user with company but no branches
        user_no_branch = User.objects.create_user(
            username='nobranch',
            password='pass',
            company=self.company
        )
        # Ensure user has no branches
        user_no_branch.branch.clear()
        
        factory = APIRequestFactory()
        request = factory.get('/api/devices/')
        request.user = user_no_branch
        
        viewset = DeviceViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        # Should fall back to all company devices
        self.assertEqual(queryset.count(), 1)
    
    def test_device_viewset_user_no_company_returns_none(self):
        """Test line 51 (last): user without company returns empty queryset"""
        from rest_framework.test import APIRequestFactory
        from devices.views import DeviceViewSet
        
        # Create user without company
        user_no_company = User.objects.create_user(
            username='nocompany',
            password='pass',
            company=None
        )
        
        factory = APIRequestFactory()
        request = factory.get('/api/devices/')
        request.user = user_no_company
        
        viewset = DeviceViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)

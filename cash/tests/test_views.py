from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from unittest.mock import patch
from django.core.exceptions import ValidationError as DjangoValidationError

from devices.models import CashRegister
from cash.models import CashSession, CashMovement
from cash.choices import SessionStatus, MovementType

User = get_user_model()


class CashSessionAPITestCase(APITestCase):
    """Test cases for Cash Session endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Create users
        self.user1 = User.objects.create_user(
            username='cashier1',
            password='testpass123',
            first_name='Juan',
            last_name='Pérez'
        )
        self.user2 = User.objects.create_user(
            username='cashier2',
            password='testpass123',
            first_name='María',
            last_name='González'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        # Create cash registers
        self.cash_register1 = CashRegister.objects.create(
            code='CAJA-01',
            name='Caja Principal',
            location='Mostrador 1',
            is_active=True
        )
        self.cash_register2 = CashRegister.objects.create(
            code='CAJA-02',
            name='Caja Secundaria',
            location='Mostrador 2',
            is_active=True
        )
        self.inactive_register = CashRegister.objects.create(
            code='CAJA-03',
            name='Caja Inactiva',
            location='Depósito',
            is_active=False
        )
        
        # API client
        self.client = APIClient()
    
    def authenticate(self, user):
        """Helper to authenticate a user"""
        self.client.force_authenticate(user=user)
    
    def test_list_sessions_unauthenticated(self):
        """Test that listing sessions requires authentication"""
        response = self.client.get('/api/cash/cash-sessions/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_sessions_empty(self):
        """Test listing sessions when there are none"""
        self.authenticate(self.user1)
        response = self.client.get('/api/cash/cash-sessions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results'] if 'results' in response.data else response.data), 0)
    
    def test_open_session_success(self):
        """Test opening a new cash session successfully"""
        self.authenticate(self.user1)
        
        data = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '1000.00'
        }
        
        response = self.client.post('/api/cash/cash-sessions/open/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], SessionStatus.OPEN)
        self.assertEqual(response.data['user'], self.user1.id)
        self.assertEqual(response.data['cash_register'], self.cash_register1.id)
        self.assertEqual(Decimal(response.data['opening_balance']), Decimal('1000.00'))
        self.assertIsNotNone(response.data['opening_date'])
        self.assertIsNone(response.data['closing_date'])
        
        # Verify opening movement was created
        session = CashSession.objects.get(id=response.data['id'])
        opening_movement = session.movements.filter(type=MovementType.OPENING).first()
        self.assertIsNotNone(opening_movement)
        self.assertEqual(opening_movement.amount, Decimal('1000.00'))
    
    def test_open_session_inactive_register(self):
        """Test that opening session on inactive register fails"""
        self.authenticate(self.user1)
        
        data = {
            'cash_register': self.inactive_register.id,
            'opening_balance': '1000.00'
        }
        
        response = self.client.post('/api/cash/cash-sessions/open/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_open_session_negative_balance(self):
        """Test that negative opening balance is rejected"""
        self.authenticate(self.user1)
        
        data = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '-100.00'
        }
        
        response = self.client.post('/api/cash/cash-sessions/open/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_open_session_user_already_has_open_session(self):
        """Test that user cannot open two sessions simultaneously"""
        self.authenticate(self.user1)
        
        # Open first session
        data1 = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '1000.00'
        }
        response1 = self.client.post('/api/cash/cash-sessions/open/', data1)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Try to open second session
        data2 = {
            'cash_register': self.cash_register2.id,
            'opening_balance': '500.00'
        }
        response2 = self.client.post('/api/cash/cash-sessions/open/', data2)
        
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_open_session_register_already_has_open_session(self):
        """Test that register cannot have two open sessions"""
        # User1 opens session
        self.authenticate(self.user1)
        data1 = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '1000.00'
        }
        response1 = self.client.post('/api/cash/cash-sessions/open/', data1)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # User2 tries to open session on same register
        self.authenticate(self.user2)
        data2 = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '500.00'
        }
        response2 = self.client.post('/api/cash/cash-sessions/open/', data2)
        
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_close_session_success(self):
        """Test closing a cash session successfully"""
        self.authenticate(self.user1)
        
        # Open session first
        data_open = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '1000.00'
        }
        response_open = self.client.post('/api/cash/cash-sessions/open/', data_open)
        session_id = response_open.data['id']
        
        # Close session
        data_close = {
            'closing_balance': '5500.00',
            'notes': 'Cierre normal'
        }
        response_close = self.client.post(
            f'/api/cash/cash-sessions/{session_id}/close/',
            data_close
        )
        
        self.assertEqual(response_close.status_code, status.HTTP_200_OK)
        self.assertEqual(response_close.data['status'], SessionStatus.CLOSED)
        self.assertEqual(Decimal(response_close.data['closing_balance']), Decimal('5500.00'))
        self.assertIsNotNone(response_close.data['closing_date'])
        self.assertEqual(response_close.data['notes'], 'Cierre normal')
        
        # Verify closing movement was created
        session = CashSession.objects.get(id=session_id)
        closing_movement = session.movements.filter(type=MovementType.CLOSING).first()
        self.assertIsNotNone(closing_movement)
        self.assertEqual(closing_movement.amount, Decimal('5500.00'))
    
    def test_close_session_already_closed(self):
        """Test that closing an already closed session fails"""
        self.authenticate(self.user1)
        
        # Open and close session
        data_open = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '1000.00'
        }
        response_open = self.client.post('/api/cash/cash-sessions/open/', data_open)
        session_id = response_open.data['id']
        
        data_close = {
            'closing_balance': '5500.00'
        }
        self.client.post(f'/api/cash/cash-sessions/{session_id}/close/', data_close)
        
        # Try to close again
        response_close2 = self.client.post(
            f'/api/cash/cash-sessions/{session_id}/close/',
            data_close
        )
        
        self.assertEqual(response_close2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response_close2.data)
    
    def test_close_session_not_owner(self):
        """Test that only session owner can close session (non-admin)"""
        self.authenticate(self.user1)
        
        # User1 opens session
        data_open = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '1000.00'
        }
        response_open = self.client.post('/api/cash/cash-sessions/open/', data_open)
        session_id = response_open.data['id']
        
        # User2 tries to close
        self.authenticate(self.user2)
        data_close = {
            'closing_balance': '5500.00'
        }
        response_close = self.client.post(
            f'/api/cash/cash-sessions/{session_id}/close/',
            data_close
        )
        
        self.assertEqual(response_close.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_close_session_admin_can_close(self):
        """Test that admin can close any session"""
        self.authenticate(self.user1)
        
        # User1 opens session
        data_open = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '1000.00'
        }
        response_open = self.client.post('/api/cash/cash-sessions/open/', data_open)
        session_id = response_open.data['id']
        
        # Admin closes
        self.authenticate(self.admin)
        data_close = {
            'closing_balance': '5500.00',
            'notes': 'Cierre administrativo'
        }
        response_close = self.client.post(
            f'/api/cash/cash-sessions/{session_id}/close/',
            data_close
        )
        
        self.assertEqual(response_close.status_code, status.HTTP_200_OK)
    
    def test_close_session_negative_balance(self):
        """Test that negative closing balance is rejected"""
        self.authenticate(self.user1)
        
        # Open session
        data_open = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '1000.00'
        }
        response_open = self.client.post('/api/cash/cash-sessions/open/', data_open)
        session_id = response_open.data['id']
        
        # Try to close with negative balance
        data_close = {
            'closing_balance': '-100.00'
        }
        response_close = self.client.post(
            f'/api/cash/cash-sessions/{session_id}/close/',
            data_close
        )
        
        self.assertEqual(response_close.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_my_active_session_exists(self):
        """Test getting current user's active session"""
        self.authenticate(self.user1)
        
        # Open session
        data_open = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '1000.00'
        }
        self.client.post('/api/cash/cash-sessions/open/', data_open)
        
        # Get active session
        response = self.client.get('/api/cash/cash-sessions/my_active/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user1.id)
        self.assertEqual(response.data['status'], SessionStatus.OPEN)
    
    def test_my_active_session_not_exists(self):
        """Test getting active session when user has none"""
        self.authenticate(self.user1)
        
        response = self.client.get('/api/cash/cash-sessions/my_active/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_session_sales_endpoint(self):
        """Test getting sales for a session"""
        self.authenticate(self.user1)
        
        # Open session
        data_open = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '1000.00'
        }
        response_open = self.client.post('/api/cash/cash-sessions/open/', data_open)
        session_id = response_open.data['id']
        
        # Get sales
        response = self.client.get(f'/api/cash/cash-sessions/{session_id}/sales/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_session_movements_endpoint(self):
        """Test getting movements for a session"""
        self.authenticate(self.user1)
        
        # Open session
        data_open = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '1000.00'
        }
        response_open = self.client.post('/api/cash/cash-sessions/open/', data_open)
        session_id = response_open.data['id']
        
        # Get movements
        response = self.client.get(f'/api/cash/cash-sessions/{session_id}/movements/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        # Should have at least opening movement
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_session_summary_endpoint(self):
        """Test getting summary for a session"""
        self.authenticate(self.user1)
        
        # Open session
        data_open = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '1000.00'
        }
        response_open = self.client.post('/api/cash/cash-sessions/open/', data_open)
        session_id = response_open.data['id']
        
        # Get summary
        response = self.client.get(f'/api/cash/cash-sessions/{session_id}/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('session', response.data)
        self.assertIn('totals', response.data)
        
        totals = response.data['totals']
        self.assertIn('opening_balance', totals)
        self.assertIn('cash_sales', totals)
        self.assertIn('expected_balance', totals)
        self.assertIn('difference', totals)
    
    def test_list_sessions_with_filters(self):
        """Test filtering sessions by status and user"""
        self.authenticate(self.user1)
        
        # Create open session for user1
        data1 = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '1000.00'
        }
        self.client.post('/api/cash/cash-sessions/open/', data1)
        
        # Create and close session for user2
        self.authenticate(self.user2)
        data2 = {
            'cash_register': self.cash_register2.id,
            'opening_balance': '500.00'
        }
        response2 = self.client.post('/api/cash/cash-sessions/open/', data2)
        session2_id = response2.data['id']
        
        self.client.post(
            f'/api/cash/cash-sessions/{session2_id}/close/',
            {'closing_balance': '1000.00'}
        )
        
        # Filter by status OPEN
        self.authenticate(self.admin)
        response = self.client.get('/api/cash/cash-sessions/?status=OPEN')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], SessionStatus.OPEN)
        
        # Filter by user
        response_user = self.client.get(f'/api/cash/cash-sessions/?user={self.user2.id}')
        results_user = response_user.data['results'] if 'results' in response_user.data else response_user.data
        self.assertEqual(len(results_user), 1)
        self.assertEqual(results_user[0]['user'], self.user2.id)
    
    def test_retrieve_session_detail(self):
        """Test retrieving session detail uses full serializer"""
        self.authenticate(self.user1)
        
        # Open session
        data_open = {
            'cash_register': self.cash_register1.id,
            'opening_balance': '1000.00'
        }
        response_open = self.client.post('/api/cash/cash-sessions/open/', data_open)
        session_id = response_open.data['id']
        
        # Retrieve detail
        response = self.client.get(f'/api/cash/cash-sessions/{session_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Full serializer includes nested data
        self.assertIn('cash_register_data', response.data)
        self.assertIn('user_data', response.data)
        self.assertIn('total_cash_sales', response.data)
        self.assertIn('expected_balance', response.data)


class CashMovementAPITestCase(APITestCase):
    """Test cases for Cash Movement endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='cashier',
            password='testpass123',
            first_name='Juan',
            last_name='Pérez'
        )
        
        self.cash_register = CashRegister.objects.create(
            code='CAJA-01',
            name='Caja Principal',
            location='Mostrador 1',
            is_active=True
        )
        
        # Create open session
        self.open_session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        # Create opening movement
        CashMovement.objects.create(
            cash_session=self.open_session,
            type=MovementType.OPENING,
            amount=Decimal('1000.00'),
            reason='Opening balance',
            created_by=self.user
        )
        
        # Create closed session
        self.closed_session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('500.00'),
            closing_balance=Decimal('1500.00'),
            status=SessionStatus.CLOSED,
            opening_date=timezone.now() - timezone.timedelta(days=1),
            closing_date=timezone.now() - timezone.timedelta(hours=12)
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_movement_cash_in_success(self):
        """Test creating cash in movement successfully"""
        data = {
            'cash_session': self.open_session.id,
            'type': MovementType.CASH_IN,
            'amount': '500.00',
            'reason': 'Cambio adicional',
            'description': 'Cambio para turno'
        }
        
        response = self.client.post('/api/cash/cash-movements/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['type'], MovementType.CASH_IN)
        self.assertEqual(Decimal(response.data['amount']), Decimal('500.00'))
        self.assertEqual(response.data['reason'], 'Cambio adicional')
        self.assertEqual(response.data['created_by'], self.user.id)
        self.assertIsNotNone(response.data['created_at'])
    
    def test_create_movement_cash_out_success(self):
        """Test creating cash out movement successfully"""
        data = {
            'cash_session': self.open_session.id,
            'type': MovementType.CASH_OUT,
            'amount': '100.00',
            'reason': 'Gastos varios',
            'description': 'Compra de suministros'
        }
        
        response = self.client.post('/api/cash/cash-movements/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['type'], MovementType.CASH_OUT)
    
    def test_create_movement_on_closed_session_fails(self):
        """Test that creating movement on closed session fails"""
        data = {
            'cash_session': self.closed_session.id,
            'type': MovementType.CASH_IN,
            'amount': '500.00',
            'reason': 'Test'
        }
        
        response = self.client.post('/api/cash/cash-movements/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_movements(self):
        """Test listing cash movements"""
        # Create additional movements
        CashMovement.objects.create(
            cash_session=self.open_session,
            type=MovementType.CASH_IN,
            amount=Decimal('200.00'),
            reason='Test',
            created_by=self.user
        )
        
        response = self.client.get('/api/cash/cash-movements/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertGreaterEqual(len(results), 2)
    
    def test_filter_movements_by_session(self):
        """Test filtering movements by session"""
        response = self.client.get(
            f'/api/cash/cash-movements/?cash_session={self.open_session.id}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if 'results' in response.data else response.data
        for movement in results:
            self.assertEqual(movement['cash_session'], self.open_session.id)
    
    def test_filter_movements_by_type(self):
        """Test filtering movements by type"""
        # Create different types
        CashMovement.objects.create(
            cash_session=self.open_session,
            type=MovementType.CASH_IN,
            amount=Decimal('200.00'),
            reason='Test in',
            created_by=self.user
        )
        CashMovement.objects.create(
            cash_session=self.open_session,
            type=MovementType.CASH_OUT,
            amount=Decimal('50.00'),
            reason='Test out',
            created_by=self.user
        )
        
        response = self.client.get('/api/cash/cash-movements/?type=CASH_IN')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if 'results' in response.data else response.data
        for movement in results:
            self.assertEqual(movement['type'], MovementType.CASH_IN)
    
    def test_movement_includes_display_name(self):
        """Test that movement response includes type_display"""
        data = {
            'cash_session': self.open_session.id,
            'type': MovementType.CASH_IN,
            'amount': '500.00',
            'reason': 'Test'
        }
        
        response = self.client.post('/api/cash/cash-movements/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('type_display', response.data)
        self.assertIn('created_by_name', response.data)
    
    def test_movement_unauthenticated(self):
        """Test that creating movement requires authentication"""
        self.client.force_authenticate(user=None)
        
        data = {
            'cash_session': self.open_session.id,
            'type': MovementType.CASH_IN,
            'amount': '500.00',
            'reason': 'Test'
        }
        
        response = self.client.post('/api/cash/cash-movements/', data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ViewEdgeCasesTestCase(APITestCase):
    """Tests for view edge cases to achieve 100% coverage"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='edgetest',
            password='test',
            first_name='Edge',
            last_name='Test'
        )
        self.cash_register = CashRegister.objects.create(
            code='EDGE-01',
            name='Edge Test Register',
            is_active=True
        )
        self.client.force_authenticate(user=self.user)
        
    def test_get_serializer_class_for_list(self):
        """Test get_serializer_class returns list serializer"""
        # Create a session
        session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        # List sessions (should use CashSessionListSerializer)
        response = self.client.get('/api/cash/cash-sessions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Response should have simplified fields from list serializer
        results = response.data['results'] if 'results' in response.data else response.data
        if len(results) > 0:
            # List serializer has cash_register_name, not cash_register_data
            self.assertIn('cash_register_name', results[0])
            
    def test_cash_movement_perform_create_validation(self):
        """Test CashMovementViewSet perform_create validation"""
        # Create closed session
        closed_session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            closing_balance=Decimal('1500.00'),
            status=SessionStatus.CLOSED,
            closing_date=timezone.now()
        )
        
        # Try to create movement on closed session via API
        data = {
            'cash_session': closed_session.id,
            'type': MovementType.CASH_IN,
            'amount': '100.00',
            'reason': 'Test'
        }
        
        response = self.client.post('/api/cash/cash-movements/', data)
        
        # Should fail with validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cash_session', response.data)

    def test_cash_register_list(self):
        """Test listing cash registers"""
        
        response = self.client.get('/api/cash/cash-registers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response might be paginated or a list
        if isinstance(response.data, dict):
            # Paginated response
            self.assertIn('results', response.data)
            self.assertGreaterEqual(len(response.data['results']), 1)
        else:
            # List response
            self.assertGreaterEqual(len(response.data), 1)
    
    def test_cash_register_retrieve(self):
        """Test retrieving cash register detail"""
        
        response = self.client.get(f'/api/cash/cash-registers/{self.cash_register.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Edge Test Register')
    
    def test_cash_register_current_session_none(self):
        """Test current_session endpoint when no session exists"""
        
        response = self.client.get(
            f'/api/cash/cash-registers/{self.cash_register.id}/current_session/'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('No open session', response.data['detail'])
    
    def test_cash_register_current_session_exists(self):
        """Test current_session endpoint when session exists"""
        
        # Create an open session
        session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        response = self.client.get(
            f'/api/cash/cash-registers/{self.cash_register.id}/current_session/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], session.id)

    def test_close_session_validation_error_handling(self):
         """Test close session with validation error"""
         
         session = CashSession.objects.create(
             cash_register=self.cash_register,
             user=self.user,
             opening_balance=Decimal('1000.00'),
             status=SessionStatus.OPEN
         )
         
         with patch.object(CashSession, 'full_clean') as mock_clean:
             mock_clean.side_effect = DjangoValidationError({
                 'closing_balance': ['Invalid value']
             })
             
             response = self.client.post(
                 f'/api/cash/cash-sessions/{session.id}/close/',
                 {'closing_balance': '1500.00', 'notes': 'Test'},
                 format='json'
             )
             
             self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
             self.assertIn('error', response.data)

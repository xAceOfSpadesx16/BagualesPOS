from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from devices.models import CashRegister
from cash.choices import SessionStatus, MovementType

User = get_user_model()


class CashIntegrationTestCase(APITestCase):
    """Integration tests for complete cash workflows"""
    
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
            is_active=True
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_complete_session_workflow(self):
        """Test complete workflow: open -> movements -> close"""
        # 1. Open session
        response_open = self.client.post('/api/cash/cash-sessions/open/', {
            'cash_register': self.cash_register.id,
            'opening_balance': '1000.00'
        })
        
        self.assertEqual(response_open.status_code, status.HTTP_201_CREATED)
        session_id = response_open.data['id']
        
        # 2. Add cash in movement
        response_in = self.client.post('/api/cash/cash-movements/', {
            'cash_session': session_id,
            'type': MovementType.CASH_IN,
            'amount': '500.00',
            'reason': 'Cambio adicional'
        })
        
        self.assertEqual(response_in.status_code, status.HTTP_201_CREATED)
        
        # 3. Add cash out movement
        response_out = self.client.post('/api/cash/cash-movements/', {
            'cash_session': session_id,
            'type': MovementType.CASH_OUT,
            'amount': '100.00',
            'reason': 'Compra suministros'
        })
        
        self.assertEqual(response_out.status_code, status.HTTP_201_CREATED)
        
        # 4. Check summary
        response_summary = self.client.get(f'/api/cash/cash-sessions/{session_id}/summary/')
        
        self.assertEqual(response_summary.status_code, status.HTTP_200_OK)
        totals = response_summary.data['totals']
        
        # Expected: 1000 (opening) + 500 (in) - 100 (out) = 1400
        self.assertEqual(Decimal(totals['opening_balance']), Decimal('1000.00'))
        self.assertEqual(Decimal(totals['cash_in']), Decimal('500.00'))
        self.assertEqual(Decimal(totals['cash_out']), Decimal('100.00'))
        self.assertEqual(Decimal(totals['expected_balance']), Decimal('1400.00'))
        
        # 5. Close session
        response_close = self.client.post(f'/api/cash/cash-sessions/{session_id}/close/', {
            'closing_balance': '1450.00',
            'notes': 'Cierre de turno'
        })
        
        self.assertEqual(response_close.status_code, status.HTTP_200_OK)
        self.assertEqual(response_close.data['status'], SessionStatus.CLOSED)
        
        # Difference should be 1450 - 1400 = 50
        self.assertEqual(Decimal(response_close.data['difference']), Decimal('50.00'))
    
    def test_cannot_open_two_sessions_same_time(self):
        """Test that user cannot have multiple open sessions"""
        # Open first session
        response1 = self.client.post('/api/cash/cash-sessions/open/', {
            'cash_register': self.cash_register.id,
            'opening_balance': '1000.00'
        })
        
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Try to open another
        cash_register2 = CashRegister.objects.create(
            code='CAJA-02',
            name='Caja 2',
            is_active=True
        )
        
        response2 = self.client.post('/api/cash/cash-sessions/open/', {
            'cash_register': cash_register2.id,
            'opening_balance': '500.00'
        })
        
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

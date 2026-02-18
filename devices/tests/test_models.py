from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from devices.models import Device, CashRegister, PriceChecker, StockTerminal, DeviceConfig

User = get_user_model()

class DeviceModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.device = Device.objects.create(
            code='DEV-001',
            name='Generic Device',
            location='Main Hall'
        )

    def test_str(self):
        self.assertEqual(str(self.device), 'Generic Device (DEV-001)')

    def test_heartbeat(self):
        self.assertFalse(self.device.is_online)
        self.assertIsNone(self.device.last_seen)
        
        self.device.heartbeat()
        
        self.assertTrue(self.device.is_online)
        self.assertIsNotNone(self.device.last_seen)
        # Check if last_seen is recent
        self.assertTrue((timezone.now() - self.device.last_seen).seconds < 5)

    def test_assign_unassign_user(self):
        self.assertIsNone(self.device.assigned_user)
        self.assertIsNone(self.device.assigned_date)
        
        self.device.assign_to_user(self.user)
        self.assertEqual(self.device.assigned_user, self.user)
        self.assertIsNotNone(self.device.assigned_date)
        
        self.device.unassign_user()
        self.assertIsNone(self.device.assigned_user)
        self.assertIsNone(self.device.assigned_date)

    def test_config_methods(self):
        # Determine default
        self.assertIsNone(self.device.get_config('theme'))
        self.assertEqual(self.device.get_config('theme', 'dark'), 'dark')
        
        # Set config
        config = self.device.set_config('theme', 'light')
        self.assertEqual(config.key, 'theme')
        self.assertEqual(config.value, 'light')
        
        # Get config
        self.assertEqual(self.device.get_config('theme'), 'light')
        
        # Update config
        self.device.set_config('theme', 'blue')
        self.assertEqual(self.device.get_config('theme'), 'blue')
        self.assertEqual(DeviceConfig.objects.count(), 1)

    def test_mac_address_validation(self):
        # Valid MAC
        self.device.mac_address = '00:1A:2B:3C:4D:5E'
        self.device.full_clean()
        
        # Invalid MAC
        self.device.mac_address = 'INVALID-MAC'
        with self.assertRaises(ValidationError) as cm:
            self.device.full_clean()
        self.assertIn('mac_address', cm.exception.message_dict)

    def test_config_str_and_choices(self):
        from devices.choices import DeviceType, DeviceStatus
        
        # Test choices
        self.assertTrue(hasattr(DeviceType, 'CASH_REGISTER'))
        self.assertTrue(hasattr(DeviceStatus, 'ONLINE'))
        
        # Test __str__
        config = self.device.set_config('theme', 'dark')
        self.assertIn('DEV-001', str(config))
        self.assertIn('theme', str(config))
        self.assertIn('dark', str(config))


class PolymorphicDeviceTestCase(TestCase):
    def test_polymorphism(self):
        CashRegister.objects.create(code='CR-01', name='Cash Register 1')
        PriceChecker.objects.create(code='PC-01', name='Price Checker 1')
        StockTerminal.objects.create(code='ST-01', name='Stock Terminal 1')
        
        devices = Device.objects.all().order_by('code')
        self.assertEqual(devices.count(), 3 if 'Generic Device' not in [d.name for d in devices] else 4) 
        # Note: generic device from other test not here unless persistent DB, checks run in transaction rollback
        
        # Check types
        cr = Device.objects.get(code='CR-01')
        self.assertIsInstance(cr, CashRegister)
        
        pc = Device.objects.get(code='PC-01')
        self.assertIsInstance(pc, PriceChecker)
        
        st = Device.objects.get(code='ST-01')
        self.assertIsInstance(st, StockTerminal)


class CashRegisterTestCase(TestCase):
    def setUp(self):
        self.register = CashRegister.objects.create(
            code='CR-TEST',
            name='Test Register'
        )

    def test_current_session_property(self):
        # Need to mock CashSession or import it
        # Since we are in devices app tests, we can import from cash.models if installed
        # But to avoid cross-app dependency issues if testing in isolation? 
        # Django tests allow cross-app imports.
        pass 
        # Will implement if needed or mock. 
        # Actually, let's try to import.
        
    # NOTE: To test current_session and has_open_session, 
    # we need CashSession model. Assuming it's available.
    def test_session_properties(self):
        from cash.models import CashSession
        from cash.choices import SessionStatus
        
        self.assertIsNone(self.register.current_session)
        self.assertFalse(self.register.has_open_session)
        
        # Open session
        user = User.objects.create_user(username='cashier', password='pwd')
        session = CashSession.objects.create(
            cash_register=self.register,
            user=user,
            opening_balance=100,
            status=SessionStatus.OPEN
        )
        
        self.assertTrue(self.register.has_open_session)
        self.assertEqual(self.register.current_session, session)
        
        # Close session
        session.status = SessionStatus.CLOSED
        session.save()
        
        self.assertFalse(self.register.has_open_session)
        self.assertIsNone(self.register.current_session)


class PriceCheckerTestCase(TestCase):
    def test_defaults(self):
        pc = PriceChecker.objects.create(code='PC-TEST', name='Test PC')
        self.assertTrue(pc.display_promotions)
        self.assertEqual(pc.timeout_seconds, 30)


class StockTerminalTestCase(TestCase):
    def test_defaults(self):
        st = StockTerminal.objects.create(code='ST-TEST', name='Test ST')
        self.assertTrue(st.can_receive_shipments)
        self.assertFalse(st.require_photo)

from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from devices.admin import DeviceParentAdmin, CashRegisterAdmin, PriceCheckerAdmin, StockTerminalAdmin, DeviceConfigAdmin
from devices.models import Device, CashRegister, PriceChecker, StockTerminal, DeviceConfig

class MockSuperUser:
    def has_perm(self, perm, obj=None):
        return True

class HelperAdminSite(AdminSite):
    pass

class DeviceAdminTestCase(TestCase):
    def setUp(self):
        self.site = HelperAdminSite()
        self.factory = RequestFactory()
        self.user = MockSuperUser()

    def test_device_parent_admin(self):
        admin = DeviceParentAdmin(Device, self.site)
        cr = CashRegister.objects.create(code='CR-01', name='Cash Register')
        
        self.assertEqual(admin.get_device_type(cr), 'CashRegister')

    def test_cash_register_admin(self):
        admin = CashRegisterAdmin(CashRegister, self.site)
        cr = CashRegister.objects.create(code='CR-01', name='Cash Register')
        
        # Test has_open_session method
        self.assertFalse(admin.has_open_session(cr))

    def test_price_checker_admin(self):
        admin = PriceCheckerAdmin(PriceChecker, self.site)
        # Just ensure instantiation works
        self.assertTrue(admin.show_in_index)

    def test_stock_terminal_admin(self):
        admin = StockTerminalAdmin(StockTerminal, self.site)
        self.assertTrue(admin.show_in_index)

    def test_device_config_admin(self):
        admin = DeviceConfigAdmin(DeviceConfig, self.site)
        # Just ensure instantiation works
        self.assertTrue(admin.list_display)

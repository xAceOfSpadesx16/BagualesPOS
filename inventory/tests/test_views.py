from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from inventory.models import Inventory
from products.models import Product, Category, Brand, Season, Color, Gender
from utils.tests import TenantTestCase, create_test_branch

User = get_user_model()

class InventoryViewSetTestCase(TenantTestCase, APITestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)
        self.branch = create_test_branch(company=self.company)
        self.category = Category.objects.create(company=self.company, name="Cat")
        self.brand = Brand.objects.create(company=self.company, name="Brand")
        self.season = Season.objects.create(name="Season")
        self.color = Color.objects.create(name="Color", code="#000000")
        self.gender = Gender.objects.create(name="Unisex")
        self.product = Product.objects.create(
            company=self.company,
            name="Prod", category=self.category, brand=self.brand, season=self.season,
            color=self.color, gender=self.gender, sale_price=100, cost_price=50
        )
        self.inventory = Inventory.objects.get(product=self.product)
        self.url = reverse('inventory-list')

    def test_list_inventory(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_inventory_with_branch_filter(self):
        response = self.client.get(self.url, {'branch': self.branch.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_inventory_user_branch_filter(self):
        self.user.branch.add(self.branch)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_update_quantity_addition(self):
        url = reverse('inventory-update-quantity', args=[self.inventory.id])
        data = {"operation": "addition", "quantity": 10}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 10)

    def test_update_quantity_subtraction(self):
        self.inventory.quantity = 20
        self.inventory.save()
        
        url = reverse('inventory-update-quantity', args=[self.inventory.id])
        data = {"operation": "subtraction", "quantity": 5}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 15)

    def test_search_inventory(self):
        other_product = Product.objects.create(
            company=self.company,
            name="Zapatillas", category=self.category, brand=self.brand, season=self.season,
            color=self.color, gender=self.gender, sale_price=200, cost_price=100,
            internal_code="ZAP123"
        )
        
        response = self.client.get(self.url, {'search': 'Zapatillas'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['product']['name'], "Zapatillas")

        response = self.client.get(self.url, {'search': 'ZAP123'})
        self.assertEqual(len(response.data['results']), 1)

    def test_ordering_inventory(self):
        self.inventory.quantity = 100
        self.inventory.save()
        
        other_product = Product.objects.create(
            company=self.company,
            name="AAA Product", category=self.category, brand=self.brand, season=self.season,
            color=self.color, gender=self.gender, sale_price=200, cost_price=100
        )
        inv2 = Inventory.objects.get(product=other_product)
        inv2.quantity = 0
        inv2.save()
            
        self.assertLess(self.inventory.id, inv2.id)
        
        response = self.client.get(self.url, {'ordering': 'quantity'})
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['quantity'], 0)
        self.assertEqual(response.data['results'][1]['quantity'], 100)
        
        response = self.client.get(self.url, {'ordering': 'product__name'})
        self.assertEqual(response.data['results'][0]['product']['name'], "AAA Product")
        self.assertEqual(response.data['results'][1]['product']['name'], "Prod")

    def test_update_quantity_errors(self):
        url = reverse('inventory-update-quantity', args=[self.inventory.id])
        
        data = {"operation": "addition", "quantity": -5}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid quantity')

        data = {"operation": "addition", "quantity": 0}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {"operation": "multiply", "quantity": 10}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid operation')

    def test_low_stock(self):
        url = reverse('inventory-low-stock')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.product.name)

        self.inventory.quantity = 10
        self.inventory.save()
        
        response = self.client.get(url)
        self.assertEqual(len(response.data), 0)

        response = self.client.get(url, {'threshold': 15})
        self.assertEqual(len(response.data), 1)

    def test_other_branches_availability(self):
        """Test getting availability across other branches excluding the ones of the user."""
        
        # Create a second branch
        from core.models import Branch
        branch2 = Branch.objects.create(company=self.company, name="Branch 2", code="BR2")
        
        # Branch 2 should automatically have 0-stock inventory for self.product per our previous signals
        inv2 = Inventory.objects.get(product=self.product, branch=branch2)
        inv2.quantity = 15
        inv2.save()
        
        url = reverse('inventory-other-branches', args=[self.inventory.id])
        
        # Scenario 1: User belongs to Branch 1
        self.user.branch.add(self.branch)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return Branch 2's inventory but NOT Branch 1's
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['branch'], branch2.id)
        self.assertEqual(response.data[0]['quantity'], 15)
        
        # Scenario 2: User has NO branch assigned
        self.user.branch.clear()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should exclude the branch of the item being queried (Branch 1)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['branch'], branch2.id)
        self.assertEqual(response.data[0]['quantity'], 15)

    def test_stock_breakdown(self):
        url = reverse('inventory-stock-breakdown')
        
        # Test non-admin access (Forbidden)
        non_admin = User.objects.create_user(username='nonadmin', password='password', company=self.company)
        self.client.force_authenticate(user=non_admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test admin access
        self.user.owned_company = self.company
        self.user.save()
        self.client.force_authenticate(user=self.user)
        
        # Set stock
        self.inventory.quantity = 50
        self.inventory.save()
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(response.data[0]['product_id'], self.product.id)
        self.assertEqual(response.data[0]['total_stock'], 50)
        
        # Test product filter
        response = self.client.get(url, {'product': self.product.id})
        self.assertEqual(len(response.data), 1)
        
        # Test branch filter
        response = self.client.get(url, {'branch': self.branch.id})
        self.assertEqual(len(response.data), 1)
        
        # Test low stock threshold
        response = self.client.get(url, {'low_stock': 100})
        self.assertEqual(len(response.data), 1)
        
        response = self.client.get(url, {'low_stock': 10})
        self.assertEqual(len(response.data), 0)


class StockAdjustmentRequestTestCase(TenantTestCase, APITestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)
        self.branch = create_test_branch(company=self.company)
        self.user.branch.add(self.branch)
        from products.models import Product, Category, Brand, Season, Color, Gender
        self.category = Category.objects.create(company=self.company, name="Cat")
        self.brand = Brand.objects.create(company=self.company, name="Brand")
        self.season = Season.objects.create(name="Season")
        self.color = Color.objects.create(name="Color", code="#000000")
        self.gender = Gender.objects.create(name="Unisex")
        self.product = Product.objects.create(
            company=self.company,
            name="Prod", category=self.category, brand=self.brand, season=self.season,
            color=self.color, gender=self.gender, sale_price=100, cost_price=50
        )
        self.inventory = Inventory.objects.get(product=self.product)
        self.inventory.quantity = 100
        self.inventory.save()
        self.url = reverse('stockadjustmentrequest-list')

    def test_perform_create_success(self):
        data = {
            "product": self.product.id,
            "adjustment_type": "REDUCTION",
            "quantity": 10,
            "reason": "Test"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['status'], 'PENDING')
        self.assertEqual(response.data['branch'], self.branch.id)

    def test_perform_create_no_branch(self):
        self.user.branch.clear()
        data = {
            "product": self.product.id,
            "adjustment_type": "REDUCTION",
            "quantity": 10,
            "reason": "Test"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_queryset(self):
        data = {
            "product": self.product.id,
            "adjustment_type": "REDUCTION",
            "quantity": 10,
            "reason": "Test"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test branch manager sees only their branch
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['results']), 1)
        
        # Superuser
        self.user.is_superuser = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['results']), 1)

    def test_approve_adjustment(self):
        # Create
        data = {"product": self.product.id, "adjustment_type": "REDUCTION", "quantity": 10, "reason": "T"}
        resp = self.client.post(self.url, data)
        adj_id = resp.data['id']
        
        # Approve as non-admin should fail
        non_admin = User.objects.create_user(username='nonadmin_app', password='password', company=self.company)
        self.client.force_authenticate(user=non_admin)
        url_approve = reverse('stockadjustmentrequest-approve', args=[adj_id])
        resp2 = self.client.post(url_approve)
        self.assertEqual(resp2.status_code, status.HTTP_403_FORBIDDEN)
        
        # Approve as admin should succeed
        self.user.owned_company = self.company
        self.user.save()
        self.client.force_authenticate(user=self.user)
        
        resp3 = self.client.post(url_approve)
        self.assertEqual(resp3.status_code, status.HTTP_200_OK)
        
        # Verify inventory
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 90)

    def test_approve_insufficient_stock(self):
        data = {"product": self.product.id, "adjustment_type": "REDUCTION", "quantity": 1000, "reason": "T"}
        resp = self.client.post(self.url, data)
        
        self.user.owned_company = self.company
        self.user.save()
        self.client.force_authenticate(user=self.user)
        
        url_approve = reverse('stockadjustmentrequest-approve', args=[resp.data['id']])
        resp2 = self.client.post(url_approve)
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_add_correct(self):
        # Add test for ADDITION and CORRECTION 
        self.user.owned_company = self.company
        self.user.save()
        
        # ADDITION
        data1 = {"product": self.product.id, "adjustment_type": "ADDITION", "quantity": 10, "reason": "T"}
        r1 = self.client.post(self.url, data1)
        self.client.post(reverse('stockadjustmentrequest-approve', args=[r1.data['id']]))
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 110)
        
        # CORRECTION
        data2 = {"product": self.product.id, "adjustment_type": "CORRECTION", "quantity": 50, "reason": "T"}
        r2 = self.client.post(self.url, data2)
        self.client.post(reverse('stockadjustmentrequest-approve', args=[r2.data['id']]))
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 50)

    def test_reject_adjustment(self):
        data = {"product": self.product.id, "adjustment_type": "REDUCTION", "quantity": 10, "reason": "T"}
        resp = self.client.post(self.url, data)
        adj_id = resp.data['id']
        url_reject = reverse('stockadjustmentrequest-reject', args=[adj_id])
        
        # Non-admin reject failure
        non_admin = User.objects.create_user(username='nonadmin_rej', password='password', company=self.company)
        self.client.force_authenticate(user=non_admin)
        resp_f = self.client.post(url_reject)
        self.assertEqual(resp_f.status_code, status.HTTP_403_FORBIDDEN)
        
        self.user.owned_company = self.company
        self.user.save()
        self.client.force_authenticate(user=self.user)
        
        resp2 = self.client.post(url_reject, {"rejection_note": "No"})
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp2.data['status'], 'REJECTED')
        
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 100) # unchanged

    def test_approve_reject_invalid_states(self):
        data = {"product": self.product.id, "adjustment_type": "REDUCTION", "quantity": 10, "reason": "T"}
        resp = self.client.post(self.url, data)
        adj_id = resp.data['id']
        url_approve = reverse('stockadjustmentrequest-approve', args=[adj_id])
        url_reject = reverse('stockadjustmentrequest-reject', args=[adj_id])
        
        self.user.owned_company = self.company
        self.user.save()
        self.client.force_authenticate(user=self.user)
        
        # Approve
        self.client.post(url_approve)
        
        # Try to approve or reject again
        r_app = self.client.post(url_approve)
        self.assertEqual(r_app.status_code, status.HTTP_400_BAD_REQUEST)
        
        r_rej = self.client.post(url_reject)
        self.assertEqual(r_rej.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_no_inventory(self):
        # Tricky test to delete inventory then approve
        data = {"product": self.product.id, "adjustment_type": "ADDITION", "quantity": 10, "reason": "T"}
        resp = self.client.post(self.url, data)
        adj_id = resp.data['id']
        
        self.inventory.delete()
        
        self.user.owned_company = self.company
        self.user.save()
        self.client.force_authenticate(user=self.user)
        
        url_approve = reverse('stockadjustmentrequest-approve', args=[adj_id])
        r = self.client.post(url_approve)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


class StockMovementTestCase(TenantTestCase, APITestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)
        self.branch = create_test_branch(company=self.company)
        self.user.branch.add(self.branch)
        from products.models import Product, Category, Brand, Season, Color, Gender
        self.category = Category.objects.create(company=self.company, name="Cat")
        self.brand = Brand.objects.create(company=self.company, name="Brand")
        self.season = Season.objects.create(name="Season")
        self.color = Color.objects.create(name="Color", code="#000000")
        self.gender = Gender.objects.create(name="Unisex")
        self.product = Product.objects.create(
            company=self.company,
            name="Prod", category=self.category, brand=self.brand, season=self.season,
            color=self.color, gender=self.gender, sale_price=100, cost_price=50
        )
        self.url = reverse('stockmovement-list')

    def test_get_queryset(self):
        from inventory.models import StockMovement
        StockMovement.objects.create(
            company=self.company,
            branch=self.branch,
            product=self.product,
            movement_type=StockMovement.MovementType.CORRECTION,
            previous_quantity=10,
            new_quantity=15,
            quantity_change=5
        )
        
        # Manager
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['results']), 1)
        
        # Superuser
        self.user.is_superuser = True
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['results']), 1)
        
        # No branch
        self.user.is_superuser = False
        self.user.branch.clear()
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['results']), 1)  # Falls back to company filtering


class InventoryViewSetCoverageTestCase(TenantTestCase, APITestCase):
    """Additional tests for 100% coverage of inventory/views.py"""
    
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)
        self.branch = create_test_branch(company=self.company)
        self.category = Category.objects.create(company=self.company, name="Cat")
        self.brand = Brand.objects.create(company=self.company, name="Brand")
        self.season = Season.objects.create(name="Season")
        self.color = Color.objects.create(name="Color", code="#000000")
        self.gender = Gender.objects.create(name="Unisex")
        self.product = Product.objects.create(
            company=self.company,
            name="Prod", category=self.category, brand=self.brand, season=self.season,
            color=self.color, gender=self.gender, sale_price=100, cost_price=50
        )
        self.inventory = Inventory.objects.get(product=self.product)
    
    def test_inventory_viewset_swagger_fake_view(self):
        """Test line 34: swagger_fake_view returns empty"""
        from rest_framework.test import APIRequestFactory
        from inventory.views import InventoryViewSet
        
        # Create user without company
        user_no_company = User.objects.create_user(
            username='nocomp_swagger',
            password='pass',
            company=None
        )
        
        factory = APIRequestFactory()
        request = factory.get('/api/inventory/')
        request.user = user_no_company
        
        viewset = InventoryViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)
    
    def test_inventory_viewset_superuser(self):
        """Test line 41: superuser sees all inventory"""
        from rest_framework.test import APIRequestFactory
        from inventory.views import InventoryViewSet
        
        superuser = User.objects.create_superuser(
            username='super_inventory',
            password='pass',
            email='super_inventory@test.com'
        )
        
        factory = APIRequestFactory()
        request = factory.get('/api/inventory/')
        request.user = superuser
        
        viewset = InventoryViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertGreaterEqual(queryset.count(), 1)
    
    def test_inventory_viewset_user_with_branches(self):
        """Test line 44: user with branches sees only their branch inventory"""
        from rest_framework.test import APIRequestFactory
        from inventory.views import InventoryViewSet
        
        user_with_branch = User.objects.create_user(
            username='withbranch',
            password='pass',
            company=self.company
        )
        user_with_branch.branch.add(self.branch)
        
        factory = APIRequestFactory()
        request = factory.get('/api/inventory/')
        request.user = user_with_branch
        
        viewset = InventoryViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertGreaterEqual(queryset.count(), 1)
    
    def test_inventory_viewset_user_no_branches_fallback(self):
        """Test lines 45-46: user with company but no branches sees company inventory"""
        from rest_framework.test import APIRequestFactory
        from inventory.views import InventoryViewSet
        
        user_no_branch = User.objects.create_user(
            username='nobranch',
            password='pass',
            company=self.company
        )
        user_no_branch.branch.clear()
        
        factory = APIRequestFactory()
        request = factory.get('/api/inventory/')
        request.user = user_no_branch
        
        viewset = InventoryViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertGreaterEqual(queryset.count(), 1)
    
    def test_inventory_viewset_user_no_company(self):
        """Test line 49 (last): user without company returns empty"""
        from rest_framework.test import APIRequestFactory
        from inventory.views import InventoryViewSet
        
        user_no_company = User.objects.create_user(
            username='nocompany',
            password='pass',
            company=None
        )
        
        factory = APIRequestFactory()
        request = factory.get('/api/inventory/')
        request.user = user_no_company
        
        viewset = InventoryViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)
    
    def test_other_branches_inventory_does_not_exist(self):
        """Test lines 199-200: Inventory.DoesNotExist exception handling"""
        # Try to get other branches for non-existent inventory
        url = reverse('inventory-other-branches', args=[999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_stock_breakdown_invalid_threshold(self):
        """Test lines 199-200: ValueError handling in stock_breakdown"""
        self.user.owned_company = self.company
        self.user.save()
        self.client.force_authenticate(user=self.user)
        
        self.inventory.quantity = 50
        self.inventory.save()
        
        # Pass invalid threshold
        url = reverse('inventory-stock-breakdown')
        response = self.client.get(url, {'low_stock': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_stock_adjustment_user_with_branches(self):
        """Test lines 233-239: StockAdjustmentRequest queryset with branches"""
        from rest_framework.test import APIRequestFactory
        from inventory.views import StockAdjustmentRequestViewSet
        from inventory.models import StockAdjustmentRequest
        
        # Create user with branches
        user_with_branch = User.objects.create_user(
            username='withbranch_adj',
            password='pass',
            company=self.company
        )
        user_with_branch.branch.add(self.branch)
        
        # Create adjustment
        StockAdjustmentRequest.objects.create(
            company=self.company,
            branch=self.branch,
            product=self.product,
            adjustment_type='REDUCTION',
            quantity=5,
            reason='Test',
            requested_by=user_with_branch,
            status='PENDING'
        )
        
        factory = APIRequestFactory()
        request = factory.get('/api/stock-adjustment-requests/')
        request.user = user_with_branch
        
        viewset = StockAdjustmentRequestViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 1)
    
    def test_stock_adjustment_user_no_branches_fallback(self):
        """Test lines 236-237: StockAdjustmentRequest fallback to company"""
        from rest_framework.test import APIRequestFactory
        from inventory.views import StockAdjustmentRequestViewSet
        from inventory.models import StockAdjustmentRequest
        
        # Create user without branches
        user_no_branch = User.objects.create_user(
            username='nobranch_adj',
            password='pass',
            company=self.company
        )
        
        # Create adjustment
        StockAdjustmentRequest.objects.create(
            company=self.company,
            branch=self.branch,
            product=self.product,
            adjustment_type='REDUCTION',
            quantity=5,
            reason='Test',
            requested_by=user_no_branch,
            status='PENDING'
        )
        
        factory = APIRequestFactory()
        request = factory.get('/api/stock-adjustment-requests/')
        request.user = user_no_branch
        
        viewset = StockAdjustmentRequestViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 1)
    
    def test_stock_adjustment_user_no_company(self):
        """Test line 239: StockAdjustmentRequest with no company"""
        from rest_framework.test import APIRequestFactory
        from inventory.views import StockAdjustmentRequestViewSet
        
        user_no_company = User.objects.create_user(
            username='nocompany_adj',
            password='pass',
            company=None
        )
        
        factory = APIRequestFactory()
        request = factory.get('/api/stock-adjustment-requests/')
        request.user = user_no_company
        
        viewset = StockAdjustmentRequestViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)
    
    def test_stock_movement_user_no_company(self):
        """Test lines 401-407: StockMovement queryset with no company"""
        from rest_framework.test import APIRequestFactory
        from inventory.views import StockMovementViewSet
        
        user_no_company = User.objects.create_user(
            username='nocompany2',
            password='pass',
            company=None
        )
        
        factory = APIRequestFactory()
        request = factory.get('/api/stock-movements/')
        request.user = user_no_company
        
        viewset = StockMovementViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)
    
    def test_stock_movement_user_with_branches(self):
        """Test line 404: StockMovement queryset with branches"""
        from rest_framework.test import APIRequestFactory
        from inventory.views import StockMovementViewSet
        from inventory.models import StockMovement
        
        # Create stock movement
        StockMovement.objects.create(
            company=self.company,
            branch=self.branch,
            product=self.product,
            movement_type=StockMovement.MovementType.CORRECTION,
            previous_quantity=10,
            new_quantity=15,
            quantity_change=5
        )
        
        user_with_branch = User.objects.create_user(
            username='withbranch_mov',
            password='pass',
            company=self.company
        )
        user_with_branch.branch.add(self.branch)
        
        factory = APIRequestFactory()
        request = factory.get('/api/stock-movements/')
        request.user = user_with_branch
        
        viewset = StockMovementViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 1)
    
    def test_stock_movement_user_no_branches_fallback(self):
        """Test lines 405-406: StockMovement queryset fallback to company"""
        from rest_framework.test import APIRequestFactory
        from inventory.views import StockMovementViewSet
        from inventory.models import StockMovement
        
        # Create stock movement
        StockMovement.objects.create(
            company=self.company,
            branch=self.branch,
            product=self.product,
            movement_type=StockMovement.MovementType.CORRECTION,
            previous_quantity=10,
            new_quantity=15,
            quantity_change=5
        )
        
        user_no_branch = User.objects.create_user(
            username='nobranch2',
            password='pass',
            company=self.company
        )
        user_no_branch.branch.clear()
        
        factory = APIRequestFactory()
        request = factory.get('/api/stock-movements/')
        request.user = user_no_branch
        
        viewset = StockMovementViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 1)


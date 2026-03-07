from django.test import TestCase
from rest_framework.exceptions import ValidationError
from core.models import Company, Branch
from core.serializers import CompanySerializer, BranchSerializer, BranchListSerializer


class CompanySerializerTest(TestCase):
    """
    Test cases for CompanySerializer
    """
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            name='Test Company',
            tax_id='12-3456789-0',
            is_active=True
        )
        # Create some branches to test branches_count
        Branch.objects.create(
            company=self.company,
            name='Branch 1',
            code='BR-001'
        )
        Branch.objects.create(
            company=self.company,
            name='Branch 2',
            code='BR-002'
        )
    
    def test_serialize_company(self):
        """Test serializing a company"""
        serializer = CompanySerializer(instance=self.company)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Company')
        self.assertEqual(data['tax_id'], '12-3456789-0')
        self.assertTrue(data['is_active'])
        self.assertEqual(data['branches_count'], 2)
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_deserialize_company(self):
        """Test deserializing and creating a company"""
        data = {
            'name': 'New Company',
            'tax_id': '98-7654321-0',
            'is_active': True
        }
        serializer = CompanySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        company = serializer.save()
        
        self.assertEqual(company.name, 'New Company')
        self.assertEqual(company.tax_id, '98-7654321-0')
        self.assertTrue(company.is_active)
    
    def test_update_company(self):
        """Test updating a company"""
        data = {
            'name': 'Updated Company',
            'is_active': False
        }
        serializer = CompanySerializer(instance=self.company, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        company = serializer.save()
        
        self.assertEqual(company.name, 'Updated Company')
        self.assertFalse(company.is_active)
    
    def test_read_only_fields(self):
        """Test that created_at and updated_at are read-only"""
        serializer = CompanySerializer(instance=self.company)
        self.assertIn('created_at', serializer.fields)
        self.assertIn('updated_at', serializer.fields)
        self.assertTrue(serializer.fields['created_at'].read_only)
        self.assertTrue(serializer.fields['updated_at'].read_only)


class BranchSerializerTest(TestCase):
    """
    Test cases for BranchSerializer
    """
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            name='Test Company',
            tax_id='12-3456789-0',
            is_active=True
        )
        self.branch = Branch.objects.create(
            company=self.company,
            name='Main Branch',
            code='MAIN-001',
            address='123 Main Street',
            is_active=True
        )
    
    def test_serialize_branch(self):
        """Test serializing a branch"""
        serializer = BranchSerializer(instance=self.branch)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Main Branch')
        self.assertEqual(data['code'], 'MAIN-001')
        self.assertEqual(data['address'], '123 Main Street')
        self.assertEqual(data['company_name'], 'Test Company')
        self.assertTrue(data['is_active'])
        self.assertIn('id', data)
        self.assertIn('company', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_deserialize_branch(self):
        """Test deserializing and creating a branch
        
        Note: The company field is read-only and must be provided via save()
        to match the ViewSet behavior where company is set automatically.
        """
        data = {
            'name': 'New Branch',
            'code': 'NEW-001',
            'address': '456 New Street',
            'is_active': True
        }
        serializer = BranchSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        # Company must be provided in save() since it's read-only in serializer
        branch = serializer.save(company=self.company)
        
        self.assertEqual(branch.name, 'New Branch')
        self.assertEqual(branch.code, 'NEW-001')
        self.assertEqual(branch.company, self.company)
    
    def test_update_branch(self):
        """Test updating a branch"""
        data = {
            'name': 'Updated Branch',
            'address': '789 Updated Street'
        }
        serializer = BranchSerializer(instance=self.branch, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        branch = serializer.save()
        
        self.assertEqual(branch.name, 'Updated Branch')
        self.assertEqual(branch.address, '789 Updated Street')
    
    def test_validate_code_unique_on_create(self):
        """Test that code validation prevents duplicate codes on create"""
        data = {
            'name': 'Another Branch',
            'code': 'MAIN-001',  # Same code as existing branch
            'is_active': True
        }
        serializer = BranchSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
        self.assertIn('already exists', str(serializer.errors['code'][0]))
    
    def test_validate_code_unique_on_update(self):
        """Test that code validation works on update"""
        # Create another branch
        other_branch = Branch.objects.create(
            company=self.company,
            name='Other Branch',
            code='OTHER-001'
        )
        
        # Try to update branch with code that already exists
        data = {
            'code': 'OTHER-001'  # Code from other_branch
        }
        serializer = BranchSerializer(instance=self.branch, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_validate_code_allows_same_code_on_update(self):
        """Test that validation allows same code when updating same instance"""
        data = {
            'code': 'MAIN-001',  # Same code as current
            'name': 'Updated Name'
        }
        serializer = BranchSerializer(instance=self.branch, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
    
    def test_read_only_fields(self):
        """Test that certain fields are read-only"""
        serializer = BranchSerializer(instance=self.branch)
        self.assertTrue(serializer.fields['company'].read_only)
        self.assertTrue(serializer.fields['company_name'].read_only)
        self.assertTrue(serializer.fields['created_at'].read_only)
        self.assertTrue(serializer.fields['updated_at'].read_only)


class BranchListSerializerTest(TestCase):
    """
    Test cases for BranchListSerializer
    """
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            name='Test Company',
            is_active=True
        )
        self.branch = Branch.objects.create(
            company=self.company,
            name='Main Branch',
            code='MAIN-001',
            is_active=True
        )
    
    def test_serialize_branch_list(self):
        """Test serializing a branch with lightweight serializer"""
        serializer = BranchListSerializer(instance=self.branch)
        data = serializer.data
        
        # Should have only essential fields
        self.assertEqual(data['name'], 'Main Branch')
        self.assertEqual(data['code'], 'MAIN-001')
        self.assertEqual(data['company_name'], 'Test Company')
        self.assertTrue(data['is_active'])
        self.assertIn('id', data)
        
        # Should not have address, created_at, etc.
        self.assertNotIn('address', data)
        self.assertNotIn('created_at', data)
        self.assertNotIn('updated_at', data)
    
    def test_serialize_multiple_branches(self):
        """Test serializing multiple branches"""
        Branch.objects.create(
            company=self.company,
            name='Second Branch',
            code='SEC-001',
            is_active=False
        )
        
        branches = Branch.objects.all()
        serializer = BranchListSerializer(branches, many=True)
        data = serializer.data
        
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Main Branch')
        self.assertEqual(data[1]['name'], 'Second Branch')

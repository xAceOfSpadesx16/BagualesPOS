from django.test import TestCase
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer, CustomTokenObtainPairSerializer

User = get_user_model()

class UserSerializerTestCase(TestCase):
    def test_user_serializer(self):
        user = User.objects.create_user(username="test", email="t@t.com", first_name="Test", last_name="User")
        serializer = UserSerializer(user)
        data = serializer.data
        self.assertEqual(data['username'], "test")
        self.assertEqual(data['email'], "t@t.com")
        self.assertEqual(data['first_name'], "Test")
        self.assertEqual(data['last_name'], "User")

class CustomTokenObtainPairSerializerTestCase(TestCase):
    def test_token_claims(self):
        user = User.objects.create_user(
            username="test", password="password", first_name="Juan", last_name="Perez"
        )
        serializer = CustomTokenObtainPairSerializer()
        token = serializer.get_token(user)
        
        self.assertEqual(token['first_name'], "Juan")
        self.assertEqual(token['last_name'], "Perez")
        self.assertEqual(token['id'], user.id)

class ProfileSerializerTestCase(TestCase):
    def test_profile_serializer(self):
        user = User.objects.create_user(username="profiletest", password="password")
        # Profile is created by signal
        profile = user.profile
        profile.phone_number = "+1234567890"
        profile.save()
        
        from users.serializers import ProfileSerializer
        serializer = ProfileSerializer(profile)
        data = serializer.data
        self.assertEqual(data['phone_number'], "+1234567890")
        self.assertEqual(data['user'], user.id)


class EmployeeSerializerCoverageTestCase(TestCase):
    """Tests for 100% coverage of users/serializers.py"""
    
    def setUp(self):
        from core.models import Company, Branch
        from django.contrib.auth.models import Group
        
        self.company = Company.objects.create(name='Test Co Serializer', tax_id='123456')
        self.branch = Branch.objects.create(company=self.company, name='Branch1', code='B1SER')
        self.admin = User.objects.create_user(
            username='admin_serializer',
            password='pass',
            company=self.company
        )
        self.admin_group, _ = Group.objects.get_or_create(name='Administrador General')
        self.cajero_group, _ = Group.objects.get_or_create(name='Cajero')
    
    def test_validate_branches_ids_empty(self):
        """Test line 167: validate_branches_ids with empty value"""
        from users.serializers import EmployeeSerializer
        
        serializer = EmployeeSerializer(context={'request': type('obj', (object,), {'user': self.admin})()})
        # Empty list should return as-is
        result = serializer.validate_branches_ids([])
        self.assertEqual(result, [])
    
    def test_validate_groups_ids_empty(self):
        """Test line 188: validate_groups_ids with empty value"""
        from users.serializers import EmployeeSerializer
        
        serializer = EmployeeSerializer(context={'request': type('obj', (object,), {'user': self.admin})()})
        # Empty list should return as-is
        result = serializer.validate_groups_ids([])
        self.assertEqual(result, [])
    
    def test_validate_branches_ids_no_request_context(self):
        """Test line 192: validate_branches_ids when request is None"""
        from users.serializers import EmployeeSerializer
        from rest_framework import serializers
        
        # Create serializer without request in context
        ser = EmployeeSerializer(context={})
        
        # Should raise validation error
        with self.assertRaises(serializers.ValidationError) as cm:
            ser.validate_branches_ids([self.branch.id])
        
        self.assertIn('Unable to validate branches', str(cm.exception))
    
    def test_employee_serializer_create_no_company_context(self):
        """Test line 218: EmployeeSerializer.create when company context is missing"""
        from users.serializers import EmployeeSerializer
        from rest_framework import serializers
        
        # Create serializer without company in context
        data = {
            'username': 'testuser',
            'password': 'pass123',
            'password_confirm': 'pass123',
            'groups_ids': [],
            'branches_ids': []
        }
        
        serializer = EmployeeSerializer(data=data, context={'request': type('obj', (object,), {'user': self.admin})()})
        serializer.is_valid()
        
        # Should raise validation error because no company in context
        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.save()
        
        self.assertIn('company', str(cm.exception))

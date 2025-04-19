from django.test import TestCase
from django.contrib.auth.models import User
from bm_app.models import Temple

class TempleModelTests(TestCase):
    def setUp(self):
        # Create a test user for temple admin
        self.test_user = User.objects.create_user(
            username='testadmin',
            email='testadmin@example.com',
            password='password123'
        )
        # Create a test temple
        self.test_temple = Temple.objects.create(
            name='Test Temple',
            location='Test Location',
            admin=self.test_user
        )

    def test_temple_creation(self):
        """Test that temple creation works correctly"""
        self.assertEqual(self.test_temple.name, 'Test Temple')
        self.assertEqual(self.test_temple.location, 'Test Location')
        self.assertEqual(self.test_temple.admin, self.test_user)
        
    def test_temple_str_method(self):
        """Test the string representation of temple objects"""
        self.assertEqual(str(self.test_temple), 'Test Temple')
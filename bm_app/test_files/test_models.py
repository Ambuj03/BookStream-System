from django.test import TestCase
from django.contrib.auth.models import User
from bm_app.models import *

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


class BooksModelTest(TestCase):

    def setUp(self):
        self.test_user = User.objects.create_user(
            username='testadmin',
            email='testadmin@example.com',
            password='password123'
        )

        self.test_temple = Temple.objects.create(
            name='Test Temple',
            location='Test Location',
            admin=self.test_user
        )

        self.test_book_category = BooksCategory.objects.create(
            bookscategory_name = "test_category_name",
            temple_id = self.test_temple.temple_id,
        )

        self.test_book = Books.objects.create(
            book_name = "Bhagavad Gitopanishad",
            book_author = "ACBSP",
            book_language = "English",
            book_price = 300,
            book_category = self.test_book_category,
            temple_id = self.test_temple.temple_id
        )

    def test_book_creation(self):
        self.assertEqual(self.test_book.book_name, "Bhagavad Gitopanishad")
        self.assertEqual(self.test_book.book_author , "ACBSP")
    
    def test_book_query(self):
        english_books = Books.objects.filter(book_language = "English")
        self.assertEqual(english_books.count(), 1)

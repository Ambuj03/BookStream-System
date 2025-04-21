#In this test we will verify that when admin updates the inventory of distributor, the flow is going on properly.

from django.test import TestCase
from django.contrib.auth.models import User
from bm_app.models import *

class InventoryAutomationTests(TestCase):
    def setUp(self):
        # Create a test user for temple admin
        self.test_admin = User.objects.create_user(
            username='testadmin',
            email='testadmin@example.com',
            password='password123',
            is_staff = 1
        )

        self.test_user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )
        # Create a test temple
        self.test_temple = Temple.objects.create(
            name='Test Temple',
            location='Test Location',
            admin=self.test_admin
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

        self.test_distributor = Distributor.objects.create(
            distributor_name = "test",
            distributor_email = "example@gmail.com",
            distributor_phonenumber = 8269891552,
            distributor_address = "xyz",
            distributor_age = "2023-12-23",
            created_at = timezone.now(),
            user_id = self.test_user.id,
            temple_id = self.test_temple.temple_id
        )

        #create a bookallocation object

        self.test_book_allocation = BookAllocation.objects.create(
            allocation_date = timezone.now(),
            notes = 'testing!!!',
            distributor_id = self.test_distributor.distributor_id,
            temple_id = self.test_temple.temple_id
        )

        #create a bookallocationdetail object
        self.test_book_allocation_detail = BookAllocationDetail.objects.create(
            quantity = 10,
            allocation_id = self.test_book_allocation.allocation_id,
            book = self.test_book,
            price = 300,
            temple_id = self.test_temple.temple_id
        )   


    #see if the distributorbook table is getting updates with the same entries or not

    def test_book_allocation_flow(self):
        # Test that DistributorBooks was automatically created
        distributor_books = DistributorBooks.objects.filter(
            distributor_id=self.test_distributor.distributor_id
        )

        self.assertEqual(distributor_books.count(), 1)

    """ Test that DistributorBooks entries are created when BookAllocationDetail is saved.
        NOTE: This test is incomplete because the actual creation logic is in the admin 
        save_model() method, not in model signals or methods.
        This test requires admin functionality that can't be easily simulated
    """

    
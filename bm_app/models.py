from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_name = models.CharField(max_length=100)
    admin_email = models.CharField(unique=True, max_length=100)
    admin_password = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'admin'

class BooksCategory(models.Model):
    bookscategory_id = models.AutoField(primary_key=True)
    bookscategory_name = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'books_category'
        
    def __str__(self):
        return self.bookscategory_name

class Books(models.Model):
    book_id = models.AutoField(primary_key=True)
    book_name = models.CharField(max_length=200)
    book_author = models.CharField(max_length=100, blank=True, null=True)
    book_language = models.CharField(max_length=50)
    book_price = models.IntegerField()
    book_category = models.ForeignKey(BooksCategory, on_delete=models.CASCADE, db_column='book_category', to_field='bookscategory_name', null = True, blank = True)

    class Meta:
        managed = False
        db_table = 'books'
        
    def __str__(self):
        return self.book_name

class Distributor(models.Model):
    distributor_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)  
    distributor_name = models.CharField(max_length=100)
    distributor_email = models.EmailField(unique=True)
    distributor_phonenumber = models.CharField(db_column='distributor_phoneNumber', max_length=15)
    distributor_address = models.TextField(blank=True, null=True)
    distributor_age = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    admin = models.ForeignKey("Admin", on_delete=models.RESTRICT, null=True, blank=True)
    
    def __str__(self):
        return self.distributor_name

    class Meta:
        managed = False
        db_table = 'distributor'

class MasterInventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Books, on_delete=models.RESTRICT, null = True, blank = True)
    admin = models.ForeignKey(Admin, on_delete=models.RESTRICT, null = True, blank = True)
    stock = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'master_inventory'

class DistributorInventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    books = models.ForeignKey(Books, on_delete=models.CASCADE, null = True, blank = True)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE, null = True, blank = True)
    books_stock = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'distributor_inventory'
        
class DistributorBooks(models.Model):
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    book_name = models.CharField(max_length=200)
    book_author = models.CharField(max_length=100)
    book_language = models.CharField(max_length=50)
    book_price = models.IntegerField()
    book_category = models.CharField(max_length=100)
    book_stock = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'distributor_books'

    def __str__(self):
        return self.book_name

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    customer_occupation = models.CharField(max_length=100, blank=True, null=True)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    customer_city = models.CharField(max_length=50, blank=True, null=True)
    customer_remarks = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customer'

class Donation(models.Model):
    donation_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT, null = True, blank = True)
    donation_date = models.DateTimeField(auto_now_add=True, null = True, blank = True)
    donation_amount = models.IntegerField()
    donation_purpose = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'donation'

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user_type = models.CharField(max_length=11)
    user_id = models.IntegerField()
    message = models.TextField()
    event_type = models.CharField(max_length=9)
    created_at = models.DateTimeField(auto_now_add=True, null = True, blank = True)
    status = models.CharField(max_length=6, default='Unread')

    class Meta:
        managed = False
        db_table = 'notification'

# Update your Receipt model
class Receipt(models.Model):
    PAYMENT_CHOICES = [
        ('ONLINE', 'ONLINE'),
        ('CASH', 'CASH')
    ]
    
    receipt_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id')
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, db_column='donation_id', null=True)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE, db_column='distributor_id')
    date = models.DateTimeField(auto_now_add=True, null=True)
    paymentMode = models.CharField(max_length=6, choices=PAYMENT_CHOICES, null=True, db_column='paymentMode')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)

    class Meta:
        managed = False
        db_table = 'receipt'

# Add new ReceiptBooks model
class ReceiptBooks(models.Model):
    id = models.AutoField(primary_key=True)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, db_column='receipt_id')
    book = models.ForeignKey(Books, on_delete=models.CASCADE, db_column='book_id')
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'receipt_books'




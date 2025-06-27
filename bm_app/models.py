from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Temple(models.Model):
    temple_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    admin = models.OneToOneField(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    class Meta:
        pass


class BooksCategory(models.Model):
    temple = models.ForeignKey(Temple, on_delete=models.PROTECT)
    bookscategory_id = models.AutoField(primary_key=True)
    bookscategory_name = models.CharField(unique=True, max_length=100)

    class Meta:
        pass
        
    def __str__(self):
        return self.bookscategory_name

class Books(models.Model):
    temple = models.ForeignKey(Temple, on_delete=models.PROTECT)
    book_id = models.AutoField(primary_key=True)
    book_name = models.CharField(max_length=200)
    book_author = models.CharField(max_length=100, blank=True, null=True)
    book_language = models.CharField(max_length=50)
    book_price = models.IntegerField()
    book_category = models.ForeignKey(BooksCategory, on_delete=models.CASCADE, db_column='book_category', to_field='bookscategory_name', null=True, blank=True)

    class Meta:
        verbose_name = 'book'
        
    def __str__(self):
        return self.book_name

class Distributor(models.Model):
    distributor_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='distributor_user')
    temple = models.ForeignKey(Temple, on_delete=models.PROTECT)
    distributor_name = models.CharField(max_length=100)
    distributor_email = models.EmailField(unique=True)
    distributor_phonenumber = models.CharField(db_column='distributor_phoneNumber', max_length=15)
    distributor_address = models.TextField(blank=True, null=True)
    distributor_age = models.DateField(blank=True, null=True)
    created_at = models.DateField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return self.distributor_name

    class Meta:
        pass

class MasterInventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Books, on_delete=models.RESTRICT)
    temple = models.ForeignKey(Temple, on_delete=models.PROTECT)
    stock = models.IntegerField(default=0)      

    class Meta:
        verbose_name = 'Master Inventory'
        verbose_name_plural = 'Master Inventory'

class DistributorBooks(models.Model):
    temple = models.ForeignKey(Temple, on_delete=models.PROTECT)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    book_name = models.CharField(max_length=200)
    book_author = models.CharField(max_length=100)
    book_language = models.CharField(max_length=50)
    book_price = models.IntegerField()
    book_category = models.CharField(max_length=100)
    book_stock = models.IntegerField()

    class Meta:
        pass

    def __str__(self):
        return self.book_name
    
    def save(self, *args, **kwargs):
        if(self.book_stock) <= 0 :
            self.delete()
            return
        super().save(*args, **kwargs)

class Customer(models.Model):
    temple = models.ForeignKey(Temple, on_delete=models.PROTECT)
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100, null = True, blank = True)
    customer_occupation = models.CharField(max_length=100, blank=True, null=True)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    customer_city = models.CharField(max_length=50, blank=True, null=True)
    customer_remarks = models.TextField(blank=True, null=True)
    Date = models.DateField(default=timezone.now)

    class Meta:
        pass
        
    def __str__(self):
        return self.customer_name

class Donation(models.Model):
    temple = models.ForeignKey(Temple, on_delete=models.PROTECT)
    donation_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT, null=True, blank=True)
    donation_date = models.DateField(default=timezone.now, null=True, blank=True)
    donation_amount = models.IntegerField(default=0, blank= True,null = True)
    donation_purpose = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        pass
        
    def __str__(self):
        return str(self.customer.customer_name)

class Notification(models.Model):
    temple = models.ForeignKey(Temple, on_delete=models.PROTECT)
    notification_id = models.AutoField(primary_key=True)
    user_type = models.CharField(max_length=11) #
    user_id = models.IntegerField() #
    message = models.TextField()
    event_type = models.CharField(max_length=9)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    status = models.CharField(max_length=6, default='Unread')#
    
    # see if you can delete these three

    class Meta:
        pass

class Receipt(models.Model):
    PAYMENT_CHOICES = [
        ('ONLINE', 'ONLINE'),
        ('CASH', 'CASH')
    ]
    temple = models.ForeignKey(Temple, on_delete=models.PROTECT)
    receipt_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id')
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, db_column='donation_id', null=True)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE, db_column='distributor_id')
    date = models.DateField(default=timezone.now, null=True)
    paymentMode = models.CharField(max_length=6, choices=PAYMENT_CHOICES, null=True, db_column='paymentMode')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    notification_sent = models.BooleanField(default=False)
    notification_status = models.CharField(max_length=50, default='PENDING')
    notification_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        pass

    def __str__(self):
        return str(self.distributor.distributor_name)

class ReceiptBooks(models.Model):
    temple = models.ForeignKey(Temple, on_delete=models.PROTECT)
    id = models.AutoField(primary_key=True)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, db_column='receipt_id')
    book_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    book_price = models.DecimalField(max_digits=10, decimal_places=2)
    

    class Meta:
        pass

class BookAllocation(models.Model):
    allocation_id = models.AutoField(primary_key=True)
    temple = models.ForeignKey(Temple, on_delete=models.PROTECT)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    allocation_date = models.DateField(default=timezone.now)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        pass
        
    def __str__(self):
        return f"{self.distributor}-Allocation Id: " + str(self.allocation_id)

class BookAllocationDetail(models.Model):
    temple = models.ForeignKey(Temple, on_delete=models.PROTECT)
    id = models.AutoField(primary_key=True)
    allocation = models.ForeignKey(BookAllocation, on_delete=models.CASCADE)
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()

    class Meta:
        pass
        




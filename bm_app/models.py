# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField


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


class Books(models.Model):
    book_id = models.AutoField(primary_key=True)
    book_name = models.CharField(max_length=100)
    book_author = models.CharField(max_length=100, blank=True, null=True)
    book_language = models.CharField(max_length=50)
    book_price = models.IntegerField()
    book_category = models.ForeignKey('BooksCategory', models.DO_NOTHING, 
                    db_column='book_category', to_field='bookscategory_name', 
                    blank=False, null=False) # changed blank and null values, check removing db column

    class Meta:
        managed = False
        db_table = 'books'


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    customer_occupation = models.CharField(max_length=100, blank=True, null=True)
    customer_phone = models.CharField(max_length=10, blank=True, null=True)
    customer_city = models.CharField(max_length=50, blank=True, null=True)
    customer_remarks = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customer'


class Distributor(models.Model):
    distributor_id = models.AutoField(primary_key=True)
    distributor_name = models.CharField(max_length=100)
    distributor_phonenumber = PhoneNumberField(blank = True, null = True)       #db_column='distributor_phoneNumber'  # Field name made lowercase.
    distributor_address = models.TextField(blank=True, null=True)
    distributor_email = models.CharField(max_length=100)
    distributor_password = models.CharField(max_length=100)
    distributor_age = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    admin = models.ForeignKey(Admin, models.DO_NOTHING) # changed admin to admin_id

    class Meta:
        managed = False
        db_table = 'distributor'


class DistributorInventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    books = models.ForeignKey(Books, models.DO_NOTHING) # from books to book_id
    distributor = models.ForeignKey(Distributor, models.DO_NOTHING) #changed from distributor to distributor_id
    books_stock = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'distributor_inventory'


class Donation(models.Model):
    donation_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, models.DO_NOTHING) # customer to customer_id
    donation_date = models.DateTimeField(blank=True, null=True)
    donation_amount = models.IntegerField()
    donation_purpose = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'donation'


class MasterInventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Books, models.DO_NOTHING)
    admin = models.ForeignKey(Admin, models.DO_NOTHING)
    stock = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'master_inventory'


#defining choices explicitly as we don't have enum here

USER_TYPE_CHOICES = [("admin","Admin"),("distributor","Distributor")]

EVENT_TYPE_CHOICES = [("low stock","Low Stock"),("others","Others")]

STATUS_CHOICES = [("read","Read"), ("unread","Unread")]


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user_type = models.CharField(max_length=11, choices= USER_TYPE_CHOICES)
    user_id = models.IntegerField()
    message = models.TextField()
    event_type = models.CharField(max_length=9, choices=EVENT_TYPE_CHOICES)
    created_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=6, choices=STATUS_CHOICES,blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notification'

# payment mode choices

PAYMENT_MODE_CHOICES = [("online","Online"),("cash","Cash")]

class Receipt(models.Model):
    receipt_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, models.DO_NOTHING)
    book = models.ForeignKey(Books, models.DO_NOTHING)
    donation = models.ForeignKey(Donation, models.DO_NOTHING, blank=True, null=True)
    distributor = models.ForeignKey(Distributor, models.DO_NOTHING)
    date = models.DateTimeField(blank=True, null=True)
    quantity = models.IntegerField()
    paymentmode = models.CharField(db_column='paymentMode', choices=PAYMENT_MODE_CHOICES,max_length=6, blank=True, null=True)  # Field name made lowercase.
 
    class Meta:
        managed = False
        db_table = 'receipt'

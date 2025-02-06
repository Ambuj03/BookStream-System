from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_name = models.CharField(max_length=100)
    admin_email = models.CharField(unique=True, max_length=100)
    admin_password = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'admin'

class BooksCategory(models.Model):
    bookscategory_id = models.AutoField(primary_key=True)
    bookscategory_name = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = True
        db_table = 'books_category'

class Books(models.Model):
    book_id = models.AutoField(primary_key=True)
    book_name = models.CharField(max_length=200)
    book_author = models.CharField(max_length=100, blank=True, null=True)
    book_language = models.CharField(max_length=50)
    book_price = models.IntegerField()
    book_category = models.ForeignKey(BooksCategory, on_delete=models.CASCADE, db_column='book_category', to_field='bookscategory_name', null = True, blank = True)

    class Meta:
        managed = True
        db_table = 'books'



# Modifying the model for login,Since we are extending Django’s built-in User model, 
# our Distributor model will inherit from AbstractUser.
class DistributorManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class Distributor(AbstractBaseUser, PermissionsMixin):

    username = None  # Remove default username field
    email = models.EmailField(unique=True, db_column='distributor_email')  # Map email
    password = models.CharField(max_length=128, db_column='distributor_password')  # Map password

    distributor_id = models.AutoField(primary_key=True)
    distributor_name = models.CharField(max_length=100)
    distributor_phonenumber = models.CharField(db_column='distributor_phoneNumber', max_length=15)
    distributor_address = models.TextField(blank=True, null=True)
    distributor_age = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    admin = models.ForeignKey("Admin", on_delete=models.RESTRICT, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = DistributorManager()

    USERNAME_FIELD = "email"  # Login will be based on email
    REQUIRED_FIELDS = []


    # Override `last_login` to prevent errors, if you need this feature add this coulmn in database
    # ALTER TABLE distributor ADD COLUMN last_login DATETIME NULL;
    last_login = None

      # Override fields to prevent Django errors
    is_superuser = None
    is_staff = None
    is_active = None

    class Meta:
        managed = False  # Keep it False since DB is already populated
        db_table = "distributor"




class MasterInventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Books, on_delete=models.RESTRICT, null = True, blank = True)
    admin = models.ForeignKey(Admin, on_delete=models.RESTRICT, null = True, blank = True)
    stock = models.IntegerField(default=0)

    class Meta:
        managed = True
        db_table = 'master_inventory'

class DistributorInventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    books = models.ForeignKey(Books, on_delete=models.CASCADE, null = True, blank = True)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE, null = True, blank = True)
    books_stock = models.IntegerField(default=0)

    class Meta:
        managed = True
        db_table = 'distributor_inventory'

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    customer_occupation = models.CharField(max_length=100, blank=True, null=True)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    customer_city = models.CharField(max_length=50, blank=True, null=True)
    customer_remarks = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'customer'

class Donation(models.Model):
    donation_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT, null = True, blank = True)
    donation_date = models.DateTimeField(auto_now_add=True, null = True, blank = True)
    donation_amount = models.IntegerField()
    donation_purpose = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
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
        managed = True
        db_table = 'notification'

class Receipt(models.Model):
    receipt_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT, null = True, blank = True)
    book = models.ForeignKey(Books, on_delete=models.RESTRICT, null = True, blank = True)
    donation = models.ForeignKey(Donation, on_delete=models.SET_NULL, blank=True, null=True)
    distributor = models.ForeignKey(Distributor, on_delete=models.RESTRICT, null = True, blank = True)
    date = models.DateTimeField(auto_now_add=True, null = True, blank = True)
    quantity = models.IntegerField()
    payment_mode = models.CharField(db_column='paymentMode', max_length=6, choices=[('ONLINE', 'Online'), ('CASH', 'Cash')], blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'receipt'

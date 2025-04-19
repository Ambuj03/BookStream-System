# Generated by Django 5.1.8 on 2025-04-19 07:43

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BookAllocation',
            fields=[
                ('allocation_id', models.AutoField(primary_key=True, serialize=False)),
                ('allocation_date', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'book_allocation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='BookAllocationDetail',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('price', models.IntegerField()),
            ],
            options={
                'db_table': 'book_allocation_detail',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Books',
            fields=[
                ('book_id', models.AutoField(primary_key=True, serialize=False)),
                ('book_name', models.CharField(max_length=200)),
                ('book_author', models.CharField(blank=True, max_length=100, null=True)),
                ('book_language', models.CharField(max_length=50)),
                ('book_price', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Book',
                'db_table': 'books',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='BooksCategory',
            fields=[
                ('bookscategory_id', models.AutoField(primary_key=True, serialize=False)),
                ('bookscategory_name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'db_table': 'books_category',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customer_id', models.AutoField(primary_key=True, serialize=False)),
                ('customer_name', models.CharField(max_length=100)),
                ('customer_occupation', models.CharField(blank=True, max_length=100, null=True)),
                ('customer_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('customer_city', models.CharField(blank=True, max_length=50, null=True)),
                ('customer_remarks', models.TextField(blank=True, null=True)),
                ('Date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'customer',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Distributor',
            fields=[
                ('distributor_id', models.AutoField(primary_key=True, serialize=False)),
                ('distributor_name', models.CharField(max_length=100)),
                ('distributor_email', models.EmailField(max_length=254, unique=True)),
                ('distributor_phonenumber', models.CharField(db_column='distributor_phoneNumber', max_length=15)),
                ('distributor_address', models.TextField(blank=True, null=True)),
                ('distributor_age', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'db_table': 'distributor',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DistributorBooks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_name', models.CharField(max_length=200)),
                ('book_author', models.CharField(max_length=100)),
                ('book_language', models.CharField(max_length=50)),
                ('book_price', models.IntegerField()),
                ('book_category', models.CharField(max_length=100)),
                ('book_stock', models.IntegerField()),
            ],
            options={
                'db_table': 'distributor_books',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('donation_id', models.AutoField(primary_key=True, serialize=False)),
                ('donation_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('donation_amount', models.IntegerField()),
                ('donation_purpose', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'donation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MasterInventory',
            fields=[
                ('inventory_id', models.AutoField(primary_key=True, serialize=False)),
                ('stock', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'master_inventory',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('notification_id', models.AutoField(primary_key=True, serialize=False)),
                ('user_type', models.CharField(max_length=11)),
                ('user_id', models.IntegerField()),
                ('message', models.TextField()),
                ('event_type', models.CharField(max_length=9)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('status', models.CharField(default='Unread', max_length=6)),
            ],
            options={
                'db_table': 'notification',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('receipt_id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('paymentMode', models.CharField(choices=[('ONLINE', 'ONLINE'), ('CASH', 'CASH')], db_column='paymentMode', max_length=6, null=True)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True)),
                ('notification_sent', models.BooleanField(default=False)),
                ('notification_status', models.CharField(default='PENDING', max_length=50)),
                ('notification_timestamp', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'receipt',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ReceiptBooks',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('book_name', models.CharField(max_length=100)),
                ('quantity', models.IntegerField()),
                ('book_price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'db_table': 'receipt_books',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Temple',
            fields=[
                ('temple_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'temple',
                'managed': False,
            },
        ),
    ]

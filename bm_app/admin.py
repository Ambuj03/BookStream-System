from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from .sms import send_receipt_sms
from django.core.paginator import Paginator
from django.http import JsonResponse
from .notifications import notify_new_book_allocation, mark_notification_as_read, get_admin_notifications, check_master_inventory_stock,check_distributor_stock

#############################################################################
# Importing third party pkgs for enhanced filtering and export functionality
from rangefilter.filters import DateRangeFilter  # For advanced date range filtering
from import_export import resources, fields  # Base import_export functionality
from import_export.admin import ExportActionModelAdmin # Admin integration
from import_export.widgets import ForeignKeyWidget  # For handling foreign keys in export

#Defining a resourse class for each model we want to export
# This tell django import-export how to handle model fields during export

class DonationResource(resources.ModelResource):
    #Handle the customer foreign key relationship properly in exports

    customer_name = fields.Field(
        column_name= 'customer_name',
        attribute='customer',
        widget=ForeignKeyWidget(Customer, 'customer_name')
    )


    class Meta:
        model = Donation

        # fields to include in export( excluding temple here)
        ## try with temple too
        fields = ('customer_name', 'donation_date', 'donation_amount' ,'donation_purpose')
        export_order = fields   

class CustomerResourse(resources.ModelResource):
    class Meta:
        model = Customer
        exclude = ('temple','customer_id')

class DistributorResource(resources.ModelResource):
    class Meta:
        model= Distributor
        exclude = ('temple','distributor_id','user',)
        


#############################################################################

def mark_notification_read_view(request, notification_id):
    try:
        mark_notification_as_read(notification_id)
        return JsonResponse({'success': True})  # Return JSON instead of redirect
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

class TempleRestrictedAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        temple = Temple.objects.get(admin=request.user)
        return qs.filter(temple=temple)
        
    def save_model(self, request, obj, form, change):
        if not obj.temple_id and not request.user.is_superuser:
            obj.temple = Temple.objects.get(admin=request.user)
        super().save_model(request, obj, form, change)
        
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            temple = Temple.objects.get(admin=request.user)
            if db_field.name in ['customer', 'distributor', 'book']:
                kwargs['queryset'] = db_field.related_model.objects.filter(temple=temple)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# We are modifying existing ModelAdmin classesto use these features
# We'll create a base class that combibes TempleRestrcitedAdmin and ExportActionModelAdmin
class TempleRestrictedExport(TempleRestrictedAdmin, ExportActionModelAdmin):
    """
    Base admin class that combines temple restrictions with import/export functionality
    This reduces code duplication across model admins
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    list_per_page = 10



@admin.register(Temple)
class TempleAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        # Get or create the temple_admin group
        temple_admin_group = Group.objects.get(name='temple_admin')
        
        if not change:  # Only for new temples
            # Set staff status and add to group
            obj.admin.is_staff = True
            obj.admin.groups.add(temple_admin_group)
            obj.admin.save()
        
        super().save_model(request, obj, form, change)

@admin.register(Distributor)
class DistributorAdmin(TempleRestrictedExport):

    resource_class = DistributorResource    
    list_display = ('distributor_name', 'distributor_email','distributor_phonenumber',)
    list_filter = ('distributor_name',)
    list_per_page = 10

    def get_exclude(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return ['temple','user']
    

@admin.register(Receipt)
class ReceiptAdmin(TempleRestrictedAdmin):
    list_display = (
        'get_customer_name', 'get_distributor_name', 
        'total_amount', 'get_donation_amount', 
        'paymentMode', 'date', 'notification_status',
        'view_receipts_link'
    )
    list_filter = ('paymentMode', 'date')
    search_fields = ('customer__customer_name', 'distributor__distributor_name')
    readonly_fields = (
        'date', 'get_customer_name', 
        'notification_sent', 'notification_status', 
        'notification_timestamp'
    )
    list_per_page = 10

    def get_customer_name(self,obj):
        return obj.customer.customer_name
    get_customer_name.short_description = 'Customer'

    def get_distributor_name(self,obj):
        return obj.distributor.distributor_name
    get_distributor_name.short_description = 'Distributor'

    def get_donation_amount(self,obj):
        return obj.donation.donation_amount
    get_donation_amount.short_description = 'Donation' 

    def get_exclude(self, request, obj):
        if request.user.is_superuser:
            return []
        return ['customer']
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        distributor_books = DistributorBooks.objects.filter(Distributor = obj.distributor)
        for book in distributor_books:
            check_distributor_stock(book)
    
    # All stuff below is to load receipts, multiply tag in the html file isn't working as of now

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:receipt_id>/receipts/', #changed from distributor_id 
                self.admin_site.admin_view(self.receipt_details_view),
                name='receipt-details',
            ),
        ]
        return custom_urls + urls
    
    def view_receipts_link(self, obj):
        url = reverse('admin:receipt-details', args=[obj.receipt_id])
        return format_html('<a class="button" href="{}">View Receipts</a>', url)
    view_receipts_link.short_description = "Receipts"
    
    def receipt_details_view(self, request, receipt_id):

        receipt = self.get_object(request, receipt_id)

        receipt_books = ReceiptBooks.objects.filter(receipt = receipt)
        
        # Get receipt books for each receipt
        receipt_data = [{
                'receipt': receipt,
                'books': receipt_books,
                'total_books': receipt_books.count(),
            }]
        
        context = {
            'title' : f'Receipt #{receipt.receipt_id} Details',
            'receipt': receipt,
            'receipt_data': receipt_data,
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request, receipt),
            'original': receipt,
            'app_label': self.model._meta.app_label,
        }
        return render(request, 'admin/bm_app/receipts.html', context)
    


# admin.site.register(Books)

@admin.register(Books)
class BooksAdmin(TempleRestrictedAdmin):
   
    list_display = ('book_name', 'book_author', 'book_language', 'book_price')
    search_fields = ('book_name', 'book_author')
    list_filter = ('book_language', 'book_category', 'temple')
    ordering = ('book_name',)
    list_per_page = 10


    def get_exclude(self, request, obj):
        if request.user.is_superuser:
            return []
        return ['temple']   

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            temple = Temple.objects.get(admin = request.user)
            obj.temple = temple
        super().save_model(request, obj, form, change)


@admin.register(MasterInventory)
class MasterInventoryAdmin(TempleRestrictedAdmin):

    list_display = ('book', 'stock',)
    search_fields = ('book__book_name',)
    list_per_page = 10  

    
    def get_exclude(self, request,obj):
        if request.user.is_superuser:
            return []
        return ['temple']

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            temple = Temple.objects.get(admin=request.user)
            obj.temple = temple

        try:
            mast_inven = MasterInventory.objects.get(book = obj.book, temple = temple)
            mast_inven.stock += obj.stock
            mast_inven.save()
        
        except:
            super().save_model(request, obj, form, change)

        
@admin.register(BookAllocation)
class BookAllocationAdmin(TempleRestrictedAdmin):
    list_display = ('get_distributor_name', 'allocation_date','allocation_id')
    search_fields = ('distributor__distributor_name',)
    list_filter =  ('distributor__distributor_name', 'allocation_date',)
    list_per_page = 10


    def get_distributor_name(self, obj):
       return obj.distributor.distributor_name
    get_distributor_name.short_description = 'Distributor'
    
    def save_model(self, request, obj, form, change):
        
        if not request.user.is_superuser:
            temple = Temple.objects.get(admin = request.user)
            obj.temple = temple
            
            #write the logic here for inventory automation here try!!
            
            query = BookAllocationDetail.objects.filter(allocation_id = obj.allocation_id)
            for objects in query :
                distributorBooks = DistributorBooks(distributor_id = "obj.distributor_id", book_name = 
                                "objects.book.book_name", book_author = "objects.book.book_author", 
                                book_language = "objects.book.book_language", book_price = "objects.price", 
                                book_category = "objects.book.book_category", book_stock = "objects.quantity")
        super().save_model(request, obj, form, change)
        
    def get_exclude(self, request, obj):
        if request.user.is_superuser:
            return []
        return ['temple']   
    
     
@admin.register(BookAllocationDetail)
class BookAllocationDetailAdmin(TempleRestrictedAdmin):
    list_display = ('allocation_id', 'get_book_name','quantity', 'price')
    search_fields = ('allocation_id__allocation_id',)
    list_filter = ('allocation_id__allocation_id',)
    list_per_page = 10

    
    def get_book_name(self, obj):
        return obj.book.book_name
    get_book_name.short_description = 'Book Name'

    
    def save_model(self, request, obj, form, change):
        
        if not request.user.is_superuser:
            temple = Temple.objects.get(admin = request.user)
            obj.temple = temple
            
            try: 
                
                with transaction.atomic():                    
                    try:
                        master_inventory = MasterInventory.objects.get(book = obj.book, temple = temple)
                        if master_inventory.stock < obj.quantity:
                            messages.error(request, f"Not enough stock for {obj.book.book_name}. Available: {master_inventory.stock}")
                            raise Exception("Insufficient Inventory")
                        
                        master_inventory.stock -= obj.quantity
                        master_inventory.save()
                        
                        #checking if the inventory is low in stocks
                        
                        check_master_inventory_stock(master_inventory)
                        
                        
                    except MasterInventory.DoesNotExist:
                        messages.error(request, f"No inventory record found for {obj.book.book_name}.")
                        raise Exception("Inventory Record Not found")
                    
                    allocation = BookAllocation.objects.get(allocation_id=obj.allocation_id)
                    distributor_obj = allocation.distributor 
                    
                    try:
                        dist_book = DistributorBooks.objects.get(
                            distributor = distributor_obj,
                            book_name = obj.book.book_name
                        )
                        
                        dist_book.book_stock += obj.quantity
                        dist_book.save()
                        messages.success(request, f"Updated inventory for {obj.book.book_name}. New stock: {dist_book.book_stock}, Distributor : {distributor_obj.distributor_name}")

                        notify_new_book_allocation(
                            distributor = distributor_obj,
                            book_name = obj.book.book_name,
                            quantity = obj.quantity,
                            temple= temple
                            
                        )
                        
                    except DistributorBooks.DoesNotExist :
                        DistributorBooks.objects.create(  
                            temple = temple,  
                            distributor=distributor_obj,
                            book_name=obj.book.book_name,
                            book_author=obj.book.book_author,
                            book_language=obj.book.book_language,
                            book_price=obj.price,
                            book_category=obj.book.book_category,
                            book_stock=obj.quantity
                        )
                        
                        notify_new_book_allocation(
                            distributor = distributor_obj,
                            book_name = obj.book.book_name,
                            quantity = obj.quantity,
                            temple= temple
                            
                        )
                        
                    messages.success(request, f"Added {obj.book.book_name} to distributor's inventory. Quantity: {obj.quantity}")
                    super().save_model(request, obj, form, change)

            except Exception as e:      
                if str(e) not in ["Insufficient Inventory" , "Inventory Record Not found"] :
                    messages.error(request, f"Error updating inventory: {str(e)}")
                    return
        else:           
            super().save_model(request, obj, form, change)
        
    def get_exclude(self, request, obj):
        if request.user.is_superuser:
            return []
        return ['temple'] 
    

@admin.register(Customer)
class CustomerAdmin(TempleRestrictedExport):
    resource_class = CustomerResourse

    list_display = ('customer_name', 'customer_phone','customer_city', 'customer_occupation')
    search_fields = ('customer_name','customer_phone', 'customer_city', 'customer_occupation')
    list_filter = ('customer_city', 'customer_occupation','Date')   
    list_per_page = 10
    readonly_fields = ('customer_name','customer_phone','customer_city', 'customer_occupation','customer_remarks',)
    
    def get_exclude(self, request,obj):
        if request.user.is_superuser:
            return []
        return ['temple']

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            temple = Temple.objects.get(admin=request.user)
            obj.temple = temple
            
        super().save_model(request, obj, form, change)

# @admin.register(Notification)
# class NotificationAdmin(TempleRestrictedAdmin):
#     list_display = ('user_type', 'message', 'status')

#     def get_exclude(self, request,obj):
#         if request.user.is_superuser:
#             return []
#         return ['temple']

#     def save_model(self, request, obj, form, change):
#         if not request.user.is_superuser:
#             temple = Temple.objects.get(admin=request.user)
#             obj.temple = temple
            
#         super().save_model(request, obj, form, change)

#Find out why donation isn't visible
@admin.register(Donation)
class DonationAdmin(TempleRestrictedExport):

    resource_class = DonationResource

    list_display = ('get_customer_name', 'donation_date', 'donation_amount', 'donation_purpose',)
    search_fields = ('customer__customer_name',)
    # bug both arent working togehthe
    list_filter = ('donation_date',)
    list_per_page = 10


    def get_customer_name(self, obj):
        return obj.customer.customer_name if obj.customer else "No Customer"
    get_customer_name.short_description = 'Customer'

    def get_exclude(self, request,obj):
        if request.user.is_superuser:
            return []
        return ['temple']

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            temple = Temple.objects.get(admin=request.user)
            obj.temple = temple
            
        super().save_model(request, obj, form, change)


# Think about registering this
# @admin.register(DistributorBooks)
# class DistributorBooksAdmin(TempleRestrictedAdmin):
#     list_display = ('distributor_id', 'book_name', 'book_stock',)

#     def get_exclude(self, request,obj):
#         if request.user.is_superuser:
#             return []
#         return ['temple']

#     def save_model(self, request, obj, form, change):
#         if not request.user.is_superuser:
#             temple = Temple.objects.get(admin=request.user)
#             obj.temple = temple
            
#         super().save_model(request, obj, form, change)

#extending admin site to add my custom urls




from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import render



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
class DistributorAdmin(TempleRestrictedAdmin):

    list_display = ('distributor_name', 'distributor_email','view_receipts_link')

    def get_exclude(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return ['temple','user']
    
    # All stuff below is to load receipts, multiply tag in the html file isn't working as of now

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:distributor_id>/receipts/',
                self.admin_site.admin_view(self.distributor_receipts_view),
                name='distributor-receipts',
            ),
        ]
        return custom_urls + urls
    
    def view_receipts_link(self, obj):
        url = reverse('admin:distributor-receipts', args=[obj.distributor_id])
        return format_html('<a class="button" href="{}">View Receipts</a>', url)
    view_receipts_link.short_description = "Receipts"
    
    def distributor_receipts_view(self, request, distributor_id):
        distributor = self.get_object(request, distributor_id)
        receipts = Receipt.objects.filter(distributor=distributor)
        
        # Get receipt books for each receipt
        receipt_data = []
        for receipt in receipts:
            receipt_books = ReceiptBooks.objects.filter(receipt=receipt)
            receipt_data.append({
                'receipt': receipt,
                'books': receipt_books,
                'total_books': receipt_books.count(),
            })
        
        context = {
            'distributor': distributor,
            'receipt_data': receipt_data,
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request, distributor),
            'title': f'Receipts for {distributor.distributor_name}',
            'original': distributor,
            'app_label': self.model._meta.app_label,
        }
        return render(request, 'admin/bm_app/distributor/receipts.html', context)
    

@admin.register(Receipt)
class ReceiptAdmin(TempleRestrictedAdmin):
    list_display = ('get_customer_name', 'get_distributor_name', 'total_amount', 'get_donation_amount', 'paymentMode', 'date')
    list_filter = ('paymentMode', 'date')
    search_fields = ('customer__customer_name', 'distributor__distributor_name')
    readonly_fields = ('date','get_customer_name')

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


# admin.site.register(Books)

@admin.register(Books)
class BooksAdmin(TempleRestrictedAdmin):
   
    list_display = ('book_name', 'book_author', 'book_language', 'book_price')
    search_fields = ('book_name', 'book_author')
    list_filter = ('book_language', 'book_category', 'temple')
    ordering = ('book_name',)

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
    
    def get_exclude(self, request,obj):
        if request.user.is_superuser:
            return []
        return ['temple']

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            temple = Temple.objects.get(admin=request.user)
            obj.temple = temple
        super().save_model(request, obj, form, change)

    

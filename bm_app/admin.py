from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *

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

admin.site.register(Distributor, TempleRestrictedAdmin)
admin.site.register(Books)
admin.site.register(BooksCategory)
from django.contrib import admin
from .models import Distributor, MasterInventory, DistributorBooks

# Register your models here.
admin.site.register(Distributor)
admin.site.register(MasterInventory)
admin.site.register(DistributorBooks)


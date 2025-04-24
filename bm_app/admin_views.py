from django.contrib.admin.views.decorators import staff_member_required
from .models import Books, MasterInventory, Distributor, Customer, Receipt, ReceiptBooks
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

@staff_member_required
def admin_dashboard(request):
    total_books = Books.objects.count()

    total_inventory = MasterInventory.objects.aggregate(Sum('stock'))['stock__sum'] or 0

    distributor_count = Distributor.objects.count()

    customer_count = Customer.objects.count()

    total_revenue = Receipt.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    total_distributed = ReceiptBooks.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0

    

    #Filtering b last 30 days

    today = timezone.now().date()
    last_month = today - timedelta(days=30)

    recent_distributed = ReceiptBooks.objects.filter(
        receipt__date__gte = last_month
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0

    recent_revenue = Receipt.objects.filter(
        date__gte = last_month
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0 

    context = {
        'total_books' : total_books,
        'total_inventory' : total_inventory,
        'distributor_count' : distributor_count,
        'customer_count' : customer_count,
        'total_revenue' : total_revenue,
        'total_distributed' : total_distributed,
        'recent_distributed' : recent_distributed,
        'recent_revenue' : recent_revenue,
    }

    return render(request, 'admin/dashboard.html', context)
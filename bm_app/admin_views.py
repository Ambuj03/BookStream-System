from django.contrib.admin.views.decorators import staff_member_required
from .models import Books, MasterInventory, Distributor, BooksCategory, Customer, Receipt, ReceiptBooks
from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

from django.http import JsonResponse
from django.db.models import Sum, F

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


@staff_member_required
def get_monthly_distribution_data(request):
    
    # Get data for last 90 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=90)
    
    # Group by month using Django's ORM
    monthly_data = (
        ReceiptBooks.objects
        .filter(receipt__date__gte=start_date, receipt__date__lte=end_date)
        .annotate(month=TruncMonth('receipt__date'))
        .values('month')
        .annotate(total=Sum('quantity'))
        .order_by('month')
    )
    
    # Format for Chart.js
    labels = []
    data = []
    
    # If we got data, format it properly
    if monthly_data:
        for item in monthly_data:
            month_date = item['month']
            month_name = month_date.strftime('%b %Y')  # Format like "Apr 2025"
            labels.append(month_name)
            data.append(item['total'])
    else:
        # Fallback to sample data if no results
        labels = ['Jan 2025', 'Feb 2025', 'Mar 2025', 'Apr 2025']
        data = [15, 22, 18, 20]
    
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'Books Distributed',
            'data': data,
            'backgroundColor': 'rgba(26, 61, 102, 0.7)',
            'borderColor': '#1a3d66',
            'borderWidth': 1
        }]
    }
    
    return JsonResponse(chart_data)


@staff_member_required
def get_top_distributors(request):
    
    #getting top 10 distributors
    top_distributors = (ReceiptBooks.objects
        .values('receipt__distributor__distributor_name')
        .annotate(total = Sum('quantity'))
        .order_by('-total')[:10]
    )

    labels = []
    data = []

    # if top_distributors:
    for item in top_distributors:
        distributor_name = item['receipt__distributor__distributor_name']
        labels.append(distributor_name)
        data.append(item['total'])

    chart_data = {
        'labels' : labels,
        'datasets' : [{
            'label' : 'Books Distributed',
            'data' : data,

        }]
    }

    return JsonResponse(chart_data)


@staff_member_required
def get_top_categories(request):
    # Get total quantity of books distributed
    total_books = ReceiptBooks.objects.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Use book_name to match with Books table and get categories
    categories_data = []
    total_matched = 0  # Track total books matched to categories
    
    # Only showing the two categories
    for category in BooksCategory.objects.all():
        # Find all books in this category
        books_in_category = Books.objects.filter(book_category=category).values_list('book_name', flat=True)
        
        # Find distribution numbers for these books
        quantity = ReceiptBooks.objects.filter(book_name__in=books_in_category).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        total_matched += quantity
        
        categories_data.append({
            'name': category.bookscategory_name,
            'quantity': quantity
        })
    
    # Calculate percentages based on matched totals (not total_books)
    for item in categories_data:
        if total_matched > 0:
            item['percentage'] = round((item['quantity'] / total_matched) * 100, 1)
        else:
            item['percentage'] = 0
    
    # Prepare chart data
    labels = [item['name'] for item in categories_data]
    data = [item['percentage'] for item in categories_data]
    
    # Use sample data if nothing found
    if not data:
        labels = ['Category 1', 'Category 2']
        data = [60, 40]
    
    chart_data = {
        'labels': labels,
        'datasets': [{
            'data': data,
            'backgroundColor': ['#1a3d66', '#38a169'],
            'borderColor': '#ffffff',
            'borderWidth': 2
        }]
    }
    
    return JsonResponse(chart_data)

@staff_member_required
def get_revenue_data(request):
    # Get data for last 6 months
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=180)
    
    # Get monthly book sales revenue and donation revenue
    book_revenue = (
        ReceiptBooks.objects
        .filter(receipt__date__gte=start_date)
        .annotate(month=TruncMonth('receipt__date'))
        .values('month')
        .annotate(revenue=Sum(F('quantity') * F('book_price')))
        .order_by('month')
    )
    
    donation_revenue = (
        Receipt.objects
        .filter(date__gte=start_date)
        .filter(donation__isnull=False)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(revenue=Sum('donation'))
        .order_by('month')
    )
    
    # Combine data by month - use datetime objects as keys instead of strings
    months_data = {}
    
    for item in book_revenue:
        month_date = item['month']  # This is a datetime object
        if month_date not in months_data:
            months_data[month_date] = {'book_revenue': 0, 'donation_revenue': 0}
        months_data[month_date]['book_revenue'] = float(item['revenue'])
    
    for item in donation_revenue:
        month_date = item['month']  # This is a datetime object
        if month_date not in months_data:
            months_data[month_date] = {'book_revenue': 0, 'donation_revenue': 0}
        months_data[month_date]['donation_revenue'] = float(item['revenue'])
    
    # Sort chronologically by date
    sorted_months = sorted(months_data.keys())
    
    # Prepare chart data with chronologically sorted months
    labels = [month.strftime('%b %Y') for month in sorted_months]
    book_data = [months_data[month]['book_revenue'] for month in sorted_months]
    donation_data = [months_data[month]['donation_revenue'] for month in sorted_months]
    
    # Use sample data if empty
    if not labels:
        labels = ['Jan 2025', 'Feb 2025', 'Mar 2025', 'Apr 2025']
        book_data = [1200, 1500, 1300, 1700]
        donation_data = [500, 700, 600, 900]
    
    chart_data = {
        'labels': labels,
        'datasets': [
            {
                'label': 'Book Revenue',
                'data': book_data,
                'backgroundColor': 'rgba(26, 61, 102, 0.7)',
                'borderColor': '#1a3d66',
                'borderWidth': 1,
                'order': 1
            },
            {
                'label': 'Donations',
                'data': donation_data,
                'backgroundColor': 'rgba(56, 161, 105, 0.7)',
                'borderColor': '#38a169',
                'borderWidth': 1,
                'order': 1
            }
        ]
    }
    
    return JsonResponse(chart_data)
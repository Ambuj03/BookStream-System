from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Receipt, ReceiptBooks, Distributor, Books, BooksCategory
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth
from django.http import JsonResponse


@login_required
@never_cache
def dashboard(request):

    today = timezone.now().date()
    last_month = today - timedelta(days = 30)

    current_distributor = Distributor.objects.get(user = request.user)

    total_books_distributed = (ReceiptBooks.objects
                                .filter(receipt__distributor = current_distributor)   
                                .aggregate(total = Sum('quantity'))['total'] or 0
                            )

    distributed_last_30 = (ReceiptBooks.objects
                                .filter(receipt__distributor = current_distributor,
                                        receipt__date__gte = last_month)   
                                .aggregate(total = Sum('quantity'))['total'] or 0
                            )

    total_revenue = (Receipt.objects
                        .filter(
                            distributor = current_distributor
                        )
                        .aggregate(Sum('total_amount'))['total_amount__sum'] or 0
                )
    
    recent_revenue = (Receipt.objects
                        .filter(
                            distributor = current_distributor,
                            date__gte = last_month
                        )
                        .aggregate(Sum('total_amount'))['total_amount__sum'] or 0
                )

    context = {
        'total_distributed' : total_books_distributed,
        'recent_distributed' : distributed_last_30,
        'total_revenue' : total_revenue,
        'recent_revenue' : recent_revenue,
    }

    return render(request, 'bm_app/dashboard.html', context)

@login_required
@never_cache
def get_monthly_distribution_data(request):
        
    current_distributor = Distributor.objects.get(user = request.user)

    #data for last 120 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days = 120)

    #grouping data by month
    monthly_data = (
        ReceiptBooks.objects
            .filter(receipt__distributor = current_distributor, 
                    receipt__date__gte=start_date, receipt__date__lte = end_date)
            .annotate(month = TruncMonth('receipt__date'))
            .values('month')
            .annotate(total = Sum('quantity'))
            .order_by('month')
        )   

    #Formatting data for chart js

    labels = []
    data = []

    for item in monthly_data:
        month_date = item['month']
        month_name = month_date.strftime('%b %Y')  # Format like "Apr 2025"
        labels.append(month_name)
        data.append(item['total'])

    chart_data = {
        'labels' : labels,
        'datasets' : [{
            'label' : 'Books Distributed',
            'data' : data,
            'backgroundColor': 'rgba(26, 61, 102, 0.7)',
            'borderColor': '#1a3d66',
            'borderWidth': 1
        }]
    }

    return JsonResponse(chart_data)

@login_required
@never_cache
def get_revenue_data(request):

    current_distributor = Distributor.objects.get(user = request.user)

    #Data for last 6months
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=180) 

    book_revenue = (Receipt.objects
                    .filter(distributor = current_distributor,
                            date__gte = start_date)
                    .annotate(month = TruncMonth('date'))
                    .values('month')
                    .annotate(revenue = Sum('total_amount'))
                    .order_by('month')
                    )
    
    donation_revenue = (
        Receipt.objects
        .filter(distributor = current_distributor,
            date__gte=start_date)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(revenue=Sum('donation__donation_amount'))
        .order_by('month')
    )

    labels = []
    book_revenue_data = []
    donation_revenue_data = []

    for item in book_revenue:
        month_date = item['month']
        month_name = month_date.strftime('%b %Y')  # Format like "Apr 2025"
        labels.append(month_name)
        book_revenue_data.append(item['revenue'])

    for item in donation_revenue:
        donation_revenue_data.append(item['revenue'])

    
    chart_data = {
        'labels': labels,
        'datasets': [
            {
                'label': 'Book Revenue',
                'data': book_revenue_data,
                'backgroundColor': 'rgba(26, 61, 102, 0.7)',
                'borderColor': '#1a3d66',
                'borderWidth': 1,
                'order': 1
            },
            {
                'label': 'Donations',
                'data': donation_revenue_data,
                'backgroundColor': 'rgba(56, 161, 105, 0.7)',
                'borderColor': '#38a169',
                'borderWidth': 1,
                'order': 1
            }
        ]
    }
    
    return JsonResponse(chart_data)

@login_required
@never_cache
def get_top_categories(request):

    categories_date = []
    total_matched = 0

    for category in BooksCategory.objects.all():
        books_in_this_cat = Books.objects.filter()
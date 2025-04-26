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

    #getting days from frontend via api
    days = int(request.GET.get('days' , 180))

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

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

    #getting days from frontend via api
    days = int(request.GET.get('days' , 180))

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days) 

    book_revenue = (Receipt.objects
                    .filter(distributor = current_distributor,
                            date__gte=start_date, date__lte = end_date)
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

    current_distributor = Distributor.objects.get(user = request.user)

    #getting days from frontend via api
    days = int(request.GET.get('days' , 180))

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days) 

    categories_data = []
    total_matched = 0

    for category in BooksCategory.objects.all():
        books_in_this_cat = Books.objects.filter(book_category = category).values_list('book_name', flat= True)

        quantity = (ReceiptBooks.objects
                    .filter(receipt__distributor = current_distributor, 
                            book_name__in = books_in_this_cat,
                            receipt__date__gte=start_date, receipt__date__lte = end_date)
                    .aggregate(total = Sum('quantity'))['total'] or 0
                    )
        total_matched += quantity

        categories_data.append({
            'name' : category.bookscategory_name,
            'quantity' : quantity
        })


    #Calculating percentage now

    for item in categories_data:
        if total_matched > 0:
            item['percentage'] = round((item['quantity'] / total_matched) * 100, 1)
        else :
            item['percentage']  = 0

    
    #Now preparing chart data

    labels = [item['name'] for item in categories_data]
    data  = [item['percentage'] for item in categories_data]

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


@login_required
@never_cache
def get_top_books(request):

    current_distributor = Distributor.objects.get(user = request.user)

    #getting days from frontend via api
    days = int(request.GET.get('days' , 180))

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days) 

    top_books = (ReceiptBooks.objects
                .filter(receipt__distributor = current_distributor,
                        receipt__date__gte=start_date, receipt__date__lte = end_date)
                .values('book_name')
                .annotate(total = Sum('quantity'))
                .order_by('-total')[:5]
                 )
    
    labels = []
    data = []

    for item in top_books:
        labels.append(item['book_name'])
        data.append(item['total'])

    chart_data = {
        'labels' : labels,
        'datasets' : [{
            'label' : 'Books Distributed',
            'data' : data,

        }]
    }

    return JsonResponse(chart_data)
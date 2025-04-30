from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render
from .models import Receipt, Distributor, ReceiptBooks
from django.core.paginator import Paginator


@login_required
@never_cache
def transaction_history_view(request):

    distributor = Distributor.objects.get(user = request.user)

    #Getting date filters 
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    transactions = (Receipt.objects
                    .filter(distributor = distributor)
                    )
    
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__lte=date_to)

    transactions = transactions.order_by('-date')

    for receipt in transactions:
        receipt_books = ReceiptBooks.objects.filter(receipt = receipt)
        receipt.books = receipt_books
        receipt.books_count = receipt_books.count()

    request_get = request.GET.copy()
    if 'page' in request_get:
        del request_get['page']

    filtered_params = request_get.urlencode()

    paginator = Paginator(transactions, 10)  
    page_number = request.GET.get('page',1)
    page_obj = paginator.get_page(page_number)



    context = {
        'transactions' : page_obj,
        'filters': {
            'date_from': date_from,
            'date_to': date_to,
        },
        'filtered_params' : filtered_params
    }

    return render(request, 'bm_app/transaction_history.html', context)

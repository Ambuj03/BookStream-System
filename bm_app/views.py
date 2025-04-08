from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import signup_form, transaction_form
from .models import *
from django.db.models import Q
from django.core.paginator import Paginator

#for formset related things
from django.db import transaction
from .bookAddForm import  get_book_formset, AddCustomBooks

from django.contrib import messages

from django.shortcuts import get_object_or_404

import json
from django.http import JsonResponse

from django.core.exceptions import ValidationError

from .models import Books, Receipt, Customer, Donation, Distributor,ReceiptBooks, BooksCategory
from decimal import Decimal

from .sms import send_receipt_sms

from .notifications import get_distributor_notifications, mark_notification_as_read

from django.contrib import admin
from .admin import get_admin_notifications

#Showing main page
def main_page(request):
    return render(request,'bm_app/main.html',{})

# showing home page
@login_required(login_url="login")
@never_cache
def home_page(request):
    print(f"DEBUG: User Authenticated: {request.user.is_authenticated}")  # Debug
    print(f"DEBUG: Logged-in User: {request.user}")  # Debug
    return render(request,'bm_app/home.html',{})



@login_required(login_url="login")
@never_cache
def books_api(request):
    # APi endpoint to get all the books.

    distributor = Distributor.objects.get(user = request.user)
    distributor_books = DistributorBooks.objects.filter(distributor = distributor)
    books_data = []

    for dist_book in distributor_books:
        books_data.append({
                    'dist_book_id': dist_book.id,  # DistributorBooks ID for reference
                    'book_id': dist_book.id,
                    'name': dist_book.book_name,
                    'available_quantity': dist_book.book_stock,
                    'price': str(dist_book.book_price)
                })

    return JsonResponse(books_data, safe = False)

# New Transaction form  

@login_required(login_url="login")
@never_cache
def new_transaction_view(request):
    try:
        distributor = Distributor.objects.get(user=request.user)
        
        if request.method == 'POST':
            form = transaction_form(request.POST, distributor=distributor)
            if form.is_valid():
                try:
                    with transaction.atomic():

                        temple_id = distributor.temple.temple_id

                        # Create customer
                        customer = Customer.objects.create(
                            customer_name=form.cleaned_data['customer_name'],
                            customer_phone=form.cleaned_data['customer_phone'],
                            customer_occupation=form.cleaned_data['customer_occupation'],
                            customer_city=form.cleaned_data['customer_city'],
                            customer_remarks=form.cleaned_data['remarks'],
                            temple_id = temple_id
                        )

                        # Create donation
                        donation = Donation.objects.create(
                            customer=customer,
                            donation_amount=form.cleaned_data['donation_amount'],
                            donation_purpose=form.cleaned_data['donation_purpose'],
                            temple_id = temple_id
                        )

                        # Create receipt
                        receipt = Receipt.objects.create(
                            customer=customer,
                            donation=donation,
                            distributor=distributor,
                            paymentMode=form.cleaned_data['paymentMode'],
                            total_amount=Decimal(request.POST.get('total_amount', '0')),
                            temple_id = temple_id
                        )
                        
                        # Process books data
                        books_data = json.loads(request.POST.get('books', '[]'))

                        if not books_data:
                            return JsonResponse({'success' : False,
                                             'error' : 'At least one book must be selected'})
                        
                        for book_data in books_data:
                            dist_book = DistributorBooks.objects.get(
                                id=book_data['dist_book_id'],
                                distributor=distributor
                            )
                            
                            quantity = int(book_data['quantity'])
                            
                            # Validate stock
                            if dist_book.book_stock < quantity:
                                raise ValidationError(f"Insufficient stock for {dist_book.book_name}")
                            
                            # Create receipt book entry
                            ReceiptBooks.objects.create(
                                receipt=receipt,
                                book_name=dist_book.book_name,
                                quantity=quantity,
                                temple_id = temple_id,
                                book_price = dist_book.book_price,
                            )
                            
                            success, message = send_receipt_sms(receipt)
                            
                            # Update stock
                            dist_book.book_stock -= quantity
                            dist_book.save()
                            
                        return JsonResponse({
                            'success': True,
                            'redirect_url': reverse('home')
                        })
                        
                except ValidationError as e:
                    return JsonResponse({'success': False, 'error': str(e)})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})
            
            return JsonResponse({'success': False, 'error': form.errors})
        else:
            form = transaction_form(distributor=distributor)
            return render(request, 'bm_app/new_transaction.html', {'form': form})
            
    except Distributor.DoesNotExist:
        return redirect('login')

@login_required(login_url='login')
@never_cache
def books_view(request):

    # Adding Paginatore logic
    distributor = Distributor.objects.get(user_id = request.user)
    books = Books.objects.filter(temple = distributor.temple)

    search_query = request.GET.get('q', '')
    
    if search_query:
        books = books.filter(
            Q(book_name__icontains=search_query) |
            Q(book_author__icontains=search_query) |
            Q(book_language__icontains=search_query)
        )

    paginator = Paginator(books, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'bm_app/books.html', {
        'page_obj': page_obj, 'search_query' : search_query,
    })



@login_required(login_url='login')
@never_cache
def inventory_view(request):

    distributor = Distributor.objects.get(user = request.user)
    distributorBooks = DistributorBooks.objects.filter(distributor = distributor)
    # inventory = DistributorInventory.objects.all()

    return render(request, 'bm_app/inventory.html', {'distributorBooks': distributorBooks})


# @login_required(login_url='login')
# @never_cache
# def add_books(request):
#     if request.method == 'POST':
#             distributor = Distributor.objects.get(user = request.user)
#             form = bookAddForm(request.POST, distributor=distributor)
#             if form is_valid():
#                 form.save()
#                 return redirect('inventory')
        
#     else :
#         form = bookAddForm()
        
#     return render(request, 'bm_app/subpage/addBbtBooks.html', {'form' : form})

def add_books(request):
                
    distributor = Distributor.objects.get(user = request.user)

    if request.method == 'POST':
            formset = get_book_formset(distributor, request.POST)
            if formset.is_valid():
                saved_books = []  # List to store returned books
                with transaction.atomic(): # Ensures all books are added or none
                    try:  
                        for form in formset:
                            if form.cleaned_data:
                                form.save()
                        return redirect('inventory')
                    except Exception as e:
                        messages.error(request, 'Error Saving Books')
                        return redirect('add_books')
        
    else :
        formset = get_book_formset(distributor)
        
    return render(request, 'bm_app/subpage/addBbtBooks.html', {'formset' : formset})

def delete_book(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(DistributorBooks, id = book_id) #Tradition filter will work well as well 
        book.delete()
        messages.success(request, 'Book deleted successfully')
        return redirect('inventory')
    
    

@login_required(login_url='login')
@never_cache
def add_custom_books(request): 

    distributor = Distributor.objects.get(user = request.user)
    if request.method == 'POST':
        form = AddCustomBooks(request.POST, distributor = distributor)
        if form.is_valid():
            form.save()
            return redirect('inventory')
    else:
        form = AddCustomBooks(distributor = distributor)

    return render(request, 'bm_app/subpage/addCustomBooks.html', {'form' : form})


# Writing a class inheriting Authentication form for field validation

class CustomAuthenticationForm(AuthenticationForm):
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if len(username) > 15:
            raise ValidationError("Username should be fewer than 15 Characters")
        if not username.isalnum():
            raise ValidationError("Username must contain only letters and numbers.")
        return username 
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("Password must contain atleast 8 characters")
        return password

def login_page(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request,user)
                return redirect('home')
        else:
            return render(request, 'bm_app/login.html', {'form': form})
    else:
        form = CustomAuthenticationForm()
    return render(request, 'bm_app/login.html', {'form': form})

def signup_page(request):
    if request.method == "POST":
        form = signup_form(request.POST)
        if form.is_valid():
            # Create User with default fields
            user = form.save()
            return redirect('login')
    else:
        form = signup_form()
    return render(request, 'bm_app/signup.html', {'form': form})


#logout view
def logout_view(request):
    logout(request)
    return redirect('main')

@login_required
def get_distributor_books(request):
    try:
        distributor = Distributor.objects.get(user=request.user)
        search_term = request.GET.get('term', '')
        # print(f"Search term: {search_term}")  # Debug print
        
        books = DistributorBooks.objects.filter(
            distributor=distributor,
            book_name__icontains=search_term,
            book_stock__gt=0
        ).values('id', 'book_name', 'book_price', 'book_stock')[:10]
        
        # print(f"Found books: {books}")  # Debug print
        
        results = {
            'results': [{'id': book['id'], 
                        'text': book['book_name'],
                        'price': book['book_price'],
                        'stock': book['book_stock']} 
                       for book in books]
        }
        # print(f"Returning: {results}")  # Debug print
        return JsonResponse(results)
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug print
        return JsonResponse({'error': str(e)}, status=400)
    

# View for notifiations

@login_required
def distributor_notifications(request):
    
    # add try and except if required
        distributor = Distributor.objects.get(user = request.user)
        notifications = get_distributor_notifications(distributor.distributor_id)

        filter_param = request.GET.get('filter')
        if filter_param == 'unread':
            notifications = [n for n in notifications if n.status == 'Unread']
        elif filter_param == 'read':
            notifications = [n for n in notifications if n.status == 'Read']

        #Adding pagi logic
        paginator = Paginator(notifications, 4)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'bm_app/distributor_notifications.html', {
            'notifications' : page_obj,
            'page_obj' : page_obj
        })
        
@login_required
def mark_notification_read(request, notification_id):
    if request.method == 'POST':
        try:
            mark_notification_as_read(notification_id)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def get_unread_notification_count(request):
    
    distributor = Distributor.objects.get(user = request.user)
    count = get_distributor_notifications(distributor.distributor_id).filter(status = 'Unread').count()
    return JsonResponse({'count' : count})

@login_required
def admin_notifications_view(request):
    notifications_list = get_admin_notifications(request.user)
    
    filter_param = request.GET.get('filter')
    if filter_param == 'unread':
        notifications_list = [n for n in notifications_list if n.status == 'Unread']
    elif filter_param == 'read':
        notifications_list = [n for n in notifications_list if n.status == 'Read']
    
    # Paginate notifications
    paginator = Paginator(notifications_list, 6) 
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'page_obj': page_obj,
        'title': 'Notifications',
        'has_permission': True,
        'site_header': admin.site.site_header,
        'site_title': admin.site.site_title,
        'index_title': admin.site.index_title,
    }
    
    return render(request, 'admin/notifications.html', context)








from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import signup_form, transaction_form
from .models import Distributor, Books, DistributorInventory, DistributorBooks
from django.db.models import Q
from django.core.paginator import Paginator

#for formset related things
from django.db import transaction
from .bookAddForm import  get_book_formset, AddCustomBooks

from django.contrib import messages

from django.shortcuts import get_object_or_404

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

# New Transaction form  

@login_required(login_url="login")
@never_cache
def new_transaction_view(request):
    try:
        # Get the distributor instance for the logged-in user
        distributor = Distributor.objects.get(user=request.user)
        
        if request.method == 'POST':
            form = transaction_form(request.POST, distributor=distributor)
            if form.is_valid():
                receipt = form.save()
                return redirect('home')
        else:
            form = transaction_form(distributor=distributor)
            
        return render(request, 'bm_app/new_transaction.html', {
            'form': form
        })
    except Distributor.DoesNotExist:
        # Handle the case where no distributor exists for the user
        return redirect('login')

@login_required(login_url='login')
@never_cache
def books_view(request):

    # Adding Paginatore logic
    books = Books.objects.all()

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
    inventory = DistributorInventory.objects.filter(distributor = distributor)
    distributorBooks = DistributorBooks.objects.filter(distributor = distributor)
    # inventory = DistributorInventory.objects.all()

    return render(request, 'bm_app/inventory.html', {'inventory' : inventory, 'distributorBooks': distributorBooks})


# @login_required(login_url='login')
# @never_cache
# def add_books(request):
#     if request.method == 'POST':
#             distributor = Distributor.objects.get(user = request.user)
#             form = bookAddForm(request.POST, distributor=distributor)
#             if form.is_valid():
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



def login_page(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
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
        form = AuthenticationForm()
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

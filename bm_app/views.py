from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import signup_form, transaction_form
from .models import Distributor, Books
from django.db.models import Q
from django.core.paginator import Paginator


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
            
            # Create Distributor with additional details
            Distributor.objects.create(
                distributor_name=form.cleaned_data['distributor_name'],
                distributor_email=form.cleaned_data['distributor_email'],
                distributor_phonenumber=form.cleaned_data['distributor_phonenumber'],
                distributor_address=form.cleaned_data['distributor_address'],
                distributor_age=form.cleaned_data['distributor_age'],
                admin=form.cleaned_data['admin']
            )
            return redirect('login')
    else:
        form = signup_form()
    return render(request, 'bm_app/signup.html', {'form': form})


#logout view
def logout_view(request):
    logout(request)
    return redirect('main')

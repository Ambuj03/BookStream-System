from django.shortcuts import render, redirect, HttpResponse
from .forms import transaction_form, login_form, signup_form

# # login required things from documentation
from django.contrib.auth import login,authenticate, logout

# from django.utils import timezone
from .models import Distributor, DistributorProfile
from django.contrib.auth.hashers import make_password  # To hash passwords before saving

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


#Showing main page
def main_page(request):
    return render(request,'bm_app/main.html',{})

# showing home page
# @login_required
def home_page(request):
    print(f"DEBUG: User Authenticated: {request.user.is_authenticated}")  # Debug
    print(f"DEBUG: Logged-in User: {request.user}")  # Debug
    return render(request,'bm_app/home.html',{})

# New Transaction form  

@login_required(login_url="bm_app:login")  # Ensures only logged-in users can access
def new_transaction_view(request):
    print("User:", request.user)  # Debugging to see the user object
    print("Is Authenticated:", request.user.is_authenticated)  # Check if logged in

    if request.user.is_authenticated:
        try:
            distributor = Distributor.objects.get(email=request.user.email)
            print("Distributor Found:", distributor)
        except Distributor.DoesNotExist:
            return HttpResponse("Distributor not found", status=400)

        if request.method == 'POST':
            my_form = transaction_form(request.POST, distributor=request.user)
            if my_form.is_valid():
                my_form.save(request)
                return redirect('bm_app:home')
            else:
                return render(request, 'bm_app/new_transaction.html', {'form': my_form})
        else:
            my_form = transaction_form()
        return render(request, 'bm_app/new_transaction.html', {'form': my_form})

    return redirect("bm_app:login")  # If user is not logged in, redirect


def login_page(request):
    if request.method == 'POST':
        form = login_form(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = Distributor.objects.get(email=email)
            except Distributor.DoesNotExist:
                return render(request, "bm_app/login.html", 
                            {'form': form, "error": "Invalid Credentials"})

            if user and user.check_password(password):
                login(request, user)
                # Create profile if it doesn't exist
                DistributorProfile.objects.get_or_create(distributor=user)
                return redirect('bm_app:profile')  # Redirect to profile page
            
            return render(request, "bm_app/login.html", 
                        {'form': form, "error": "Invalid Credentials"})
    else:
        form = login_form()
    return render(request, "bm_app/login.html", {'form': form})


def signup_page(request):
    if request.method == "POST":
        form = signup_form(request.POST)
        if form.is_valid():
            # Extract all cleaned data from the form
            distributor = form.save(commit=False)  # Don't save yet
            distributor.password = make_password(form.cleaned_data["password1"])  # Hash password
            distributor.save()  # Now save the distributor

            return redirect("bm_app:login")  # Redirect to login after signup
        else:
            return render(request, "bm_app/signup.html", {"form": form})  # Re-render form with errors
    else:
        form = signup_form()  # Empty form for GET request
    return render(request, "bm_app/signup.html", {"form": form})

@require_http_methods(["GET", "POST"])  # Allow both GET and POST methods
def logout_view(request):
    logout(request)
    return redirect('bm_app:login')  # Explicitly redirect to the login page using namespace

def book_search(request):
    # For now, render a simple template
    return render(request, 'bm_app/book_search.html', {})

@login_required(login_url="bm_app:login")
def profile_view(request):
    profile, created = DistributorProfile.objects.get_or_create(distributor=request.user)
    distribution_history = profile.get_distribution_history()
    total_books = profile.get_total_books_distributed()
    
    context = {
        'profile': profile,
        'distribution_history': distribution_history,
        'total_books': total_books,
    }
    return render(request, 'bm_app/profile.html', context)
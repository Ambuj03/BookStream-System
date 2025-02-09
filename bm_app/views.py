from django.shortcuts import render, redirect, HttpResponse
from .forms import transaction_form, login_form, signup_form

# # login required things from documentation
from django.contrib.auth import login,authenticate

# from django.utils import timezone
from .models import Distributor
from django.contrib.auth.hashers import make_password  # To hash passwords before saving

from django.contrib.auth.decorators import login_required




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

@login_required(login_url="login")  # Ensures only logged-in users can access
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
                return redirect('home')
            else:
                return render(request, 'bm_app/new_transaction.html', {'form': my_form})
        else:
            my_form = transaction_form()
        return render(request, 'bm_app/new_transaction.html', {'form': my_form})

    return redirect("login")  # If user is not logged in, redirect




def login_page(request):
    if request.method == 'POST':
        form = login_form(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            print(f"Attempting login with: {email} / {password}")  # Debugging

            try:
                user = Distributor.objects.get(email=email)  # Fetch user by email
                print(f"User found in DB: {user}")  # Debugging
            except Distributor.DoesNotExist:
                print("User not found in DB")  # Debugging
                return render(request, "bm_app/login.html", {'form': form, "error": "Invalid Credentials"})

            # Authenticate user
            user = Distributor.objects.filter(email=email).first()

            if user and user.check_password(password):
                login(request, user)
                return redirect('home')
            print(f"Authentication result: {user}")  # Debugging

            if user is not None:
                login(request, user)  # Log in the user
                print(f"User {user} logged in successfully")  # Debugging
                return redirect('home')
            else:
                print("Authentication failed")  # Debugging
                return render(request, "bm_app/login.html", {'form': form, "error": "Invalid Credentials"})
        
        else:
            print("Invalid form data")  # Debugging
            return render(request, "bm_app/login.html", {'form': form, "error": "Invalid form"})
    
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

            return redirect("login")  # Redirect to login after signup
        else:
            return render(request, "signup.html", {"form": form})  # Re-render form with errors
    else:
        form = signup_form()  # Empty form for GET request
    return render(request, "signup.html", {"form": form})
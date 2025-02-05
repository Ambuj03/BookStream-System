from django.shortcuts import render, redirect, HttpResponse
from .forms import transaction_form, login_form, signup_form

# # login required things from documentation
from django.contrib.auth import login,authenticate

# from django.utils import timezone
from .models import Distributor
from django.contrib.auth.hashers import make_password  # To hash passwords before saving




#Showing main page
def main_page(request):
    return render(request,'bm_app/main.html',{})

# showing home page
def home_page(request):
    return render(request,'bm_app/home.html',{})

# New Transaction form
def new_transaction_view(request):

    if request.method == 'POST':
        print(request.POST)
        my_form = transaction_form(request.POST) #to be used according to the Form/ModelForm used
        if my_form.is_valid():
            my_form.save()
            return redirect('home')
        
    else:
        my_form = transaction_form()
        # context = {
        #     'form' : my_form
        # }
    return render(request, 'bm_app/new_transaction.html', {'form' : my_form})


def login_page(request):
    if request.method == 'POST':
        form = login_form(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = Distributor.objects.get(email=email)  # Fetch user by email
            except Distributor.DoesNotExist:
                user = None

            if user and user.check_password(password):  # Verify password
                login(request, user)  # Log the user in
                return redirect('home')  # Use the name from `urls.py`
            else:
                return render(request, "bm_app/login.html", {'form': form, "error": "Invalid Credentials"})
        else:
            return render(request, "bm_app/login.html", {'form': form, "error": "Invalid form"})
    else:
        form = login_form()
    return render(request, "bm_app/login.html", {'form': form})



def signup_page(request):
    if request.method == "POST":
        form = signup_form(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]
            admin = form.cleaned_data["admin"]  # Fetch selected admin

            if not admin:
                return HttpResponse("Admin selection is required!", status=400)

            # Create a new distributor
            distributor = Distributor.objects.create(
                email=email,
                password=make_password(password),  # Hash the password
                admin=admin  # Assign selected admin
            )
            distributor.save()

            return redirect("login_page")  # Redirect to login after signup
        else:
            return render(request, "signup.html", {"form": form})  # Re-render with errors
    else:
        form = signup_form()  # Empty form for GET request
    return render(request, "signup.html", {"form": form})

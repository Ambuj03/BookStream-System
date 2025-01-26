from django.shortcuts import render, get_object_or_404, redirect


#Showing home page
def home_page(request):
    return render(request,'bm_app/home.html',{})

# showing login page
def login_page(request):
    return render(request,'bm_app/login.html',{})

# showing signup page
def signup_page(request):
    return render(request,'bm_app/signup.html',{})




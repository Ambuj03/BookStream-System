from django.urls import path
from .views import main_page, login_page, signup_page, home_page

urlpatterns = [
    path('', main_page, name='main'),
    path('login/', login_page, name='login'),
    path('signup/', signup_page, name='signup'),
    path('home/', home_page, name='home'),
]
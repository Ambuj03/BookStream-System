from django.urls import path
from .views import main_page, login_page, signup_page, home_page, new_transaction_view, logout_view    

urlpatterns = [
    path('', main_page, name='main'),
    path('login/', login_page, name='login'),
    path('signup/', signup_page, name='signup'),
    path('home/', home_page, name='home'),
    path('home/new_transaction', new_transaction_view, name='new_transaction'),
    path('logout/', logout_view, name='logout'),
]
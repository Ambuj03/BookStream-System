from django.urls import path
from .views import main_page, login_page, signup_page, home_page, new_transaction_view
from .views import login_view

urlpatterns = [
    path('', main_page, name='main'),
    path('login/', login_view, name='login'),
    path('signup/', signup_page, name='signup'),
    path('home/', home_page, name='home'),
    path('home/new_transaction', new_transaction_view),
    # path('login/', login_view, name = "login"),
]
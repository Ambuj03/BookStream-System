from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import main_page, login_page, signup_page, home_page, new_transaction_view

urlpatterns = [
    path('', main_page, name='main'),
    path('login/', login_page, name='login'),
    path('signup/', signup_page, name='signup'),
    path('home/', home_page, name='home'),
    path('home/new_transaction', new_transaction_view, name='new_transaction'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # path('login/', login_view, name = "login"),
]
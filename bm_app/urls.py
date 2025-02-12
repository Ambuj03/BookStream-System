from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import main_page, login_page, signup_page, home_page, new_transaction_view, book_search, profile_view, logout_view

app_name = 'bm_app'

urlpatterns = [
    path('', main_page, name='main'),
    path('login/', login_page, name='login'),
    path('signup/', signup_page, name='signup'),
    path('home/', home_page, name='home'),
    path('home/new_transaction', new_transaction_view, name='new_transaction'),
    path('book_search/', book_search, name='book_search'),
    path('profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),  # Add this line

    # path('login/', login_view, name = "login"),
]
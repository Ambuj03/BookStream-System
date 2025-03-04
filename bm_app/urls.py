from django.urls import path
from .views import inventory_view, main_page, login_page, signup_page, home_page, new_transaction_view, logout_view,books_view, add_books, add_custom_books


urlpatterns = [
    path('', main_page, name='main'),
    path('login/', login_page, name='login'),
    path('signup/', signup_page, name='signup'),
    path('home/', home_page, name='home'),
    path('home/new_transaction', new_transaction_view, name='new_transaction'),
    path('home/inventory', inventory_view, name = 'inventory'),
    path('home/inventory/add_books', add_books, name = "add_books"),
    path('home/inventory/add_custom_books', add_custom_books, name = "add_custom_books"),
    path('home/books', books_view, name='books'),
    path('logout/', logout_view, name='logout')
]
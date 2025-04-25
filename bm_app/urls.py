from django.urls import path
from .views import inventory_view, main_page, login_page, signup_page
from .views import home_page, new_transaction_view, logout_view,books_view, add_books, add_custom_books, delete_book, get_distributor_books
from .views import books_api
from .views import distributor_notifications, mark_notification_read, get_unread_notification_count
from .dashboard_view import dashboard, get_monthly_distribution_data

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
    path('logout/', logout_view, name='logout'),
    path('delete-book/<int:book_id>/', delete_book, name='delete_book'), 
    path('api/books/', books_api, name='books_api'),
    path('api/distributor-books/', get_distributor_books, name='get_distributor_books'),

    #dashboard urls
    path('home/dashboard/', dashboard, name = 'dashboard'),
    path('api/distributor/monthly-distribution/',get_monthly_distribution_data, name = 'monthly_distribution_data'),

    # notification related urls
    path('notifications/', distributor_notifications, name = 'distributor_notifications'),
    path('notifications/mark-read/<int:notification_id>/', mark_notification_read, name = 'mark_notification_read'),
    path('notifications/count', get_unread_notification_count, name = 'unread_notification_count'),
]
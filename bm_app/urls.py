from django.urls import path
from .views import inventory_view, main_page, login_page, signup_page
from .views import home_page, new_transaction_view, logout_view,books_view, add_books, add_custom_books, delete_book, get_distributor_books
from .views import books_api, landing_page
from .views import distributor_notifications, mark_notification_read, get_unread_notification_count
from .dashboard_view import dashboard, get_monthly_distribution_data,get_top_books, get_revenue_data, get_top_categories
from .transaction_view import transaction_history_view
from .profile_view import view_profile, edit_profile, change_password, profile_dashboard

urlpatterns = [
    path('home1/', landing_page, name = "landing"),
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

    #Transaction History
    path('home/transaction_history/', transaction_history_view, name = 'transaction_history'),

    #dashboard urls
    path('home/dashboard/', dashboard, name = 'dashboard'),
    path('api/distributor/monthly-distribution/',get_monthly_distribution_data, name = 'monthly_distribution_data'),
    path('api/distributor/revenue/',get_revenue_data, name = 'revenue_data'),
    path('api/distributor/categories/',get_top_categories, name = 'top_categories_data'),
    path('api/distributor/top-books/',get_top_books, name = 'top_books_data'),

    # notification related urls
    path('home/notifications/', distributor_notifications, name = 'distributor_notifications'),
    path('notifications/mark-read/<int:notification_id>/', mark_notification_read, name = 'mark_notification_read'),
    path('notifications/count', get_unread_notification_count, name = 'unread_notification_count'),

    #Profile related stuff
    path('profile/dashboard/', profile_dashboard, name='profile_dashboard'),
    path('home/view_profile/', view_profile, name = 'view_profile'),
    path('home/edit_profile/', edit_profile, name = 'edit_profile'),
    path('home/change_password/', change_password, name = 'change_password'),

]
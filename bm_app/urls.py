from django.urls import path
from .views import home_page, login_page, signup_page

urlpatterns = [
    path('', home_page, name='home'),
    path('login/', login_page, name='login'),
    path('signup/', signup_page, name='signup'),
]
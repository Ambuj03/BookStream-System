from django.urls import path
from .import views

urlPatterns = [
    path('bm_app/', views.book_list, name = 'book_list'),
]   
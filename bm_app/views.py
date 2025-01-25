from django.shortcuts import render, get_object_or_404, redirect
from .models import Books

# Listing all the books
def book_list(request):
    books = Books.objects.all()
    return render(request, 'bm_app/templates/bm_app/book_list.html',{'books' : books})
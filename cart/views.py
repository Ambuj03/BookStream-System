from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import CartItem
from bm_app.models import Books
from .forms import AddToCartForm, UpdateCartForm

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            book_id = form.cleaned_data['book_id']
            quantity = form.cleaned_data['quantity']
            
            try:
                book = Books.objects.get(book_id=book_id)
                cart_item, created = CartItem.objects.get_or_create(
                    distributor=request.user,
                    book=book,
                    defaults={'quantity': quantity}
                )
                
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
                    
                return JsonResponse({
                    'status': 'success',
                    'message': 'Added to cart successfully'
                })
            except Books.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Book not found'
                }, status=404)
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    }, status=400)

@login_required
def view_cart(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(distributor=request.user)
    else:
        cart_items = []
    total = sum(item.get_subtotal() for item in cart_items)
    
    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def update_cart(request, item_id):
    try:
        cart_item = CartItem.objects.get(cart_item_id=item_id, distributor=request.user)
        if request.method == 'POST':
            form = UpdateCartForm(request.POST, instance=cart_item)
            if form.is_valid():
                quantity = form.cleaned_data['quantity']
                if quantity > 0:
                    cart_item.quantity = quantity
                    cart_item.save()
                else:
                    cart_item.delete()
                return JsonResponse({'status': 'success'})
    except CartItem.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)
    return JsonResponse({'status': 'error'}, status=400) 
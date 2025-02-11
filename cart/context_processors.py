def cart_context(request):
    try:
        from .models import CartItem
        cart_count = CartItem.objects.filter(distributor=request.user).count() if request.user.is_authenticated else 0
    except Exception:
        cart_count = 0
    return {'cart_count': cart_count} 
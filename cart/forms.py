from django import forms
from .models import CartItem

class AddToCartForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1)
    book_id = forms.IntegerField(widget=forms.HiddenInput())
    
    class Meta:
        model = CartItem
        fields = ['quantity']

class UpdateCartForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=0)  # 0 to remove item
    
    class Meta:
        model = CartItem
        fields = ['quantity'] 
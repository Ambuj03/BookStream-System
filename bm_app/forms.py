from django import forms

from .models import Books

class transaction_form(forms.Form):
    book = forms.ModelChoiceField(queryset=Books.objects.all(), label = 'Select a book',
            to_field_name='book_name')

    quantity = forms.IntegerField()
    donation = forms.IntegerField()
    customer_name = forms.CharField()
    customer_phone = forms.NumberInput()
    customer_occupation = forms.CharField()
    remarks = forms.CharField()


    def __init__(self, *args, **kwargs):
        super(transaction_form, self).__init__(*args, **kwargs)
        self.fields['book'].label_from_instance = lambda obj: obj.book_name
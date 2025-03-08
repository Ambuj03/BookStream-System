from django import forms

from .models import Books, DistributorBooks

class BookAddForm(forms.Form):
    book = forms.ModelChoiceField(queryset=Books.objects.all(), label='Select a book')
    quantity = forms.IntegerField(label='Select the quantity')
    
    def __init__(self, *args, distributor=None, **kwargs):
        super(BookAddForm, self).__init__(*args, **kwargs) # why up and down matters?
        self.distributor = distributor
        
    def save(self):
        data = self.cleaned_data

        if not data:
            return None

        book = data['book']
        quantity = data['quantity']

        # get_or_create could also have been used, try it later.
        existing_book = DistributorBooks.objects.filter(
            book_name = book.book_name
        ).first()

        if existing_book:
            existing_book.book_stock += quantity
            existing_book.save()
            return existing_book

        else: 
            
            distributorBooks = DistributorBooks.objects.create(
                distributor_id = self.distributor.distributor_id,
                book_name = data['book'],
                book_author = book.book_author,
                book_language = book.book_language,
                book_price = book.book_price,
                book_category = book.book_category,
                book_stock = data['quantity']
        )
        
        return distributorBooks
    

# Adding FormSet Factory

from django.forms import formset_factory

# As we are having multiple form instances, we will need to pass the distributor insatance for 
#each one of them, it's different from previous approach, the functioon  below is for that only.

def get_book_formset(distributor, *args, **kwargs):
    FormSet = formset_factory(
        BookAddForm,
        extra=11,
        min_num=1,
        max_num=15
    )

    formset = FormSet(*args, **kwargs)

    for form in formset:
        form.distributor = distributor

    return formset


class AddCustomBooks(forms.Form):
    # Set distributor id and book_category manually

    book_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    book_author = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    book_language =forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    book_price = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class' : 'form-control'}))
    book_stock = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class' : 'form-control'}))

    def __init__(self, *args, distributor=None, **kwargs):
        super(AddCustomBooks, self).__init__(*args, **kwargs) # why up and down matters?
        self.distributor = distributor

    def save(self):
        data = self.cleaned_data        

        distributor = DistributorBooks.objects.create(
            distributor_id = self.distributor.distributor_id,
            book_name = data['book_name'],
            book_author = data['book_author'],
            book_language = data['book_language'],
            book_price = data['book_price'],
            book_category = "NON_BBT",
            book_stock = data['book_stock']

        )
        
        return distributor
    

    
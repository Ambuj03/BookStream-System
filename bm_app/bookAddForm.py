from django import forms

from .models import Books, DistributorBooks

class bookAddForm(forms.Form):
    book = forms.ModelChoiceField(queryset=Books.objects.all())
    quantity = forms.IntegerField()
    
    def __init__(self, *args, distributor=None, **kwargs):
        self.distributor = distributor
        super(bookAddForm, self).__init__(*args, **kwargs)
        
    def save(self):
        data = self.cleaned_data

        books = data['book']
        distributorBooks = DistributorBooks.objects.create(
                distributor_id = self.distributor.distributor_id,
                book_name = data['book'],
                book_author = books.book_author,
                book_language = books.book_language,
                book_price = books.book_price,
                book_category = books.book_category,
                book_stock = data['quantity']
        )
        
        return distributorBooks
        
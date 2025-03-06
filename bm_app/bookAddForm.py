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
        
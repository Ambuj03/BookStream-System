from django import forms

from .models import Books, Receipt, Customer, Donation, Distributor

from django.contrib.auth.forms import UserCreationForm


class transaction_form(forms.Form):
    book = forms.ModelChoiceField(queryset=Books.objects.all(), label = 'Select a book',
            to_field_name='book_name')

    quantity = forms.IntegerField()
    donation_amount = forms.IntegerField()
    donation_purpose = forms.CharField()
    customer_name = forms.CharField()
    customer_phone = forms.CharField(widget=forms.TextInput(attrs={'type': 'tel'}))
    customer_occupation = forms.CharField()
    customer_city = forms.CharField()
    remarks = forms.CharField()

    def __init__(self, *args, **kwargs): #study object oriented programming to understand this
        super(transaction_form, self).__init__(*args, **kwargs)
        # import pdb; pdb.set_trace()
        self.fields['book'].label_from_instance = lambda obj: obj.book_name

    
    def save(self):
        data = self.cleaned_data
        # saving customer dataa

        customer = Customer(
            # customer_id = data['customer_id'],
            customer_name=data['customer_name'],
            customer_phone=data['customer_phone'],
            customer_occupation=data['customer_occupation'],
            customer_city=data['customer_city'],
            customer_remarks=data['remarks']
        )

        customer.save()

        #updating the donations table

        donation = Donation(
            customer_id = 1,
            donation_amount = data['donation_amount'],
            donation_purpose = data['donation_purpose']
        )

        donation.save()

        #save receipt data
        receipt = Receipt(
            customer_id = 1, #try to declare a seperate function.
            book_id = 1, # fetched from bokk table referenced by book name
            distributor_id = 1, # will come through authorization, make login
            book=data['book'],
            quantity=data['quantity'],
            # donation=data['donation_amount'],
            # customer_name=data['customer_name'],
            # customer_phone=data['customer_phone'],
            # customer_occupation=data['customer_occupation'],
            # remarks=data['remarks'], doesnt exists in the original table
            donation = donation,
            customer = customer
        )
        receipt.save()


class login_form(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput)
# class signup_form(form.Form):
# add some fields


from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Distributor, Admin  # Import both models

class signup_form(UserCreationForm):
    distributor_name = forms.CharField(max_length=100, label='Distributor Name')
    distributor_phonenumber = forms.CharField(max_length=15, label='Phone Number')
    distributor_address = forms.CharField(max_length=200, label="Address")
    distributor_age = forms.DateField(label="Age", widget=forms.DateInput(attrs={'type': 'date'}))
    admin = forms.ModelChoiceField(queryset=Admin.objects.all(), required=True, label="Admin")  # Ensure Admin is chosen

    class Meta:
        model = Distributor
        fields = ('email', 'distributor_name', 'distributor_phonenumber', 'distributor_address', 'distributor_age', 'admin')

    def save(self, commit=True):
        distributor = super().save(commit=False)
        distributor.admin = self.cleaned_data["admin"]  # Assign selected admin
        if commit:
            distributor.save()
        return distributor

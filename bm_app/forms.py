from django import forms

from .models import  Receipt, Distributor, Admin

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

import re # regex


#Transaction Form***************************************************************

# Function to validate Indian phone numbers
def validate_indian_phone(value):
    if not re.match(r"^[6789]\d{9}$", value):
        raise ValidationError("Enter a valid Indian phone number (starting with 6,7,8,9).")

class transaction_form(forms.ModelForm):
    donation_amount = forms.IntegerField()
    donation_purpose = forms.CharField(max_length=255)
    customer_name = forms.CharField(max_length=50)
    customer_phone = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'tel'}),
        validators=[validate_indian_phone]
    )
    customer_occupation = forms.CharField(max_length=50)
    customer_city = forms.CharField(max_length=50)
    remarks = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Receipt
        fields = ['paymentMode']

    def __init__(self, *args, distributor=None, **kwargs):
        self.distributor = distributor
        super(transaction_form, self).__init__(*args, **kwargs)


#LOGIN FORM ********************************************************************
# Not needed since we are using inbuilt Auth form
# class login_form(forms.Form):
#     username = forms.CharField(
#         label="Username",
#         widget=forms.TextInput(attrs={'placeholder': 'Enter username'})
#     )

#     password = forms.CharField(
#         label="Password",
#         widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'})
#     )

#     def clean_username(self):
#         username = self.cleaned_data.get("username")
#         try:
#             user = User.objects.get(username=username)
#             distributor = Distributor.objects.get(user = user)
#             return username
#         except (User.DoesNotExist, Distributor.DoesNotExist):
#             raise forms.ValidationError("Invalid Username")

    

#SIGNUP FORM*******************************************************************
class signup_form(UserCreationForm):
    # Default UserCreationForm fields:
    # - username
    # - password1
    # - password2
    
    # Additional fields for Distributor
    distributor_name = forms.CharField(max_length=100)
    distributor_email = forms.EmailField()
    distributor_phonenumber = forms.CharField(max_length=10)
    distributor_address = forms.CharField(widget=forms.Textarea, required=False)
    distributor_age = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    admin = forms.ModelChoiceField(queryset=Admin.objects.all(), empty_label="Select Admin")

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')  # Using default fields

    def clean_distributor_phonenumber(self):
        phone = self.cleaned_data.get('distributor_phonenumber')
        if not re.match(r'^[6789]\d{9}$', phone):
            raise forms.ValidationError("Enter valid Indian phone number.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=True)
        
        # Create Distributor and link it to User
        distributor = Distributor.objects.create(
            user=user,  # Link the user
            distributor_name=self.cleaned_data['distributor_name'],
            distributor_email=self.cleaned_data['distributor_email'],
            distributor_phonenumber=self.cleaned_data['distributor_phonenumber'],
            distributor_address=self.cleaned_data['distributor_address'],
            distributor_age=self.cleaned_data['distributor_age'],
            admin=self.cleaned_data['admin']
        )
        return user


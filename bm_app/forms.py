from django import forms

from .models import  Receipt, Distributor, Temple

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

import re # regex
from django.core.validators import RegexValidator

from django.utils import timezone


#Transaction Form***************************************************************

# Function to validate Indian phone numbers
def validate_indian_phone(value):
    if not re.match(r"^[6789]\d{9}$", value):
        raise ValidationError("Enter a valid Indian phone number (starting with 6,7,8,9).")

name_validator = RegexValidator(
    regex = '^[a-zA-Z ]+$',
    message = 'It must contain only letters and spaces.'
)

class transaction_form(forms.ModelForm):
    donation_amount = forms.IntegerField(required=False)
    donation_purpose = forms.CharField(max_length=30, validators=[name_validator], required=False)
    customer_name = forms.CharField(max_length=20, validators = [name_validator], required=False)
    customer_phone = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'tel'}),
        validators=[validate_indian_phone], required= False
    )
    customer_occupation = forms.CharField(max_length=20, validators = [name_validator], required=False)
    customer_city = forms.CharField(max_length=15, validators=[name_validator], required=False)
    remarks = forms.CharField(widget=forms.Textarea, required=False, max_length= 150)

    class Meta:
        model = Receipt
        fields = ['paymentMode']

        # code is now redundant since we are usong user instance as distributor in receipt 
        # and reciept is being saved in the view not here as previously

    def __init__(self, *args, distributor=None, **kwargs):
        self.distributor = distributor
        super(transaction_form, self).__init__(*args, **kwargs)


#SIGNUP FORM*******************************************************************
class signup_form(UserCreationForm):
    # Default UserCreationForm fields:
    # - username
    # - password1
    # - password2

    def __init__(self, *args, **kwargs):
        super(signup_form, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = "Required. 15 characters or fewer. Letters and numbers only."

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if len(username) > 15:
            raise ValidationError("Username should be fewer than 15 Characters")
        if not username.isalnum():
            raise ValidationError("Username must contain only letters and numbers, No spaces.")
        return username 
    
    # Additional fields for Distributor
    distributor_name = forms.CharField(max_length=20, validators= [name_validator])
    distributor_email = forms.EmailField()
    distributor_phonenumber = forms.CharField(max_length=10)
    distributor_address = forms.CharField(widget=forms.Textarea, required=False, max_length=150)
    distributor_birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    temple = forms.ModelChoiceField(queryset=Temple.objects.all(), empty_label="Select Temple")

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')  # Using default fields

    def clean_distributor_phonenumber(self):
        phone = self.cleaned_data.get('distributor_phonenumber')
        if not re.match(r'^[6789]\d{9}$', phone):
            raise forms.ValidationError("Enter valid Indian phone number.")
        return phone
    
    def clean_distributor_email(self):
        email = self.cleaned_data.get('distributor_email')
        # RFC 5322 compliant email regex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise forms.ValidationError("Please enter a valid email address.")
        return email
    
    def clean_distributor_birth_date(self):
        birth_date = self.cleaned_data.get('distributor_birth_date')
        if birth_date > timezone.now().date():
            raise forms.ValidationError("Birth date cannot be in the future.")
        return birth_date

    def save(self, commit=True):
        user = super().save(commit=True)
        
        # Create Distributor and link it to User
        distributor = Distributor.objects.create(
            user=user,  # Link the user
            distributor_name=self.cleaned_data['distributor_name'],
            distributor_email=self.cleaned_data['distributor_email'],
            distributor_phonenumber=self.cleaned_data['distributor_phonenumber'],
            distributor_address=self.cleaned_data['distributor_address'],
            distributor_age=self.cleaned_data['distributor_birth_date'],
            temple=self.cleaned_data['temple']
        )
        return user


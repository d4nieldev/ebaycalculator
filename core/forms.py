from datetime import date

from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.models import User
from .models import SaleEntry, Gift, Cost, HipShipper


class DateInput(forms.DateInput):
    # Present DateInput as input type=date box.
    input_type = 'date'


class SignUpForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password', 'autocomplete':'new-password'}),
    )

    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email', 'aria-describedby': 'emailHelp'}),
        }


class SaleEntryForm(ModelForm):
    class Meta:
        model = SaleEntry
        exclude = ('user',)
        widgets = {
            'date': DateInput(attrs={'class': 'form-control form-add-sale', 'id':'f_date'}),
            'ebay_price': forms.NumberInput(attrs={'class': 'form-control form-add-sale', 'placeholder': 'eBay Price', 'id':'f_ebay_price'}),
            'amazon_price': forms.NumberInput(attrs={'class': 'form-control form-add-sale', 'placeholder': 'Amazon Price', 'id':'f_amazon_price'}),
            'ebay_tax': forms.NumberInput(attrs={'class': 'form-control col-1 form-add-sale', 'placeholder': 'eBay Tax', 'id':'f_ebay_tax'}),
            'paypal_tax': forms.NumberInput(attrs={'class': 'form-control col-1 form-add-sale', 'placeholder': 'Paypal Tax', 'id':'f_paypal_tax'}),
            'tm_fee': forms.NumberInput(attrs={'class': 'form-control col-1 form-add-sale', 'placeholder': 'TM Fee', 'id':'f_tm_fee'}),
            'promoted': forms.NumberInput(attrs={'class': 'form-control col-1 form-add-sale', 'placeholder': 'Promoted', 'id':'f_promoted'}),
            'profit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Profit', 'readonly':'true', 'id':'f_profit'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control form-add-sale', 'placeholder': 'Discount', 'id':'f_discount'}),
            'country': forms.TextInput(attrs={'class': 'form-control form-add-sale', 'placeholder': 'Country', 'id':'f_country'}),
        }


class GiftForm(ModelForm):
    class Meta:
        model = Gift
        exclude = ('user',)
        widgets = {
            'date': DateInput(attrs={'class': 'form-control', 'value': date.today, 'id':'f_gift_date'}),
            'gift_money': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Gift Card (100, 300 ...)', 'id':'f_gift_money', 'onkeyup': 'calc_add_to_balance()'}),
            'gift_tax': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tax', 'id':'f_gift_tax', 'onkeyup': 'calc_add_to_balance()'}),
        }


class CostForm(ModelForm):
    class Meta:
        model = Cost
        exclude = ('user',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name', 'id':'f_cost_name'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Value', 'id':'f_cost_value'}),
        }

class HipShipperForm(ModelForm):
    class Meta:
        model = HipShipper
        fields = '__all__'
        widgets = {
            'buyer_paid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buyer Paid', 'id':'f_buyer_paid'}),
            'seller_paid': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Seller Paid', 'id':'f_seller_paid'}),
        }


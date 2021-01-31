from datetime import date

from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

from .models import SaleEntry, Gift


class SignUpForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}),
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


class DateInput(forms.DateInput):
    input_type = 'date'

class SaleEntryForm(ModelForm):
    class Meta:
        model = SaleEntry
        fields = "__all__"
        widgets = {
            'date': DateInput(attrs={'class': 'form-control'}),
            'ebay_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'eBay Price', 'id':'f_ebay_price', 'onkeyup': 'calc_profit()'}),
            'amazon_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amazon Price', 'id':'f_amazon_price', 'onkeyup': 'calc_profit()'}),
            'ebay_tax': forms.NumberInput(attrs={'class': 'form-control col-1', 'placeholder': 'eBay Tax', 'id':'f_ebay_tax', 'onkeyup': 'calc_profit()'}),
            'paypal_tax': forms.NumberInput(attrs={'class': 'form-control col-1', 'placeholder': 'Paypal Tax', 'id':'f_paypal_tax', 'onkeyup': 'calc_profit()'}),
            'tm_fee': forms.NumberInput(attrs={'class': 'form-control col-1', 'placeholder': 'TM Fee', 'id':'f_tm_fee', 'onkeyup': 'calc_profit()'}),
            'promoted': forms.NumberInput(attrs={'class': 'form-control col-1', 'placeholder': 'Promoted', 'id':'f_promoted', 'onkeyup': 'calc_profit()'}),
            'profit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Profit', 'readonly':'true', 'id':'f_profit'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Discount', 'id':'f_discount'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country', 'id':'f_country'})
        }

    def __init__(self, *args, **kwargs):
        '''
        relate the sale registration form to the user who created it.
        '''
        user_id = kwargs.pop('user_id')
        super().__init__(*args, **kwargs)
        self.fields['user'] = forms.ModelChoiceField(queryset=User.objects.filter(id=user_id), empty_label=None, initial=User.objects.get(id=user_id))
        self.fields['user'].widget.attrs['class'] = 'no-display'


class GiftForm(ModelForm):
    class Meta:
        model = Gift
        fields = "__all__"
        widgets = {
            'date': DateInput(attrs={'class': 'form-control', 'value': date.today}),
            'gift_money': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Gift Card (100, 300 ...)', 'id':'f_gift_money', 'onkeyup': 'calc_add_to_balance()', 'value': '0'}),
            'gift_tax': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tax', 'id':'f_gift_tax', 'onkeyup': 'calc_add_to_balance()', 'value': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        '''
        relate the gift form to the user who created it.
        '''
        user_id = kwargs.pop('user_id')
        super().__init__(*args, **kwargs)
        self.fields['user'] = forms.ModelChoiceField(queryset=User.objects.filter(id=user_id), empty_label=None, initial=User.objects.get(id=user_id))
        self.fields['user'].widget.attrs['class'] = 'no-display'


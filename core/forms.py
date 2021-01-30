from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

from .models import SaleEntry


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
            'ebay_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'eBay Price', 'id':'f_ebay_price', 'onchange': 'calc_profit()'}),
            'amazon_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amazon Price', 'id':'f_amazon_price', 'onchange': 'calc_profit()'}),
            'ebay_tax': forms.NumberInput(attrs={'class': 'form-control col-1', 'placeholder': 'eBay Tax', 'id':'f_ebay_tax', 'onchange': 'calc_profit()'}),
            'paypal_tax': forms.NumberInput(attrs={'class': 'form-control col-1', 'placeholder': 'Paypal Tax', 'id':'f_paypal_tax', 'onchange': 'calc_profit()'}),
            'tm_fee': forms.NumberInput(attrs={'class': 'form-control col-1', 'placeholder': 'TM Fee', 'id':'f_tm_fee', 'onchange': 'calc_profit()'}),
            'promoted': forms.NumberInput(attrs={'class': 'form-control col-1', 'placeholder': 'Promoted', 'id':'f_promoted', 'onchange': 'calc_profit()'}),
            'profit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Profit', 'readonly':'true', 'id':'f_profit'})
        }

    def __init__(self, *args, **kwargs):
        '''
        relate the sale registration form to the user who created it.
        '''
        user_id = kwargs.pop('user_id')
        super().__init__(*args, **kwargs)
        self.fields['user'] = forms.ModelChoiceField(queryset=User.objects.filter(id=user_id), empty_label=None, initial=User.objects.get(id=user_id))
        self.fields['user'].widget.attrs['class'] = 'no-display'


import collections

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.shortcuts import render, redirect

from django.contrib import messages

from django.core.exceptions import ObjectDoesNotExist

from .forms import SignUpForm, SaleEntryForm, GiftForm, CostForm, HipShipperForm, PreferencesForm

from .models import SaleEntry, Balance, Gift, Cost, HipShipper, ReturnedSale, Preferences

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def HANDLE_LOGIN_BASE(request, page_to_render, context):
    '''
    submit the data from login form to authenticate the user.

    #### Parameters
    `request : django.http.HttpRequest` The request upon submitting the log in form

    `page_to_render : str` The name of the page to render after logging in

    `context : dict` The context needed to be passed to the html template
    '''
    if request.method == 'POST':
        if "btn_login" in request.POST:
            username = request.POST.get('txt_login_username')
            password = request.POST.get('txt_login_pass')

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect('panel')
            else:
                messages.error(request, 'Username or password are incorrect')
                context['open_login'] = True
                return render(request, page_to_render, context, status=400)


def SORT_DICT(dict_notsorted):
    '''Sort a dictionary of dates.
    Used for showing the dates in the select input in nice order.

    #### Parameters
    `dict_notsorted : dict` The unsorted dict
    
    #### Example:
    {2020: [7,5,9], 2019: [2,1,12]} --> {2019: [1,2,12], 2020: [5,7,9]}

    '''
    lst = dict_notsorted
    lst = collections.OrderedDict(sorted(lst.items()))

    for item in lst.items():
        item[1].sort()

    return lst


def GET_SALES_YEARS_MONTHS(request):
    '''
    Returns a dictionary with all years and months the user has registred sales.

    #### Parameters
    `request : django.http.HttpRequest` The request

    #### Example
    {2020: [11,12], 2021: [1]}
    '''
    sales = SaleEntry.objects.filter(user=request.user)
    start_day = Preferences.objects.get(user=request.user).start_month_day
    years_months = {}

    for sale in sales:
        if sale.date.year not in years_months.keys():
            years_months[sale.date.year] = []

    month = 1
    for year in years_months:
        for sale in SaleEntry.objects.filter(user=request.user.id, date__year=year):
            if sale.date.day >= start_day:
                # if the day is start day or more - it's this month
                if sale.date.month not in years_months[year]:
                    years_months[year].append(sale.date.month)
            else:
                # if the day is less than start day - it's the prev month
                if sale.date.month > 1:
                    if sale.date.month - 1 not in years_months[year]:
                        years_months[year].append(sale.date.month-1)
                else:
                    if 12 not in years_months[year]:
                        years_months[year].append(12)
            
    return SORT_DICT(years_months)


def VALIDATE_DATE(date):
    day = int(date.split('-')[2])
    print(date)
    
    try:
        datetime.date(year=int(date.split('-')[0]), month=int(date.split('-')[1]), day=day)
    except ValueError:
        return VALIDATE_DATE(f'{date.split("-")[0]}-{date.split("-")[1]}-{day-1}')
    else:
        print("final date: " + date)
        return date


def GET_GIFTS_YEARS_MONTHS(request):
    '''
    Returns a dictionary with all years and months the user has registred sales

    #### Parameters
    `request : django.http.HttpRequest` The request

    #### Example
    {2020: [11,12], 2021: [1]}
    '''
    gifts = Gift.objects.filter(user=request.user.id)
    start_day = Preferences.objects.get(user=request.user).start_month_day
    years_months = {}

    for gift in gifts:
        if gift.date.year not in years_months.keys():
            years_months[gift.date.year] = []

    for year in years_months:
        for gift in Gift.objects.filter(user=request.user.id, date__year=year):
            if gift.date.day >= start_day:
                # if the day is start day or more - it's this month
                if gift.date.month not in years_months[year]:
                    years_months[year].append(gift.date.month)
            else:
                # if the day is less than start day - it's the prev month
                if gift.date.month > 1:
                    if gift.date.month - 1 not in years_months[year]:
                        years_months[year].append(gift.date.month-1)
                else:
                    if 12 not in years_months[year]:
                        years_months[year].append(12)
                
    return SORT_DICT(years_months)


def index(request):
    '''View the index HTML page, register new users, and handle login.

    #### Parameters
    'request : django.http.HttpRequest` The request
    '''
    if request.user.is_authenticated:
        # logged in users will be automatically redirected to the panel page
        return redirect('panel')
    else:
        form = SignUpForm()
        context = {}
        
        if request.method == 'POST':
            if "btn_signup" in request.POST:
                form = SignUpForm(request.POST)

                if form.is_valid():
                    form.save()

                    last_user = User.objects.latest('id')

                    # create balance object
                    user_balance = Balance(user=last_user)
                    user_balance.save()

                    # create preferences object
                    user_preferences = Preferences(user=last_user)
                    user_preferences.save()
                    
                    messages.success(request, "Account was created successfully! you can now login as an existing user.")

                    # open the login form after successful sign up
                    context['open_login'] = True

                    context['form'] = form
                    return render(request, 'index.html', context)
        
        context['form'] = form
        
        login_handle = HANDLE_LOGIN_BASE(request, 'index.html', context)
        # check if user logged in - if true authenticate and log in. else, do nothing.
        return login_handle if login_handle else render(request, 'index.html', context)


@login_required(login_url='index')
def panel(request):
    '''View the panel HTML page.
    Restricted only for registered users.
    
    #### Paramaters
    `request : django.http.HttpRequest` The request
    '''  

    context = {
        'years_months': GET_SALES_YEARS_MONTHS(request),
        'gifts_years_months': GET_GIFTS_YEARS_MONTHS(request),
        'form': SaleEntryForm(),
        'giftform': GiftForm(),
        'costform': CostForm(),
        'hipshipperform': HipShipperForm(),
        'preferencesform': PreferencesForm(),
        'hipshippers': HipShipper.objects.all(),
        'user_balance': Balance.objects.get(user=request.user).balance,
        'paypal_balance': Balance.objects.get(user=request.user).paypal_balance,
        'costs': Cost.objects.filter(user=request.user),
        'preferences': Preferences.objects.get(user=request.user),
    }
    
    return render(request, 'panel.html', context)


def help(request):
    '''View the help HTML page.

    #### Parameters
    `request : django.http.HttpRequest` The request
    '''
    return render(request, 'help.html')

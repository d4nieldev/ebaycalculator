import collections

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.shortcuts import render, redirect

from django.contrib import messages

from .forms import SignUpForm, SaleEntryForm, GiftForm

from .models import SaleEntry, Balance, Gift


def HANDLE_LOGIN_BASE(request, current_page, context):
    '''
    This function handles the login form - need to apply to every form we want to sign in from
    forms that are using this method: index
    '''
    if request.method == 'POST':
        if "btn_login" in request.POST:
            username = request.POST.get('txt_login_username')
            password = request.POST.get('txt_login_pass')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('panel')
            else:
                messages.error(request, 'Username or password are incorrect')
                context['open_login'] = True
                return render(request, current_page, context, status=400)
    return None


def HANDLE_LOGOUT_BASE(request):
    '''
    This function handles the logout mechanism. No need to use it anywhere.
    Already imported from urls
    '''
    logout(request)
    return redirect('index')


def SORT_DICT(dict_notsorted):
    lst = dict_notsorted
    lst = collections.OrderedDict(sorted(lst.items()))

    for item in lst.items():
        item[1].sort()

    return lst


def GET_SALES_YEARS_MONTHS(request):
    '''
    This function returns a dictionary with all years and months the user has registred sales
    return example --> {2020: [12, 11], 2021: [1]}
    '''
    sales = SaleEntry.objects.filter(user=request.user.id)
    years_months = {}

    for sale in sales:
        if sale.date.year not in years_months.keys():
            years_months[sale.date.year] = []

    for year in years_months:
        for sale in SaleEntry.objects.filter(user=request.user.id, date__range=[f'{year}-01-16', f'{year+1}-01-15']):
            if sale.date.day >= 16:
                # if the day is 16 or more - it's this month
                if sale.date.month not in years_months[year]:
                    years_months[year].append(sale.date.month)
            else:
                # if the day is less than 16 - it's the prev month
                if sale.date.month > 1:
                    if sale.date.month - 1 not in years_months[year]:
                        years_months[year].append(sale.date.month-1)
                else:
                    if 12 not in years_months[year]:
                        years_months[year].append(12)
                

    
    return SORT_DICT(years_months)


def GET_GIFTS_YEARS_MONTHS(request):
    '''
    This function returns a dictionary with all years and months the user has registred sales
    return example --> {2020: [12, 11], 2021: [1]}
    '''
    gifts = Gift.objects.filter(user=request.user.id)
    years_months = {}

    for gift in gifts:
        if gift.date.year not in years_months.keys():
            years_months[gift.date.year] = []

    for year in years_months:
        for gift in Gift.objects.filter(user=request.user.id, date__range=[f'{year}-01-16', f'{year+1}-01-15']):
            if gift.date.day >= 16:
                # if the day is 16 or more - it's this month
                if gift.date.month not in years_months[year]:
                    years_months[year].append(gift.date.month)
            else:
                # if the day is less than 16 - it's the prev month
                if gift.date.month > 1:
                    if gift.date.month - 1 not in years_months[year]:
                        years_months[year].append(gift.date.month-1)
                else:
                    if 12 not in years_months[year]:
                        years_months[year].append(12)
                

    
    return SORT_DICT(years_months)


def index(request):
    '''
    index view
    All it does is sign up users and handle the sign in
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
                    user_balance = Balance(user=last_user, balance=0)
                    user_balance.save()
                    
                    messages.success(request, "Account was created successfully! you can now login as an existing user.")

                    # open the login form after successful sign up
                    context['open_login'] = True
                    context['form'] = form
                    return render(request, 'index.html', context)
        
        context['form'] = form
        # handle login
        login_handle = HANDLE_LOGIN_BASE(request, 'index.html', context)
        return login_handle if login_handle is not None else render(request, 'index.html', context)


@login_required(login_url='index')
def panel(request):
    '''
    panel view
    '''
    context = {}

    years_months = GET_SALES_YEARS_MONTHS(request)
    context['years_months'] = years_months

    gifts_years_months = GET_GIFTS_YEARS_MONTHS(request)
    context['gifts_years_months'] = gifts_years_months

    form = SaleEntryForm()
    context['form'] = form

    giftform = GiftForm()
    context['giftform'] = giftform

    user_sales = SaleEntry.objects.filter(user=request.user.id).order_by('date')
    context['user_sales'] = user_sales

    context['user_balance'] = Balance.objects.get(user=request.user).balance
    
    if request.method == "GET":
        if "btn_select_date" in request.GET:
            # filter form
            selected_filter = request.GET.get('s_filter_sales_by_date')

            if str(selected_filter) != 'all':
                year = int(str(selected_filter).split('-')[0])
                month = int(str(selected_filter).split('-')[1])

                context['user_sales_filtered_y'] = year
                context['user_sales_filtered_m'] = month
                
                date_from = f'{year}-{month}-16'
                date_to = f'{year}-{month+1}-15'
                
                if month == 12:
                    date_from = f'{year}-12-16'
                    date_to = f'{year+1}-01-15'
                if month == 9:
                    date_from = f'{year}-0{month}-16'
                    date_to = f'{year}-{month+1}-15'
                elif month < 10:
                    date_from = f'{year}-0{month}-16'
                    date_to = f'{year}-0{month+1}-15'
                

                context['user_sales'] = SaleEntry.objects.filter(user=request.user.id, date__range=[date_from, date_to]).order_by('date')
            else:
                context['user_sales'] = user_sales
    
    context['form'] = form
    context['giftform'] = giftform
    
    return render(request, 'panel.html', context)

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
        for sale in SaleEntry.objects.filter(user=request.user.id, date__year=year):
            if sale.date.month not in years_months[year]:
                years_months[year].append(sale.date.month)

    
    return SORT_DICT(years_months)


def GET_GIFTS_YEARS_MONTHS(request):
    gifts = Gift.objects.filter(user=request.user.id)
    years_months = {}

    for gift in gifts:
        if gift.date.year not in years_months.keys():
            years_months[gift.date.year] = []

    for year in years_months:
        for gift in Gift.objects.filter(user=request.user.id, date__year=year):
            if gift.date.month not in years_months[year]:
                years_months[year].append(gift.date.month)
    
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

    form = SaleEntryForm(user_id=request.user.id)
    context['form'] = form

    giftform = GiftForm(user_id=request.user.id)
    context['giftform'] = giftform

    user_sales = SaleEntry.objects.filter(user=request.user.id)
    context['user_sales'] = user_sales

    gifts = None
    context['gifts'] = gifts

    context['user_balance'] = Balance.objects.get(user=request.user).balance

    if request.method == 'POST':  
        if "btn_register_sale" in request.POST:
            # register sale form
            form = SaleEntryForm(request.POST, user_id=request.user.id)
            if form.is_valid():
                form.save()

                messages.info(request, 'Sale has been registred')

            return redirect('panel')
        
        if 'btn_change_balance' in request.POST:
            # change balance form
            giftform = GiftForm(request.POST, user_id=request.user.id)
            if giftform.is_valid():
                giftform.save()

                add_to_balance = float(request.POST.get('txt_balance_add'))
                user_balance_obj = Balance.objects.get(user=request.user)
                user_balance_obj.balance = user_balance_obj.balance + add_to_balance
                user_balance_obj.save()

                return redirect('panel')
                

    if request.method == "GET":
        if "btn_filter_gifts_date" in request.GET:
            # filter gifts form
            dates = request.GET.get('s_filter_gifts_by_date')
            if dates:
                year = int(str(dates).split('-')[0])
                month = int(str(dates).split('-')[1])
                context['gifts'] = Gift.objects.filter(user=request.user.id, date__year=year, date__month=month)
                context['gifts_selected_year'] = year
                context['gifts_selected_month'] = month
            else:
                context['gifts'] = None

        if "btn_select_date" in request.GET:
            # filter form
            selected_filter = request.GET.get('s_filter_sales_by_date')

            if str(selected_filter) != 'all':
                year = int(str(selected_filter).split('-')[0])
                month = int(str(selected_filter).split('-')[1])

                context['user_sales_filtered_y'] = year
                context['user_sales_filtered_m'] = month
                context['user_sales'] = SaleEntry.objects.filter(user=request.user.id, date__year=year, date__month=month)
            else:
                context['user_sales'] = user_sales
    
    context['form'] = form
    context['giftform'] = giftform
    
    return render(request, 'panel.html', context)

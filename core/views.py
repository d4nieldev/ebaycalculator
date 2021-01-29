from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from django.shortcuts import render, redirect

from django.contrib import messages

from .forms import SignUpForm, SaleEntryForm

from .models import SaleEntry


def HANDLE_LOGIN_BASE(request, current_page, context):
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
    logout(request)
    return redirect('index')


def GET_SALES_YEARS_MONTHS(request):
    sales = SaleEntry.objects.filter(user=request.user.id)
    years_months = {}

    for sale in sales:
        if sale.date.year not in years_months.keys():
            years_months[sale.date.year] = []

    for year in years_months:
        for sale in SaleEntry.objects.filter(user=request.user.id, date__year=year):
            if sale.date.month not in years_months[year]:
                years_months[year].append(sale.date.month)
    
    return years_months


def index(request):
    if request.user.is_authenticated:
        return redirect('panel')
    else:
        form = SignUpForm()
        context = {}
        
        if request.method == 'POST':
            if "btn_signup" in request.POST:
                form = SignUpForm(request.POST)
                if form.is_valid():
                    form.save()

                    username = form.cleaned_data.get('username')
                    messages.success(request, "Account was created for " + username)
                    context['open_login'] = True
                    context['form'] = form
                    return render(request, 'index.html', context)
        
        context['form'] = form
        login_handle = HANDLE_LOGIN_BASE(request, 'index.html', context)
        return login_handle if login_handle is not None else render(request, 'index.html', context)


@login_required(login_url='index')
def panel(request):
    context = {}

    years_months = GET_SALES_YEARS_MONTHS(request)
    context['years_months'] = years_months

    form = SaleEntryForm(user_id=request.user.id)
    context['form'] = form

    user_sales = SaleEntry.objects.filter(user=request.user.id)
    context['user_sales'] = user_sales

    if request.method == 'POST':
        if "btn_select_date" in request.POST:
            selected_filter = request.POST.get('s_filter_sales_by_date')

            if str(selected_filter) != 'all':
                year = int(str(selected_filter).split('-')[0])
                month = int(str(selected_filter).split('-')[1])

                context['user_sales_filtered_y'] = year
                context['user_sales_filtered_m'] = month
                context['user_sales'] = SaleEntry.objects.filter(user=request.user.id, date__year=year, date__month=month)
            else:
                context['user_sales'] = user_sales
            return render(request, 'panel.html', context)
            
        if "btn_register_sale" in request.POST:
            form = SaleEntryForm(request.POST, user_id=request.user.id)
            if form.is_valid():
                form.save()

                messages.info(request, 'Sale has been registred')

            return redirect('panel')

    
    context['form'] = form
    
    return render(request, 'panel.html', context)

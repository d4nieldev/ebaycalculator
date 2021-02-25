from django.views.decorators.csrf import csrf_exempt

from django.core import serializers

from django.http import JsonResponse

from django.contrib.auth import logout

from django.shortcuts import redirect, HttpResponse

from django.contrib.auth.models import User
from .models import SaleEntry, Balance, Gift, Cost, HipShipper

from .forms import SaleEntryForm, GiftForm, CostForm, HipShipperForm


def HANDLE_LOGOUT_BASE(request):
    '''HANDLE_LOGOUT_BASE

    This function handles the logout mechanism. No need to use it anywhere.
    Already imported from urls
    '''
    logout(request)
    return redirect('index')


@csrf_exempt
def update_sale(request):
    '''update_sale

    This function gets an ajax response with 4 parameters: id, value, lastvalue, type.
    The relevant field is updated and the profit is recalculated. if there's a need, the balance is updated too.
    '''
    id = request.POST.get('id', '')
    value = request.POST.get('value', '')
    lastvalue = request.POST.get('lastvalue', '')
    type = request.POST.get('type', '')

    sale = SaleEntry.objects.get(id=id)
    balance_obj = Balance.objects.get(user=sale.user)

    if type == "ebay_price":
        sale.ebay_price = float(value)

    if type == "amazon_price":
        balance_obj.balance += sale.amazon_price - float(value)
        sale.amazon_price = float(value)

    if type == "ebay_tax":
        sale.ebay_tax = float(value)

    if type == "paypal_tax":
        sale.paypal_tax = float(value)

    if type == "tm_fee":
        balance_obj.balance += sale.tm_fee - float(value)
        sale.tm_fee = float(value)
    
    if type == "promoted":
        sale.promoted = float(value)

    if type == "discount":
        balance_obj.balance -= sale.amazon_price - float(value)
        sale.discount = float(value)
    
    if type == "country":
        sale.country = value if not str(value).strip() == "" else '-----'
    
    balance_obj.save()

    kwargs = {'update_type':type, 'update_value_diff':float(value) - float(lastvalue)}

    sale.profit = sale.calc_profit()
    
    sale.save(**kwargs)

    return redirect('panel')

@csrf_exempt
def delete_sale(request):
    '''delete_sale

    This function gets an ajax response with the sale the user wishes to delete and deletes this sale.
    '''
    id = request.POST.get('id', '')
    SaleEntry.objects.get(id=id).delete()
    return redirect('panel')


@csrf_exempt
def add_sale(request):
    '''add_sale

    This function gets an ajax response which containes a form with all the fields needed to create a SaleEntry and creating one.
    '''
    if request.method == 'POST':
        form = SaleEntryForm(request.POST)

        if form.is_valid():
            sale = form.save(commit=False)
            sale.user = request.user
            sale.save()

            return JsonResponse({"sale_id": sale.id})

    return JsonResponse({"error": 'an error occured'})


@csrf_exempt
def filter_gifts(request):
    '''filter_gifts

    The function gets a month and finds the relevant gifts registered in this month.
    The gifts query set is returned to the html page via a json response
    '''
    if request.method == 'GET':
        gifts_qs = None
        date = str(request.GET['date'])

        if date != 'Show Gift Cards From':
            # get the date range
            year = int(date.split('-')[0])
            month = int(date.split('-')[1])

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

            # get the relevant gifts
            gifts_qs = Gift.objects.filter(user=request.user.id, date__range=[date_from, date_to])

            # serialize the query set so it could be given as a json response
            data = serializers.serialize('json', gifts_qs)
            return HttpResponse(data, content_type="application/json")
    
    return JsonResponse({'data': 'no data'}, status=200)

@csrf_exempt
def add_balance(request):
    '''add_balance

    This function creates a new gift (which is automatically added to the balance).
    '''
    if request.method == 'POST':
        form = GiftForm(request.POST)

        if form.is_valid():
            gift = form.save(commit=False)
            gift.user = request.user
            gift.save()

            return JsonResponse({'balance': Balance.objects.get(user=request.user).balance})

    return JsonResponse({'error': 'an error has occured'})


@csrf_exempt
def add_cost(request):
    '''add_cost

    This function creates a new Cost object.
    On success, the costs queryset of the pqrticular user is returned.
    '''
    if request.method == "POST":
        form = CostForm(request.POST)

        if form.is_valid():
            cost = form.save(commit=False)
            cost.user = request.user
            cost.save()

            # get the relevant costs
            costs_qs = Cost.objects.filter(user=request.user.id)

            # serialize the query set so it could be given as a json response
            data = serializers.serialize('json', costs_qs)
            return HttpResponse(data, content_type="application/json")
    return JsonResponse({"data": "no data"})


@csrf_exempt
def delete_cost(request):
    '''delete_cost

    This function deletes a selected cost.
    On success, this function returnes the new costs query set.
    '''
    if request.method == 'POST':
        id = request.POST.get('id', '')
        Cost.objects.get(id=id).delete()

        # get the relevant costs
        costs_qs = Cost.objects.filter(user=request.user.id)
        
        # serialize the query set so it could be given as a json response
        data = serializers.serialize('json', costs_qs, fields=('id', 'name', 'value'))
        return HttpResponse(data, content_type="application/json")

    return JsonResponse({"data":"no data"})


@csrf_exempt
def add_hipshipper(request):
    '''add_hipshipper

    This function creates a new Hipshipper object.
    '''
    if request.method == 'POST':
        form = HipShipperForm(request.POST)
        if form.is_valid():
            hipshipper = form.save(commit=False)
            hipshipper.sale_entry = SaleEntry.objects.get(id=request.POST['sale_entry'])
            hipshipper.save()
            
            return JsonResponse({"success": request.POST})

    return JsonResponse({
        "fail": request.POST,
        "errors": form.errors})

from django.views.decorators.csrf import csrf_exempt

from django.core import serializers

from django.http import JsonResponse

from .models import SaleEntry, Balance, Gift, Cost
from .forms import SaleEntryForm, GiftForm, CostForm, HipShipperForm

from django.contrib.auth.models import User

from django.shortcuts import redirect, HttpResponse, render


@csrf_exempt
def update_sale(request):
    id = request.POST.get('id', '')
    value = request.POST.get('value', '')
    type = request.POST.get('type', '')

    sale = SaleEntry.objects.get(id=id)
    balance_obj = Balance.objects.get(user=sale.user)

    if type == "ebay_price":
        sale.ebay_price = float(value)
        sale.profit = sale.calc_profit()

    if type == "amazon_price":
        balance_obj.balance = balance_obj.balance + (sale.amazon_price - float(value))
        sale.amazon_price = float(value)
        sale.profit = sale.calc_profit()

    if type == "ebay_tax":
        sale.ebay_tax = float(value)
        sale.profit = sale.calc_profit()

    if type == "paypal_tax":
        sale.paypal_tax = float(value)
        sale.profit = sale.calc_profit()

    if type == "tm_fee":
        balance_obj.balance = balance_obj.balance + (sale.tm_fee - float(value))
        sale.tm_fee = float(value)
        sale.profit = sale.calc_profit()
    
    if type == "promoted":
        sale.promoted = float(value)
        sale.profit = sale.calc_profit()

    if type == "discount":
        balance_obj.balance = balance_obj.balance - (sale.amazon_price - float(value))
        sale.discount = float(value)
        sale.profit = sale.calc_profit()
    
    if type == "country":
        sale.country = value if not str(value).strip() == "" else '-----'
    
    balance_obj.save()
    sale.save()

    return redirect('panel')

@csrf_exempt
def delete_sale(request):
    id = request.POST.get('id', '')
    SaleEntry.objects.get(id=id).delete()
    return redirect('panel')


@csrf_exempt
def add_sale(request):
    if request.method == 'POST':
        form = SaleEntryForm(request.POST)

        if form.is_valid():
            sale = form.save(commit=False)
            sale.user = request.user
            sale.save()

            return JsonResponse({"sale_id": sale.id})

    return HttpResponse('')


@csrf_exempt
def filter_gifts(request):
    if request.method == 'GET':
        gifts_qs = None
        date = str(request.GET['date'])

        if date != 'Show Gift Cards From':
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

            gifts_qs = Gift.objects.filter(user=request.user.id, date__range=[date_from, date_to])
            data = serializers.serialize('json', gifts_qs)
            return HttpResponse(data, content_type="application/json")
    
    return JsonResponse({'data': 'no data'}, status=200)

@csrf_exempt
def add_balance(request):
    if request.method == 'POST':
        form = GiftForm(request.POST)

        if form.is_valid():
            gift = form.save(commit=False)
            gift.user = request.user
            gift.save()

            return JsonResponse({'balance': Balance.objects.get(user=request.user).balance})

    return HttpResponse('')


@csrf_exempt
def add_cost(request):
    if request.method == "POST":
        form = CostForm(request.POST)

        if form.is_valid():
            cost = form.save(commit=False)
            cost.user = request.user
            cost.save()

            costs_qs = Cost.objects.filter(user=request.user.id)
            data = serializers.serialize('json', costs_qs)
            return HttpResponse(data, content_type="application/json")
    return JsonResponse({"data": "no data"})


@csrf_exempt
def delete_cost(request):
    if request.method == 'POST':
        id = request.POST.get('id', '')
        Cost.objects.get(id=id).delete()

        costs_qs = Cost.objects.filter(user=request.user.id)
        data = serializers.serialize('json', costs_qs, fields=('id', 'name', 'value'))
        return HttpResponse(data, content_type="application/json")
    return HttpResponse('')


@csrf_exempt
def add_hipshipper(request):
    if request.method == 'POST':
        form = HipShipperForm(request.POST)

        if form.is_valid():
            form.save()
            return JsonResponse({"success": request.POST})
    return JsonResponse({
        "fail": request.POST,
        "errors": form.errors})
    


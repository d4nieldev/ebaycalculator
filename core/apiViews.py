from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse

from .models import SaleEntry, Balance

from django.contrib.auth.models import User

from django.shortcuts import redirect


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


from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import pandas as pd

from itertools import chain

from django.core.exceptions import ObjectDoesNotExist

from django.views.decorators.csrf import csrf_exempt

from django.core import serializers

from django.http import JsonResponse

from django.contrib.auth import logout

from django.shortcuts import redirect, HttpResponse

from django.contrib.auth.models import User
from .models import SaleEntry, Balance, Gift, Cost, HipShipper, ReturnedSale, Preferences

from .forms import SaleEntryForm, GiftForm, CostForm, HipShipperForm

from .views import VALIDATE_DATE


def HANDLE_LOGOUT_BASE(request):
    '''
    Handles the logout mechanism. No need to use it anywhere.
    
    #### Parameters
    `request : django.http.HttpRequest` the request that triggered the caller function
    '''
    logout(request)

    return redirect('index')


@csrf_exempt
def update_sale(request):
    '''
    The relevant field is updated and the profit is recalculated. if there's a need, the balance is updated too.

    Attributes
    ----------
    request : django.http.HttpRequest
        the request that triggered this function
    '''

    # get the values
    id = request.POST.get('id', '')
    value = request.POST.get('value', '')
    lastvalue = request.POST.get('lastvalue', '')
    type = request.POST.get('type', '')

    # get the sale object
    sale = SaleEntry.objects.get(id=id)

    if type == "ebay_price":
        sale.ebay_price = float(value)
    if type == "amazon_price":
        sale.amazon_price = float(value)
    if type == "ebay_tax":
        sale.ebay_tax = float(value)
    if type == "paypal_tax":
        sale.paypal_tax = float(value)
    if type == "tm_fee":
        sale.tm_fee = float(value)
    if type == "promoted":
        sale.promoted = float(value)
    if type == "discount":
        sale.discount = float(value)
    if type == "country":
        sale.country = value if not str(value).strip() == "" else '-----'

    # tell the server that the sale is updated and the update type with the value
    kwargs = {
        'update_type':type,
        'update_value_diff':(float(value) - float(lastvalue)) if type != 'country' else value
        }

    # recalculate the profit
    sale.profit = sale.calc_profit()
    
    sale.save(**kwargs)

    # reload the page
    return redirect('panel')

@csrf_exempt
def delete_sale(request):
    '''
    Gets an ajax response with the sale the user wishes to delete and deletes this sale.

    Attributes
    ----------
    request : django.http.HttpRequest
        the request that triggered this function 
    '''
    id = request.POST.get('id', '')

    SaleEntry.objects.get(id=id).delete()
    
    # reload the page
    return redirect('panel')


@csrf_exempt
def add_sale(request):
    '''
    Gets an ajax response which containes a form with all the fields needed to create a SaleEntry and creating one.

    Attributes
    ----------
    request : django.http.HttpRequest
        the request that triggered this function 
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
    '''
    Gets a month and finds the relevant gifts registered in this month.
    The gifts query set is returned to the html page via a json response.

    Attributes
    ----------
    request : django.http.HttpRequest
        the request that triggered this function 
    '''
    if request.method == 'GET':
        gifts_qs = None
        date = str(request.GET['date'])
        start_day = Preferences.objects.get(user=request.user).start_month_day
        sort_by_date = Preferences.objects.get(user=request.user).sort_by_date

        if date != 'Show Gift Cards From':
            if date == 'all':
                gifts_qs = Gift.objects.filter(user=request.user.id)

            else:
                # get the date range
                year = int(date.split('-')[0])
                month = int(date.split('-')[1])

                date_from = datetime(year=year, month=month, day=start_day)
                date_to = date_from + relativedelta(months=+1) - timedelta(days=1)

                # get the relevant gifts
                gifts_qs = Gift.objects.filter(user=request.user.id, date__range=[date_from, date_to])

            if sort_by_date:
                gifts_qs = gifts_qs.order_by('date')

            # serialize the query set so it could be given as a json response
            data = serializers.serialize('json', gifts_qs)
            return HttpResponse(data, content_type="application/json")
    
    # return an indication that there is an error
    return JsonResponse({'data': 'no data'}, status=200)

@csrf_exempt
def add_balance(request):
    '''
    Creates a new gift (which is automatically added to the balance).

    Attributes
    ----------
    request : django.http.HttpRequest
        the request that triggered this function 
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
def delete_gift(request):
    """Deletes a given gift

    Attributes
    ----------
    request : django.HttpRequest
        the request that triggered this function
    """
    if request.method == 'POST':
        id = request.POST.get('id', '')

        Gift.objects.get(id=id).delete()

        # get the relevant gifts
        gifts_qs = Gift.objects.filter(user=request.user.id)
        
        # serialize the query set so it could be given as a json response
        data = serializers.serialize('json', gifts_qs, fields=('id', 'gift_amount', 'gift_tax'))
        return HttpResponse(data, content_type="application/json")

    return JsonResponse({"data":"no data"})


@csrf_exempt
def add_cost(request):
    '''
    Creates a new Cost object.
    On success, the costs queryset of the pqrticular user is returned.

    Attributes
    ----------
    request : django.http.HttpRequest
        the request that triggered this function 
    '''
    if request.method == "POST":
        form = CostForm(request.POST)

        if form.is_valid():
            cost = form.save(commit=False)
            cost.user = request.user
            cost.is_constant = request.POST['is_constant'] == 'true'
            cost.save()

            return JsonResponse({'success': 'cost saved successfully'})
        else:
            print(form.errors)

    return JsonResponse({"data": "no data"})


@csrf_exempt
def delete_cost(request):
    '''
    Deletes a selected cost.
    On success, this function returnes the new costs query set.

    Attributes
    ----------
    request : django.http.HttpRequest
        the request that triggered this function 
    '''
    if request.method == 'POST':
        id = request.POST.get('id', '')

        Cost.objects.get(id=id).delete()

        return JsonResponse({'success': 'cost deleted successfully'})

    return JsonResponse({"data":"no data"})


@csrf_exempt
def load_costs(request):
    costs_qs = Cost.objects.filter(user=request.user)
    data = serializers.serialize('json', costs_qs)
    return HttpResponse(data, content_type="application/json")

@csrf_exempt
def add_hipshipper(request):
    '''
    Creates a new Hipshipper object.

    Attributes
    ----------
    request : django.http.HttpRequest
        the request that triggered this function 
    '''
    if request.method == 'POST':
        form = HipShipperForm(request.POST)
        if form.is_valid():
            if HipShipper.objects.filter(sale_entry=SaleEntry.objects.get(id=request.POST['sale_entry'])).count() == 0: # new hipshipper
                # save the object with the selected sale.
                hipshipper = form.save(commit=False)
                hipshipper.sale_entry = SaleEntry.objects.get(id=request.POST['sale_entry'])

                hipshipper.save()
                
                hipshipper.sale_entry.profit = hipshipper.sale_entry.calc_profit()
                hipshipper.sale_entry.save()
                
                return JsonResponse({"success": request.POST})

            else: # old hipshipper
                """ hipshipper = HipShipper.objects.get(sale_entry=SaleEntry.objects.get(id=request.POST['sale_entry']))
                hipshipper.buyer_paid = request.POST['buyer_paid']
                hipshipper.seller_paid = request.POST['seller_paid'] """

    return JsonResponse({
        "fail": request.POST,
        "errors": form.errors})

@csrf_exempt
def update_hipshipper(request):
    kwargs = {
        'old_buyer_paid': float(request.POST["lastvalue"].split('/')[1].replace('Buyer', '')),
        'old_seller_paid': float(request.POST["lastvalue"].split('/')[2].replace('Seller', ''))
    }

    hipshipper_to_update = HipShipper.objects.get(sale_entry=request.POST["sale_id"])
    hipshipper_to_update.buyer_paid = request.POST["buyer_paid"]
    hipshipper_to_update.seller_paid = request.POST["seller_paid"]

    hipshipper_to_update.save(**kwargs)


@csrf_exempt
def update_return_status(request):
    if request.method == 'POST':
        sale = SaleEntry.objects.get(id=request.POST['sale_id'])
        try:
            returned_sale = ReturnedSale.objects.get(sale=sale)
            returned_sale.is_pending = request.POST['is_pending'] == 'true'
            returned_sale.save()
        except ObjectDoesNotExist:
            ReturnedSale(sale=sale, is_pending=True).save()

        return JsonResponse({
            "success": f'returned sale [{sale}] was updated!',
            })
    return JsonResponse({"error": "an error occured"})


@csrf_exempt
def delete_returned_sale(request):
    if request.method == 'POST':
        sale = ReturnedSale.objects.get(sale=SaleEntry.objects.get(id=request.POST['sale_id']))
        sale.delete()

        return JsonResponse({
            "success": f'returned sale [{sale}] was canceled!',
            })
    return JsonResponse({"error": "an error occured"})


@csrf_exempt
def update_paypal_balance(request):
    if request.method == 'POST':
        user_balance = Balance.objects.get(user=request.user)
        user_balance.paypal_balance = float(request.POST['value'])
        user_balance.save()

        return JsonResponse({
            'success': 'paypal balance updated successfully!'
        })
    
    return JsonResponse({
        'error': 'an error occured...'
    })

@csrf_exempt
def filter_sales(request):
    if request.method == 'POST':
        date = request.POST['date']
        model_to_filter_by = request.POST['model_to_filter_by']

        start_day = Preferences.objects.get(user=request.user).start_month_day
        sort_by_date = Preferences.objects.get(user=request.user).sort_by_date
        
        if str(date) != 'all':
            year = int(str(date).split('-')[0])
            month = int(str(date).split('-')[1])
            
            date_from = datetime(year=year, month=month, day=start_day)
            date_to = date_from + relativedelta(months=+1) - timedelta(days=1)
            
            date_range = [date_from, date_to]
            sales_qs = SaleEntry.objects.filter(user=request.user, date__range=[date_from, date_to])
        else:
            sales_qs = SaleEntry.objects.filter(user=request.user)
        
        if sort_by_date:
            returned_qs = ReturnedSale.objects.filter(sale__user=request.user).order_by('sale__date')
            hipshipper_qs = HipShipper.objects.filter(sale_entry__user=request.user).order_by('sale_entry__date')
            sales_qs = sales_qs.order_by('date')
        else:
            returned_qs = ReturnedSale.objects.filter(sale__user=request.user)
            hipshipper_qs = HipShipper.objects.filter(sale_entry__user=request.user)

        if model_to_filter_by != "all":
            temp_qs = []
            print(model_to_filter_by)
            for sale in sales_qs:
                in_returned_qs = ReturnedSale.objects.filter(sale=sale).count() > 0

                approved_bool = model_to_filter_by == "approved" and not in_returned_qs
                pending_bool = model_to_filter_by == "pending" and in_returned_qs and ReturnedSale.objects.get(sale=sale).is_pending
                returned_bool = model_to_filter_by == "returned" and in_returned_qs and not ReturnedSale.objects.get(sale=sale).is_pending
                pending_returned_bool = model_to_filter_by == "returned_pending" and in_returned_qs
                shipping_bool = model_to_filter_by == "shipping" and HipShipper.objects.filter(sale_entry=sale).count() > 0

                print(sale in returned_qs)

                if approved_bool or pending_bool or returned_bool or pending_returned_bool or shipping_bool:
                    temp_qs.append(sale)

            none_qs = SaleEntry.objects.none()
            sales_qs = list(chain(none_qs, temp_qs))
            print(sales_qs)
        
        data = ''
        if sales_qs:
            sales_data = serializers.serialize('json', sales_qs)
            data = sales_data
        if returned_qs and not model_to_filter_by == "approved":
            returned_data = serializers.serialize('json', returned_qs)
            if data:
                data = data[:-1] + ", " + returned_data[1:]
            else:
                data = returned_data
        if hipshipper_qs:
            hipshipper_data = serializers.serialize('json', hipshipper_qs)
            if data:
                data = data[:-1] + ", " + hipshipper_data[1:]
            else:
                data = hipshipper_data

        return HttpResponse(data, content_type="application/json")

@csrf_exempt
def verify_profits(request):
    error_counts = 0
    for sale in SaleEntry.objects.filter(user=request.user):
        if (sale.profit != sale.calc_profit()):
            error_counts += 1
            sale.profit = sale.calc_profit()

    if (error_counts > 0):
        string = f"{error_counts} errors found and fixed!"
    else:
        string = "No errors found."

    return HttpResponse(string);

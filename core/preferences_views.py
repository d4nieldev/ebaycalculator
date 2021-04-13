from .models import Preferences

from django.http import JsonResponse, HttpResponse

from django.views.decorators.csrf import csrf_exempt

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from django.core import serializers

import json


@csrf_exempt
def toggle_paypal_editable(request):
    if request.method == "POST" and bool(request.POST['value']):
        try:
            user_prefs = Preferences.objects.get(user=request.user)
        except ObjectDoesNotExist:
            user_prefs = Preferences(user=request.user)

        user_prefs.is_paypal_editable = not user_prefs.is_paypal_editable
        try:
            user_prefs.save()
        except ValidationError:
            return JsonResponse({
                'ERROR': '',
                'user prefs.is_paypal_editable': user_prefs.is_paypal_editable,
                'request': request.POST
            })

        print(user_prefs)

        return JsonResponse({
            "success": 'success',
        })
    
    return JsonResponse({
        "error": "error has occured"
    })


@csrf_exempt
def edit_preferences(request):
    if request.method == "POST":
        user_prefs = Preferences.objects.get(user=request.user)
        elem_changed = request.POST['element_changed']
        if request.POST['value'] == 'true':
            value = True
        elif request.POST['value'] == 'false':
            value = False

        err_response = {}
        if elem_changed == "f_default_month":
            err_response['f_default_month'] = value
            user_prefs.default_month = value
        elif elem_changed == "f_start_month_day":
            err_response['f_start_month_day'] = int(request.POST['value'])
            user_prefs.start_month_day = int(request.POST['value'])
        elif elem_changed == "f_sort_by_date":
            err_response['f_sort_by_date'] = value
            user_prefs.sort_by_date = value
        
        try:
            user_prefs.save()
        except ValidationError as err:
            err_response['ERROR MESSAGE'] = err.message
            return JsonResponse(err_response)
        return JsonResponse({"success": f"{elem_changed} changed to {value} successfully!"})
    return JsonResponse({"failure": "an error has occured"})

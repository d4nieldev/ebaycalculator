from .models import Preferences

from django.http import JsonResponse, HttpResponse

from django.views.decorators.csrf import csrf_exempt

from django.core.exceptions import ObjectDoesNotExist

from django.core import serializers

import json


@csrf_exempt
def toggle_paypal_editable(request):
    if request.method == "POST":
        try:
            user_prefs = Preferences.objects.get(user=request.user)
        except ObjectDoesNotExist:
            user_prefs = Preferences(user=request.user)

        print("HERE")

        if (request.POST['value'] == "false"):
            user_prefs.is_paypal_editable = True
        else:
            user_prefs.is_paypal_editable = False
        user_prefs.save()

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
        value = request.POST['value']

        if elem_changed == "f_default_month":
            user_prefs.default_month = value == "true"
        elif elem_changed == "f_start_month_day":
            user_prefs.start_month_day = int(value)
        elif elem_changed == "f_sort_by_date":
            user_prefs.sort_by_date = value == "true"
        
        user_prefs.save()
        return JsonResponse({"success": f"{elem_changed} changed to {value} successfully!"})
    return JsonResponse({"failure": "an error has occured"})

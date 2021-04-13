from .models import Preferences
from .forms import PreferencesForm

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
    if request.method == 'POST':
        response = {}
        user_prefs = Preferences.objects.get(user=request.user)
        response['old_prefs'] = str(user_prefs)
        form = PreferencesForm(request.POST, instance=user_prefs)
        if form.is_valid():
            obj = form.save()
            response['new_prefs'] = str(obj)
            response['success'] = "preferences saved successfully!"

            return JsonResponse(response)
    
    return JsonResponse({"failure": "an error has occured..."})


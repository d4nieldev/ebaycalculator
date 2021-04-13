from .models import Preferences
from .forms import PreferencesForm

from django.http import JsonResponse, HttpResponse

from django.views.decorators.csrf import csrf_exempt

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from django.core import serializers

import json


@csrf_exempt
def edit_preferences(request):
    if request.method == 'POST':
        response = {}
        user_prefs = Preferences.objects.get(user=request.user)
        response['old_prefs'] = str(user_prefs)
        form = PreferencesForm(request.POST, instance=user_prefs)
        response['POST request'] = request.POST
        if form.is_valid():
            obj = form.save()
            response['new_prefs'] = str(obj)
            response['success'] = "preferences saved successfully!"

            return JsonResponse(response)
    
    return JsonResponse({"failure": "an error has occured..."})


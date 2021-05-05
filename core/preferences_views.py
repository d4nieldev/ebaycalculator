from .models import Preferences
from .forms import PreferencesForm

from django.http import JsonResponse, HttpResponse

from django.views.decorators.csrf import csrf_exempt

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from django.core import serializers

import json


@csrf_exempt
def edit_preferences(request):
    '''Responsible for changing the preferences.

    #### Parameters
    `request : django.http.HttpRequest` The request
    '''
    if request.method == 'POST':
        user_prefs = Preferences.objects.get(user=request.user)
        form = PreferencesForm(request.POST, instance=user_prefs)
        
        if form.is_valid():
            form.save()

            return JsonResponse({'success': "preferences saved successfully!"})
    
    return JsonResponse({"failure": "an error has occured..."})


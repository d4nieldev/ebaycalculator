from .models import Preferences

from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt

from django.core.exceptions import ObjectDoesNotExist


@csrf_exempt
def toggle_paypal_editable(request):
    if request.method == "POST":
        try:
            user_prefs = Preferences.objects.get(user=request.user)
        except ObjectDoesNotExist:
            user_prefs = Preferences(user=request.user)
        user_prefs.is_paypal_editable = request.POST['value'] == 'false'
        user_prefs.save()

        print(user_prefs)

        return JsonResponse({
            "success": 'success',
        })
    
    return JsonResponse({
        "error": "error has occured"
    })
        

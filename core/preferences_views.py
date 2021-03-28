from .models import Preferences

from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def toggle_paypal_editable(request):
    if request.POST:
        user_prefs = Preferences.objects.get(user=request.user)
        user_prefs.is_paypal_editable = not request.POST['value'] == 'true'
        user_prefs.save()

        print(user_prefs)

        return JsonResponse({
            "success": 'success',
        })
    
    return JsonResponse({
        "error": "error has occured"
    })
        

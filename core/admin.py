from django.contrib import admin

from .models import SaleEntry, Balance, Gift, Cost

admin.site.register(SaleEntry)
admin.site.register(Balance)
admin.site.register(Gift)
admin.site.register(Cost)

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
urlpatterns = [
    path('', include('core.urls'))
]
if settings.DEBUG:
    urlpatterns.append(path('admin/', admin.site.urls))

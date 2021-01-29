from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('panel', views.panel, name='panel'),
    path('logout', views.HANDLE_LOGOUT_BASE, name='logout'),
]

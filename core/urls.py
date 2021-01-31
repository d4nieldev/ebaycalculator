from django.urls import path

from . import views, apiViews

urlpatterns = [
    path('', views.index, name='index'),
    path('panel', views.panel, name='panel'),
    path('logout', views.HANDLE_LOGOUT_BASE, name='logout'),
    path('update_sale', apiViews.update_sale, name='update_sale'),
    path('delete_sale', apiViews.delete_sale, name='delete_sale'),
]

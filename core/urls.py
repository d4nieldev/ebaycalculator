from django.urls import path

from . import views, apiViews

urlpatterns = [
    # Actual HTML pages
    path('', views.index, name='index'),
    path('panel', views.panel, name='panel'),
    
    # methods called mostly from ajax
    path('logout', apiViews.HANDLE_LOGOUT_BASE, name='logout'),
    path('update_sale', apiViews.update_sale, name='update_sale'),
    path('delete_sale', apiViews.delete_sale, name='delete_sale'),
    path('add_sale', apiViews.add_sale, name='add_sale'),
    path('filter_gifts', apiViews.filter_gifts, name="filter_gifts"),
    path('add_balance', apiViews.add_balance, name="add_balance"),
    path('add_cost', apiViews.add_cost, name="add_cost"),
    path('delete_cost', apiViews.delete_cost, name="delete_cost"),
    path('add_hipshipper', apiViews.add_hipshipper, name="add_hipshipper"),
    path('delete_gift', apiViews.delete_gift, name="delete_gift"),
]

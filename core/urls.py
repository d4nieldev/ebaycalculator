from django.urls import path

from . import views, apiViews, preferences_views

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
    path('update_hipshipper', apiViews.update_hipshipper, name="update_hipshipper"),
    path('delete_gift', apiViews.delete_gift, name="delete_gift"),
    path('return_sale', apiViews.return_sale, name="return_sale"),
    path('cancel_return_sale', apiViews.cancel_return_sale, name="cancel_return_sale"),
    path('update_paypal_balance', apiViews.update_paypal_balance, name="update_paypal_balance"),
    path('filter_sales', apiViews.filter_sales, name="filter_sales"),

    # preferences
    path('edit_preferences', preferences_views.edit_preferences, name="edit_preferences")
    
]

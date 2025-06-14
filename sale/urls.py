from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('state_list',views.state_list,name='state_list'),
    path('cost_card_form/<int:id>',views.cost_card_form,name='cost_card_form'),\
    path('permit_entry/', views.permit_entry, name='permit_entry'),
    path('permit_pending_sale_invoice/',views.permit_pending_sale_invoice,name='permit_pending_sale_invoice'),
    path('vehicle_for_loading/',views.vehicle_for_loading,name = 'vehicle_for_loading'),
    path('permit_item_entry/', views.permit_item_entry, name='permit_item_entry'),
    path('sale_invoice/<int:id>', views.sale_invoice, name='sale_invoice'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 

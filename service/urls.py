from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Quotations
    path('quotations/', views.service_quotation_list, name='service_quotation_list'),
    path('quotations/create/', views.service_quotation_create, name='service_quotation_create'),
    path('quotations/<int:pk>/edit/', views.service_quotation_update, name='service_quotation_update'),
    path('quotations/<int:pk>/approve/', views.service_quotation_update, name='service_quotation_approve'),
    path('quotations/<int:pk>/delete/', views.service_quotation_delete, name='service_quotation_delete'),
    path('quotation/<int:pk>/approve/', views.service_quotation_approve, name='service_quotation_approve'),
    path('service_quotation_items/<int:pk>/', views.service_quotation_items, name='service_quotation_items'),
    
    # Orders
    path('dashboard/', views.service_order_dashboard, name='service_order_dashboard'),
    path('orders/', views.service_order_list, name='service_order_list'),
    path('orders/create/', views.service_order_create, name='service_order_create'),
    path('orders/<int:pk>/edit/', views.service_order_update, name='service_order_update'),
    path('orders/<int:pk>/approve/', views.service_order_approve, name='service_order_approve'),
    path('orders/<int:pk>/delete/', views.service_order_delete, name='service_order_delete'),
    path('service_order_items/<int:pk>/', views.service_order_items, name='service_order_items'),
    path('status_update/<int:pk>/', views.service_order_completion_status, name='service_order_status_update'),

    # Invoices
    path('invoices/>', views.service_invoice_list, name='service_invoice_list'),
    path('service_invoice/', views.service_invoice, name='service_invoice'),
    path('invoices/create/<int:id>/', views.service_invoice_create, name='service_invoice_create'),
    path('invoices/<int:pk>/edit/', views.service_invoice_update, name='service_invoice_update'),
    path('invoices/<int:pk>/delete/', views.service_invoice_delete, name='service_invoice_delete'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 

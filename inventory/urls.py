from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('index/',views.index,name='index'),
    path('add_supplier/',views.add_supplier,name='add_supplier'),
    path('quotation_entry/',views.quotation_entry,name='quotation_entry'),
    path('quotation_items/<int:id>',views.quotation_items,name='quotation_items'),
    path('update_quotation/<int:id>',views.update_quotation,name='update_quotation'),
    path('assign_quotation_approver/<int:id>/',views.assign_quotation_approver,name='assign_quotation_approver'),
    path('assign_po_approver/<int:id>/',views.assign_po_approver,name='assign_po_approver'),
    path('approve_quotation/<int:id>/',views.approve_quotation,name='approve_quotation'),
    path('quotation_list/',views.quotation_list,name='quotation_list'),  
    path('quotation_pending_po_generation/',views.quotation_pending_po_generation,name='quotation_pending_po_generation'), 
    path('po_entry/<int:id>/',views.po_entry,name='po_entry'),
    path('purchase_order_items/<int:id>/',views.purchase_order_items,name='purchase_order_items'),
    path('freight_purchase_order/<int:id>/',views.freight_purchase_order,name = 'freight_purchase_order'),    
    path('po_list/',views.po_list,name='po_list'),
    path('update_po/<int:id>',views.update_po,name='update_po'), #iThis is with pk
    path('process_po/<int:id>',views.process_po,name='process_po'), #input PO NO to process
    path('freight_po/<int:id>',views.freight_purchase_order,name='freight_po'), #input PO NO to process
    path('lcr_po_join/<int:id>',views.po_lcr_join,name='lcr_po_join'),
    path('approve_po/<int:pk>/',views.approve_po,name='approve_po'),
    path('gate_entry/',views.generate_gate_entry,name='gate_entry'),
    path('gate_entry_register/',views.gate_entry_register,name='gate_entry_register'),    
    path('vehicle_out_time/<int:id>/',views.vehicle_out_time,name='vehicle_out_time'),
    path('receipts_pending_mrn/',views.receipts_pending_mrn,name='receipts_pending_mrn'),
    path('generate_mrn/<int:id>/',views.generate_mrn,name='generate_mrn'),
    path('process_mrn/<int:id>/',views.process_mrn,name='process_mrn'),
    path('vehicle_awaiting_unloading/',views.gate_entry_awaiting_unloading,name='vehicle_awaiting_unloading'),
    path('vehicle_unload/<int:id>/',views.vehicle_unload,name='vehicle_unload'),
    path('vehicle_unload_items/<int:id>/',views.vehicle_unload_items,name='vehicle_unload_items'),
    path('vehicle_awaiting_quality_check/',views.vehicle_awaiting_quality_check,name='vehicle_awaiting_quality_check'),   
    path('quality_check/<int:id>/',views.quality_check,name='quality_check'),
    path('update_flag/<int:id>/',views.update_flag,name='update_flag'),
    path('mrn_awaiting_stock_location/',views.mrn_awating_stock_location,name='mrn_awaiting_stock_location'),
    path('mrn_report_view/',views.mrn_report_view,name='mrn_report'),
    
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 

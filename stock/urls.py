from django.urls import path
from . import views

urlpatterns = [
    path('stock_entry/<int:id>/', views.stock_entry, name='stock_entry'),
    path('create_blend_bom/',views.create_blend_bom,name='create_blend_bom'),
    path('bom_items/<int:id>/',views.bom_items,name='bom_items'),
    path('create_blend/',views.create_blend,name='create_blend'),
    path('material_requisition/<int:id>/',views.material_requisition,name='material_requisition'),
    path('blend_awaiting_issue/',views.blend_awating_issue,name='blend_awaiting_issue'),
    path('issue_to_blend/<int:id>/',views.issue_to_blend,name='issue_to_blend'),
    path('stock_location_update/',views.stock_location_update,name='stock_location_update'),
    path('update_stock_ledger/<int:id>/',views.update_stock_ledger,name='update_stock_ledger'),
    path('account_entry/<int:blend>/',views.account_entry,name='account_entry'),
    path('bottling_material_requisition/<int:id>/',views.bottling_material_requisition,name='bottling_material_requisition'),
    path('bottling_awaiting_issue/',views.bottling_awaiting_issue,name='bottling_awaiting_issue'),
    path('issue_to_bottling/<int:id>/',views.issue_to_bottling,name='issue_to_bottling'),
    path('stock_ledger/',views.stock_ledger_view,name='stock_ledger'),

    # path('success/', some_success_view, name='success'),  # Replace with your actual success view
]

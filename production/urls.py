from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('blend_awaiting_processing/',blend_awaiting_processing,name='blend_awaiting_processing'),    
    path('blend_wip/<int:id>/',blend_wip,name='blend_wip'),
    # path('wip_accounting_entry/<int:id>/',wip_accounting_entry,name='wip_accounting_entry'),
    path('blend_awaiting_transfer/',blend_awaiting_transfer,name='blend_awaiting_transfer'),
    # path('update_finished_blend_stock_ledger/<int:fb_id>/',update_finished_blend_stock_ledger,name='update_finished_blend_stock_ledger')
    path('wip_issue/<int:id>',wip_issue,name='wip_issue'),
    path('daily_production_plan/',daily_production_plan,name='daily_production_plan'),
    path('daily_production_plan_line/',daily_production_plan_line,name='daily_production_plan_line'),
    path('daily_production_plan_list/',daily_production_plan_list,name='daily_production_plan_list'),
    path('update_daily_production_plan/<int:id>/',update_daily_production_plan,name='update_daily_production_plan'),
    path('open_production_plan/',open_production_plan,name='open_production_plan'),
    path('production_entry/<int:id>',production_entry,name='production_entry'),
    path('production_entry_line/',production_entry_line,name='production_entry_line'),    
    path('blend_requisition/<int:id>/',blend_requisition,name='blend_requisition'), 
    
    # path('finish_blend_issue/<int:id>',finish_blend_issue,name='finish_blend_issue'),
    # path('finished_blend_issue_accounting_entry/<int:id>/',finished_blend_issue_accounting_entry,name='finished_blend_issue_accounting_entry'),
    # path('receive_blend_for_bottling/',receive_blend_for_bottling,name='receive_blend_for_bottling'),
    path('prodction_entry/',production_entry,name='production_entry'),
    path('rm_consumption/<int:id>',raw_material_consumption,name='rm_consumption'),
    # path('blend_consumption/<int:id>/',blend_consumption,name='blend_consumption'),
    path('update_wip_overhead_cost/<int:id>/',update_wip_overhead_cost,name='update_wip_overhead_cost'),
     

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
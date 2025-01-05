from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    # path('blend_awaiting_processing/',blend_awaiting_processing,name='blend_awaiting_processing'),    
    # path('blend_wip/<int:id>/',blend_wip,name='blend_wip'),
    # path('wip_accounting_entry/<int:id>/',wip_accounting_entry,name='wip_accounting_entry'),
    # path('blend_awating_transfer/',blend_awaiting_transfer,name='blend_awaiting_transfer'),
    # path('wip_issue/<int:id>',wip_issue,name='wip_issue'),
    # path('wips_accounting_entry/<int:id>',wip_issue_accounting_entry,name = 'wips_accounting_entry' ),
    # path('receive_blend/',receive_blend,name='receive_blend'),
    # path('finished_blend/<int:id>/',finished_blend,name='finished_blend'),
    # path('finished_blend_accounting_entry/<int:id>/',finished_blend_accounting_entry,name='finished_blend_accounting_entry'),
    # path('blend_awaiting_bottling/',blend_awaiting_bottling,name='blend_awaiting_bottling'),
    # path('blend_requisition/',blend_requisition,name='blend_requisition'), 
    # path('finish_blend_issue/<int:id>',finish_blend_issue,name='finish_blend_issue'),
    # path('finished_blend_issue_accounting_entry/<int:id>/',finished_blend_issue_accounting_entry,name='finished_blend_issue_accounting_entry'),
    # path('receive_blend_for_bottling/',receive_blend_for_bottling,name='receive_blend_for_bottling'),
    # path('finished_goods/',finished_goods,name='finished_goods'),
    # path('finished_goods_items/<int:id>',finished_goods_items,name='finished_goods_items'),
    # path('transfer_for_bottling/',blend_transfer_for_bottling,name='blend_transfer_for_bottling'),
    # path('dg_consumption/<int:id>',dg_consumption,name='dg_consumption'),
    # path('blend_consumption/<int:id>/',blend_consumption,name='blend_consumption'),
    # path('update_wip_overhead_cost/<int:id>/',update_wip_overhead_cost,name='update_wip_overhead_cost'),
     

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
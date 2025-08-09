from django.urls import path
from . import views

urlpatterns = [
    
    path('update_account_chart_orm/', views.update_account_chart_orm, name='update_account_chart_orm'),
    path('bank_payment_view/',views.bank_payment_view,name='bank_payment_view'),
    path('bank_receipt_view/',views.bank_receipt_view,name='bank_receipt_view'),
    path('journal_entry/',views.journal_entry_view,name='journal_entry'),
    path('create_journal/',views.create_journal,name='create_journal'),
    
]

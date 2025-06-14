from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inv/',include('inventory.urls')),
    path('stock/',include('stock.urls')),
    path('',include('login.urls')),
    path('prod/',include('production.urls')),
    path('acc/',include('accounts.urls')),
    path('sale/',include('sale.urls')),
    path('service/',include('service.urls')),
    
]

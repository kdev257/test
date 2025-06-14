from django.contrib import admin
from .models import Slabs,Cost_Card,Cost_Card_Item,Permit,Permit_Item,Sales_Invoice,Sales_Invoice_Item,Customer,Customer_Profile

# Register your models here.
admin.site.register(Customer)
admin.site.register(Customer_Profile)
admin.site.register(Slabs)
admin.site.register(Cost_Card)
admin.site.register(Cost_Card_Item)
admin.site.register(Permit)
admin.site.register(Permit_Item)
admin.site.register(Sales_Invoice)  
admin.site.register(Sales_Invoice_Item)
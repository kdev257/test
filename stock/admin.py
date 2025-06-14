from django.contrib import admin
from .models import Blend_Bom,Bom_Items,Blend,Stock_Entry,Stock_Ledger
# Register your models here.

admin.site.register(Blend_Bom)
admin.site.register(Bom_Items)
admin.site.register(Blend)  
admin.site.register(Stock_Entry)    
admin.site.register(Stock_Ledger)

from django.contrib import admin
from .models import Bottling_lines,Daily_Production_Plan,Map_Brand_SKU_Item,Overheads_Absorbed

# Register your models here.
admin.site.register(Bottling_lines)
admin.site.register(Daily_Production_Plan)
admin.site.register(Map_Brand_SKU_Item)
admin.site.register(Overheads_Absorbed)
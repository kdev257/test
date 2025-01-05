# from django.db import models
# from django.utils import timezone
# from django.core.validators import MinValueValidator
# from inventory.models import Material_Receipt_Note
# from masters.models import Transaction_Type,User,Unit_of_Measurement,Unit,Brand,Item,SKU,Unit_Sub_Location, Unit_Stock_Location,Stock_Location,Account_Chart,State
# from stock.models import Blend
# from accounts.models import Inv_Transaction,Overheads
# from inventory.functions import generate_document_number
# from django.db import transaction as db_transaction
        


# class Blend_WIP(models.Model):
#     transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,related_name='wip_tt')
#     transaction_number = models.CharField(max_length=20)
#     transaction_date = models.DateField()
#     blend = models.ForeignKey(Blend,on_delete=models.CASCADE,related_name='wip_blend')
#     unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='wip_unit',blank=True,null=True)    
#     # issue = models.OneToOneField(Stock_Entry,on_delete=models.CASCADE,related_name='wip_issue',blank=True,null=True) 
#     stock_location = models.ForeignKey(Unit_Sub_Location,on_delete=models.CASCADE,blank=True,null=True,related_name='storage_location') ## issue.to_location which is recieving the transfer
#     water = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],blank=True,null=True)
#     blend_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],blank=True,null=True)
#     blend_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],blank=True,null=True)
#     average_cost = models.DecimalField(max_digits=30,decimal_places=4,validators=[MinValueValidator(0.0)],blank=True,null=True)
#     issue_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
#     issue_to = models.ForeignKey(Unit_Sub_Location,on_delete=models.CASCADE,blank=True,null=True,verbose_name='Issue To Location',related_name='issue_to_location')    
#     issue_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
#     opening_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
#     opening_value= models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
#     closing_quantity=models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
#     closing_value=models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
#     contra_account = models.ForeignKey(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='wip_contra_account')
#     wip_inventory_account = models.ForeignKey(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='wip_inventory_account')    
#     is_issued = models.BooleanField(default=False)
#     created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='blendor',blank=True,null=True)
#     created = models.DateTimeField(blank=True,null=True)
#     modified = models.DateTimeField(blank=True,null=True)
    
    
    
#     def __str__(self):
#         return f'{self.transaction_number} -- {self.blend_quantity} -- {self.blend_value}'
    
#     def save(self,*args, **kwargs):
#         if not self.created:
#             self.created = timezone.now()
#         self.modified = timezone.now()
    
#         if self.transaction_type.transaction_name == 'WIPR':
#             self.transaction_date = timezone.now()
#             self.unit = self.blend.unit
#             if not self.pk:
#                 if not self.transaction_number:
#                     self.transaction_number= generate_document_number(
#                     transaction_type=self.transaction_type,
#                     model_class=Blend_WIP,
#                     unit = self.unit,
#                     number_field= 'transaction_number',               
#                 )
#         elif self.transaction_type.transaction_name == 'WIPS':
#             self.transaction_date = timezone.now()
#             self.unit = self.blend.unit
#             if not self.pk:
#                 if not self.transaction_number:
#                     self.transaction_number= generate_document_number(
#                     transaction_type=self.transaction_type,
#                     model_class=Blend_WIP,
#                     unit = self.unit,
#                     number_field= 'transaction_number',               
#                 )
            
#         super().save(*args, **kwargs)    
     
    
# class Finished_Blend(models.Model):
#     transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE)
#     transaction_number = models.CharField(max_length=30)
#     transaction_date = models.DateField()
#     unit = models.ForeignKey(Unit,on_delete=models.CASCADE,blank=True,null=True)
#     blend = models.ForeignKey(Blend,on_delete=models.CASCADE,related_name='finished_blend',blank=True,null=True)
#     blend_wip = models.ForeignKey(Blend_WIP,on_delete=models.CASCADE,related_name='wip_number') 
#     location = models.ForeignKey(Unit_Sub_Location,on_delete=models.CASCADE,related_name='blend_location')  
#     to_location = models.ForeignKey(Unit_Sub_Location,on_delete=models.CASCADE,related_name='to_location',blank=True,null=True)       
#     opening_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
#     opening_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
#     receipt_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
#     receipt_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
#     requisition = models.ForeignKey('Blend_Requisition',on_delete=models.CASCADE,blank=True,null=True)
#     issue_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
#     issue_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
#     closing_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
#     closing_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
#     average_cost = models.DecimalField(max_digits=30,decimal_places=4,validators=[MinValueValidator(0.0)],default=0)
#     bottled_quantity = models.DecimalField(max_digits=30,decimal_places=4,validators=[MinValueValidator(0.0)],default=0)
#     average_issue_rate = models.DecimalField(max_digits=10,decimal_places=4,validators=[MinValueValidator(0.0)],default=0)
#     inventory_account = models.ForeignKey(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='Blend_Debit_Account')
#     contra_account = models.ForeignKey(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='blend_credit_Account')
#     is_issued = models.BooleanField(default=False)
#     created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='finish_blend',blank=True,null=True)
#     created = models.DateTimeField(blank=True,null=True)
#     modified = models.DateTimeField(blank=True,null=True)
   
#     def __str__(self):
#         return f'{self.transaction_number} -- {self.transaction_date})'
    
#     def save(self,*args, **kwargs):
#         if self.transaction_type.transaction_name =='BR':
#             if not self.created:
#                 self.created = timezone.now()
#             self.modified = timezone.now()
#             self.transaction_date = timezone.now()       
#             if not self.pk:
#                 if not self.transaction_number:
#                     self.transaction_number=generate_document_number(
#                         model_class= Finished_Blend,
#                         transaction_type = self.transaction_type,
#                         unit = self.unit, 
#                         number_field= 'transaction_number'
#                     )
#         elif self.transaction_type.transaction_name == 'BI':
#             if not self.created:
#                 self.created = timezone.now()
#             self.modified = timezone.now()
#             self.transaction_date = timezone.now()       
#             if not self.pk:
#                 if not self.transaction_number:
#                     self.transaction_number=generate_document_number(
#                         model_class= Finished_Blend,
#                         transaction_type = self.transaction_type,
#                         unit = self.unit, 
#                         number_field= 'transaction_number'
#                     )            
#         super().save(*args, **kwargs)
                        

# class Blend_Requisition(models.Model):
#     transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE)
#     transaction_number = models.CharField(max_length=30)
#     transaction_date = models.DateField()
#     unit = models.ForeignKey(Unit,on_delete=models.CASCADE,blank=True,null=True)
#     blend = models.ForeignKey(Blend,on_delete=models.CASCADE,related_name='requistion_blend',blank=True,null=True)
#     finish_blend = models.ForeignKey(Finished_Blend,on_delete=models.CASCADE,related_name='req_fb_number',blank=True,null=True) 
#     to_location = models.ForeignKey(Unit_Sub_Location,on_delete=models.CASCADE,related_name='req_blend_location')
#     brand = models.ForeignKey(Brand,on_delete=models.CASCADE,related_name='requisitioned_blend')
#     sku = models.ForeignKey(SKU,on_delete= models.CASCADE,related_name='requistioned_sku')
#     quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],verbose_name='Quanity To be manufactured in Bottles')
#     uom = models.ForeignKey(Unit_of_Measurement,on_delete=models.CASCADE)
#     blend_required = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
#     created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='req_by',blank=True,null=True)
#     created = models.DateTimeField(blank=True,null=True)
#     modified = models.DateTimeField(blank=True,null=True) 
    
#     def __str__(self):
#         return f'{self.id} -- {self.transaction_type}--{self.blend} '  
    
#     def save(self,*args, **kwargs):
#         if not self.pk:
#              self.transaction_date = timezone.now()        
#         if not self.created:           
#             self.created = timezone.now()
#         self.modified = timezone.now()
#         self.transaction_date = timezone.now()       
#         if not self.pk:
#             if not self.transaction_number:
#                 self.transaction_number=generate_document_number(
#                     model_class= Finished_Blend,
#                     transaction_type = self.transaction_type,
#                     unit = self.unit, 
#                     number_field= 'transaction_number'
#                 )
                    
#         super().save(*args, **kwargs)
            
# class Receive_Blend_For_Bottling(models.Model):
#     transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,related_name='receive_tt') 
#     transaction_number = models.CharField(max_length=30)
#     transaction_date = models.DateTimeField()
#     unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='bottling_unit')
#     blend = models.ForeignKey(Blend, on_delete=models.CASCADE,related_name='blend_for_bottling')  
#     finished_goods= models.ForeignKey('Finished_Goods', on_delete=models.CASCADE,related_name='finish_good_id',blank=True,null=True) 
#     finished_blend = models.ForeignKey(Finished_Blend, on_delete=models.CASCADE,related_name='blend_for_bottling',blank=True,null=True)    
#     location = models.ForeignKey(Unit_Sub_Location,on_delete=models.CASCADE,related_name='blend_receive_location')
#     opening_quantity = models.DecimalField(max_digits=20,decimal_places=3,validators=[MinValueValidator(0,0)],default=0)
#     opening_value = models.DecimalField(max_digits=20,decimal_places=2,validators=[MinValueValidator(0,0)],default=0)
#     receipt_quantity = models.DecimalField(max_digits=20,decimal_places=3,validators=[MinValueValidator(0,0)],default=0)
#     receipt_value = models.DecimalField(max_digits=20,decimal_places=2,validators=[MinValueValidator(0,0)],default=0)
#     consumption_quantity = models.DecimalField(max_digits=20,decimal_places=2,validators=[MinValueValidator(0,0)],default=0)
#     consumption_value =models.DecimalField(max_digits=20,decimal_places=2,validators=[MinValueValidator(0,0)],default=0)   
#     closing_quantity = models.DecimalField(max_digits=20,decimal_places=2,validators=[MinValueValidator(0,0)],default=0)
#     closing_value = models.DecimalField(max_digits=20,decimal_places=2,validators=[MinValueValidator(0,0)],default=0)
#     average_rate = models.DecimalField(max_digits=20,decimal_places=2,validators=[MinValueValidator(0,0)],default=0)
#     account = models.ForeignKey(Account_Chart,on_delete=models.CASCADE,blank=True,null=True)
#     is_stock_updated = models.BooleanField(default=False)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name='bottling_created_by',blank=True,null=True)
#     created = models.DateTimeField()
#     modified = models.DateTimeField()
    
#     fields = [transaction_type,transaction_number,transaction_date,opening_quantity,opening_value,receipt_quantity,receipt_value,closing_quantity,closing_value,average_rate,account,created,created,modified]

#     def __str__(self):
#         return f'{self.transaction_number} {self.blend}'
    
    
    
#     def save(self,*args, **kwargs):
#         if not self.transaction_date:
#             self.transaction_date = timezone.now()
#         if not self.created:
#             self.created = timezone.now()
#         self.modified = timezone.now()
#         if not self.pk:
#             self.transaction_number=generate_document_number(
#                 model_class=Receive_Blend_For_Bottling,
#                 transaction_type= self.transaction_type,
#                 unit = self.unit,
#                 number_field='transaction_number'
                
#             )
#         super().save(*args, **kwargs)
    
# class WorkInProgress(models.Model):
#     transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,blank=True,null=True)
#     transaction_number= models.CharField(max_length=30,default="")
#     transaction_date = models.DateTimeField()
#     blend = models.ForeignKey(Blend,on_delete=models.CASCADE,verbose_name='Blend_Number')
#     unit = models.ForeignKey(Unit,on_delete=models.CASCADE)
#     brand = models.ForeignKey(Brand,on_delete=models.CASCADE)
#     sku = models.ForeignKey(SKU,on_delete=models.CASCADE,blank=True,null=True)
#     material_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)    
#     overhead_absorbed = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
#     total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
#     is_completed = models.BooleanField(default=False)
#     created_by = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
#     created = models.DateTimeField(blank=True,null=True)
#     modified =  models.DateTimeField(blank=True,null=True)

#     def calculate_total_cost(self):
#         self.total_cost = (
#             self.material_cost + 
#             self.labor_cost + 
#             self.variable_overhead_absorbed + 
#             self.fixed_overhead_absorbed
#         )
#         self.save()
        
#     def save(self,*args, **kwargs):
#         if not self.pk:           
#             self.transaction_date=timezone.now()
#             self.created = timezone.now()
#         self.modified = timezone.now()
        
#         super().save(*args, **kwargs)
    

# class Finished_Goods(models.Model):
#     transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,related_name='fg_transaction') 
#     transaction_number = models.CharField(max_length=30)
#     transaction_date = models.DateTimeField()
#     blend = models.ForeignKey(Blend,on_delete=models.CASCADE,blank=True,null=True)
#     finished_blend = models.ForeignKey(Finished_Blend, on_delete=models.CASCADE,related_name='fg_blend',blank=True,null=True)
#     unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='fg_unit_name')    
#     created_by= models.ForeignKey(User,on_delete=models.CASCADE,related_name='fg_created_by')
#     created = models.DateField()
#     modified = models.DateField()
       
#     def __str__(self):
#         return f'{self.transaction_number} -- {self.transaction_date}'
    
#     def save(self,*args, **kwargs):
#         if not self.pk:
#             self.transaction_date=timezone.now()
#             self.created = timezone.now()
#             if not self.transaction_number:
#                 self.transaction_number=generate_document_number(
#                     model_class=Finished_Goods,
#                     transaction_type=self.transaction_type,
#                     unit = self.unit,
#                     number_field= 'transaction_number'
#                 )
#         self.modified = timezone.now()
                
#         super().save(*args, **kwargs)
    
# class Map_FG_Brand_SKU_Stock_location(models.Model):
#     brand = models.ForeignKey(Brand,on_delete=models.CASCADE,related_name='fg_stock_location')
#     sku = models.ForeignKey(SKU,on_delete=models.CASCADE,related_name='sku_stock_location')
#     unit = models.ForeignKey(Unit,on_delete=models.CASCADE,blank=True,null=True)
#     location = models.ForeignKey(Unit_Sub_Location,on_delete=models.CASCADE,related_name='fg_sku_location')
    
#     def __str__(self):
#         return f"{self.brand} -- {self.sku} -- {self.location}"
    

# class Finished_Goods_Items(models.Model):
#     finished_goods = models.ForeignKey(Finished_Goods,on_delete=models.CASCADE,related_name='fg_id')
#     brand = models.ForeignKey(Brand,on_delete=models.CASCADE,related_name='fg_brand')
#     sku = models.ForeignKey(SKU,on_delete=models.CASCADE,related_name='fg_sku')
#     location= models.ForeignKey(Map_FG_Brand_SKU_Stock_location,on_delete=models.CASCADE,blank=True,null=True)
#     unit = models.ForeignKey(Unit,on_delete=models.CASCADE,blank=True,null=True)
#     blend = models.ForeignKey(Blend,on_delete=models.CASCADE,blank=True,null=True)
#     state = models.ForeignKey(State,on_delete=models.CASCADE,related_name='fg_state')
#     opening_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Opening Quantity cannot be less than zero')],default=0)
#     opening_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Opening value cannot be less than zero')],default=0)
#     production_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Production Quantity cannot be less than zero')],default=0)
#     production_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Production value cannot be less than zero')],default=0)
#     despatch_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Despatch Quantity cannot be less than zero')],default=0)
#     despatch_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Despatch Value cannot be less than zero')],default=0)
#     closing_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Closing Quantity cannot be less than zero')],default=0)
#     closing_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Closing Quantity cannot be less than zero')],default=0)
#     average_cost = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Average Cost cannot be less than zero')],default=0)
#     account = models.ForeignKey(Account_Chart,on_delete=models.CASCADE,related_name='fg_Account')
    
#     def __str__(self):
#         return f'{self.finished_goods} -- {self.brand}{self.sku} -- {self.production_quantity}--{self.production_value}'
    
# class Blend_Consumption(models.Model):
#     finish_goods = models.ForeignKey(Finished_Goods_Items,on_delete=models.CASCADE,related_name='fg_blend_consumption')
#     blend = models.ForeignKey(Blend,on_delete=models.CASCADE,blank=True,null=True)
#     finished_blend = models.ForeignKey(Finished_Blend,on_delete=models.CASCADE,blank=True,null=True)
#     opening_quantity= models.DecimalField(max_digits=20,decimal_places=2,validators=[MinValueValidator(0.0,message='Opening_quantity cannot be less than zero')])
#     opening_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Opening Quantity cannot be less than zero')])
#     opening_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Opening value cannot be less than zero')])
#     receipt_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Receipt Quantity cannot be less than zero')])
#     receipt_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Receipt value cannot be less than zero')])
#     consumption_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Receipt Quantity cannot be less than zero')])
#     consumption_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Receipt value cannot be less than zero')])
#     closing_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Closing Quantity cannot be less than zero')])
#     closing_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0,message='Closing Quantity cannot be less than zero')])
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name='blend_consumption_created_by')
#     created = models.DateTimeField()
#     modified = models.DateTimeField()    
    
# class Overheads_Absorbed(models.Model):
#     name = models.ForeignKey(Overheads,on_delete=models.CASCADE,related_name='absorbed_overhead')
#     blend = models.ForeignKey(Blend,on_delete=models.CASCADE,blank=True,null=True)
#     unit = models.ForeignKey(Unit,on_delete=models.CASCADE,blank=True,null=True)        
#     rate = models.DecimalField(max_digits=10,decimal_places=2)
#     amount = models.DecimalField(max_digits=10,decimal_places=2,default=0)
#     uom = models.ForeignKey(Unit_of_Measurement,on_delete=models.CASCADE)
    
#     class Meta:
#         verbose_name_plural = "Overheads Absorbed"
    
#     def __str__(self):
#         return f"{self.name}--{self.rate}--{self.amount}"
    
    


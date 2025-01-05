from django.db import models
from django.db import transaction as db_transaction
from django.core.validators import MinValueValidator
from django.db.models import F,Sum
from inventory.models import Item, Material_Receipt_Note,Transaction_Type,Gate_Entry,User,User_Roles,Mrn_Items
from masters.models import Unit,User,User_Roles,Unit_Sub_Location,Unit_Stock_Location,Stock_Location,Unit_of_Measurement,Brand,Account_Chart,SKU
from accounts.models import Inv_Transaction
from inventory.functions import generate_document_number
from django.utils import timezone

# # Create your models here.
class Blend_Bom(models.Model):
    BOM_TYPE_CHOICES =(
        ('Blend','Blend'),
        ('Bottling','Bottling'),
    )
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,related_name='bom_transaction_type')
    bom_type = models.CharField(max_length=20, choices=BOM_TYPE_CHOICES,default='Blend_bom_type')
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='bom_unit')
    bom_number = models.CharField(max_length=30)
    bom_date = models.DateTimeField()
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE,related_name='bom_brand')
    sku = models.ForeignKey(SKU,on_delete=models.CASCADE,related_name='bom_sku')  
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='bom_creator')
    created= models.DateTimeField()
    modified = models.DateTimeField()
    
    def __str__(self):
       return f"{self.transaction_type}-{self.bom_number}"
   
    def save(self,*args, **kwargs):
        self.modified = timezone.now()
        if not self.pk:
            self.bom_date = timezone.now()
            self.created = timezone.now()
            if not self.bom_number:
                self.bom_number=generate_document_number(
                    model_class=Blend_Bom,
                    transaction_type=self.transaction_type,
                    unit= self.unit,
                    number_field='bom_number'
                )
        super().save(*args, **kwargs)
    
class Bom_Items(models.Model):
    bom = models.ForeignKey(Blend_Bom,on_delete=models.CASCADE)    
    item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name='bom_item')
    bom_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    uom = models.ForeignKey(Unit_of_Measurement,on_delete=models.CASCADE,related_name='bom_uom')
    
    def __str__(self):
        return f'{self.bom} -- {self.item} -- {self.bom_quantity}'
  

# class Blend(models.Model):
#     transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE)
#     batch_number = models.CharField(max_length=100,editable=False)
#     unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='blend_unit')
#     brand = models.ForeignKey(Brand,on_delete=models.CASCADE,related_name='blend_brand')    
#     batch_quantity = models.DecimalField(max_digits=10, decimal_places=2)
#     bom = models.ForeignKey(Blend_Bom,on_delete=models.CASCADE,default=1)
#     batch_date = models.DateField(default=timezone.now,editable=False)    
#     uom = models.ForeignKey(Unit_of_Measurement,on_delete=models.CASCADE,related_name='blend_uom')
#     status = models.CharField(max_length=20,default=100)
     
#     created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='blend_creator')   

#     def __str__(self):
#         return f"{self.brand} -{self.batch_number})"
    
#     def save(self, *args, **kwargs):
#         if not self.pk:
#             if not self.batch_number:
#                 self.batch_number = generate_document_number(
#                     model_class= Blend,
#                     unit = self.unit,
#                     transaction_type= self.transaction_type,
#                     number_field= 'batch_number'                 
#                 )
#         super().save(*args, **kwargs)

# class Material_Requisition(models.Model):
#     transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE)
#     requisition_number = models.CharField(max_length=20)
#     requisition_date = models.DateField()
#     production = models.DecimalField(max_digits=20,decimal_places=2,validators=[MinValueValidator(0.0)],default=0,verbose_name='Production Quantity in Cases')
#     bom = models.ForeignKey(Blend_Bom,on_delete=models.CASCADE)
#     unit = models.ForeignKey(Unit,on_delete=models.CASCADE,blank=True,null=True)
#     blend = models.ForeignKey(Blend,on_delete=models.CASCADE,blank=True,null=True)    
#     item = models.ForeignKey(Item,on_delete=models.CASCADE,blank=True,null=True)
#     required_quantity = models.PositiveIntegerField(default=0)
#     uom = models.ForeignKey(Unit_of_Measurement,on_delete=models.CASCADE,blank=True,null=True)
#     # issue_slip = models.ForeignKey('Stock_Entry',on_delete=models.CASCADE,blank=True,null=True)
#     created_by = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    
#     class Meta:
#         constraints = [
#             models.UniqueConstraint(fields=['bom','item','blend','requisition_date'], name='unique_bom_item_blend_requisition_date')
#         ]
        
#     def __str__(self):
#         return f'{self.requisition_number} --{self.item}--{self.required_quantity}'
    
#     def save(self,*args, **kwargs):
#         if not self.pk:
#             self.requisition_date = timezone.now()
#         self.unit = self.blend.unit
#         super().save(*args, **kwargs)

# class Stock_Entry(models.Model):
#     '''Model to record receipt of material i.e Mrn transactions''' 
#     transaction_type = models.ForeignKey(Transaction_Type, on_delete=models.CASCADE, blank=True, null=True)
#     transaction_number = models.CharField(max_length=50, default='')
#     transaction_date = models.DateField()
#     unit = models.ForeignKey(Unit, on_delete=models.CASCADE, blank=True,null=True)
#     mrn  = models.ForeignKey(Mrn_Items, on_delete=models.CASCADE, related_name='report', blank=True, null=True)            
#     item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='entry_item',blank=True,null=True)   
#     quantity = models.DecimalField(editable=False, max_digits=20, decimal_places=2, default=0,validators=[MinValueValidator(0.0,'Reciept Quanity can not be less than 0'),])
#     value = models.DecimalField(max_digits=20, decimal_places=2, default=0)
#     stock_location = models.ForeignKey(Unit_Sub_Location, on_delete=models.CASCADE, related_name='stock_location',blank=True,null=True)
#     blend = models.ForeignKey(Blend,on_delete=models.CASCADE,related_name='stock_entry_blend',blank=True,null=True)
#     requisition = models.ForeignKey(Material_Requisition,on_delete=models.CASCADE,related_name='stock_requisition',blank=True,null=True)
#     issue_quantity = models.DecimalField(max_digits=20, decimal_places=2, default=0,validators=[MinValueValidator(0.0,'Issue Quanity can not be less than 0'),])
#     issue_value = models.DecimalField(max_digits=20, decimal_places=2, default=0)
#     to_location = models.ForeignKey(Unit_Sub_Location, on_delete=models.CASCADE, related_name='issue_stock_location',blank=True,null=True)
#     created_by = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
#     created = models.DateTimeField(blank=True,null=True)
#     modified = models.DateTimeField(blank=True,null=True)
    
#     def __str__(self):
#         return f'{self.mrn}--{self.unit}'
    
#     def save(self,*args, **kwargs):
#         if not self.pk:
#             self.transaction_date = timezone.now()
#             self.created = timezone.now()
#         self.modified= timezone.now()
            
#         if not self.transaction_number:
#             self.transaction_number=generate_document_number(
#                 model_class=Stock_Entry,
#                 unit= self.unit,
#                 transaction_type=self.transaction_type,
#                 number_field='transaction_number'
#             )
        
        
#         super().save(*args, **kwargs)
    
# class Stock_Issue(models.Model):
#     transaction_type = models.ForeignKey(Transaction_Type, on_delete=models.CASCADE,related_name='issue_transaction_type')
#     transaction_number = models.CharField(max_length=50)
#     transaction_date = models.DateField()
#     unit = models.ForeignKey(Unit, on_delete=models.CASCADE,related_name='issue_unit')
#     stock_entry  = models.ForeignKey(Stock_Entry, on_delete=models.CASCADE, related_name='issue_entry')            
#     item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='issue_item')   
    
#     created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='issue_created_by')
#     created = models.DateTimeField(blank=True,null=True)
#     modified = models.DateTimeField(blank=True,null=True)
    
#     def __str__(self):
#         return f'{self.mrn}--{self.unit}'
    
#     def save(self,*args, **kwargs):
#         if not self.pk:
#             self.transaction_date = timezone.now()
#             self.created = timezone.now()
#         self.modified= timezone.now()
            
#         if not self.transaction_number:
#             self.transaction_number=generate_document_number(
#                 model_class=Stock_Issue,
#                 unit= self.unit,
#                 transaction_type=self.transaction_type,
#                 number_field='transaction_number'
#             )
        
#         super().save(*args, **kwargs)

                
# class Stock_Ledger(models.Model):
#     item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name='stock_ledger_item')
#     opening_quantity = models.DecimalField(max_digits=50,decimal_places=2,validators=[MinValueValidator(0.0,'Opening Quanytity can not be less than 0'),])
#     opening_value = models.DecimalField(max_digits=20, decimal_places=2,default=0,validators=[MinValueValidator(0.0,'Opening value can not be less than 0'),])
#     receipt_entry = models.OneToOneField(Stock_Entry,on_delete=models.CASCADE,related_name='stock_reciept_entry')
#     issue_entry = models.OneToOneField(Stock_Entry,on_delete=models.CASCADE,related_name='stock_issue_entry')
#     closing_quantity = models.DecimalField(max_digits=50,decimal_places=2,validators=[MinValueValidator(0.0,'Opening Quanytity can not be less than 0'),])
#     closing_value = models.DecimalField(max_digits=20, decimal_places=2,default=0,validators=[MinValueValidator(0.0,'Opening value can not be less than 0'),])
                
#     def __str__(self):
#         return f'{self.receipt_entry,self.issue_entry}'
            
    
        
        
        
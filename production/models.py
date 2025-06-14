from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from inventory.models import Material_Receipt_Note
from masters.models import Transaction_Type,User,Unit_of_Measurement,Unit,Brand,Item,SKU,Unit_Sub_Location, Unit_Stock_Location,Stock_Location,Account_Chart,State
from stock.models import Blend,Stock_Entry
from accounts.models import Inv_Transaction,Overheads
from inventory.functions import generate_document_number
from django.db import transaction as db_transaction
        
class Blend_WIP(models.Model):
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,related_name='blend_wip_transaction_type')
    transaction_number = models.CharField(max_length=20)
    transaction_date = models.DateField()
    blend = models.ForeignKey(Blend,on_delete=models.CASCADE,related_name='blend_wip_blend')
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='blend_wip_unit',blank=True,null=True)    
    issue = models.ForeignKey(Stock_Entry,on_delete=models.CASCADE,related_name='blend_wip_issue',blank=True,null=True) 
    stock_location = models.ForeignKey(Unit_Sub_Location,on_delete=models.CASCADE,blank=True,null=True,related_name='blend_wip_storage_location') ## issue.to_location which is recieving the transfer
    water = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],blank=True,null=True)
    blend_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],blank=True,null=True)
    blend_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],blank=True,null=True)
    average_cost = models.DecimalField(max_digits=30,decimal_places=4,validators=[MinValueValidator(0.0)],blank=True,null=True)
    issue_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
    to_location = models.ForeignKey(Unit_Sub_Location,on_delete=models.CASCADE,blank=True,null=True,verbose_name='Issue To Location',related_name='blend_wip_to_location')    
    issue_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
    opening_quantity = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
    opening_value= models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
    closing_quantity=models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)
    closing_value=models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0)    
    status = models.CharField(max_length=10,default=100)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='blendor',blank=True,null=True)
    created = models.DateTimeField(blank=True,null=True)
    modified = models.DateTimeField(blank=True,null=True)
    
    
    
    def __str__(self):
        return f'{self.transaction_number} -- {self.blend_quantity} -- {self.blend_value}'
    
    def save(self,*args, **kwargs):
        if not self.created:
            self.created = timezone.now()
        self.modified = timezone.now()
        self.transaction_date = timezone.now()
        if not self.transaction_number:
            self.transaction_number = generate_document_number(
                model_class=Blend_WIP,
                transaction_type= self.transaction_type,
                unit=self.unit,
                number_field='transaction_number'
                
            )
    
        
        super().save(*args, **kwargs)    
                        
class Bottling_lines(models.Model):
    MACHINE_TYPE_CHOICES=(
        ('Mannual','Mannual'),
        ('Automatic','Automatic'),
        ('Semi-Auto','Semi-Auto')
    )
    line_number = models.CharField(max_length=50)
    line_name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    unit = models.ForeignKey(Unit_of_Measurement,on_delete=models.CASCADE,related_name='bottling_line_unit')
    line_type = models.CharField(max_length=50,choices=MACHINE_TYPE_CHOICES)
    
    def __str__(self):
        return f'{self.line_number} --{self.line_name}'

class Daily_Production_Plan(models.Model):
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE)
    transaction_number = models.CharField(max_length=30)
    transaction_date = models.DateField()
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='daily_production_plan_unit',blank=True,null=True)
    blend = models.ForeignKey(Blend,on_delete=models.CASCADE,related_name='daily_production_plan_blend',blank=True,null=True)
    bottled = models.BooleanField(default=False)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='daily_production_plan_created_by',blank=True,null=True)
    created = models.DateTimeField(blank=True,null=True)
    modified = models.DateTimeField(blank=True,null=True)
    
    def __str__(self):
        return f'{self.transaction_number} -- {self.transaction_date})'
        
    
    def save(self,*args, **kwargs):
        self.modified = timezone.now()
        if not self.pk:
            self.created = timezone.now()
            self.transaction_date = timezone.now()        
            if not self.transaction_number:
                self.transaction_number=generate_document_number(
                    model_class=Daily_Production_Plan,
                    unit=self.unit,
                    transaction_type=self.transaction_type,
                    number_field='transaction_number'
                )
                
        super().save(*args, **kwargs)
    
class Production_Plan_Line(models.Model):
    plan = models.ForeignKey(Daily_Production_Plan,on_delete=models.CASCADE,related_name='production_plan_line')
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE,related_name='daily_production_plan_brand')
    sku = models.ForeignKey(SKU,on_delete=models.CASCADE,related_name='daily_production_plan_sku')
    production = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Production in Cases')
    state = models.ForeignKey(State,on_delete=models.CASCADE,blank=True,null=True)
    line = models.ForeignKey(Bottling_lines,on_delete=models.CASCADE,related_name='daily_production_plan_line')
    
    def __str__(self):
        return f'{self.plan} -- {self.brand} -- {self.sku} -- {self.production}'

class Map_Brand_SKU_Item(models.Model):
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE,related_name='brand_sku_item')
    sku = models.ForeignKey(SKU,on_delete=models.CASCADE,related_name='sku_item')
    item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name='item_sku')
    account = models.OneToOneField(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='mapped_finished_goods_account')
    stock_location=models.ForeignKey(Unit_Sub_Location,on_delete=models.CASCADE,blank=True,null=True)
    sale_account = models.OneToOneField(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='mapped_sale_account')
    cost_of_sale_account = models.OneToOneField(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='mapped_cost_of_sale_account')
    
    def __str__(self):
        return f'{self.brand} -- {self.sku} -- {self.item}'    


class Production_Report(models.Model):
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE)
    transaction_number = models.CharField(max_length=30)
    transaction_date = models.DateField()
    plan = models.ForeignKey(Daily_Production_Plan,on_delete=models.CASCADE,related_name='production_report_plan')
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='production_report_unit')
    status = models.BooleanField(default=False)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='production_report_created_by')
    created = models.DateTimeField(blank=True,null=True)    
    modified = models.DateTimeField(blank=True,null=True)
    
    def __str__(self):
        return f'{self.transaction_number} -- {self.transaction_date})'
    
    def save(self,*args, **kwargs):
        if not self.created:
            self.created = timezone.now()
        self.modified = timezone.now()
        self.transaction_date = timezone.now()       
        if not self.pk:
            if not self.transaction_number:
                self.transaction_number=generate_document_number(
                    model_class= Production_Report,
                    unit=self.unit,
                    transaction_type = self.transaction_type, 
                    number_field= 'transaction_number'
                )
       
        super().save(*args, **kwargs)

class Production_Report_Line(models.Model):
    report = models.ForeignKey(Production_Report,on_delete=models.CASCADE,related_name='production_report_line')
    item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name='production_report_item',blank=True,null=True)
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='production_report_line_unit')
    blend = models.ForeignKey(Blend,on_delete=models.CASCADE,related_name='production_report_blend')
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE,related_name='production_report_brand',blank=True,null=True)
    sku = models.ForeignKey(SKU,on_delete=models.CASCADE,related_name='production_report_sku',blank=True,null=True)
    production = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='Production in Cases')
    production_value = models.DecimalField(max_digits=30,decimal_places=2,validators=[MinValueValidator(0.0)],default=0) #Claculated field based on production and average cost
    average_cost = models.DecimalField(max_digits=30,decimal_places=4,validators=[MinValueValidator(0.0)],default=0)
    state = models.ForeignKey(State,on_delete=models.CASCADE,blank=True,null=True)
    line = models.ForeignKey(Bottling_lines,on_delete=models.CASCADE,related_name='production_report_line',blank=True,null=True)
    
    def __str__(self):
        return f'{self.report} -- {self.item} -- {self.production}'
  

    
class Overheads_Absorbed(models.Model):
    '''This model define overhead absorotion rate during a particular period'''
    
    name = models.ForeignKey(Overheads,on_delete=models.CASCADE,related_name='absorbed_overhead')   
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,blank=True,null=True)        
    rate = models.DecimalField(max_digits=10,decimal_places=2)
    from_date = models.DateField(blank=True,null=True)
    to_date = models.DateField(blank=True,null=True)
    uom = models.ForeignKey(Unit_of_Measurement,on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True) 
    
    class Meta:
        verbose_name_plural = "Overheads Absorbed"
    
    def __str__(self):
        return f"{self.name}--{self.rate}"

class Blend_Overhead_Absorbed(models.Model):
    '''This model stores actual overhead absorbed on a particular batch of production'''
    transaction_type = models.ForeignKey(Transaction_Type, on_delete=models.CASCADE, related_name='blend_overhead_absorbed_transaction_type',default=18)
    transaction_number = models.CharField(max_length=20,blank=True,null=True)
    transaction_date = models.DateTimeField(blank=True,null=True)
    report = models.ForeignKey(Production_Report,on_delete=models.CASCADE,related_name='production_report')
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='overhead_unit',blank=True,null=True)
    overhead = models.ForeignKey(Overheads_Absorbed,on_delete=models.CASCADE,related_name='overhead_name')
    blend = models.ForeignKey(Blend,on_delete=models.CASCADE,related_name='overhead_blend')
    amount = models.DecimalField(max_digits=20,decimal_places=2)
   
    
    def __str__(self):
        return f'{self.report} -- {self.overhead} -- {self.blend} -- {self.amount}'
    
    
    
        
    


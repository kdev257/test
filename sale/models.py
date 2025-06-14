from django.db import models
from django.utils import timezone
from django.db.models import Q,F,Sum,Count,Avg,Max,Min
from django.db.models.functions import Coalesce
from inventory.functions import generate_document_number
from masters.models import User,Unit,Customer,Customer_Profile,Item,Brand,SKU,Unit_of_Measurement,State_Excise_levies,State_Excise_Levies_Rate,Transaction_Type,State,Vehicle_Type,Supplier,Formula

# Create your models here.
class Slabs(models.Model):
    state = models.ForeignKey(State,on_delete=models.CASCADE)
    min_value = models.FloatField(default=0)
    max_value = models.FloatField(default=0)
    levy_name = models.ForeignKey(State_Excise_levies,on_delete=models.CASCADE,default=1)
    levy_rate = models.FloatField()
    uom = models.ForeignKey(Unit_of_Measurement,on_delete=models.CASCADE,default=1)
    levy_formula = models.ForeignKey(Formula,on_delete=models.CASCADE,related_name='slab_formaula')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)  
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
        

    def __str__(self):
        return f'{self.state,self.levy_name,self.min_value,self.max_value,self.uom}'

class Cost_Card(models.Model):        
    state = models.ForeignKey(State,on_delete=models.CASCADE,default=1)
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE,default=1)
    sku = models.ForeignKey(SKU,on_delete=models.CASCADE,default=2)
    edp= models.FloatField(verbose_name='Ex-Distillery_Price per Case')
    mop= models.FloatField(verbose_name='Market Operting Rate Per Case',blank=True,null=True)
    msp=  models.FloatField(verbose_name='Minimum Sale Price Per Case',blank=True,null=True)
    mrp = models.FloatField(verbose_name='Maximum Retail Price Per Case',blank=True,null=True)
    valid_from = models.DateField()
    valid_till = models.DateField()    
    created = models.DateTimeField()
    modified = models.DateTimeField()
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.state} - {self.brand} - {self.sku}'
    
    # class Meta:
        # unique_together = 'state','brand','sku','valid_from','valid_till'
    
    def save(self,*args, **kwargs):
        if not self.pk:
            self.created = timezone.now()
        self.modified = timezone.now()
        
        super().save(*args, **kwargs)

class Cost_Card_Item(models.Model):    
    cost_card = models.ForeignKey(Cost_Card,on_delete=models.CASCADE)
    levy_name = models.CharField(max_length=50)
    levy_rate = models.DecimalField(max_digits=10,decimal_places=3)
    levy_unit = models.CharField(max_length=20)
    levy_amount= models.DecimalField(max_digits=12,decimal_places=2)
    valid_from = models.DateField()
    valid_till = models.DateField()
    payee = models.CharField(max_length=10)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.levy_name}'

class Outward_Freight(models.Model):    
    transporter = models.ForeignKey(Supplier, on_delete=models.CASCADE,related_name='sale_freight_supplier')
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='or_unit')
    load_qty = models.IntegerField(default=0)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    distance = models.FloatField(blank=True, null=True)
    freight = models.IntegerField(default=0)
    vehicle_type = models.ForeignKey(Vehicle_Type, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name='or_created_by')

    def __str__(self):
        return f"{self.transporter} to {self.vehicle_type}"


class Permit(models.Model):
    STATUS_CHOICES =(
        ('100','pending_order'),
        ('200','order_made'),
        ('300','executed')
    )
    permit_number = models.CharField(max_length=255,unique=True)
    permit_date = models.DateField()
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)    
    valid_till = models.DateField()
    status = models.CharField(choices=STATUS_CHOICES,max_length=50,default='100')
    created = models.DateTimeField(blank=True,null=True)
    modified = models.DateTimeField(blank=True,null=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='permit_creator')    
    
    def __str__(self):
        return f'{self.customer}--{self.permit_number} -- {self.permit_date}'
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created = timezone.now()
        self.modified = timezone.now()        
            
        super(Permit, self).save(*args, **kwargs)

class Permit_Item(models.Model):
    permit = models.ForeignKey(Permit,on_delete=models.CASCADE,related_name='related_permit')
    product_item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name='permit_item')
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE,related_name='permit_brand')
    sku = models.ForeignKey(SKU,on_delete=models.CASCADE,related_name='permit_sku')
    quantity = models.DecimalField(max_digits=10,decimal_places=2)
    uom = models.ForeignKey(Unit_of_Measurement,on_delete=models.CASCADE,related_name='permit_uom')
    
    
    def __str__(self):
        return f"{self.permit.permit_number},{self.permit.permit_date}"

class Vehicle_For_Loading(models.Model):
    LOADING_MATERIAL_CHOICES=(
        ('Liquor','Liquor'),
        ('Scrap','Scrap'),
        ('Other','Other')
    )
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='loading_truck_unit')
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,related_name='loading_truck_transaction_type')
    entry_number = models.CharField(max_length=30)
    entry_date = models.DateTimeField()
    vehicle_number = models.CharField(max_length=20)
    vehicle_type = models.ForeignKey(Vehicle_Type,on_delete=models.CASCADE,related_name='loading_truck_vehicle_type')
    material = models.CharField(choices=LOADING_MATERIAL_CHOICES,max_length=20)
    driver_name = models.CharField(max_length=50)
    license_number = models.CharField(max_length=50)
    license_validity = models.DateField()
    licensing_state = models.ForeignKey(State,on_delete=models.CASCADE,related_name='loading_truck_licensing_state')
    engine_number = models.CharField(max_length=50)
    out_time = models.DateTimeField(blank=True,null=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='loading_truck_created_by')
    
    def __str__(self):
        return f'{self.vehicle_number}--{self.entry_date}'
    
    def save(self,*args, **kwargs):
        if not self.pk:
            self.entry_date = timezone.now()
            self.created = timezone.now()
        self.modified = timezone.now()
        if not self.entry_number:
            self.entry_number=generate_document_number(
                transaction_type=self.transaction_type,
                unit = self.unit,
                model_class= Vehicle_For_Loading,
                number_field= 'entry_number'
            )
        super(Vehicle_For_Loading,self).save(*args, **kwargs)


    
class Sales_Invoice(models.Model):
    invoice_number = models.CharField(max_length=20,unique=True)
    invoice_date = models.DateTimeField()
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,related_name='sale_invoice_transaction_type')
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='sale_invoice_unit')
    permit = models.ForeignKey(Permit,on_delete=models.CASCADE,related_name='sale_invoice_permit') 
    truck = models.ForeignKey(Vehicle_For_Loading,on_delete=models.CASCADE,related_name='sale_invoice_truck')
    lr_number = models.CharField(max_length=50,default='',verbose_name='Lorry Receipt  Number')
    lr_date = models.DateField(blank=True,null=True,verbose_name='Lorry Receipt Date')
    excise_pass = models.CharField(max_length=50,default='')
    excise_pass_date = models.DateField(blank=True,null=True) 
    basic_amount = models.DecimalField(max_digits=50,decimal_places=0,default=0)
    levies_total = models.DecimalField(max_digits=30,decimal_places=0,default=0)
    tcs = models.DecimalField(max_digits=20,decimal_places=2,default=0)
    total_invoice_amount = models.DecimalField(max_digits=50,decimal_places=2,default=0)    
    created = models.DateTimeField()
    modified = models.DateTimeField()   
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='invoice_created_by')
    
    def __str__(self):
        return f'{self.invoice_number},{self.invoice_date},{self.transaction_type},{self.permit}'
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.invoice_date = timezone.now()
            self.created = timezone.now()
            self.unit = self.permit.customer.unit
        self.modified = timezone.now()
        if not self.invoice_number:
            self.invoice_number = generate_document_number(
                model_class=Sales_Invoice,
                unit=self.permit.customer.unit,
                transaction_type= self.transaction_type,
                number_field='invoice_number',
            )
        super(Sales_Invoice, self).save(*args, **kwargs)
        
class Sales_Invoice_Item(models.Model):
    invoice = models.ForeignKey(Sales_Invoice,on_delete=models.CASCADE,related_name='related_invoice')
    product_item = models.ForeignKey(Permit_Item,on_delete=models.CASCADE,related_name='invoice_item')
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE,related_name='invoice_brand')
    sku = models.ForeignKey(SKU,on_delete=models.CASCADE,related_name='invoice_sku')    
    invoice_quantity = models.DecimalField(max_digits=10,decimal_places=2)
    basic_amount = models.DecimalField(max_digits=50,decimal_places=2,default=0)
    levies_amount = models.DecimalField(max_digits=20,decimal_places=2,default=0)    
    
    def __str__(self):
        return f'{self.invoice.invoice_number},{self.invoice.invoice_date},{self.invoice.transaction_type},{self.invoice.permit}'
    
class Sale_Invoice_Levies(models.Model):
    invoice = models.ForeignKey(Sales_Invoice,on_delete=models.CASCADE,related_name='invoice_levy')
    invoice_line = models.ForeignKey(Sales_Invoice_Item,on_delete=models.CASCADE,related_name='invoice_levy_lines',blank=True,null=True)
    levy_name = models.ForeignKey(State_Excise_Levies_Rate,on_delete=models.CASCADE,related_name='invoice_levy_name')
    levy_amount = models.DecimalField(max_digits=20,decimal_places=2,default=0)
    
    def __str__(self):
        return f"{self.levy_name}--{self.levy_amount}"
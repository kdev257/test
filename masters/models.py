from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from django.core.exceptions import ValidationError
# from sale.models import *
from django.utils import timezone
from django.core.validators import MinValueValidator

class Currency(models.Model):
    name = models.CharField(max_length=20)
    conversion_rate = models.DecimalField(max_digits=10,decimal_places=2)
    
    def __str__(self):
        return f'{self.name} - {self.conversion_rate}'


class State(models.Model):
    state_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f'{self.state_name}'

class Company(models.Model):
    company_name = models.CharField(max_length=200)
    address = models.CharField(max_length=100,default="")
    city = models.CharField(max_length=100,default="")
    pin = models.CharField(max_length=6,default="")    
    state = models.OneToOneField(State, on_delete=models.CASCADE, related_name='companies')
    pan_no = models.CharField(max_length=10,default="")
    tan_no = models.CharField(max_length=10,default="")
    
    def __str__(self):
        return f'{self.company_name}'


    
class Unit(models.Model):
    UNIT_TYPE_CHOICES = (
        ('Factory', 'Factory'),
        ('Region_Office', 'Region_Office'),
        ('Zonal_Office', 'Zonal_Office'),
        ('HeadOffice','HeadOffice')
    )
    company = models.ForeignKey(Company,on_delete=models.CASCADE, default=1)
    unit_name = models.CharField(max_length=200)    
    address = models.TextField(max_length=300,default="")
    city = models.CharField(max_length=50,default="")
    pin = models.CharField(max_length=6)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='units')
    unit_type = models.CharField(choices=UNIT_TYPE_CHOICES, max_length=100)
    gstin = models.CharField(max_length=15)        
    vat_no = models.CharField(max_length=50,blank=True,null=True)
    contact = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    landphone= models.CharField(max_length=10,blank=True,null=True)
    email = models.EmailField(unique=True,blank=True,null=True)
    
    
    def __str__(self):
        return f'{self.unit_name}'

class User(AbstractUser):
    USER_TYPE_CHOICES=(
        ('Transporter','Transporter'),
        ('Service_Provider','Service_Provider'),
        ('Admin','Admin'),        
        ('Employee','Employee'),        
        ('Goods_Supplier','Goods_Supplier'),        
    )
    company = models.ForeignKey(Company,on_delete=models.CASCADE,related_name='user_company',blank=True,null=True)
    name = models.CharField(max_length=200,default="")
    user_type = models.CharField(choices=USER_TYPE_CHOICES,max_length=20)    
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.id} {self.username}'
        



class User_Roles(models.Model):
    DEPARTMENT_CHOICES=(
        ('Finance','Finance'),
        ('Marketing','Marketing'),
        ('Sale','Sale'),
        ('Supply_Chain','Supply_Chain'),
        ('Procurement','Procurement'),
        ('Store','Store'),
        ('Quality_Control','Quality_Control'),
        ('Security','Security'),
        ('Manufacturing','Manufacturing')
        
    )    
    user_id = models.OneToOneField(User,on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE)
    department= models.CharField(choices=DEPARTMENT_CHOICES,max_length=100)
    can_create = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_approve = models.BooleanField(default=False)
        
    def __str__(self):
        return f"{self.user_id.username} - {self.department}"      
    
class Account_Class(models.Model):
    account_class = models.CharField(max_length=100)    
    opening_balance = models.DecimalField(max_digits=30,decimal_places=2,default=0)
    debit_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created = models.DateTimeField(blank=True,null=True)
    modified = models.DateTimeField(blank=True,null=True)
    
    def __str__(self):
        return f'{self.account_class} {self.opening_balance} {self.debit_amount} {self.credit_amount} {self.closing_balance}'
    
    def save(self,*args, **kwargs):
        if not self.pk:
            self.created = timezone.now()
        self.modified = timezone.now()        
        super().save(*args, **kwargs)
    
    # def update_balances(self):
    #     # Calculate new closing balance for Account_Chart
    #     self.closing_balance = self.opening_balance + self.debit_amount - self.credit_amount

    #     # Update self (avoiding infinite recursion)
    #     super().save(update_fields=['closing_balance'])  # Update only closing balance


class Account_Sub_Class(models.Model):
    account_class = models.ForeignKey(Account_Class, on_delete=models.CASCADE)    
    sub_class = models.CharField(max_length=100)
    opening_balance = models.DecimalField(max_digits=20,decimal_places=2,default=0) 
    debit_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created = models.DateTimeField(blank=True,null=True)
    modified = models.DateTimeField(blank=True,null=True)
    
    def __str__(self):
        return f'{self.sub_class} {self.opening_balance} {self.debit_amount} {self.credit_amount} {self.closing_balance}'
    
    def save(self,*args, **kwargs):
        if not self.pk:
            self.created = timezone.now()
        self.modified = timezone.now()        
        super().save(*args, **kwargs)
    

class Account_Category(models.Model):
    category = models.CharField(max_length=100)
    sub_class = models.ForeignKey(Account_Sub_Class, on_delete=models.CASCADE)
    opening_balance = models.DecimalField(max_digits=30,decimal_places=2,default=0)
    debit_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created = models.DateTimeField(blank=True,null=True)
    modified = models.DateTimeField(blank=True,null=True)
    
    def __str__(self):
        return f'{self.category} {self.opening_balance} {self.debit_amount} {self.credit_amount} {self.closing_balance}'
    def save(self,*args, **kwargs):
        if not self.pk:
            self.created = timezone.now()
        self.modified = timezone.now()        
        super().save(*args, **kwargs)
        
class Account_Sub_Category(models.Model):
    sub_category = models.CharField(max_length=100)
    category = models.ForeignKey(Account_Category, on_delete=models.CASCADE)
    opening_balance = models.DecimalField(max_digits=30,decimal_places=2,default=0)
    debit_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created = models.DateTimeField(blank=True,null=True)
    modified = models.DateTimeField(blank=True,null=True)
    
    def __str__(self):
        return f'{self.sub_category} {self.opening_balance} {self.debit_amount} {self.credit_amount} {self.closing_balance}'
    
    def save(self,*args, **kwargs):
        if not self.pk:
            self.created = timezone.now()
        self.modified = timezone.now()
        
        super().save(*args, **kwargs)

    

class Account_Chart(models.Model):
    account_code = models.CharField(max_length=4,default="",unique=True)
    account_name = models.CharField(max_length=100)          
    sub_category = models.ForeignKey(Account_Sub_Category, on_delete=models.CASCADE)
    opening_balance = models.DecimalField(max_digits=30,decimal_places=2,default=0)
    debit_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created = models.DateTimeField(blank=True,null=True)
    modified = models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return f'{self.account_name} {self.opening_balance} {self.debit_amount} {self.credit_amount} {self.closing_balance}--{self.account_code}'
    
    def save(self,*args, **kwargs):
        if not self.pk:
            self.created = timezone.now()
        self.modified = timezone.now()
        
        super().save(*args, **kwargs)

    
    
#     def __str__(self):        
#         return f'User: {self.name}, Type: {self.user_type}'
        
class Supplier_Profile(models.Model):
    company = models.ForeignKey(Company, on_delete= models.CASCADE,related_name='company_supplier',default=1)
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='sp_user')
    supplier_name = models.CharField(max_length=100)
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='sp_unit')     
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.ForeignKey(State,on_delete=models.CASCADE)
    is_msme = models.BooleanField(default=False)
    zip = models.CharField(max_length=11)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by  = models.ForeignKey(User,on_delete=models.CASCADE,related_name='Supplier_user')
    
    def __str__(self):
        return self.supplier_name


class Transaction_Type(models.Model):
    transaction_name = models.CharField(max_length=100)
    description = models.CharField(max_length=30,blank=True,null=True)
    
    def __str__(self):
        return f"{self.transaction_name}"

class DOA(models.Model):
    level = models.CharField(max_length=100)  # e.g., "Level 1", "Level 2", "Head Office"
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE)  # e.g., "Quotation", "Purchase Order"
    monetary_limit = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.level} - {self.user.username} - {self.transaction_type} - {self.monetary_limit}"     

    

class Spirit_Class(models.Model):
    spirit_class_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f'{self.spirit_class_name}'
    
class Brand_Variant(models.Model):
    variant_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f'{self.variant_name}'
    
class Brand(models.Model):
    company = models.ForeignKey(Company,on_delete=models.CASCADE, default=1)        
    brand_name = models.CharField(max_length=100)
    spirit_class = models.ForeignKey(Spirit_Class, verbose_name="Class", on_delete=models.CASCADE, related_name='brands')
    variant = models.ForeignKey(Brand_Variant, on_delete=models.CASCADE, related_name='brands')
    wip_blend_account =models.ForeignKey(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='brand_wip_blend_account',verbose_name='Process Stock in Proceesing Tank')
    wip_finished_blend= models.ForeignKey(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='brand_wip_finished_blend_account',verbose_name='Finished_Blend in Holding Tank')
    wip_account = models.ForeignKey(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='brand_wip_account',verbose_name='Stock at Bottling Tank Shop Floor')
    finished_goods_account =  models.ForeignKey(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='brand_finished_goods_account',verbose_name='Finished Goods Accout')
    
    def __str__(self):
        return f'{self.brand_name}'
    
class Unit_of_Measurement(models.Model):
    uom = models.CharField(max_length=50)
    
    def __str__(self):
        return f'{self.uom}'

class SKU(models.Model):
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    sku = models.CharField(max_length=50)
    uom = models.ForeignKey(Unit_of_Measurement, on_delete=models.CASCADE, verbose_name='Unit of Measurement', related_name='skus')
    
    def __str__(self):
        return f'{self.sku}, {self.uom}'

class Case(models.Model):
    sku = models.ForeignKey(SKU,on_delete=models.CASCADE)
    bottle = models.FloatField()
    bl = models.FloatField()
    pl = models.FloatField()
    al = models.FloatField()

    def __str__(self):
        return f'{self.sku},{self.bottle}'
    
class Item_Category(models.Model):
    cat_name = models.CharField(max_length=50)
    
    def __str__(self):
        return f'{self.cat_name}'
    
class Item_Class(models.Model):
    class_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f'{self.class_name}'
    
class Item(models.Model):
    ITEM_TAX_CHOICES =(
        ('Non_GST','Non_GST'),
        ('GST','GST'),
    )
    hsn_code = models.CharField(max_length=8) 
    item_name = models.CharField(max_length=200)
    item_cat = models.ForeignKey(Item_Category, on_delete=models.CASCADE, related_name='items')
    item_class = models.ForeignKey(Item_Class, on_delete=models.CASCADE, related_name='items')
    item_unit = models.ForeignKey(Unit_of_Measurement, on_delete=models.CASCADE, related_name='items')
    item_tax_type = models.CharField(choices=ITEM_TAX_CHOICES,default='GST',max_length=50)
    account= models.ForeignKey(Account_Chart,on_delete=models.CASCADE,default=1)
        
    def __str__(self):
        return f'{self.hsn_code}--{self.item_name}-{self.item_unit}'
    
class Business(models.Model):
    business = models.CharField(max_length=50)
    
    def __str__(self):
        return f'{self.business}'


class Gst_On_Goods(models.Model):   
    item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name='gst_item')
    tax_name = models.CharField(max_length=20)
    rate = models.DecimalField(max_digits=7,decimal_places=2,default=0)
    account= models.ForeignKey(Account_Chart,on_delete=models.CASCADE,related_name='goods_gst_account')
    
    def __str__(self):
        return f'{self.item} - {self.tax_name} {self.rate}'

class Service(models.Model):
    NATURE_CHOICES = (
        ('Intra_State','Intra-State'),
        ('Inter_State','Inter_State'),
    )
    PAYMENT_CHOICES =(
        ('FCM','FCM'),
        ('RCM','RCM'),
    )
    SERVICE_TYPE_CHOICES=(
        ('Specified','Specified'),
        ('Non-Specified','Non-Specified')
    )
    sac_code = models.CharField(max_length=6)
    service_name = models.CharField(max_length=50)
    nature_of_supply = models.CharField(choices=NATURE_CHOICES,max_length=30,default='Inter_State')
    service_type = models.CharField(max_length=30,choices=SERVICE_TYPE_CHOICES,default='Non-Specified')
    gst_rate = models.DecimalField(max_digits=10,decimal_places=2,default=18)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_CHOICES,default='FCM')
    
    
    def __str__(self):
        return f'{self.sac_code} - {self.service_name}'
    


    
class Custom_Duty(models.Model):
    hsn = models.CharField(max_length=8)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='duty_item')
    tax_name = models.CharField(max_length=20)    
    rate = models.DecimalField(max_digits=8,decimal_places=2,default=0)
    account= models.ForeignKey(Account_Chart,on_delete=models.CASCADE,related_name='custom_account')
    
    def __str__(self):
        return f'{self.hsn} - {self.item} - {self.tax_name} {self.rate}'

class State_Excise_levies(models.Model):     
    tax_name = models.CharField(max_length=30) 
    
    def __str__(self):
        return (self.tax_name)   

class State_Excise_taxes_On_Goods(models.Model):
    INCIDENCE_CHOICES=(
        ('Inward','Inward'),
        ('Outward','Outward')
    )
    state = models.ForeignKey(State,on_delete=models.CASCADE,related_name='state_excise')   
    incidence = models.CharField(choices=INCIDENCE_CHOICES,max_length=20)
    tax_name = models.ForeignKey(State_Excise_levies,on_delete=models.CASCADE,related_name='exicse_levies')
    levy_unit = models.ForeignKey(Unit_of_Measurement,on_delete=models.CASCADE,related_name='levy_unit')
    rate = models.DecimalField(max_digits=8,decimal_places=2,default=0)
    account= models.ForeignKey(Account_Chart,on_delete=models.CASCADE,related_name='excise_account')
    
    def __str__(self):
        return f' {self.tax_name} {self.rate}'

class State_Tax_on_Sale_Of_Goods(models.Model):
    state = models.ForeignKey(State,on_delete=models.CASCADE,related_name='state_tax')
    item = models.ForeignKey(Item,on_delete= models.CASCADE, related_name='state_item')
    tax_name = models.CharField(max_length=30)    
    rate = models.DecimalField(max_digits=8,decimal_places=2,default=0)
    creditable = models.BooleanField(default=False)
    account = models.ForeignKey(Account_Chart,on_delete=models.CASCADE,related_name='vat_account')
    
    def __str__(self):
        return f'{self.state} - {self.item} - {self.tax_name} {self.rate}'



# class State_Excise_Levies(models.Model):
#     LEVY_METHOD_CHOICES =(
#         ('formula','formula'),
#         ('slab','slab'),
#     )
#     PAYEE_CHOICES=(
#         ('Company','Company'),
#         ('Wholesale','Wholesale'),
#         ('Retailer','Retailer'),
#     )
#     state = models.ForeignKey(State,on_delete=models.CASCADE,related_name='sbsel_state')
#     levy_name  = models.ForeignKey(,on_delete=models.CASCADE,related_name='sbsel_levies')
#     levy_rate = models.FloatField(blank=True,null=True)
#     levy_unit= models.ForeignKey(Unit_of_Measurement,on_delete=models.CASCADE,blank=True,null=True)
#     levy_formula = models.CharField(max_length=255,blank=True,null=True,default="")
#     slab = models.CharField(choices=LEVY_METHOD_CHOICES,max_length=255,default="")
#     payee = models.CharField(max_length=20,choices=PAYEE_CHOICES,default='Company')    
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#     created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sbsel_created_by')



    

class Supplier(models.Model):
    ASSESSEE_TYPE=(
        ('Individual','Individual'),
        ('HEF','HUF'),
        ('Partnership','Partnership'),
        ('Company','Company'),
        ('LLP','LLP'),
        ('Trust','Trust'),
        ('Other','Other'),
    )   
    LOCATION_CHOICES=(
        ('India','India'),
        ('Overseas','Overseas'),
        
    ) 
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='unit_suppliers')
    supplier_name = models.CharField(max_length=200)
    assessee_type = models.CharField(max_length=50,choices=ASSESSEE_TYPE,default="")
    location = models.CharField(max_length=20,choices=LOCATION_CHOICES,default='India')
    currency = models.ForeignKey(Currency,on_delete=models.CASCADE,default=1)
    related = models.BooleanField(default=False)
    gstin = models.CharField(max_length=15,default="")
    supplier_state = models.ForeignKey(State,on_delete=models.CASCADE,default=1)
    account = models.ForeignKey(Account_Chart,on_delete=models.CASCADE,default=1)    
        
    def __str__(self):
        return f'{self.supplier_name}'
    


class Supplier_Service(models.Model):
    LEVY_MODE_CHOICES =(
        ('FCM','FCM'),
        ('RCM','RCM'),
    )    
    supplier= models.ForeignKey(Supplier,on_delete=models.CASCADE,default=13)
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,default=1)
    service =  models.ForeignKey(Service,on_delete=models.CASCADE,default=1)
    levy_mode = models.CharField(max_length=20,choices=LEVY_MODE_CHOICES)        
    
    
    def __str__(self):
        return f"{self.supplier} - {self.service} - {self.levy_mode}"

class Vehicle_Type(models.Model):    
    vehicle_type = models.CharField(max_length=50)
    vehicle_capacity = models.DecimalField(max_digits=10, decimal_places=2)
    Unit_of_Measurement = models.ForeignKey(Unit_of_Measurement, on_delete=models.CASCADE, related_name='vehicle_types')
    
    def __str__(self):
        return f'{self.vehicle_type}-{self.vehicle_capacity}'
    
class TDS(models.Model):
    DEDUCTEE_CHOICES=(
        ('Individual','Individual'),
        ('HEF','HUF'),
        ('Partnership','Partnership'),
        ('Company','Company'),
        ('LLP','LLP'),
        ('Trust','Trust'),
        ('Other','Other'),
    )
    section = models.CharField(max_length=20)
    classification = models.CharField(max_length=100,default="")   
    service_classification = models.ForeignKey(Service,on_delete=models.CASCADE,default=1)
    deductee_type = models.CharField(max_length=50,choices=DEDUCTEE_CHOICES)
    rate = models.DecimalField(max_digits=5,decimal_places=2)
    
    def __str__(self):
        return f'{self.section} | {self.classification}   | {self.rate}'
    
class Lower_TDS(models.Model):
    DEDUCTEE_CHOICES=(
        ('Individual','Individual'),
        ('HUF','HUF'),
        ('Partnership','Partnership'),
        ('Company','Company'),
        ('LLP','LLP'),
        ('Trust','Trust'),
        ('Other','Other'),
    )
    supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE,blank=True,null=True)
    section = models.ForeignKey(TDS,on_delete=models.CASCADE,blank=True,null=True)
    classification = models.CharField(max_length=100,default="")
    sub_classification = models.CharField(max_length=100,default="")
    deductee_type = models.CharField(max_length=50,choices=DEDUCTEE_CHOICES,default='')    
    lower_rate = models.DecimalField(max_digits=5,decimal_places=2)
    limit = models.DecimalField(max_digits=20,decimal_places=2,default=0)
    document = models.FileField(upload_to='media',blank=True,null=True)
    
    def __str__(self):
        return f"{self.supplier} | {self.section} | {self.limit}"


class Freight(models.Model):
    FREIGHT_TYPE_CHOICES = [
        ('air','Air'),
        ('sea','Sea'),
        ('road','Road'),
        ('rail','Rail'),
        ('courier','Courier'),
    ]
      
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,default=1,related_name='freights')
    mode = models.CharField(choices=FREIGHT_TYPE_CHOICES, max_length=50)
    service = models.ForeignKey(Supplier_Service,on_delete=models.CASCADE,default=1,related_name='transporter_service')  
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE,related_name='goods_supplier',blank=True,null=True)   
    origin_city = models.CharField(max_length=100)
    destinaton_city = models.CharField(max_length=100)
    vehicle_type = models.ForeignKey(Vehicle_Type, on_delete=models.CASCADE, related_name='freights')
    dumerages_rate= models.DecimalField(default=0,verbose_name='Dumerage Rate Per Day',max_digits=10,decimal_places=2)
    toll_tax = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    freight = models.DecimalField(max_digits=10, decimal_places=2)    
    transporter_account = models.ForeignKey(Account_Chart,on_delete=models.CASCADE,related_name='transporter',blank=True,null=True)
    provision_account= models.ForeignKey(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='provision')
    cgst_account = models.ForeignKey(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='cgst_account')    
    sgst_account = models.ForeignKey(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='sgst_account')    
    igst_account = models.ForeignKey(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='igst_account')    
    tds_account = models.ForeignKey(Account_Chart,on_delete=models.CASCADE,blank=True,null=True,related_name='tds_account')
       
    
    def __str__(self):
        return f'{self.supplier} --{self.origin_city}'



class Landed_Cost_Rule(models.Model):
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,default=1)    
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE,related_name='lcr_supplier')    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='lcr_item')    
    misc_costs = models.DecimalField(max_digits=10, decimal_places=2,default=0,help_text= 'Pls insert per unit  value same wiil be picked to calculate landed cost')
    clearance = models.ForeignKey(Supplier_Service,on_delete=models.CASCADE,blank=True,null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['id']) # Explicitly adds an index           
        ]
        verbose_name_plural = 'Landed Cost Rule'
        unique_together = ['unit', 'item', 'supplier']

    

    def __str__(self):
        return f"Rule for {self.supplier} - {self.item}"

    


    
class Standard_Quality_Specifications(models.Model):
    name = models.CharField(max_length=30)
    item_cat = models.ForeignKey(Item_Category,on_delete=models.CASCADE,default="")
    standard_value= models.CharField(max_length=20)
    uom = models.ForeignKey(Unit_of_Measurement,on_delete=models.CASCADE,default=1,blank=True,null=True)
    
    def __str__(self):
        return f'{self.name}-{self.item_cat}-{self.standard_value}-{self.uom}'

class Stock_Location(models.Model):    
    loc_name = models.CharField(max_length=255) 
    capacity = models.DecimalField(max_digits=20, decimal_places=2,default=0)
    item = models.ForeignKey(Item,on_delete=models.CASCADE,null=True,blank=True)
    opening_quantity = models.DecimalField(max_digits=30,decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    opening_value = models.DecimalField(max_digits=30,decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    receipt_quantity = models.DecimalField(max_digits=10, decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    receipt_value = models.DecimalField(max_digits=30,decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    issued_quantity = models.DecimalField(max_digits=10, decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    issue_value = models.DecimalField(max_digits=30,decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    closing_quantity = models.DecimalField(max_digits=10, decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    closing_value = models.DecimalField(max_digits=30,decimal_places=2,default=0,validators=[MinValueValidator(0.0)])

    def __str__(self):
        return self.loc_name    

class Unit_Stock_Location(models.Model):
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,default=1)
    unit_stock_location = models.CharField(max_length=255)
    item = models.ForeignKey(Item,on_delete=models.CASCADE,null=True,blank=True)    
    stock_location = models.ForeignKey(Stock_Location, on_delete=models.CASCADE, related_name='sublocations') 
    capacity = models.DecimalField(max_digits=20, decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    opening_quantity = models.DecimalField(max_digits=30,decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    opening_value = models.DecimalField(max_digits=30,decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    receipt_quantity = models.DecimalField(max_digits=10, decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    receipt_value = models.DecimalField(max_digits=30,decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    issued_quantity = models.DecimalField(max_digits=10, decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    issue_value = models.DecimalField(max_digits=30,decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    closing_quantity = models.DecimalField(max_digits=10, decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    closing_value = models.DecimalField(max_digits=30,decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    average_rate = models.DecimalField(max_digits=10,decimal_places=2,default=0) 
    

    def __str__(self):
        return f"{self.unit_stock_location}"
    

class Unit_Sub_Location(models.Model):
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,default=1)
    sub_loc_name = models.CharField(max_length=255)    
    unit_stock_location = models.ForeignKey(Unit_Stock_Location, on_delete=models.CASCADE, related_name='sublocations',default=1)      
    item = models.ForeignKey(Item,on_delete=models.CASCADE,null=True,blank=True)
    capacity = models.DecimalField(max_digits=20, decimal_places=2,default=0)
    opening_quantity = models.DecimalField(max_digits=30,decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    opening_value = models.DecimalField(max_digits=30,decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    receipt_quantity = models.DecimalField(max_digits=10, decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    receipt_value = models.DecimalField(max_digits=10, decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    issued_quantity = models.DecimalField(max_digits=10, decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    issue_value = models.DecimalField(max_digits=10, decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    closing_quantity = models.DecimalField(max_digits=10, decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    closing_value = models.DecimalField(max_digits=10, decimal_places=2,default=0,validators=[MinValueValidator(0.0)])
    average_rate = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    created     = models.DateTimeField(editable=False,blank=True,null=True)
    modified    = models.DateTimeField(blank=True,null=True)
    

    def __str__(self):
        return f"{self.sub_loc_name} - {self.closing_quantity}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created = timezone.now()
        self.modified = timezone.now()
        # Calculate changes in quantities and values
        
        previous = Unit_Sub_Location.objects.filter(pk=self.pk).first()
        if previous:
            if (self.receipt_quantity != previous.receipt_quantity or
                self.receipt_value != previous.receipt_value or
                self.issued_quantity != previous.issued_quantity or
                self.issue_value != previous.issue_value):
                
                # Update Unit_Stock_Location values
                self.update_unit_stock_location()
                
           

        # Call the superclass save method to save the instance
        super().save(*args, **kwargs)

    def update_unit_stock_location(self):
        # Retrieve the parent Unit_Stock_Location
        unit_stock_location = self.unit_stock_location
        if unit_stock_location:
            # Update the parent Unit_Stock_Location
            unit_stock_location.receipt_quantity += self.receipt_quantity
            unit_stock_location.receipt_value += self.receipt_value
            unit_stock_location.issued_quantity += self.issued_quantity 
            unit_stock_location.issue_value += self.issue_value
            unit_stock_location.closing_quantity = unit_stock_location.opening_quantity+unit_stock_location.receipt_quantity-unit_stock_location.issued_quantity
            unit_stock_location.closing_value = unit_stock_location.opening_value+unit_stock_location.receipt_value- unit_stock_location.issue_value
            unit_stock_location.average_rate = unit_stock_location.closing_value / unit_stock_location.closing_quantity
                        
            # Update the parent Stock_Location
            stock_location = unit_stock_location.stock_location
            stock_location.receipt_quantity += self.receipt_quantity
            stock_location.receipt_value += self.receipt_value
            stock_location.issued_quantity += self.issued_quantity 
            stock_location.issue_value += self.issue_value
            stock_location.closing_quantity = stock_location.opening_quantity + stock_location.receipt_quantity- stock_location.issued_quantity
            stock_location.closing_value = stock_location.opening_value + stock_location.receipt_value- stock_location.issue_value
            unit_stock_location.save()
            stock_location.save()
            # Update Accounting Entry
           
                        
    
class Service_Contracts(models.Model):
    BASIS_CHOICES = (
        ('Per_Day','Per_Day'),
        ('Per-Consignment','Per_Consignment'),
        ('Lump_Sum','Lump_Sum')
        
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    service = models.ForeignKey(Supplier_Service,on_delete=models.CASCADE)
    delivarable_name= models.CharField(max_length=50)
    basis = models.CharField(choices=BASIS_CHOICES,max_length=30,default='Per_Consignment')
    service_charge = models.DecimalField(max_digits=10,decimal_places=2)
    
    def __str__(self):
        return f'{self.supplier} -- {self.service} -- {self.delivarable_name} --{self.service_charge}'

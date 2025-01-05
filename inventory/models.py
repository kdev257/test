from django.db import models
from django.db import transaction as db_transaction
from django.core.exceptions import ObjectDoesNotExist
from masters.models import User,Company,Unit,State,User_Roles,Transaction_Type,Supplier,Item,Currency,Business,Standard_Quality_Specifications,Unit_Sub_Location,Service,Supplier_Service,Landed_Cost_Rule,Freight,Item_Category
from datetime import datetime
from django.db.models import Max
from django.utils import timezone
from django.db.models import F
from django.contrib import messages
from django.core.exceptions import ValidationError
from .functions import generate_document_number
from django.db.models.signals import post_save
from django.dispatch import receiver

    

class Quotation(models.Model):
    DELIVERY_TERM_CHOICES=(
        ('Ex-Factory','Ex-Factory'),
        ('CIF','CIF'),
        ('Delivered','Delivered'),
        ('Prepaid' ,'Prepaid'),
    )
    TAX_CHOICES=(
        ('Inclusive','Inclusive'),
        ('Extra' ,'Extra'),
    )
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,default=1)
    quotation_no = models.CharField(max_length=100)
    quotation_date= models.DateTimeField(default=datetime.now)
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='quo_unit')
    supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE,related_name='quo_supplier')
    delivery_terms= models.CharField(choices=DELIVERY_TERM_CHOICES,max_length=100)    
    valid_from = models.DateTimeField()
    valid_till = models.DateTimeField()
    credit_terms= models.SmallIntegerField()
    taxes = models.CharField(choices=TAX_CHOICES,max_length=50,default='Extra',help_text='Pls. Choose')
    currency = models.ForeignKey(Currency,on_delete=models.CASCADE,default=1)
    form_c = models.BooleanField(default=False,help_text='Pls Tick if purchase is against form C')
    approved=  models.BooleanField(default=False)
    document = models.FileField(upload_to='media',blank=True,null=True,help_text='Pls. upload the quotaion here')
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='q_creator',blank=True,null=True)
    misc_cost = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    quotation_value = models.DecimalField(default=0,max_digits=30,decimal_places=2)
    quotation_quantity = models.DecimalField(default=0,max_digits=20,decimal_places=2)
    balance_quantity = models.DecimalField(max_digits=20,decimal_places=2,blank=True,null=True)
    approver = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True,related_name='q_approver') 
    created = models.DateTimeField(blank=True,null=True)   
    modified = models.DateTimeField(blank=True,null=True)   
    
            
    def __str__(self):
        return f'{self.quotation_no} {self.unit} {self.supplier}'
    
    def save(self,*args, **kwargs):
        if not self.pk:
            self.created= timezone.now()
        self.modified = timezone.now()
        super().save(*args, **kwargs)
    
class Quotation_Items(models.Model):
    quotation = models.ForeignKey(Quotation,on_delete=models.CASCADE,related_name='quotation_item')
    item = models.ForeignKey(Item,on_delete=models.CASCADE)    
    quantity = models.DecimalField(max_digits=20,decimal_places=2)
    unit_rate = models.DecimalField(max_digits=10,decimal_places=2)    
    value = models.DecimalField(max_digits=20,decimal_places=2,editable=False)
    inr_value = models.DecimalField(max_digits=30,decimal_places=2,default=0) 
    misc_cost = models.DecimalField(max_digits=20,decimal_places=2,default=0) #to inland haulage etc
    balance_quantity = models.DecimalField(max_digits=20,decimal_places=2,default=0)
   
    def __str__(self):
        return f"{self.quotation}"
    

    
class Purchase_Order(models.Model):
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,default=2)    
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='po_unit')    
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE,related_name='quote')
    po_number = models.CharField(max_length=100, blank=True,null=True)
    po_date = models.DateField(default=timezone.now)
    po_quantity = models.DecimalField(max_digits=20,decimal_places=2,default=0)
    tax = models.DecimalField(max_digits=20,decimal_places=2,default=0)
    po_value = models.DecimalField(max_digits=40,decimal_places=2,default=0)
    freight = models.ForeignKey(Freight,on_delete=models.CASCADE,blank=True,null=True,verbose_name='Freight_Rule')
    inr_value = models.DecimalField(max_digits=40,decimal_places=2,default=0)    
    balance_quantity= models.DecimalField(max_digits=20,decimal_places=2,default=0)    
    approved = models.BooleanField(default=False) 
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    approver = models.ForeignKey(User, on_delete=models.CASCADE,related_name='purchase_order_approved_by',blank=True,null=True)
    approval_date = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(blank=True,null=True)
    modified= models.DateTimeField(blank=True,null=True)
    
    def __str__(self):
        return f'{self.po_number} - {self.po_date} -{self.quotation}'   

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created = timezone.now()
            self.po_date = timezone.now()
        self.modified = timezone.now()        
        if not self.po_number:
            self.po_number = generate_document_number(
            model_class=Purchase_Order,           
            transaction_type=self.transaction_type,
            unit=self.unit,  # Ensure this is the correct unit
            number_field= 'po_number'    ) 
        super().save(*args, **kwargs)  # Save the Purchase Order

class Purchase_Order_Items(models.Model):
    purchase_order = models.ForeignKey(Purchase_Order,on_delete=models.CASCADE,related_name='order')
    quotation_item = models.ForeignKey(Item,on_delete=models.CASCADE,blank=True,null=True)
    quantity = models.DecimalField(max_digits=20,decimal_places=2,default=0)
    rate = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    value = models.DecimalField(max_digits=20,decimal_places=2,editable=False)
    inr_value = models.DecimalField(max_digits=30,decimal_places=2,default=0)
    balance_quantity = models.DecimalField(max_digits=20,decimal_places=2,editable=False,default=0)  
    vat = models.DecimalField(max_digits=20,decimal_places=2,default=0)    
    cst = models.DecimalField(max_digits=20,decimal_places=2,default=0)
    cgst = models.DecimalField(max_digits=30,decimal_places=2,default=0)
    sgst = models.DecimalField(max_digits=30,decimal_places=2,default=0)
    igst = models.DecimalField(max_digits=30,decimal_places=2,default=0)
    creditable= models.BooleanField(default=False)  
    
    def __str__(self):
        return f'{self.purchase_order}'
   

class Freight_Purchase_Order(models.Model):
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE)
    po = models.OneToOneField(Purchase_Order,on_delete=models.CASCADE,blank=True,null=True)
    po_number = models.CharField(max_length=100, blank=True,null=True)
    po_date = models.DateField()
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name='service_business',default=1)        
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='frt_unit') 
    service = models.ForeignKey(Service,on_delete=models.CASCADE,default=1)
    supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE,related_name='transporter')
    po_amount = models.DecimalField(max_digits=20,decimal_places=2,default=0)
    inr_amount = models.DecimalField(max_digits=20,decimal_places=2,default=0)    
    cgst = models.DecimalField(max_digits=30,decimal_places=2,default=0)
    sgst = models.DecimalField(max_digits=30,decimal_places=2,default=0)
    igst = models.DecimalField(max_digits=30,decimal_places=2,default=0) 
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    approver = models.ForeignKey(User, on_delete=models.CASCADE,related_name='frt_approved_by',blank=True,null=True)
    approval_date = models.DateTimeField(auto_now_add=True)
    #to updated later
    is_mrn = models.BooleanField(default=False)   
    is_bill = models.BooleanField(default=False)

    
    def __str__(self):
        return f'{self.po_number} - {self.po_date}'   

    def save(self, *args, **kwargs):
        if not self.po_date:
            self.po_date = timezone.now()
        if not self.pk:
            number_field = 'po_number'
            transaction_type = self.transaction_type
        if not self.po_number:
            self.po_number = generate_document_number(
            model_class=Freight_Purchase_Order,
            transaction_type=transaction_type,
            unit=self.unit,  
            number_field=number_field    )       
        super().save(*args, **kwargs)  # Save the Purchase Order

    
class Gate_Entry(models.Model):
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,default=1) 
    po = models.ForeignKey(Purchase_Order,on_delete=models.CASCADE,verbose_name='Enter Purchase Order Number')
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,blank=True,null=True)
    gate_entry_number = models.CharField(max_length=50)
    gate_entry_date = models.DateTimeField(auto_now_add =True)
    truck_number = models.CharField(max_length=20)
    lorry_receipt_number = models.CharField(max_length=50)
    lorry_receipt_date = models.DateField()
    driver_name = models.CharField(max_length=100)
    license_number= models.CharField(max_length=100)
    invoice_no = models.CharField(max_length=100)
    invoice_date = models.DateField()
    item_cat = models.ForeignKey(Item_Category,on_delete=models.CASCADE)
    invoice_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    invoice_value = models.DecimalField(max_digits=20,decimal_places=2)
    is_unloaded = models.BooleanField(default=False)
    is_quality_ok = models.BooleanField(default=False)
    is_mrn_made = models.BooleanField(default=False)
    mrn_no = models.CharField(max_length=30,blank=True,null=True)
    mrn_date = models.DateField(blank=True,null=True)
    out_time = models.DateTimeField(blank=True,null=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    
    def __str__(self):
        return f"{self.po},{self.gate_entry_number}{self.gate_entry_date}"
    
    def save(self,*args, **kwargs):
        if not self.unit:
            self.unit = self.po.unit
        if not self.pk:
            if not self.gate_entry_number:
                self.gate_entry_number= generate_document_number(
                model_class=Gate_Entry,
                transaction_type=self.transaction_type,
                unit=self.unit, 
                number_field='gate_entry_number'
                )
            super().save(*args, **kwargs)

class Vehicle_Unloading_Report(models.Model):
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,default=22)
    transaction_number = models.CharField(max_length=20)
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,default=1)
    gate_entry = models.OneToOneField(Gate_Entry,on_delete=models.CASCADE)
    unloading_date = models.DateTimeField(blank=True,null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    
    def __str__(self):
        return f'{self.transaction_number} {self.gate_entry}'
    
    def save(self,*args, **kwargs):               
        if not self.pk:
            self.unloading_date = timezone.now()
            if not self.transaction_number:
                self.transaction_number = generate_document_number(
                    model_class= Vehicle_Unloading_Report,
                    transaction_type=self.transaction_type,
                    unit = self.unit,     
                    number_field= 'transaction_number'
                )
        super().save(*args, **kwargs)  # Save the unloadig slip    

class Vehicle_Unload_Items(models.Model):
    vur = models.ForeignKey(Vehicle_Unloading_Report,on_delete=models.CASCADE,related_name='unloaded_item',verbose_name='Vehicle_Unload_Report')
    item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name='unloaded_item')
    bill_quantity = models.DecimalField(max_digits=20,decimal_places=2)
    actual_quantity = models.DecimalField(max_digits=20,decimal_places=2)
        
    def __str__(self):
        return f'{self.item}--{self.actual_quantity}'

class Material_Receipt_Note(models.Model):
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,default=1)    
    gate_entry = models.OneToOneField(Gate_Entry,on_delete=models.CASCADE,related_name='related_ge')
    unload_report = models.ForeignKey(Vehicle_Unloading_Report,on_delete=models.CASCADE,related_name='unloaded_items',blank=True,null=True)
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,default=1)    
    mrn_number = models.CharField(max_length=100, blank=True,null=True,editable=False)
    mrn_date = models.DateField(auto_now_add=True)      
    e_way_bill_no = models.CharField(max_length=20)
    quality_approval = models.BooleanField(default=False)    
    form_c_issue_status = models.BooleanField(default=False)
    form_no = models.CharField(max_length=50,blank=True,null=True)
    created = models.BooleanField(default=False)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True,related_name='created_by')
    approver= models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True,related_name='approver')
    approval_date = models.DateField(blank=True,null=True)
    
    
    class Meta:
        indexes = [
            models.Index(fields=['mrn_number', 'mrn_date']) # Explicitly adds an index           
        ]
        
    def __str__(self):
        return f'{self.mrn_number}'
    
    def save(self, *args, **kwargs):      
        self.unit = self.gate_entry.unit
        if not self.pk:
            if not self.mrn_number:
                self.mrn_number = generate_document_number(
                    model_class=Material_Receipt_Note,
                    transaction_type= self.transaction_type,
                    unit= self.unit,
                    number_field = 'mrn_number'                    
                    
                )       
        super().save(*args, **kwargs)  # Save the Purchase Order
  

class Mrn_Items(models.Model):
    mrn = models.ForeignKey(Material_Receipt_Note,on_delete=models.CASCADE,related_name='mrn_instance')
    item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name='mrn_item')
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,blank=True,null=True)
    invoice_quantity  = models.DecimalField(max_digits=15,decimal_places=2,blank=True,null=True)    
    actual_quantity  = models.DecimalField(max_digits=15,decimal_places=2,blank=True,null=True)    
    value = models.DecimalField(max_digits=30,decimal_places=2,editable=False,default=0)
    vat = models.DecimalField(max_digits=10,decimal_places=2,editable=False,default=0)
    cst = models.DecimalField(max_digits=10,decimal_places=2,editable=False,default=0)
    cgst = models.DecimalField(max_digits=10,decimal_places=2,editable=False,default=0)    
    sgst = models.DecimalField(max_digits=10,decimal_places=2,editable=False,default=0)    
    igst = models.DecimalField(max_digits=10,decimal_places=2,editable=False,default=0)    
    freight= models.DecimalField(max_digits=10,decimal_places=2,editable=False,default=0)
    cgst_freight= models.DecimalField(max_digits=10,decimal_places=2,editable=False,default=0)
    sgst_freight= models.DecimalField(max_digits=10,decimal_places=2,editable=False,default=0)
    igst_freight= models.DecimalField(max_digits=10,decimal_places=2,editable=False,default=0)
    custom_duty = models.DecimalField(max_digits=50,decimal_places=2,default=0)
    excise_levies = models.DecimalField(max_digits=50,decimal_places=2,default=0)    
    custom_clearance = models.DecimalField(max_digits=50,decimal_places=2,default=0)
    landed_cost = models.DecimalField(max_digits=50,decimal_places=2,default=0)
    stock_location = models.ForeignKey(Unit_Sub_Location,on_delete=models.CASCADE,blank=True,null=True)
    
    def __str__(self):
        return f'{self.item} --{self.actual_quantity}'
    
    
        

class Quality_Check(models.Model):
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,default=21)
    # transaction_number = models.CharField(max_length=30)
    gate_entry = models.ForeignKey(Gate_Entry,on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,default=1)
    inspection_number = models.CharField(max_length=20)    
    inspection_date = models.DateField(default=timezone.now)                
    specification = models.ForeignKey(Standard_Quality_Specifications,on_delete=models.CASCADE)
    observed_value = models.CharField(max_length=20,blank=True,null=True)
    is_ok = models.BooleanField(default=False)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)   
    
    
    class Meta:
        unique_together = ('gate_entry', 'specification')  
    
    def __str__(self):
        return f'{self.inspection_number} -{self.specification}-{self.observed_value}'   
    
    def save(self,*args, **kwargs):
        self.unit = self.gate_entry.unit
        if not self.inspection_number:
            self.inspection_number=generate_document_number(
            model_class= Quality_Check,
            transaction_type=self.transaction_type,
            unit=self.unit,     
            number_field='inspection_number'
            )
        super().save(*args, **kwargs)  # Save the unloadig slip
             
class Po_Lcr_Join(models.Model):
    po = models.OneToOneField(Purchase_Order,on_delete=models.CASCADE,related_name='join_po')
    lcr = models.ForeignKey(Landed_Cost_Rule,on_delete=models.CASCADE,related_name='join_lcr')
    freight = models.ForeignKey(Freight,on_delete=models.CASCADE,related_name='join_freight',blank=True,null=True)
    clearance = models.ForeignKey(Supplier_Service,on_delete=models.CASCADE,blank=True,null=True)
    
    def __str__(self):
        return f'{self.po} -- {self.lcr} -- {self.freight}'

    
    
class Tax_Table(models.Model):    
    transaction_type= models.ForeignKey(Transaction_Type, on_delete=models.CASCADE,blank=True,)
    transaction_number = models.CharField(max_length=100,blank=True,null=True)
    transaction_date = models.DateField(blank=True,null=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE,blank=True,null=True)
    supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE,blank=True,null=True)
    nature_of_supply = models.CharField(max_length=100,blank=True,null=True)
    taxable_value = models.DecimalField(max_digits=20,decimal_places=2,blank=True,null=True)
    cgst = models.DecimalField(max_digits=20,decimal_places=2,blank=True,null=True)
    sgst = models.DecimalField(max_digits=20,decimal_places=2,blank=True,null=True)
    igst = models.DecimalField(max_digits=20,decimal_places=2,blank=True,null=True)
    place_of_supply = models.CharField(max_length=50,blank=True,null=True)
    time_of_supply= models.DateTimeField(blank=True,null=True)    
    section = models.CharField(max_length=20,blank=True,null=True)
    classification= models.CharField(max_length=20,blank=True,null=True)   
    sub_classifcation=models.CharField(max_length=20,blank=True,null=True)
    deductee_type=models.CharField(max_length=20,blank=True,null=True)
    rate= models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    tds = models.DecimalField(max_digits=20,decimal_places=2,blank=True,null=True)
    #to be update when bill is supllied by party
    bill_number = models.CharField(max_length=50,blank=True,null=True)
    bill_date = models.DateField(blank=True,null=True)
    bill_amount = models.DecimalField(max_digits=20,decimal_places=2,blank=True,null=True)
    
    def __str__(self):
        return f'{self.transaction_type}'
    
    
        
    
        

    
    
    
        
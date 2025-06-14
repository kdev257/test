from django.db import models
from masters.models import User,Service,Supplier,Transaction_Type,Unit,State,Cost_Center,Currency,Sub_Cost_Center,Business
from django.utils import timezone
from django.db.models import Sum,Count,Avg,Max,Min
from django.contrib import messages
from inventory.functions import generate_document_number

# Create your models here.

class Service_Quotation(models.Model):
    tax_choices = (        
        ('Inclusive','Inclusive'),
        ('Exclusive','Exclusive'),
        
    )
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,related_name='transaction_type')
    transaction_number = models.CharField(max_length=20,unique=True,verbose_name='Quotation Number')
    transaction_date = models.DateField()
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='quotation_unit') 
    supplier = models.ForeignKey(User,on_delete=models.CASCADE,related_name='quotation_service_supplier')    
    taxes = models.CharField(max_length=20,choices=tax_choices,default='Exclusive')
    currency = models.ForeignKey(Currency,on_delete=models.CASCADE,related_name='quotation_currency')
    amount = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    inr_amount = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)    
    valid_till = models.DateField(blank=True,null=True)
    credit_terms = models.CharField(max_length=200,blank=True,null=True)    
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='quotation_created_by')
    approver = models.ForeignKey(User,on_delete=models.CASCADE,related_name='quotation_approver',null=True,blank=True)    
    status = models.CharField(max_length=20,choices=(('Pending','Pending'),('Approved','Approved'),('Closed','closed')),default='Pending')
    approval_date = models.DateField(null=True,blank=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    
    
    def __str__(self):
        return f'{self.transaction_number} - {self.supplier}'
    
    def save(self,*args,**kwargs):
        if not self.pk:
            self.created = timezone.now()
            self.transaction_date = timezone.now()
            self.valid_till = timezone.now() + timezone.timedelta(days=45)            
        self.modified = timezone.now()
        if not self.transaction_number:
            self.transaction_number = generate_document_number(
                model_class=Service_Quotation,
                unit = self.unit,
                transaction_type = self.transaction_type,
                number_field='transaction_number',
            )
        super(Service_Quotation,self).save(*args,**kwargs)

class Service_Quotation_Items(models.Model):
    quotation = models.ForeignKey(Service_Quotation,on_delete=models.CASCADE,related_name='quotation_items')
    service = models.ForeignKey(Service,on_delete=models.CASCADE,related_name='service_quotation_items')
    service_description = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10,decimal_places=2)
    amount = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    inr_amount = models.DecimalField(max_digits=10,decimal_places=2)
    
    def __str__(self):
        return f'{self.quotation} - {self.service}'
    
    def save(self,*args,**kwargs):
        if not self.pk:
            self.amount = self.quantity * self.rate
        super(Service_Quotation_Items,self).save(*args,**kwargs)
    
class Service_Order(models.Model):
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name='service_order_business')
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,related_name='service_order_transaction_type')
    transaction_number = models.CharField(max_length=20,unique=True,verbose_name='Order Number')
    transaction_date = models.DateField()
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='service_order_unit')
    sub_cost_center = models.ForeignKey(Sub_Cost_Center,on_delete=models.CASCADE,related_name='service_order_cost_center')
    states = models.ManyToManyField(State, related_name='service_order_states', blank=True)
    quotation = models.ForeignKey(Service_Quotation, on_delete=models.CASCADE, related_name='service_order_quotation')    
    amount = models.DecimalField(max_digits=20,decimal_places=2,default=0)
    inr_amount = models.DecimalField(max_digits=20,decimal_places=2,default=0)
    tax = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='service_order_created_by')
    approver = models.ForeignKey(User,on_delete=models.CASCADE,related_name='service_order_approver',null=True,blank=True)  
    created=models.DateTimeField()
    modified=models.DateTimeField()     
    status = models.CharField(max_length=20,choices=(('Pending','Pending'),('Approved','Approved'),('Closed','Closed')),default='Pending')
    
    def __str__(self):
        return f'{self.transaction_number} - {self.quotation.supplier} --{self.states}'
    
    def save(self,*args,**kwargs):
        if not self.pk:
            self.created = timezone.now()
            self.transaction_date = timezone.now()
        self.modified = timezone.now()
        if not self.transaction_number:
            self.transaction_number = generate_document_number(
                model_class=Service_Order,
                unit = self.unit,
                transaction_type = self.transaction_type,
                number_field='transaction_number',
            )
        super(Service_Order,self).save(*args,**kwargs)
        
class Service_Order_Items(models.Model):
    COMPLETETION_STATUTS = (
        ('WorkinProgress','WorkinProgress'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
    )
    service_order = models.ForeignKey(Service_Order,on_delete=models.CASCADE,related_name='service_order_items')
    service = models.ForeignKey(Service,on_delete=models.CASCADE,related_name='service_order_service')
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10,decimal_places=2)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    cgst = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    sgst = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    igst = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    completion_status= models.CharField(max_length=20,choices=COMPLETETION_STATUTS,default='WorkinProgress')
    status_date = models.DateField(null=True,blank=True)
    completion_date = models.DateField(null=True,blank=True)
    completion_percentage = models.DecimalField(max_digits=5,decimal_places=2,default=0)
    updated_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='service_order_items_updated_by',null=True,blank=True)
    service_invoice = models.ForeignKey('Service_Invoice', on_delete=models.CASCADE, related_name='service_order_items_invoice', null=True, blank=True)
    
    
    def __str__(self):
        return f'{self.service_order} - {self.service}'  
    

class Service_Invoice(models.Model):
    transaction_type = models.ForeignKey(Transaction_Type,on_delete=models.CASCADE,related_name='service_invoice_transaction_type')
    transaction_number = models.CharField(max_length=20,unique=True,verbose_name='Invoice Number')
    transaction_date = models.DateField()
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,related_name='service_invoice_unit')
    service_order = models.ForeignKey(Service_Order, on_delete=models.CASCADE, related_name='service_invoices')
    invoice_number = models.CharField(max_length=20,unique=True,verbose_name='Invoice Number')
    invoice_date = models.DateField()
    invoice_amount = models.DecimalField(max_digits=20,decimal_places=2,default=0)
    inr_amount = models.DecimalField(max_digits=20,decimal_places=2,default=0)
    cgst = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    sgst = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    igst = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    creditable = models.BooleanField(default=False)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='service_invoice_created_by')
    approver = models.ForeignKey(User,on_delete=models.CASCADE,related_name='service_invoice_approver',null=True,blank=True)  
    created=models.DateTimeField()
    modified=models.DateTimeField()     
    status = models.CharField(max_length=20,choices=(('Pending','Pending'),('Paid','Paid')),default='Pending')
    
    def __str__(self):
        return f'{self.transaction_number} - {self.service_order.quotation.supplier}'
    
    def save(self,*args,**kwargs):
        if not self.pk:
            self.created = timezone.now()
            self.transaction_date = timezone.now()
        self.modified = timezone.now()
        if not self.transaction_number:
            self.transaction_number = generate_document_number(
                model_class=Service_Invoice,
                unit = self.unit,
                transaction_type = self.transaction_type,
                number_field='transaction_number',
            )
        super(Service_Invoice,self).save(*args,**kwargs)
    
class Service_Invoice_Items(models.Model):
    service_invoice = models.ForeignKey(Service_Invoice,on_delete=models.CASCADE,related_name='service_invoice_items')
    service = models.ForeignKey(Service,on_delete=models.CASCADE,related_name='service_invoice_service')
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10,decimal_places=2)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    inr_amount = models.DecimalField(max_digits=10,decimal_places=2)
    cgst = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    sgst = models.DecimalField(max_digits=10,decimal_places=2,default=0)    
    igst = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    updated_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='service_invoice_items_updated_by',null=True,blank=True) 
     
    
    def __str__(self):
        return f'{self.service_invoice} - {self.service}'
    
    

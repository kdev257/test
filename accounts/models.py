from django.db import models
from django.db import transaction as db_transaction
from django.core.exceptions import ValidationError
# from production.models import Blend
from masters.models import Account_Chart,Account_Sub_Category,Account_Category,Account_Sub_Class,Account_Class,Unit,Transaction_Type,User,User_Roles,Unit_of_Measurement
from inventory.functions import generate_document_number,generate_transaction_no
from django.utils import timezone

# Create your models here.

class Inv_Transaction(models.Model):  
    
    TRANSACTION_CAT= [
        ('Select', 'Select'),
        ('Debit', 'Debit'),
        ('Credit', 'Credit'),        
    ]
    
    transaction_type = models.ForeignKey(Transaction_Type, on_delete=models.CASCADE, blank=True, null=True)
    transaction_number = models.CharField(max_length=100, editable=False)
    transaction_cat = models.CharField(max_length=50, choices=TRANSACTION_CAT, blank=True, null=True)
    transaction_date = models.DateField()
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, default=1)
    account_chart = models.ForeignKey(Account_Chart, on_delete=models.CASCADE, related_name='transactions')
    debit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reference = models.CharField(max_length=255, null=True, blank=True)
    approved = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['id','unit'])  # Explicitly adds an index            
        ]

    def __str__(self):
        return f'{self.transaction_date} | {self.account_chart} | {self.transaction_type} | {self.debit_amount} | {self.credit_amount}'
   
    def save(self, *args, **kwargs):
        if not self.transaction_date:
            self.transaction_date = timezone.now()
        
        super().save(*args, **kwargs)
        
        
class Overheads(models.Model):
    OVERHEAD_TYPE_CHOICES=(
        ('Production_Overheads','Production_Overheads'),
        ('Admin_OVerheads','Admin_Overheads'),
        ('Sales_Overheads','Sales_Overheads'),
        ('Marketing_Overhead','Marketing_Overheads'),
        ('Distribution_Overheads','Distribution_Overheads')
    )
    CATEGORY_CHOICES=(
        ('Fixed_Overheads','Fixed_Overheads'),
        ('Variable_Overheads','Variable_Overheads'),
        ('Budgeted_Overhead','Budgeted_Overheads'),
    )
    name = models.CharField(max_length=50,verbose_name='Overhead_Name')
    type = models.CharField(max_length=100,choices=OVERHEAD_TYPE_CHOICES,verbose_name='Overhead_Type')
    category = models.CharField(max_length=50,choices=CATEGORY_CHOICES,verbose_name='Overhead_Category')
    account = models.ForeignKey(Account_Chart,on_delete=models.CASCADE,verbose_name='Pls. Map the Overhead Account')
    
    class Meta:
        verbose_name_plural = "Overheads"
    
    def __str__(self):
        return f"{self.name}--{self.type}"


    
    


    
    
    
             
        
    

from django import forms
from masters.models import Transaction_Type,User,Supplier_Profile
from .models import (
    Service_Quotation, Service_Quotation_Items,
    Service_Order, Service_Order_Items,
    Service_Invoice, Service_Invoice_Items
)

class ServiceQuotationForm(forms.ModelForm):
    class Meta:
        model = Service_Quotation
        fields = '__all__'
        exclude = 'transaction_number', 'created', 'modified', 'status','transaction_date', 'created_by', 'approver','created','modified', 'status','approval_date','amount','inr_amount'
        
        widgets = {
            'valid_till': forms.DateInput(attrs={'type': 'date'}),            
        }
    def __init__(self, *args, **kwargs):    
        super(ServiceQuotationForm, self).__init__(*args, **kwargs)
        self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(transaction_name='SQ')
        self.fields['supplier'].queryset = User.objects.filter(user_type= 'Service_Provider')
        
        

class ServiceQuotationItemForm(forms.ModelForm):
    po_quantity = forms.DecimalField(
        max_digits=20,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter PO Quantity'}),
        
    )

    class Meta:
        model = Service_Quotation_Items
        fields = '__all__'
        exclude = 'amount','inr_amount','po_quantity'
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
        }


class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = Service_Order
        fields = '__all__'
        exclude = 'amount','transaction_number','transaction_date','created_by','created','modified','status','approver','approval_date','inr_amount','tax'
    def __init__(self, *args, **kwargs):
        super(ServiceOrderForm, self).__init__(*args, **kwargs)
        self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(transaction_name='SO')
        self.fields['quotation'].queryset = Service_Quotation.objects.filter(status='Approved')
            
            
            
        widgets = {
            'valid_till': forms.DateInput(attrs={'type': 'date'}),
            'transaction_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ServiceOrderItemForm(forms.ModelForm):
    invoice_quantity = forms.DecimalField(
        max_digits=20,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Invoice Quantity'}),
        
    )

    class Meta:
        model = Service_Order_Items
        fields = 'service', 'quantity', 'rate', 
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control', 'style': 'width:500px;'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'invoice_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Invoice Quantity'}),
        }

    # def __init__(self, *args, **kwargs):
    #     super(ServiceOrderItemForm, self).__init__(*args, **kwargs)
    #     self.fields['invoice_quantity'].widget.attrs.pop('readonly', None)
    #     self.fields['invoice_quantity'].widget.attrs.pop('disabled', None)

class Service_Order_Items_Completion_Status_Form(forms.ModelForm):
    class Meta:
        model = Service_Order_Items
        
        fields = ['id','service','completion_status','completion_date','completion_percentage','status_date']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control', 'style': 'width:500px;'}),
            'completion_status': forms.Select(attrs={'class': 'form-control'}),
            'completion_date': forms.DateInput(attrs={'type': 'date'}),
            'status_date': forms.DateInput(attrs={'type': 'date'}),
            'completion_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Completion Percentage'}),
            
            
        }

class ServiceInvoiceForm(forms.ModelForm):
    class Meta:
        model = Service_Invoice
        fields = '__all__'
        exclude = 'transaction_number', 'created', 'modified', 'status', 'created_by', 'approver', 'approval_date', 'amount', 'inr_amount','transaction_date','cgst','sgst','igst','creditable'
        widgets = {            
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'service_order': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(ServiceInvoiceForm, self).__init__(*args, **kwargs)
        self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(transaction_name='SI')
        self.fields['service_order'].queryset = Service_Order.objects.filter(status='Completed')
        # self.fields['unit'].queryset = Supplier_Profile.objects.all()
        

class ServiceInvoiceItemForm(forms.ModelForm):
    class Meta:
        model = Service_Invoice_Items
        fields = 'service', 'quantity', 'rate', 'amount'
        exclude = 'inr_amount',
        
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control', 'style': 'width:500px;'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

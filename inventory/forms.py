from django import forms
from django.forms import inlineformset_factory
from .models import Quotation,Quotation_Items,Purchase_Order,Purchase_Order_Items,Po_Lcr_Join,Gate_Entry,Material_Receipt_Note,Quality_Check,Vehicle_Unloading_Report,Vehicle_Unload_Items
from masters.models import User_Roles,User,Standard_Quality_Specifications,Item,Supplier,Freight,Supplier_Service,Transaction_Type,Landed_Cost_Rule
from django.utils import timezone
from django.core.exceptions import ValidationError

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = 'supplier_name','assessee_type','gstin','supplier_state','account'
        

class FreightForm(forms.ModelForm):
    class Meta:
        model = Freight
        fields = '__all__'

class QuotationForm(forms.ModelForm):    
    class Meta:
        model = Quotation
        fields = [
            'transaction_type','quotation_no', 'quotation_date', 
            'supplier', 'delivery_terms', 'valid_from', 'valid_till', 'misc_cost',
            'credit_terms','taxes','form_c', 'document','currency'
        ]
        
        
        widgets={
            'quotation_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'valid_from': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'valid_till': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(QuotationForm, self).__init__(*args, **kwargs)

        if user:
            try:
                user_unit = user.user_roles.unit
               
            except User_Roles.DoesNotExist:
                user_unit = None
            # if user and self.instance.supplier.location == "Overseas":
            #     self.fields['inland_haulage'].queryset = Supplier.objects.filter()
            # else:
            #     self.fields.pop('inland_haulage')  # Remove the inland_haulage field if not needed
            # #     unit=user_unit,)

class AddItemForm(forms.Form):
    add_item = forms.ChoiceField(
        choices=[('yes', 'Yes'), ('no', 'No')],
        widget=forms.RadioSelect,
        label="Do you want to add an item?"
    )


class QuotationItemsForm(forms.ModelForm):
    class Meta:
        model = Quotation_Items
        fields = 'quotation','item','quantity','unit_rate',
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(QuotationItemsForm, self).__init__(*args, **kwargs)
        
        if user:
            try:
                user_unit = user.user_roles.unit
               
            except User_Roles.DoesNotExist:
                user_unit = None
            
            self.fields['quotation'].queryset = Quotation.objects.filter(unit=user_unit,approved=False)
        
            
class QuotationItemEditForm(forms.ModelForm):
    po_quantity = forms.DecimalField(
        max_digits=20,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter PO Quantity'}),
        
    )

    class Meta:
        model = Quotation_Items
        fields = ['id','item', 'quantity', 'po_quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make 'item' and 'quantity' fields read-only if necessary
        self.fields['item'].widget.attrs['readonly'] = True
        self.fields['quantity'].widget.attrs['readonly'] = True
                    

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = Purchase_Order
        fields = ['business', 'transaction_type', 'quotation', 'freight', 'service']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)        
        quotation = kwargs.pop('quotation', None)  # Get the Quotation instance
        super(PurchaseOrderForm, self).__init__(*args, **kwargs)

        if quotation:
            self.fields['quotation'].initial = quotation

            # Example: hide 'service' field for overseas suppliers
            if quotation.supplier.location != 'Overseas':                
                self.fields.pop('service', None)
            if quotation.delivery_terms != "Ex-Factory":
                self.fields.pop('freight', None)

        if user:
            try:
                user_unit = user.user_roles.unit
            except User_Roles.DoesNotExist:
                user_unit = None

        self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(id=2)
        self.fields['freight'].queryset = Freight.objects.filter(unit=user_unit)
        

class PurchaseOrderItemForm(forms.ModelForm):
    class Meta: 
        model = Purchase_Order_Items 
        fields = ['balance_quantity' ]  
        


class PoLcrJoinForm(forms.ModelForm):
    clearance = forms.ModelChoiceField(
        queryset=Supplier_Service.objects.none(),  # Adjust this to your Clearance model
        required=False,
        label="Clearance",
    )

    class Meta:
        model = Po_Lcr_Join
        fields = ['lcr', 'freight', 'clearance']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        po = kwargs.pop('po', None)  # Get the Purchase Order instance
        super(PoLcrJoinForm, self).__init__(*args, **kwargs)

        if user and po:
            try:
                user_unit = user.user_roles.unit
            except User_Roles.DoesNotExist:
                user_unit = None

            # Filter the queryset based on user unit and item related to the Purchase Order
            self.fields['lcr'].queryset = Landed_Cost_Rule.objects.filter(
                unit=user_unit,
                supplier = po.quotation.supplier
                
            )

            # Set freight field conditionally based on delivery type
            if po.quotation.delivery_terms == "Ex-Factory":
                self.fields['freight'].queryset = Freight.objects.filter(
                    unit=user_unit,
                )
            else:
                self.fields.pop('freight')  # Remove the freight field if not needed

            # Set clearance field conditionally based on supplier location
            if po.quotation.supplier.location == "Overseas":
                self.fields['clearance'].queryset = Supplier_Service.objects.filter(
                    unit=user_unit,
                )
            else:
                self.fields.pop('clearance')  # Remove the clearance field if not needed

            
                        
class GateEntryForm(forms.ModelForm):
    class Meta:
        model = Gate_Entry
        fields = ('transaction_type', 'po', 'truck_number','lorry_receipt_number','lorry_receipt_date', 'driver_name', 'license_number', 'invoice_no',
        'invoice_date', 'invoice_quantity', 'invoice_value', 'item_cat')
        
        widgets={
            'lorry_receipt_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'invoice_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),            
            }


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        po = kwargs.pop('po', None)  # Get the Purchase Order instance
        super(GateEntryForm, self).__init__(*args, **kwargs)  # Corrected the super() call

        if user:
            try:
                user_unit = user.user_roles.unit
            except User_Roles.DoesNotExist:
                user_unit = None

            # Filtering the Purchase Orders based on user unit and approval status
            self.fields['po'].queryset = Purchase_Order.objects.filter(
                # unit=user_unit,
                approved=True,
                balance_quantity__gt = 0,
                unit = user_unit
                
            )
            self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(id=3)
class GenerateMrnForm(forms.ModelForm):
    class Meta:
        model = Material_Receipt_Note
        fields = ('transaction_type','e_way_bill_no')        
        

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        po = kwargs.pop('po', None)  # Get the Purchase Order instance
        super(GenerateMrnForm, self).__init__(*args, **kwargs)  # Corrected the super() call

        if user:
            try:
                user_unit = user.user_roles.unit
            except User_Roles.DoesNotExist:
                 user_unit = None

             # Filtering the Purchase Orders based on user unit and approval status
            self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(id=6)
       

class QualityCheckForm(forms.ModelForm):
    class Meta:
        model = Quality_Check
        fields = ['gate_entry', 'specification', 'observed_value', 'is_ok']

    def __init__(self, *args, **kwargs):
        # Fetch the current gate_entry instance either from initial data or the model instance
        gate_entry = kwargs.get('initial', {}).get('gate_entry', None) or getattr(getattr(self, 'instance', None), 'gate_entry', None)
        super(QualityCheckForm, self).__init__(*args, **kwargs)

        if gate_entry:
            # Assuming `gate_entry` has a related `item` field
            gate_entry_item = gate_entry.item_cat

            # Get the specifications for this item
            specifications_for_item = Standard_Quality_Specifications.objects.filter(item_cat=gate_entry_item)

            # Get specifications that already have observed values for the given gate_entry
            observed_specifications = Quality_Check.objects.filter(
                gate_entry=gate_entry
            ).exclude(observed_value__isnull=True).values_list('specification', flat=True)

            # Filter out the observed specifications
            self.fields['specification'].queryset = specifications_for_item.exclude(id__in=observed_specifications)

        
        

# class QualityCheckApproveForm(forms.ModelForm):
#     class Meta:
#         model = Approve_Quality_Check
#         fields = 'approval_number','is_ok' 
    
#     def __init__(self,*args, **kwargs):
#         user = kwargs.pop('user',None)
#         super(QualityCheckApproveForm,self).__init__(*args,**kwargs)
#         if user:
#             unit = user.user_roles.unit
        
#         isok = Approve_Quality_Check.objects.filter(is_ok = False)
            
#         self.fields['approval_number'].queryset = Approve_Quality_Check.objects.filter(
#             is_ok = False
#         )

class VehicleUnloadForm(forms.ModelForm):
    class Meta:
        model = Vehicle_Unloading_Report
        fields = 'gate_entry',       
        

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        po = kwargs.pop('po', None)  # Get the Purchase Order instance        
        super(VehicleUnloadForm, self).__init__(*args, **kwargs)  # Corrected the super() call

        if user:
            try:
                user_unit = user.user_roles.unit
            except User_Roles.DoesNotExist:
                user_unit = None

            # Filtering the Purchase Orders based on user unit and approval status
            self.fields['gate_entry'].queryset = Gate_Entry.objects.filter(                
                    is_unloaded=False,
                    is_quality_ok = True,
                    unit = user_unit,                                
                )

class VehicleUnloadItemForm(forms.ModelForm):
    class Meta:
        model = Vehicle_Unload_Items
        fields = 'item','bill_quantity','actual_quantity'
                 
from django import forms
from .models import Unit_Sub_Location,Blend,Blend_Bom,Bom_Items,Material_Requisition,Stock_Entry
from masters.models import User,User_Roles,Transaction_Type,Item,Unit
from inventory.models import Material_Receipt_Note,Gate_Entry,Mrn_Items
from django.db.models import Sum,F

class BomForm(forms.ModelForm):
    class Meta:
        model = Blend_Bom
        fields = '__all__'
        exclude = 'bom_number','bom_date','created_by','created','modified'
        
    def __init__(self, *args, **kwargs):
        
        super(BomForm, self).__init__(*args, **kwargs)  
        self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(transaction_name='BOM')
        
        
class BomItemsForm(forms.ModelForm):
    class Meta:
        model = Bom_Items
        fields = '__all__'


class BlendForm(forms.ModelForm):
    class Meta:
        model= Blend
        fields = "__all__"
        exclude = 'unit','created_by','status'
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(BlendForm, self).__init__(*args, **kwargs)
        if user:
            try:
                unit = user.user_roles.unit
            except User_Roles.DoesNotExist:
                unit = None
        self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(transaction_name='Blend')
        # self.fields['created_by'].queryset = User.objects.filter(id=user.id)    
        
class MaterialRequisionForm(forms.ModelForm):
    class Meta:
        model = Material_Requisition
        fields ='transaction_type', 'bom' ,'blend','production'
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(MaterialRequisionForm, self).__init__(*args, **kwargs)
        self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(transaction_name='RQ')
        
            
        
        
        
        self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(transaction_name='RQ')


class StockEntryForm(forms.ModelForm):
    class Meta:
        model = Stock_Entry
        fields ='transaction_type', 'mrn','stock_location'
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
                
        super(StockEntryForm, self).__init__(*args, **kwargs)
        if user:
            try:
                unit = user.user_roles.unit
            except User_Roles.DoesNotExist:
                unit = None
        self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(id=6)
        self.fields['mrn'].queryset = Mrn_Items.objects.filter(stock_location__isnull = True)
        self.fields['stock_location'].queryset = Unit_Sub_Location.objects.filter(unit=unit)
        
    
                
class IssueForm(forms.ModelForm):
    class Meta: 
        model= Stock_Entry
        fields = 'transaction_type','requisition','stock_location','to_location'
       
        
    def __init__(self,*args, **kwargs):
        user = kwargs.pop('user',None)
        super(IssueForm,self).__init__(*args, **kwargs)
        if user:
            unit = user.user_roles.unit
            self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(transaction_name='Issue') 
            self.fields['to_location'].queryset = Unit_Sub_Location.objects.filter(unit=unit)
            self.fields['stock_location'].queryset = Unit_Sub_Location.objects.filter(unit=unit)
            # self.fields['mrn_ref'].queryset = Unit_Sub_Location.objects.filter(unit=unit)            
            requisitioned_item = Material_Requisition.objects.filter(issue_slip__isnull=True)

            # # Get the items that have already been issued
            fully_issued_items = Stock_Entry.objects.filter(
            issue_quantity__isnull=False).values('requisition').annotate(total_issued=Sum('issue_quantity')).filter(
            total_issued=F('requisition__required_quantity')).values_list('requisition', flat=True)
            
            self.fields['requisition'].queryset = requisitioned_item.exclude(id__in=fully_issued_items).filter(unit=unit)

# class BottlingIssueForm(forms.ModelForm):
#     class Meta: 
#         model= Stock_Entry
#         fields = 'transaction_type','item','blend','requisition','stock_location','to_location','issue_quantity'
       
        
#     def __init__(self,*args, **kwargs):
#         user = kwargs.pop('user',None)
#         super(BottlingIssueForm,self).__init__(*args, **kwargs)
#         if user:
#             unit = user.user_roles.unit
#             self.fields['blend'].queryset = Blend.objects.filter(unit=unit,is_dg_issued=False)
#             self.fields['from_location'].queryset = Unit_Sub_Location.objects.filter(unit=unit).exclude(closing_quantity=0)
#             self.fields['to_location'].queryset = Unit_Sub_Location.objects.filter(unit=unit)
#             self.fields['mrn_ref'].queryset = Unit_Sub_Location.objects.filter(unit=unit)
            
#             requisitioned_item = Material_Requisition.objects.filter(issue_slip__isnull=True)

#             # Get the items that have already been issued
#             fully_issued_items = Stock_Entry.objects.filter(
#             issue_quantity__isnull=False).values('requisition').annotate(total_issued=Sum('issue_quantity')).filter(
#             total_issued=F('requisition__required_quantity')).values_list('requisition', flat=True)
            
#             self.fields['requisition'].queryset = requisitioned_item.exclude(id__in=fully_issued_items).filter(unit=unit)
            

# class BottlingIssueReturnForm(forms.ModelForm):
#     class Meta: 
#         model= Issue
#         fields = 'id','transaction_type','item','issue_quantity','return_quantity'


class DateRangeForm(forms.Form):
    start_date = forms.DateField(label='Start Date', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    end_date = forms.DateField(label='End Date', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    item = forms.ModelChoiceField(queryset=Item.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    

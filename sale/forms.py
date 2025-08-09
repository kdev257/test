from django import forms
from .models import *
from masters.models import Customer


class Cost_Card_Form_Punjab(forms.ModelForm):    
    class Meta:
        model = Cost_Card
        fields = '__all__'
        widgets = {
                    'valid_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                    'valid_till': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                }
        exclude = ['created','updated','created_by','msp','bottle','pl','bl','al','mrp','rm','wsm','modified']

class Cost_Card_Form_Haryana(forms.ModelForm):    
    class Meta:
        model = Cost_Card
        fields = '__all__'       
        widgets = {
                    'valid_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                    'valid_till': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                }
        exclude = ['created','updated','created_by','bottle','pl','bl','al','mrp','rm','wsm','modified','mop']

        

       
# class Slab_Value_Form(forms.ModelForm):
#     class Meta:
#         model = Slabs
#         fields= 'state','levy_name','min_value','max_value','levy_rate','unit','levy_formula',
    
class Permit_Entry_Form(forms.ModelForm):
    class Meta:
        model = Permit
        fields = '__all__'
        exclude = 'status','created','modified','created_by',
        widgets = {
            'permit_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valid_till': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            
            self.fields['customer'].queryset = Customer.objects.filter()

class Permit_Item_Form(forms.ModelForm):
    class Meta:
        model = Permit_Item
        fields = '__all__'
            
     
class Vehicle_For_Loading_Form(forms.ModelForm):
    class Meta:
        model = Vehicle_For_Loading
        fields = '__all__'
        exclude = 'created','modified','created_by','entry_number','entry_date','out_time'
        widgets = {
            # 'entry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'license_validity':forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }
    def __init__(self, *args, **kwargs):
        unit = kwargs.pop('unit',None)
        user = kwargs.pop('user',None)
        super().__init__(*args, **kwargs)
        if user:
            unit = user.user_roles.unit
            self.fields['unit'].queryset = Unit.objects.filter(id=unit.id)
            self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(transaction_name='VFL')
            
class Sale_Invoice_Form(forms.ModelForm):
    class Meta:
        model = Sales_Invoice
        fields = 'excise_pass','excise_pass_date','lr_number','lr_date','truck'
        widgets = {
            'excise_pass_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lr_date':forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }
        
        def __init__(self, *args, **kwargs):
            
            super().__init__(*args, **kwargs)
            self.fields['truck'].queryset = Vehicle_For_Loading.objects.filter(out_time__isnull=True)
                
from django import forms
from accounts.models import Unit,Transaction_Type,Inv_Transaction,Account_Chart
from django.forms import modelformset_factory
from masters.models import User,User_Roles

class JournalEntryForm(forms.ModelForm):
        class Meta:
            model = Inv_Transaction
            fields =  'transaction_type','transaction_cat','unit','account_chart','debit_amount','credit_amount','reference' 
              
            widgets = {
                'transaction_type': forms.Select(attrs={'class': 'form-control', 'style': 'height: 50px;'}),
                'unit': forms.Select(attrs={'class': 'form-control', 'style': 'height: 50px;'}),
                'account_chart': forms.Select(attrs={'class': 'form-control', 'style': 'height: 50px;'}),
                'transaction_cat': forms.Select(attrs={'class': 'form-control', 'style': 'height: 50px;'}),
                'debit_amount': forms.NumberInput(attrs={'class': 'form-control', 'style': 'height: 50px;'}),
                'credit_amount': forms.NumberInput(attrs={'class': 'form-control', 'style': 'height: 50px;'}),
                'reference': forms.TextInput(attrs={'class': 'form-control', 'style': 'height: 50px;'}),
            }
        # def clean(self):
        #     cleaned_data = super().clean()
        #     transaction_cat = cleaned_data.get('transaction_cat')
        #     debit_amount = cleaned_data.get('debit_amount')
        #     credit_amount = cleaned_data.get('credit_amount')

        #     if transaction_cat == 'Debit':
        #         if debit_amount is None or debit_amount == 0:
        #             self.add_error('debit_amount', 'Debit amount is required for a debit transaction.')
        #         cleaned_data['credit_amount'] = 0  # Ignore credit for Debit transactions

        #     elif transaction_cat == 'Credit':
        #         if credit_amount is None or credit_amount == 0:
        #             self.add_error('credit_amount', 'Credit amount is required for a credit transaction.')
        #         cleaned_data['debit_amount'] = 0  # Ignore debit for Credit transactions

        #     return cleaned_data
        
        # def __init__(self,*args, **kwargs):
        #     user = kwargs.pop('user',None)
        #     super(JournalEntryForm,self).__init__(*args, **kwargs)
        #     if user:
        #         unit = user.user_roles.unit
        #     self.fields['debit_account'].queryset= Account_Chart.objects.filter(unit=unit)
        #     self.fields['credit_account'].queryset= Account_Chart.objects.filter(unit=unit)
    
        
JournalEntryFormSet = modelformset_factory( Inv_Transaction,form=JournalEntryForm, extra=2 )



      

    # Optional: Add validation for amount to prevent negative numbers
        

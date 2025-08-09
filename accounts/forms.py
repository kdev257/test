from django import forms
from accounts.models import Unit,Transaction_Type,Inv_Transaction
from django.forms import modelformset_factory
from masters.models import User,User_Roles,AccountingYear,UnitAccountBalance,Account_Chart
from django.forms.models import inlineformset_factory
from decimal import Decimal

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
        
JournalEntryFormSet = modelformset_factory( Inv_Transaction,form=JournalEntryForm, extra=2 )

class DateRangeForm(forms.Form):    
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(),widget=forms.Select(attrs={'class': 'form-control', 'style': 'height: 50px;'}),required=False,help_text='Pls leave blank to select all units')
    accounting_year = forms.ModelChoiceField(queryset=AccountingYear.objects.all(),widget=forms.Select(attrs={'class': 'form-control', 'style': 'height: 50px;'}),required=False,help_text='Pls Select the Accounting Year')
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'style': 'height: 50px;'}),)
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'style': 'height: 50px;'}),)
    
# Transaction Form
class SelectBankForm(forms.Form):
    account_chart = forms.ModelChoiceField(
        queryset=Account_Chart.objects.filter(sub_category=26),
        label="Select Bank Account",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class BankPaymentForm(forms.ModelForm):
    account_chart = forms.ModelChoiceField(
        queryset=Account_Chart.objects.filter(sub_category=26),
        label="Select Bank Account",
        widget=forms.Select(attrs={'class': 'form-control'})
        )
    transaction_amount = forms.DecimalField(
        # label="Transaction Amount",
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Amount'})
    )
    other_account = forms.ModelChoiceField(
        queryset=Account_Chart.objects.filter(sub_category__category=4),
        label="Select Account",
        widget=forms.Select(attrs={'class': 'form-control'})    
    )     
            
    
    class Meta:
        model = Inv_Transaction
        exclude = ['transaction_number', 'transaction_date', 'credit_amount']


class BankReceiptForm(forms.ModelForm):
    account_chart = forms.ModelChoiceField(
        queryset=Account_Chart.objects.filter(sub_category=26),
        label="Select Bank Account",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    transaction_amount = forms.DecimalField(
        label="Transaction Amount",
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Amount'})
    )
    other_account = forms.ModelChoiceField(
        queryset=Account_Chart.objects.filter(sub_category=22),
        label="Select Account",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    credit_amount = forms.DecimalField(label="credit_amount", max_digits=12, decimal_places=2)
    reference = forms.CharField(label="Narration", required=False, widget=forms.Textarea(attrs={'rows': 1}))

    unit = forms.ModelChoiceField(
    queryset=Unit.objects.all(),
    label="Select Unit",
    widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Inv_Transaction
        exclude = ['transaction_number', 'transaction_date', 'debit_amount']

    
class Journal_Entry_New_Form(forms.ModelForm):
    class Meta:
        model = Inv_Transaction
        fields = 'transaction_type', 'unit'
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(id=24)

class Journal_Entry_debit_Detail_Form(forms.ModelForm):
    class Meta:
        model = Inv_Transaction
        fields = 'transaction_cat', 'account_chart', 'debit_amount', 'reference'
        widgets = {
            'transaction_cat': forms.Select(attrs={'class': 'form-control'}),
            'account_chart': forms.Select(attrs={'class': 'form-control'}),
            'debit_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
        }
    

class Journal_Entry_credit_Detail_Form(forms.ModelForm):
    class Meta:
        model = Inv_Transaction
        fields = 'transaction_cat', 'account_chart', 'credit_amount', 'reference'
        widgets = {
            'transaction_cat': forms.Select(attrs={'class': 'form-control'}),
            'account_chart': forms.Select(attrs={'class': 'form-control'}),
            'credit_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
        }
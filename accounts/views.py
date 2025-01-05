from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Inv_Transaction, Account_Chart
from django.db import transaction as db_transaction
from inventory.functions import generate_document_number,generate_transaction_no,update_account_chart
from .forms import JournalEntryFormSet
from masters.models import Transaction_Type,Unit
from masters.models import User,User_Roles
from django.forms import modelformset_factory
from masters.models import User,User_Roles
from .forms import JournalEntryFormSet,JournalEntryForm  # Import both forms
from django.db import transaction as db_transaction

def create_journal_entry(request):   
    if request.method == 'POST':
        formset = JournalEntryFormSet(request.POST)
        
        if formset.is_valid():
            total_debit = 0
            total_credit = 0
            unit = None
            

            # First loop to calculate total debit and credit
            for form in formset:
                cleaned_data = form.cleaned_data
                transaction_type = cleaned_data.get('transaction_type')  # Assuming same for all rows
                unit = cleaned_data.get('unit')  # Assuming same for all rows
                
                debit_amount = cleaned_data.get('debit_amount', 0)
                credit_amount = cleaned_data.get('credit_amount', 0)

                total_debit += debit_amount
                total_credit += credit_amount

            # Now check if totals match
            if total_debit != total_credit:
                print(f"Error: Total Debit ({total_debit}) does not match Total Credit ({total_credit}).")
                formset.add_error(None, "Total debit and credit amounts do not match.")
            else:
                # Proceed with transaction creation since totals match
                transaction_number = generate_document_number(model_class= Inv_Transaction,unit=unit, transaction_type=transaction_type,number_field='transaction_number')
                
                
                with db_transaction.atomic():
                    for form in formset:
                        cleaned_data = form.cleaned_data
                        account_chart = cleaned_data['account_chart']
                        debit_amount = cleaned_data['debit_amount'] or 0  # Default to 0 if None
                        credit_amount = cleaned_data['credit_amount'] or 0  # Default to 0 if None
                        reference = cleaned_data['reference']

                        if debit_amount > 0:  # Ensure only positive debit amounts are considered
                            Inv_Transaction.objects.create(
                                transaction_number=transaction_number,
                                transaction_type=transaction_type,  # Use the debit_type instance
                                transaction_cat=cleaned_data['transaction_cat'],
                                unit=unit,
                                account_chart=account_chart,  # Assuming account_chart is passed as instance
                                debit_amount=debit_amount,
                                credit_amount=0,
                                reference=reference
                            )
                            messages.success(request,f"Created debit entry: {debit_amount} for account: {account_chart}")
                            update_account_chart(id=account_chart,debit_amount=debit_amount,credit_amount=credit_amount)
                        
                        if credit_amount > 0:  # Ensure only positive credit amounts are considered
                            Inv_Transaction.objects.create(
                                transaction_number=transaction_number,
                                transaction_type=transaction_type,  # Use the credit_type instance
                                transaction_cat=cleaned_data['transaction_cat'],
                                unit=unit,
                                account_chart=account_chart,  # Assuming account_chart is passed as instance
                                credit_amount=credit_amount,
                                debit_amount=0,
                                reference=reference
                            )                       
                            
                            messages.success(request,f"Created credit entry: {credit_amount} for account: {account_chart}")
                            update_account_chart(id=account_chart,debit_amount=debit_amount,credit_amount=credit_amount)
                        
                
                return redirect('journal_entry')  # Adjust to your needs

        else:            
            print('Formset errors:', formset.errors)
    
    else:    
        formset = JournalEntryFormSet(queryset=Inv_Transaction.objects.none())  # Empty formset for journal entries

    return render(request, 'accounts/forms/create_journal_entry.html', { 'formset': formset})





 
    



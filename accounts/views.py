from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import now ,timedelta
from .models import Inv_Transaction
from django.db import transaction as db_transaction
from inventory.functions import generate_document_number,update_account_chart
from .forms import JournalEntryFormSet
from masters.models import Transaction_Type,Unit,AccountingYear,UnitAccountBalance,Account_Chart
from masters.models import User,User_Roles
from django.forms import modelformset_factory
from masters.models import User,User_Roles
from .forms import JournalEntryFormSet,JournalEntryForm,BankPaymentForm,BankReceiptForm,Journal_Entry_New_Form,Journal_Entry_debit_Detail_Form, Journal_Entry_credit_Detail_Form
from django.db import transaction as db_transaction
from django.db.models import Sum, F
from .forms import DateRangeForm
from icecream import ic
from decimal import Decimal



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
                            update_account_chart(id=account_chart.id,debit_amount=debit_amount,credit_amount=credit_amount)
                        
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
                            update_account_chart(id=account_chart.id,debit_amount=debit_amount,credit_amount=credit_amount)
                        
                
                return redirect('journal_entry')  # Adjust to your needs

        else:            
            print('Formset errors:', formset.errors)
    
    else:    
        formset = JournalEntryFormSet(queryset=Inv_Transaction.objects.none())  # Empty formset for journal entries

    return render(request, 'accounts/forms/create_journal_entry.html', { 'formset': formset})



# from django.db.models import Sum
# from django.utils import timezone
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .models import Inv_Transaction, 
# UnitAccountBalance, AccountingYear, Account_Chart
# from .forms import DateRangeForm  # assumes year & unit are in form


def update_account_chart_orm(request):
    if request.method == 'POST':
        form = DateRangeForm(request.POST)  # Remove start/end date fields from this form
        if form.is_valid():
            unit = form.cleaned_data['unit']
            accounting_year = form.cleaned_data['accounting_year']

            start_date = accounting_year.start_date
            end_date = accounting_year.end_date
            prev_day = start_date - timedelta(days=1)

            aggregated_data = Inv_Transaction.objects.filter(
                unit=unit,
                transaction_date__range=(start_date, end_date)
            ).values('account_chart').annotate(
                total_debit=Sum('debit_amount'),
                total_credit=Sum('credit_amount')
            ).order_by('account_chart')

            for data in aggregated_data:
                account_id = data['account_chart']
                total_debit = data['total_debit'] or 0
                total_credit = data['total_credit'] or 0

                account = Account_Chart.objects.get(id=account_id)

                # Get opening from previous year’s closing (if any)
                prev_balance = UnitAccountBalance.objects.filter(
                    account_chart=account,
                    unit=unit,
                    closing_balance_date=prev_day
                ).first()

                opening_balance = prev_balance.closing_balance if prev_balance else account.opening_balance

                closing_balance = opening_balance + total_debit - total_credit

                UnitAccountBalance.objects.update_or_create(
                    account_chart=account,
                    unit=unit,
                    year=accounting_year,
                    defaults={
                        'opening_balance': opening_balance,
                        'debit_amount': total_debit,
                        'credit_amount': total_credit,
                        'closing_balance': closing_balance,
                    }
                )

            messages.success(request, 'Unit-wise yearly balances updated successfully.')
            return redirect('employee_profile')
    else:
        form = DateRangeForm()  # Only include 'unit' and 'accounting_year'

    return render(request, 'accounts/forms/update_account_chart_orm.html', {'form': form})

# # from decimal import Decimal

# def update_unit_account_balance(unit, accounting_year):
#     # Get previous year
#     previous_year = AccountingYear.objects.filter(end_date__lt=accounting_year.start_date).order_by('-end_date').first()
#     if not previous_year:
#         return  # No carry-forward possible

#     # Get profit & loss account
#     pnl_account = Account_Chart.objects.get(name="Profit and Loss Account")  # or use some flag or code

#     # Totals
#     total_income = Decimal(0)
#     total_expenditure = Decimal(0)

#     # Loop through all previous balances
#     previous_balances = UnitAccountBalance.objects.filter(unit=unit, year=previous_year)

#     for bal in previous_balances:
#         account_class = bal.account_chart.sub_category.category.sub_class.account_class

#         if account_class in ['Asset', 'Liability']:
#             # Carry forward to new year
#             UnitAccountBalance.objects.update_or_create(
#                 unit=unit,
#                 year=accounting_year,
#                 account_chart=bal.account_chart,
#                 defaults={
#                     'opening_balance': bal.closing_balance,
#                     'debit_amount': Decimal(0),
#                     'credit_amount': Decimal(0),
#                     'closing_balance': bal.closing_balance,  # will be updated later
#                     'opening_balance_date': accounting_year.start_date,
#                     'closing_balance_date': accounting_year.end_date,
#                 }
#             )
#         elif account_class == 'Income':
#             total_income += bal.closing_balance
#         elif account_class == 'Expenditure':
#             total_expenditure += bal.closing_balance

#     # Calculate profit or loss
#     profit_or_loss = total_income - total_expenditure

#     # Post it to P&L Account
#     UnitAccountBalance.objects.update_or_create(
#         unit=unit,
#         year=accounting_year,
#         account_chart=pnl_account,
#         defaults={
#             'opening_balance': profit_or_loss,
#             'debit_amount': Decimal(0),
#             'credit_amount': Decimal(0),
#             'closing_balance': profit_or_loss,
#             'opening_balance_date': accounting_year.start_date,
#             'closing_balance_date': accounting_year.end_date,
#         }
#     )

# from django.db.models import Sum
# from django.utils.timezone import now
# from django.contrib import messages
# from django.shortcuts import render, redirect
# from .models import Inv_Transaction, UnitAccountBalance, AccountingYear, Account_Chart
# from accounts.models import Account_Class  # adjust import as needed

# def update_unit_account_balance(request):
#     if request.method == 'POST':
#         year_id = request.POST.get('year')
#         unit_id = request.POST.get('unit')

#         try:
#             year = AccountingYear.objects.get(id=year_id)
#             unit = Unit.objects.get(id=unit_id)
#         except (AccountingYear.DoesNotExist, Unit.DoesNotExist):
#             messages.error(request, "Invalid Unit or Year selected.")
#             return redirect('some_form_view')

#         start_date = year.start_date
#         end_date = year.end_date
#         opening_balance_date = start_date
#         closing_balance_date = end_date

#         # Aggregate debit and credit from transactions for this unit & year
#         transactions = Inv_Transaction.objects.filter(
#             unit=unit,
#             transaction_date__range=(start_date, end_date)
#         ).values('account_chart').annotate(
#             total_debit=Sum('debit_amount') or 0,
#             total_credit=Sum('credit_amount') or 0
#         )

#         total_income = 0
#         total_expenditure = 0

#         for data in transactions:
#             account_id = data['account_chart']
#             total_debit = data['total_debit'] or 0
#             total_credit = data['total_credit'] or 0

#             try:
#                 account = Account_Chart.objects.get(id=account_id)
#             except Account_Chart.DoesNotExist:
#                 continue

#             account_class = account.account_sub_class.category.account_class.name

#             # Determine opening balance only for Asset or Liability
#             if account_class in ['Asset', 'Liability']:
#                 try:
#                     # Get previous year's closing balance as opening
#                     prev_year = AccountingYear.objects.filter(
#                         end_date__lt=start_date
#                     ).order_by('-end_date').first()

#                     opening_balance = UnitAccountBalance.objects.get(
#                         unit=unit,
#                         account_chart=account,
#                         year=prev_year
#                     ).closing_balance
#                 except:
#                     opening_balance = 0
#             else:
#                 opening_balance = 0  # No carry forward for income/expenditure

#             closing_balance = opening_balance + total_debit - total_credit

#             # Save or update UnitAccountBalance
#             UnitAccountBalance.objects.update_or_create(
#                 account_chart=account,
#                 unit=unit,
#                 year=year,
#                 defaults={
#                     'opening_balance': opening_balance,
#                     'debit_amount': total_debit,
#                     'credit_amount': total_credit,
#                     'closing_balance': closing_balance,
#                     'opening_balance_date': opening_balance_date,
#                     'closing_balance_date': closing_balance_date,
#                     'last_updated': now()
#                 }
#             )

#             # Accumulate for P&L calculation
#             if account_class == 'Expenditure':
#                 total_expenditure += total_debit - total_credit
#             elif account_class == 'Income':
#                 total_income += total_credit - total_debit

#         # Transfer net profit/loss to P&L account
#         net_profit = total_income - total_expenditure
#         try:
#             profit_loss_account = Account_Chart.objects.get(name__icontains="profit and loss")
#         except Account_Chart.DoesNotExist:
#             messages.warning(request, "Profit and Loss Account not found. Please create it.")
#             return redirect('some_form_view')

#         UnitAccountBalance.objects.update_or_create(
#             account_chart=profit_loss_account,
#             unit=unit,
#             year=year,
#             defaults={
#                 'opening_balance': 0,
#                 'debit_amount': 0,
#                 'credit_amount': 0,
#                 'closing_balance': net_profit,
#                 'opening_balance_date': opening_balance_date,
#                 'closing_balance_date': closing_balance_date,
#                 'last_updated': now()
#             }
#         )

#         messages.success(request, "Unit account balances updated successfully.")
#         return redirect('employee_profile')

#     # GET request: Render form
#     context = {
#         'units': Unit.objects.all(),
#         'years': AccountingYear.objects.all()
#     }
#     return render(request, 'accounts/forms/update_unit_account_balance.html', context)
    
    
def bank_payment_view(request):
    if request.method == "POST":
        transaction_type = Transaction_Type.objects.get(id=22)
        unit = request.user.user_roles.unit
        transaction_number = generate_document_number(
            model_class=Inv_Transaction,
            transaction_type=transaction_type,
            unit = unit,
            number_field='transaction_number'
        )     
        form = BankPaymentForm(request.POST)
        if form.is_valid():  
            transaction_amount= form.cleaned_data['transaction_amount']          
            debit_amounts = request.POST.getlist("debit_amount")
            account_ids = request.POST.getlist("other_account")

            total_debit = sum(float(amount) for amount in debit_amounts if amount)
            
            if total_debit != transaction_amount:
                messages.error(request, "Total debit amount must match the transaction amount.")
                return render(request, "accounts/forms/bank_payment_form.html", {"form": form})

            # Get selected bank account
            bank_account = form.cleaned_data["account_chart"]
            reference = form.cleaned_data["reference"]
            # unit = form.cleaned_data["unit"]
            # transaction_type = form.cleaned_data["transaction_type"]

            # Create a credit entry for the bank
            bank_transaction = Inv_Transaction(
                transaction_type=transaction_type,
                transaction_number=transaction_number,
                transaction_cat="Credit",
                transaction_date=now(),
                unit=unit,
                account_chart=bank_account,
                credit_amount=transaction_amount,
                reference=reference,
                approved=False
            )
            bank_transaction.save()
            # update_account_chart(id=bank_account.id,debit_amount=0,credit_amount=transaction_amount)

            # Create a debit entry for each selected account
            for index, account_id in enumerate(account_ids):
                account = Account_Chart.objects.get(id=account_id)               
                vendor_transaction=Inv_Transaction(
                    transaction_type=transaction_type,
                    transaction_number=transaction_number,
                    transaction_cat="Debit",
                    transaction_date=now(),
                    unit=unit,
                    account_chart=account,
                    debit_amount=float(debit_amounts[index]),
                    reference=reference,
                    approved=False
                )
                vendor_transaction.save()
                update_account_chart(
                    id=account.id, 
                    debit_amount=Decimal(debit_amounts[index]), 
                    credit_amount=0
                )
                
            messages.success(request, "Transaction saved successfully.")
            return redirect("employee_profile")  # Change to the correct redirect URL
        else:
            print(form.errors)

    else:
        form = BankPaymentForm()

    return render(request, "accounts/forms/bank_payment_form.html", {"form": form})


def bank_receipt_view(request):
    if request.method == "POST":
        transaction_type = Transaction_Type.objects.get(id=23)
        unit = request.user.user_roles.unit
        transaction_number = generate_document_number(
            model_class=Inv_Transaction,
            transaction_type=transaction_type,
            unit = unit,
            number_field='transaction_number'
        )     
        form = BankReceiptForm(request.POST)
        if form.is_valid():  
            transaction_amount= form.cleaned_data['transaction_amount']          
            credit_amount = request.POST.getlist("credit_amount")
            account_ids = request.POST.getlist("other_account")

            total_credit = sum(float(amount) for amount in credit_amount if amount)
            
            if total_credit != transaction_amount:
                messages.error(request, "Total debit amount must match the transaction amount.")
                return render(request, "accounts/forms/bank_payment_form.html", {"form": form})

            # Get selected bank account
            bank_account = form.cleaned_data["account_chart"]
            reference = form.cleaned_data["reference"]
            # unit = form.cleaned_data["unit"]
            # transaction_type = form.cleaned_data["transaction_type"]

            # Create a credit entry for the bank
            bank_transaction = Inv_Transaction(
                transaction_type=transaction_type,
                transaction_number=transaction_number,
                transaction_cat="Debit",
                transaction_date=now(),
                unit=unit,
                account_chart=bank_account,
                debit_amount=transaction_amount,
                reference=reference,
                approved=False
            )
            bank_transaction.save()
            update_account_chart(id=bank_account.id,debit_amount=transaction_amount,credit_amount=0)

            # Create a credit entry for each selected account
            for index, account_id in enumerate(account_ids):
                account = Account_Chart.objects.get(id=account_id)               
                vendor_transaction=Inv_Transaction(
                    transaction_type=transaction_type,
                    transaction_number=transaction_number,
                    transaction_cat="Credit",
                    transaction_date=now(),
                    unit=unit,
                    account_chart=account,
                    credit_amount=float(credit_amount[index]),
                    reference=reference,
                    approved=False
                )
                vendor_transaction.save()
                update_account_chart(
                    id=account.id, 
                    debit_amount= 0,
                    credit_amount=Decimal(credit_amount[index])
                )
                
            messages.success(request, "Transaction saved successfully.")
            return redirect("employee_profile")  # Change to the correct redirect URL
        else:
            print(form.errors)

    else:
        form = BankReceiptForm()

    return render(request, "accounts/forms/bank_receipt_form.html", {"form": form})

def journal_entry_view(request):
    DebitFormSet = modelformset_factory(
        Inv_Transaction, form=Journal_Entry_debit_Detail_Form, extra=1, can_delete=True
    )
    CreditFormSet = modelformset_factory(
        Inv_Transaction, form=Journal_Entry_credit_Detail_Form, extra=1, can_delete=True
    )

    if request.method == 'POST':
        header_form = Journal_Entry_New_Form(request.POST)
        debit_formset = DebitFormSet(request.POST, prefix='debit')
        credit_formset = CreditFormSet(request.POST, prefix='credit')

        if header_form.is_valid() and debit_formset.is_valid() and credit_formset.is_valid():
            transaction_type = header_form.cleaned_data['transaction_type']
            unit = header_form.cleaned_data['unit']
            transaction_date = timezone.now()
            transaction_number = generate_document_number(
                model_class=Inv_Transaction,
                transaction_type=transaction_type,
                unit=unit,
                number_field='transaction_number'
            )

            for form in debit_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    Inv_Transaction.objects.create(
                        transaction_number=transaction_number,
                        transaction_type=transaction_type,
                        transaction_date=transaction_date,
                        transaction_cat=form.cleaned_data['transaction_cat'],
                        unit=unit,
                        account_chart=form.cleaned_data['account_chart'],
                        debit_amount=form.cleaned_data['debit_amount'],
                        credit_amount=0,
                        reference=form.cleaned_data['reference']
                    )

            for form in credit_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    Inv_Transaction.objects.create(
                        transaction_number=transaction_number,
                        transaction_type=transaction_type,
                        transaction_date=transaction_date,
                        transaction_cat=form.cleaned_data['transaction_cat'],
                        unit=unit,
                        account_chart=form.cleaned_data['account_chart'],
                        debit_amount=0,
                        credit_amount=form.cleaned_data['credit_amount'],
                        reference=form.cleaned_data['reference']
                    )

            messages.success(request, "Journal entry saved successfully.")
            return redirect('journal_entry')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        header_form = Journal_Entry_New_Form()
        debit_formset = DebitFormSet(queryset=Inv_Transaction.objects.none(), prefix='debit')
        credit_formset = CreditFormSet(queryset=Inv_Transaction.objects.none(), prefix='credit')

    return render(request, 'accounts/forms/journal_entry_form_new.html', {
        'header_form': header_form,
        'debit_formset': debit_formset,
        'credit_formset': credit_formset,
    })

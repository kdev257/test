from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from masters.models import Currency,Supplier_Profile,Account_Chart
from accounts.models import Inv_Transaction
from inventory.functions import calculate_tax, assign_approver,gst_on_service,assign_approver_services, update_account_chart,calculate_tds
from .forms import *
from inventory.forms import AddItemForm
from django.forms import modelformset_factory
from icecream import ic
import logging
logger = logging.getLogger(__name__)
from django.db import transaction as db_transaction
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.contrib import messages
from decimal import Decimal
from django.db.models import Sum, F, Q
import logging
# Create your views here.


# -------- Service Quotation Views --------

def service_quotation_list(request):
    quotations = Service_Quotation.objects.filter(Q(created_by=request.user) | Q(approver=request.user)).order_by('-created')
    return render(request, 'service/quotation_list.html', {'quotations': quotations})

def service_quotation_create(request):    
    if request.method == 'POST':
        with db_transaction.atomic():
            try:
                form = ServiceQuotationForm(request.POST)        
                if form.is_valid():
                    instance =form.save(commit=False)
                    instance.created_by = request.user
                    instance.save()
                    return redirect('service_quotation_items', pk=instance.pk)
            except Exception as e:
                db_transaction.rollback()                           
                form.add_error(None, "An error occurred while saving the quotation. Please try again.")
                raise e
    else:
        form = ServiceQuotationForm()
    return render(request, 'service/quotation_form.html', {'form': form})


def service_quotation_items(request, pk):
    # Retrieve the Quotation instance
    quotation_instance = get_object_or_404(Service_Quotation, pk=pk)
    cost_center = quotation_instance.supplier.sp_user.cost_center    
    if request.method == 'POST':        
        try:
            with db_transaction.atomic():
                form = ServiceQuotationItemForm(request.POST)
                decision_form = AddItemForm(request.POST)
                if form.is_valid() and decision_form.is_valid():
                # Extract data from form
                    service = form.cleaned_data['service']
                    quantity = form.cleaned_data['quantity']
                    unit_rate = form.cleaned_data['rate']
                    currency =quotation_instance.currency
                    # Calculate and save the instance
                    instance = form.save(commit=False)
                    instance.quotation = quotation_instance  # Link to the quotation
                    instance.amount = Decimal(round(quantity * unit_rate, 2))
                    rate = Currency.objects.get(id=currency.id)
                    if rate is not None:
                        conversion_rate = rate.conversion_rate
                        instance.inr_amount = round(instance.amount * conversion_rate, 2)
                    else:
                        raise ValueError("Conversion rate not found for the given currency and date.")
                    instance.save()
                    
                    # Process the decision form
                    response = decision_form.cleaned_data['add_item']
                    if response == 'yes':
                        return redirect('service_quotation_items', pk=quotation_instance.pk)
                    else:
                        #update the quotation instance                                        
                        quotation_amount=Service_Quotation_Items.objects.filter(quotation=quotation_instance.id).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
                        quotation_inr_amount=Service_Quotation_Items.objects.filter(quotation=quotation_instance.id).aggregate(total_inr_amount=Sum('inr_amount'))['total_inr_amount'] or 0
                        Service_Quotation.objects.filter(id=quotation_instance.id).update(amount=quotation_amount)
                        Service_Quotation.objects.filter(id=quotation_instance.id).update(inr_amount=quotation_inr_amount)
                        assign_approver = assign_approver_services(
                            transaction_type=quotation_instance.transaction_type,
                            inr_value=quotation_inr_amount,
                            unit=quotation_instance.unit,
                            cost_center=cost_center
                        )
                        ic(assign_approver)
                        Service_Quotation.objects.filter(id=quotation_instance.id).update(approver=assign_approver)
                        return redirect('view_supplier_profile')
                    
        except Exception as e:
            messages.error(request,{e})
    else:
        form = ServiceQuotationItemForm()
        decision_form = AddItemForm()

    return render(request, 'service/service_quotation_items_form.html', {'form': form, 'decision_form': decision_form, 'quotation': quotation_instance})


def service_quotation_update(request, pk):
    quotation = get_object_or_404(Service_Quotation, pk=pk)
    if request.method == 'POST':
        form = ServiceQuotationForm(request.POST, instance=quotation)
        if form.is_valid():
            form.save()
            return redirect('service_quotation_list')
    else:
        form = ServiceQuotationForm(instance=quotation)
    return render(request, 'service/quotation_form.html', {'form': form})

def service_quotation_delete(request, pk):
    quotation = get_object_or_404(Service_Quotation, pk=pk)
    if request.method == 'POST':
        quotation.delete()
        return redirect('service_quotation_list')
    return render(request, 'service/quotation_confirm_delete.html', {'quotation': quotation})

def service_quotation_approve(request, pk):    
    quotation = get_object_or_404(Service_Quotation, pk=pk)
    if quotation.approver==request.user:        
        quotation.status = 'Approved'
        quotation.approval_date = timezone.now()
        quotation.save()
        messages.success(request,'Quotation has been Successfully Approved')
        return redirect('employee_profile')
    else:
        messages.error(request,'Sorry... You are not authorized to approve this order')
    return redirect('service_order_list')


# -------- Service Order Views --------

def service_order_list(request):
    orders = Service_Order.objects.filter(Q(created_by=request.user) | Q(approver=request.user))
    return render(request, 'service/order_list.html', {'orders': orders})

def service_order_create(request):
    # quotation = get_object_or_404(Service_Quotation, pk=id)
    
    if request.method == 'POST':
        form = ServiceOrderForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            form.save()
            pk = instance.pk
            return redirect('service_order_items', pk=pk)
    else:
        form = ServiceOrderForm()
    return render(request, 'service/order_form.html', {'form': form})

def service_order_update(request, pk):
    order = get_object_or_404(Service_Order, pk=pk)
    if request.method == 'POST':
        form = ServiceOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('service_order_list')
    else:
        form = ServiceOrderForm(instance=order)
    return render(request, 'service/order_form.html', {'form': form})

def service_order_delete(request, pk):
    order = get_object_or_404(Service_Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('service_order_list')
    return render(request, 'service/confirm_delete_order.html', {'order': order})
 
def service_order_approve(request, pk):    
    order = get_object_or_404(Service_Order, pk=pk)
    if order.approver==request.user:        
        order.status = 'Approved'
        order.save()
        messages.success(request,'Order has been Successfully Approved')
        return redirect('employee_profile')
    else:
        messages.error(request,'Sorry... You are not authorized to approve this order')
    return redirect('service_order_list')
    
def service_order_items(request,pk):
    '''This View is used to add items to the purchase order'''    
    purchase_order_instance= Service_Order.objects.get(id=pk)
    items = Service_Quotation_Items.objects.filter(quotation=purchase_order_instance.quotation)    
    QuotationItemFormSet = modelformset_factory(Service_Quotation_Items,form=ServiceQuotationItemForm,extra=0)
    if request.method == 'POST':
        formset = QuotationItemFormSet(request.POST, queryset=items)    
        if formset.is_valid():
            try:
                with db_transaction.atomic():
                    cgst=sgst=igst=0                    
                    for form, item in zip(formset, items):                        
                        po_quantity = form.cleaned_data.get('po_quantity')

                        #  Skip if no quantity is provided
                        if not po_quantity or po_quantity == 0:
                            continue

                        # it.balance_quantity -= po_quantity
                        # it.quotation.balance_quantity -= po_quantity
                        item.save() 
                        item.quotation.save()

                        purchase_order = Service_Order.objects.select_for_update().filter(quotation=item.quotation.id).last()
                        # purchase_order.quantity += Decimal(po_quantity)
                        profile = Supplier_Profile.objects.select_related('user').get(user=purchase_order.quotation.supplier.id)
                        supplier_state = profile.state
                        rate = item.rate
                        service = item.service
                        value = po_quantity * rate
                        cost_center = purchase_order.sub_cost_center
                        
                        conversion_rate = item.quotation.currency.conversion_rate
                        inr_amount = value * conversion_rate
                        
                        # quotation_item = Service.objects.get(id=it.service.id)

                        tax = gst_on_service(
                            po =purchase_order,
                            service=service,
                            value=inr_amount,
                            supplier_state=supplier_state,
                        )
                                                    

                        cgst, sgst, igst =  tax['CGST'], tax['SGST'], tax['IGST']
                        creditable = tax['creditable']
                        tax_amount = cgst + sgst + igst
                        purchase_order.tax += tax_amount
                        ic(cgst, sgst, igst, tax_amount)
                        # purchase_order.amount += value
                        # purchase_order.inr_amount += inr_amount
                        # purchase_order.save()
                        # Use select_related to update the related quotation status efficiently
                        purchase_order = Service_Order.objects.select_related('quotation').get(id=purchase_order.id)
                        purchase_order.quotation.status = 'Closed'
                        purchase_order.amount += value
                        purchase_order.inr_amount += inr_amount
                        purchase_order.tax += tax_amount
                        purchase_order.quotation.save()
                        purchase_order.save()

                        purchase_order.save()

                        instance = Service_Order_Items(
                            service_order=purchase_order,
                            service = item.service,
                            quantity=po_quantity,
                            rate=rate,
                            amount = value,
                            cgst=cgst,
                            sgst=sgst,
                            igst=igst,
                            # creditable=creditable
                        )
                        instance.save()
                    
                        

                    purchase_order.approver=assign_approver_services(transaction_type=purchase_order.transaction_type,cost_center=cost_center,inr_value=purchase_order.inr_amount,unit=purchase_order.unit)
                    purchase_order.save()
                    messages.success(request,'Purchase Order Saved Successfully')
                    return redirect('employee_profile')
                    
            except Exception as e:
                db_transaction.set(rollback=True)  # Rollback transaction in case of error
                messages.error(request,e)
        else:
            messages.error(request,'Formset is invalid')
            print(formset.errors)
    else:
        formset = QuotationItemFormSet(queryset=items)
    return render(request, 'service/service_order_item_form.html', {
       'formset': formset})

def service_order_dashboard(request):
    total_orders = Service_Order.objects.filter(created_by=request.user).count()
    pending_orders = Service_Order.objects.filter(status='Pending',created_by=request.user).count()
    approved_orders = Service_Order.objects.filter(status='Approved').count()
    closed_orders = Service_Order.objects.filter(status='Closed').count()
    context= {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'approved_orders': approved_orders,
        'closed_orders': closed_orders
    }

    return render(request, 'service/dashboard.html',context)



# -------- Service Invoice Views --------

def service_invoice_list(request):
    invoices = Service_Invoice.objects.all()
    return render(request, 'service/invoice_list.html', {'invoices': invoices})



def service_order_completion_status(request, pk):
    order = get_object_or_404(Service_Order, id=pk)
    if order.status == 'Approved':
        items = Service_Order_Items.objects.filter(service_order=order.id)
        for item in items:
            description = item.service_order.quotation.quotation_items.all().values_list('service_description', flat=True).first()

        ServiceOrderItemFormSet = modelformset_factory(
        Service_Order_Items,
        form=Service_Order_Items_Completion_Status_Form,
        extra=0
        )

        if request.method == 'POST':
            formset = ServiceOrderItemFormSet(request.POST, queryset=items)

            if formset.is_valid():
                try:
                    with db_transaction.atomic():
                        for form in formset:
                            item = form.save(commit=False)  # Get unsaved instance
                        
                            # Optional: Add or override fields manually
                            item.updated_by = request.user
                            
                        # Optional: Auto-calculate status
                            if item.completion_percentage >= 100:
                                item.status = 'Completed'
                            elif item.completion_percentage > 0:
                                item.status = 'In Progress'
                            else:
                                item.status = 'Pending'

                            item.save()
                            Service_Order.objects.filter(id=pk).update(status='Completed')                    
                        messages.success(request, "Service order items updated successfully.")
                        return redirect('service_order_list')                
                except Exception as e:
                    messages.error(request, f"An error occurred: {e}")
                    logger.error(f"Error while processing service order completion status: {e}")
                    raise db_transaction.TransactionManagementError(f"Rolling back due to exception: {e}")
             
            else:
                messages.error(request, "Formset is invalid. Please correct the errors.")
                logger.error(f"Formset errors: {formset.errors}")
                print(formset.errors)
        else:
            formset = ServiceOrderItemFormSet(queryset=items)

        return render(request, 'service/order_completion_status_form.html', {
            'formset': formset,
            'order': order,
            'description': description
           
        })
    else:
        messages.error(request, "This order is not in an 'Approved' state and cannot be updated.")
        return redirect('service_order_list')
    

def service_invoice(request):
    if request.method == 'POST':
        form = ServiceInvoiceForm(request.POST)
        if form.is_valid():            
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            messages.success(request, "Invoice created successfully.")
            return redirect('service_invoice_create', id=invoice.service_order.id)
    else:
        form = ServiceInvoiceForm() 
    return render(request, 'service/invoice_form.html', {'form': form})

def service_invoice_create(request, id):    
    order = get_object_or_404(Service_Order, pk=id)
    items = Service_Order_Items.objects.filter(Q(service_order=order) & Q(service_invoice__isnull=True))
    service_invoice = Service_Invoice.objects.filter(service_order=order).last()
    if not service_invoice:
        messages.error(request, "No invoice found for this service order.")
        return redirect('orders/')    
    # Initialize totals
    total_amount = 0
    total_inr = 0
    total_cgst = 0
    total_sgst = 0
    total_igst = 0
        

    ServiceOrderFormSet = modelformset_factory(
        Service_Order_Items,
        form=ServiceOrderItemForm,
        extra=0
    )

    if request.method == 'POST':        
        formset = ServiceOrderFormSet(request.POST, queryset=items)
        if formset.is_valid():
            # try:
                with db_transaction.atomic():                    
                    creditable = False                    
                    for form,item in zip(formset, items):                        
                        invoice_quantity = form.cleaned_data.get('invoice_quantity')
                        if not invoice_quantity or invoice_quantity == 0:
                            continue
                        rate = item.rate
                        invoice_amount = invoice_quantity * rate
                        invoice_inr_amount = invoice_amount * order.quotation.currency.conversion_rate

                        tax = gst_on_service(
                            po=order,
                            service=item.service,
                            value=invoice_inr_amount,
                            supplier_state=order.quotation.supplier.sp_user.state,
                        )

                        cgst = tax['CGST']
                        sgst = tax['SGST']
                        igst = tax['IGST']
                        creditable = tax['creditable']

                        Service_Invoice_Items.objects.create(
                            service_invoice=service_invoice,
                            service=item.service,
                            quantity=invoice_quantity,
                            rate=rate,
                            amount=invoice_amount,
                            inr_amount=invoice_inr_amount,
                            cgst=cgst,
                            sgst=sgst,
                            igst=igst,
                            updated_by=request.user
                        )

                        total_amount += invoice_amount
                        total_inr += invoice_inr_amount
                        total_cgst += cgst
                        total_sgst += sgst
                        total_igst += igst
                        item.service_invoice=service_invoice # Link items to the invoice
                        item.save()  # Save each item after linking to the invoice

                    service_invoice.invoice_amount = total_amount
                    service_invoice.inr_amount = total_inr
                    service_invoice.cgst = total_cgst
                    service_invoice.sgst = total_sgst
                    service_invoice.igst = total_igst
                    ic(total_igst)                    
                    service_invoice.creditable = creditable
                    service_invoice.save()
                    
                    tds_amount = calculate_tds(supplier=order.quotation.supplier,service_classification= item.service,inr_value= service_invoice.inr_amount)
                    ic(tds_amount)
                    
                    if item.service.payment_mode == 'RCM':                        
                        passed_amount = total_amount
                        debit = total_amount + total_cgst + total_sgst + total_igst
                        
                    else:
                        passed_amount = total_amount + total_cgst + total_sgst + total_igst
                        
                    if passed_amount - service_invoice.invoice_amount < 5:
                        #Create Accounting Entries
                        total_debits=total_credits=0
                        Inv_Transaction.objects.create(
                        transaction_number=service_invoice.transaction_number,
                        transaction_date=service_invoice.transaction_date,
                        transaction_type = service_invoice.transaction_type,
                        transaction_cat = 'Debit',
                        unit = order.unit,
                        debit_amount = debit,
                        credit_amount= 0,
                        account_chart = item.service.account,
                        reference = f"Debit towards supply of service vide invoice {service_invoice.invoice_number} dated {service_invoice.invoice_date}"
                        )
                        update_account_chart(id=item.service.account.id,debit_amount=debit,credit_amount=0)
                        account = service_invoice.service_order.quotation.supplier.account
                        total_debits += debit
                        Inv_Transaction.objects.create(
                        transaction_number=service_invoice.transaction_number,
                        transaction_date=service_invoice.transaction_date,
                        transaction_type = service_invoice.transaction_type,
                        transaction_cat = 'Credit',
                        unit = order.unit,
                        debit_amount = 0,
                        credit_amount= total_amount,
                        account_chart = account,
                        reference = f"credit towards supply of service vide invoice {service_invoice.invoice_number} dated {service_invoice.invoice_date}"
                        )
                        update_account_chart(id=service_invoice.service_order.quotation.supplier.account.id,debit_amount=0,credit_amount=total_amount)
                        total_credits += total_amount
                        if igst > 0:
                            Inv_Transaction.objects.create(
                            transaction_number=service_invoice.transaction_number,
                            transaction_date=service_invoice.transaction_date,
                            transaction_type = service_invoice.transaction_type,
                            transaction_cat = 'Credit',
                            unit = order.unit,
                            debit_amount = 0,
                            credit_amount= total_igst,
                            account_chart = Account_Chart.objects.get(account_name = 'IGST Payable'),
                            reference = f"credit towards supply of service vide invoice {service_invoice.invoice_number} dated {service_invoice.invoice_date}"
                            )
                            update_account_chart(id=Account_Chart.objects.get(account_name = 'IGST Payable').id,debit_amount=0,credit_amount=igst)
                            total_credits += total_igst
                        if cgst > 0:
                            Inv_Transaction.objects.create(
                            transaction_number=service_invoice.transaction_number,
                            transaction_date=service_invoice.transaction_date,
                            transaction_type = service_invoice.transaction_type,
                            transaction_cat = 'Credit',
                            unit = order.unit,
                            debit_amount = 0,
                            credit_amount= total_cgst,
                            account_chart = Account_Chart.objects.get(account_name = 'CGST Payable').id,
                            reference = f"credit towards supply of service vide invoice {service_invoice.invoice_number} dated {service_invoice.invoice_date}"
                            )
                            update_account_chart(id=Account_Chart.objects.get(account_name = 'CGST Payable').id,debit_amount=0,credit_amount=cgst)
                            total_credits += total_cgst
                        if sgst > 0:
                            Inv_Transaction.objects.create(
                            transaction_number=service_invoice.transaction_number,
                            transaction_date=service_invoice.transaction_date,
                            transaction_type = service_invoice.transaction_type,
                            transaction_cat = 'Credit',
                            unit = order.unit,
                            debit_amount = 0,
                            credit_amount= total_sgst,
                            account_chart = Account_Chart.objects.get(account_name = 'SGST Payable').id,
                            reference = f"credit towards supply of service vide invoice {service_invoice.invoice_number} dated {service_invoice.invoice_date}"
                            )
                            update_account_chart(id=Account_Chart.objects.get(account_name = 'SGST Payable').id,debit_amount=0,credit_amount=sgst)
                            total_credits += total_sgst
                            if total_debits != total_credits:
                                messages.error(request, "Total debits and credits do not match. Please check the invoice items.")
                                db_transaction.set(rollback=True)  # Rollback transaction in case of error                  
                                return redirect('service_invoice_create', id=order.id)
                        if tds_amount > 0:
                            Inv_Transaction.objects.create(
                            transaction_number=service_invoice.transaction_number,
                            transaction_date=service_invoice.transaction_date,
                            transaction_type = service_invoice.transaction_type,
                            transaction_cat = 'Credit',
                            unit = order.unit,
                            debit_amount = 0,
                            credit_amount= tds_amount,
                            account_chart = Account_Chart.objects.get(account_name = 'TDS Payable'),
                            reference = f"credit towards TDS on supply of service vide invoice {service_invoice.invoice_number} dated {service_invoice.invoice_date}"
                            )
                            update_account_chart(id=Account_Chart.objects.get(account_name = 'TDS Payable').id,debit_amount=0,credit_amount=tds_amount)
                            #create debit entry for TDS in supplier account
                            Inv_Transaction.objects.create(
                            transaction_number=service_invoice.transaction_number,
                            transaction_date=service_invoice.transaction_date,
                            transaction_type = service_invoice.transaction_type,    
                            transaction_cat = 'Debit',
                            unit = order.unit,      
                            debit_amount = tds_amount,
                            credit_amount= 0,
                            account_chart =account,
                            reference = f"Debit towards TDS on supply of service vide invoice {service_invoice.invoice_number} dated {service_invoice.invoice_date}"
                            )   
                    else:
                        messages.error(request, "Total amount mismatch. Please check the invoice items.")                        
                        return redirect('service_invoice_create', id=order.id)
                        
                    messages.success(request, "Invoice created successfully.")
                    return redirect('service_invoice_list')
                raise db_transaction.TransactionManagementError("Rolling back due to an error in processing invoice items.")
                db.transaction.set(rollback=True)  # Rollback transaction in case of error

            # except Exception as e:
                # messages.error(request, f"An error occurred: {e}")
                
            
        else:
            messages.error(request, "Please correct the errors.")
            print(formset.errors)
    else:
        formset = ServiceOrderFormSet(queryset=items)

    return render(request, 'service/invoice_item_form.html', {
        'formset': formset,
        'order': order
    })
    
def service_invoice_update(request, pk):
    invoice = get_object_or_404(Service_Invoice, pk=pk)
    # set service_invoice field to null in service_order_items
    Service_Order_Items.objects.filter(service_invoice=invoice).update(service_invoice=None)
    if request.method == 'POST':
        form = ServiceInvoiceForm(request.POST, instance=invoice)
        if form.is_valid():            
            return redirect('service_invoice_create', id=invoice.service_order.id)
    else:
        form = ServiceInvoiceForm(instance=invoice)
    return render(request, 'service/invoice_form.html', {'form': form})

def service_invoice_delete(request, pk):
    invoice = get_object_or_404(Service_Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        return redirect('service_invoice_list')
    return render(request, 'service/invoice_confirm_delete.html', {'invoice': invoice})


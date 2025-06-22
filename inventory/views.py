from django.shortcuts import render,get_object_or_404,redirect
from masters.models import Account_Chart,User,User_Roles,DOA,Transaction_Type,State_Excise_taxes_On_Goods,Service,Currency
from .models import Purchase_Order,Material_Receipt_Note,Quality_Check,Gate_Entry,Vehicle_Unloading_Report,Freight_Purchase_Order,Mrn_Items,Receipt_Not_Vouchered
from accounts.models import Inv_Transaction
from django.contrib import messages
from .forms import *
from django.db import transaction as db_transaction
from django.forms import modelformset_factory
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db.models import Sum
from .functions import calculate_custom,calculate_tax,assign_approver,update_account_chart,generate_document_number
from decimal import Decimal
from django.db.models import Q  # Import Q for complex lookups
import logging
logger = logging.getLogger(__name__)
from icecream import ic

# Create your views here.
def index(request):
    return render(request,'inventory/index.html')

@login_required
def add_supplier(request):
    unit = request.user.user_roles.unit  
    if request.method == "POST":
        form = SupplierForm(request.POST, initial={'unit': unit})
        if form.is_valid():
            form.save()
        try:
            # Your code for supplier creation here
            messages.success(request, 'Supplier Created Successfully')
        except Exception as e:
            # Log the exception for debugging
            logger.error(f"Error while creating supplier: {e}")
            # Display the error message to the user
            messages.error(request, f"Something went wrong. Error: {e}")
    else:
        form = SupplierForm( initial={'unit': unit})
    return render(request,'inventory/forms/supplier_form.html',{'form':form})
        
        

@login_required    
def quotation_entry(request):
        if request.method == 'POST': 
            form = QuotationForm(request.POST,user=request.user)
            if form.is_valid():
                transaction_type = form.cleaned_data['transaction_type']                
                instance = form.save(commit=False)                
                instance.unit = request.user.user_roles.unit                          
                instance.created_by= request.user
                
                # Save the instance after an approver is assigned
                instance.save()
            messages.success(request, 'Quotation Entry Successful')
            id = instance.id        
            return redirect('quotation_items',id)

        else:
           form = QuotationForm(user=request.user)
        return render(request,'inventory/forms/1.quotation_entry_form.html',{'form':form})    
    



def quotation_items(request, id):
    # Retrieve the Quotation instance
    quotation_instance = get_object_or_404(Quotation, id=id)

    if request.method == 'POST':
        currend_date = now()
        try:
            with db_transaction.atomic():
                form = QuotationItemsForm(request.POST,user=request.user)
                decision_form = AddItemForm(request.POST)

                if form.is_valid() and decision_form.is_valid():
                # Extract data from form
                    item = form.cleaned_data['item']
                    quantity = form.cleaned_data['quantity']
                    unit_rate = form.cleaned_data['unit_rate']
                    currency =quotation_instance.currency
                    # Calculate and save the instance
                    instance = form.save(commit=False)
                    instance.quotation = quotation_instance  # Link to the quotation
                    instance.value = Decimal(round(quantity * unit_rate, 2))
                    rate = Currency.objects.get(id=currency.id)
                    if rate is not None:
                        conversion_rate = rate.conversion_rate
                        instance.inr_value = round(instance.value * conversion_rate, 2)
                    else:
                        raise ValueError("Conversion rate not found for the given currency and date.")
                    instance.balance_quantity = quantity
                    instance.save()

                    # Process the decision form
                    response = decision_form.cleaned_data['add_item']
                    if response == 'yes':
                        return redirect('quotation_items', id)
                    else:
                        update_quotation(id)
                    return redirect('employee_profile')
        except Exception as e:
            messages.error(request,{e})
    else:
        form = QuotationItemsForm(user=request.user)
        decision_form = AddItemForm()

    return render(request, 'inventory/forms/2.quotation_items_form.html', {'form': form, 'decision_form': decision_form, 'quotation': quotation_instance})


def update_quotation(id):
    quotation_instance = Quotation.objects.get(id=id)
    total_quantity = Quotation_Items.objects.filter(quotation=id).aggregate(sum_quantity =Sum('quantity'))
    total_quantity = total_quantity['sum_quantity']    
    result = Quotation_Items.objects.filter(quotation=id).aggregate(sum_value=Sum('inr_value'))
    total_value = result['sum_value'] if result['sum_value'] is not None else Decimal('0.00')   
    quotation_instance.quotation_value = total_value
    quotation_instance.quotation_quantity=total_quantity
    quotation_instance.balance_quantity = total_quantity
    quotation_instance.save()
    id = quotation_instance.id
    assign_quotation_approver(id)
            
def assign_quotation_approver(id):
    quotation_to_approve = Quotation.objects.get(id=id)
    transaction_type = quotation_to_approve.transaction_type
    inr_value = quotation_to_approve.quotation_value
    unit = quotation_to_approve.unit    
    quotation_to_approve.approver =assign_approver(transaction_type=transaction_type,inr_value=inr_value,unit=unit)
    quotation_to_approve.save()
    
    
    
    



@login_required
def quotation_list(request):
    q_list = Quotation_Items.objects.all()
    return render(request,'inventory/quotation_list.html',{'list':q_list})
 
@login_required
def approve_quotation(request,id):
    to_approve = Quotation.objects.get(id=id)
    to_approve.approved = True
    to_approve.approver=User.objects.get(id=request.user.id)
    to_approve.save()
    return redirect('employee_profile')    

def quotation_pending_po_generation(request):
    unit = request.user.user_roles.unit
    current_date = now()
    pending_quotation = Quotation.objects.filter(approved=True,unit=unit,valid_from__lte=current_date,valid_till__gte=current_date,balance_quantity__gt = 0)
    return render(request,'inventory/quotation_list.html',{'pending':pending_quotation})


@login_required
def po_entry(request, id):
    '''This form generates a PO from a quotation'''
    quotation = get_object_or_404(Quotation, id=id)
    if request.method == 'POST':
        with db_transaction.atomic():
            try:
                form = PurchaseOrderForm(request.POST, user=request.user, quotation=quotation)
                if form.is_valid():                    
                    instance = form.save(commit=False)
                    instance.unit = request.user.user_roles.unit
                    instance.created_by = request.user
                    instance.created = True
                    instance.save()
                    return redirect('purchase_order_items', instance.id)
                else:
                    messages.error(request, 'Form is not valid. Please check the errors below.')
                    logger.error(f"Form errors: {form.errors}")
            except Exception as e:
                
                messages.error(request, f"An error occurred: {str(e)}")
                logger.error(f"Error while generating PO: {e}")
                raise db_transaction.TransactionManagementError(f"Rolling back as exception {e} has caused this error")
    else:
        form = PurchaseOrderForm(user=request.user, quotation=quotation)

    return render(request, 'inventory/forms/generate_po.html', {'form': form})


def purchase_order_items(request,id):
    '''This View is used to add items to the purchase order'''    
    purchase_order_instance= Purchase_Order.objects.get(id=id)
    items = Quotation_Items.objects.filter(quotation=purchase_order_instance.quotation)    
    QuotationItemFormSet = modelformset_factory(Quotation_Items,form=QuotationItemEditForm,extra=0)
    if request.method == 'POST':        
        formset = QuotationItemFormSet(request.POST, queryset=items)    
        if formset.is_valid():
            try:
                with db_transaction.atomic():
                    vat=cst=cgst=sgst=igst=0                    
                    for form, it in zip(formset, items):                        
                        po_quantity = form.cleaned_data.get('po_quantity')

                        #  Skip if no quantity is provided
                        if not po_quantity or po_quantity == 0:
                            continue

                        it.balance_quantity -= po_quantity
                        it.quotation.balance_quantity -= po_quantity
                        it.save() 
                        it.quotation.save()

                        purchase_order = Purchase_Order.objects.select_for_update().filter(quotation=it.quotation.id).last()
                        purchase_order.po_quantity += Decimal(po_quantity)
                        rate = it.unit_rate
                        value = po_quantity * rate
                        purchase_order.po_value += value
                        conversion_rate = it.quotation.supplier.currency.conversion_rate
                        inr_value = value * conversion_rate
                        purchase_order.inr_value += inr_value                       
                        balance_quantity = po_quantity
                        purchase_order.balance_quantity += po_quantity
                        state = it.quotation.supplier.supplier_state
                        quotation_item = Item.objects.get(id=it.item.id)

                        tax = calculate_tax(
                            po=purchase_order,
                            value=inr_value,
                            supplier_state=state,
                            item=it.item
                        )

                        vat, cst, cgst, sgst, igst = tax['VAT'], tax['CST'], tax['CGST'], tax['SGST'], tax['IGST']
                        creditable = tax['creditable']
                        tax_amount = vat + cst + cgst + sgst + igst
                        purchase_order.tax += tax_amount

                        purchase_order.save()

                        instance = Purchase_Order_Items(
                            purchase_order=purchase_order,
                            quantity=po_quantity,
                            rate=rate,
                            value=value,
                            inr_value=inr_value,
                            quotation_item=quotation_item,
                            balance_quantity=balance_quantity,
                            vat=vat,
                            cst=cst,
                            cgst=cgst,
                            sgst=sgst,
                            igst=igst,
                            creditable=creditable
                        )
                        instance.save()

                    purchase_order.approver=assign_approver(transaction_type=purchase_order.transaction_type,inr_value=purchase_order.inr_value,unit=purchase_order.unit)
                    purchase_order.save()
                    messages.success(request,'Purchase Order Saved Successfully')
                    if purchase_order.quotation.delivery_terms == 'Ex-Factory':
                        id  = purchase_order.id                        
                        return redirect('freight_purchase_order',id)
                    else:
                        return redirect('employee_profile')
            except Exception as e:
                messages.error(request,e)
                logger.error(f"Error while processing purchase order items: {e}")
                raise db_transaction.TransactionManagementError(f"Rolling back as exception {e} has caused this error")
    else:
        formset = QuotationItemFormSet(queryset=items)
    return render(request, 'inventory/forms/purchase_order_item_form.html', {
       'formset': formset})

def assign_po_approver(request,id):
    po_to_approve = Purchase_Order.objects.get(id=id)
    transaction_type = po_to_approve.transaction_type
    inr_value = po_to_approve.inr_value
    unit = po_to_approve.unit    
    po_to_approve.approver =assign_approver(transaction_type=transaction_type,inr_value=inr_value,unit=unit)
    po_to_approve.save()
    return redirect('employee_profile')



@login_required
def po_lcr_join(request, id):
    '''This view is used to join PO with landed cost rule and freight rule so that the landed cost of the transaction can be captured at this stage.'''
    with db_transaction.atomic():
        po = get_object_or_404(Purchase_Order, id=id)       
        
        if request.method == 'POST':
            form = PoLcrJoinForm(request.POST, user=request.user,po=po)
            if form.is_valid():
                instance = form.save(commit=False)  # Don't save yet
                instance.po_id = po.id  # Set the po_no_id field                
                instance.save()  # Save the instance with the po_no_id set
                id = instance.po_id
                return redirect('process_po',id)
        else:
            form = PoLcrJoinForm(user=request.user, initial={'purchase_order': po},po=po)


        return render(request, 'inventory/forms/lcr_po_join.html', {'form': form})

@login_required
def process_po(request, id):
    with db_transaction.atomic():
        po_info_dir = {}    
        lcr = Po_Lcr_Join.objects.get(po_id=id)    
        po = Purchase_Order.objects.get(id=id)
        quotation = Quotation.objects.get(id=po)
        items = Quotation_Items.objects.filter(quotation=quotation)        
    
        transaction_type = po.transaction_type
        unit = po.unit      
        supplier_state = po.quotation.supplier.supplier_state
        inr_value = po.inr_value
        po.vat = 0.00
        po.cst = 0.00
        tax_on_goods = 0.00
        po.cgst = po.sgst = po.igst =  0.00  # initialize variables

        # Calculate tax on goods
        tax_type = ""
        vat,cst,cgst,sgst,igst,creditable = calculate_tax(po=po,value=po.inr_value,lcr=lcr,supplier_state=supplier_state)
        po.vat =vat
        if po.vat > 0:
            tax_type = 'VAT' 
        po.cst = cst
        if po.cst > 0:
            tax_type ='CST'
        po.cgst = cgst
        po.sgst =sgst
        if po.cgst > 0 and po.sgst > 0:
            tax_type = 'CGST/SGST'
        po.igst = igst
        if po.igst > 0:
            tax_type ='IGST'
        
        # po_value =po.inr_value + po.vat + po.cst + po.cgst + po.sgst + po.igst
        po.approver = assign_approver(transaction_type=transaction_type,unit=unit,inr_value= inr_value)
        if not po.approver:
            # Handle the case where no approver could be assigned
            messages.error(request, "No approver found for this PO.")                   
        tax_on_goods = Decimal(po.vat + po.cst + po.cgst + po.sgst + po.igst) 
        po.save()
    # calaculate balance quantity remaining in quotation
        quote = po.quotation
        quote.balance_quantity -= po.quantity
        if quote.balance_quantity < 0:
            raise ValueError("Balance quantity cannot be negative.")    
        quote.save()
        po_info_dir = {
            'company': po.unit.company,
            'unit': po.unit,
            'unit_gst':po.unit.gstin,        
            'po_number': po.po_number,
            'po_date': po.po_date,
            'approved': po.approved,
            'supplier': lcr.lcr.supplier,
            's_gstin': lcr.lcr.supplier.gstin,
            'state': po.quotation.supplier.supplier_state,
            'item': lcr.lcr.item,
            'tax_type' : tax_type,      
            'form_c': po.quotation.form_c,
            'quotation': po.quotation,
            'q_date': po.quotation.quotation_date,
            'quantity': po.quantity,
            'm_unit': lcr.lcr.item.item_unit,
            'rate': po.quotation.unit_rate,
            'value': po.po_value,        
            'tax_goods': round(tax_on_goods, 2),        
            'total_price': round(po.inr_value + tax_on_goods, 2),
            'misc_cost': lcr.lcr.misc_costs,
            # 'total_landed_cost': po.po_value + freight+ tax_on_goods + tax_on_freight + lcr.lcr.misc_costs,
            'balance_quantity':quote.balance_quantity
            }
        if po.quotation.delivery_terms == 'Ex-Factory':
            return redirect('freight_po',id=po.id)
        else:
            return redirect('employee_profile')

    return render(request, 'inventory/process_po.html', {'po_info_dir': po_info_dir})
    
def freight_purchase_order(request,id):    
    po = Purchase_Order.objects.get(id=id) 
    transaction_type = Transaction_Type.objects.get(transaction_name='FSR')
    business =po.business
    unit_state = po.unit.state
    # lcr = Po_Lcr_Join.objects.get(po_id=po)
    freight = po.freight.freight
    mode = po.freight.mode
    service = po.freight.service.service.id    
    transporter = po.freight.service.supplier
    currency = transporter.currency
    inr_amount = freight * currency.conversion_rate
    supplier_state = transporter.supplier_state
    service = Service.objects.get(id=service)
    rate = service.gst_rate
    gst_amount = freight * rate / 100
    created_by= request.user
    cgst=sgst=igst=0    
    if unit_state == supplier_state:
        cgst = gst_amount / 2 or 0
        sgst = gst_amount / 2 or 0
    else:
        igst = gst_amount or 0

    freight_po = Freight_Purchase_Order.objects.create(transaction_type=transaction_type,po_amount=freight,cgst=cgst,sgst=sgst,igst=igst,business= business,created_by=created_by,service=Service.objects.get(id=service.id),supplier=transporter,unit=po.unit,po=po,inr_amount=inr_amount)
    freight_po.save()    
    messages.success(request,'Freight Po generated Successfully')    
    
    return redirect('employee_profile')

@login_required    
def po_list(request):    
    po =0
    po_list = Purchase_Order.objects.all()        
    tax_fields = set()    
    for po in po_list:
        vat = po.vat
        cst = po.cst
        gst = po.gst         
        po = po.po_number
        if vat != 0:
            tax_fields.add('VAT')
        if cst != 0:
            tax_fields.add('CST')
        if gst != 0:
            tax_fields.add('CGST')
                    
    # item = Po_Lcr_Join.objects.select_related('lcr__item').filter(po=po.list)
    return render(request,'inventory/po_list.html',{'po_list':po_list,'tax_fields':tax_fields})
        
@login_required
def update_po(request,id):
    # Retrieve the Purchase Order object for undataion
    po_to_update = get_object_or_404(Purchase_Order,id=id)
    if po_to_update.approved == False:    
        if request.method == 'POST':
            form = PurchaseOrderForm(request.POST, instance=po_to_update)
            if form.is_valid():
                # Update the Purchase Order instance
                form.save()
                messages.success(request, 'Purchase Order updated successfully.')
                # return redirect('some_view_name')  # Redirect to a view showing the updated PO or list of POs
        else:
            form = PurchaseOrderForm(instance=po_to_update)    
        return render(request, 'inventory/forms/update_po.html', {'form': form, 'po': po_to_update})
    else:
        messages.error(request,'You can not update a Approved PO')
    return redirect('po_entry')

@login_required
def approve_po(request, pk):
    po_to_approve = get_object_or_404(Purchase_Order, id=pk)
    # Approve the Purchase Order
    po_to_approve.approved = True
    po_to_approve.approval_date = timezone.now()
    po_to_approve.save()             
    # Display success message
    messages.success(request, 'Purchase Order approved successfully.')
    # return HttpResponse(f'Purchase Order {pk} approved')    
    return redirect('employee_profile')

@login_required  
def generate_gate_entry(request):
    if request.user.user_roles.department =='Security':
        if request.method =='POST':
            form = GateEntryForm(request.POST,user=request.user)
            if form.is_valid():
               instance = form.save(commit=False)
               instance.created_by = User.objects.select_for_update().get(id=request.user.id)
               instance.save()      
               return redirect('employee_profile')
            messages.success(request,"Gate Entry Successfull")
        else:
            form = GateEntryForm(user=request.user)
        return render(request,'inventory/forms/gate_entry_form.html',{'form':form})
    else:
        messages.error(request,'You are not authorized to perfome this function')
    return redirect('gate_entry')
        
@login_required
def gate_entry_register(request):
    # Get the search query from the request
    query = request.GET.get('q')  # 'q' is the search field name in the form

    # If a search query is provided, filter the Gate_Entry objects
    if query:        
        register = Gate_Entry.objects.filter(
            Q(gate_entry_number__icontains=query) |
            Q(truck_number__icontains=query) |
            Q(driver_name__icontains=query) |
            Q(license_number__icontains=query) |
            Q(invoice_no__icontains=query)
        )
    else:
        register = Gate_Entry.objects.all()

    # Render the template with the filtered queryset
    return render(request, 'inventory/forms/gate_entry_register.html', {'register': register, 'query': query})

@login_required
def gate_entry_awaiting_unloading(request):
    # Get the search query from the request
    query = request.GET.get('q')  # 'q' is the search field name in the form

    # If a search query is provided, filter the Gate_Entry objects
    if query:        
        register = Gate_Entry.objects.filter(
            Q(gate_entry_number__icontains=query) |
            Q(truck_number__icontains=query) |
            Q(driver_name__icontains=query) |
            Q(license_number__icontains=query) |
            Q(invoice_no__icontains=query)
        )
    else:
        unit = request.user.user_roles.unit
        register = Gate_Entry.objects.filter(is_unloaded=False,unit=unit)
        
        context ={
            'query' :query,
            'register':register,            
        }
        
        return render(request,'inventory/vehicle_awaiting_unloading.html', context)

@login_required
def vehicle_awaiting_quality_check(request):
    # Get the search query from the request
    query = request.GET.get('q')  # 'q' is the search field name in the form

    # If a search query is provided, filter the Gate_Entry objects
    if query:        
        register = Gate_Entry.objects.filter(
            Q(gate_entry_number__icontains=query) |
            Q(truck_number__icontains=query) |
            Q(driver_name__icontains=query) |
            Q(license_number__icontains=query) |
            Q(invoice_no__icontains=query)
        )
    else:
        register = Gate_Entry.objects.filter(is_quality_ok=False)        
        
        context ={
            'query' :query,
            'register':register,            
        }
        
        return render(request,'inventory/vehicle_awaiting_quality_check.html', context)

@login_required
def mrn_awating_stock_location(request):
    query = request.GET.get('q')  # 'q' is the search field name in the form

    # If a search query is provided, filter the Gate_Entry objects
    if query:        
        register = Material_Receipt_Note.filter(
            Q(mrn_number__icontains=query) |
            Q(e_way_bill_no__icontains=query) |
            Q(form_c_issue_status__icontains=query) |
            Q(form_no__icontains=query) |
            Q(created_by__icontains=query) |
            Q(gate_entry__icontains=query) |
            Q(unit__icontains=query) 
            
        )
    else:
        unit = request.user.user_roles.unit
        register =  Mrn_Items.objects.filter(stock_location__isnull= True,unit=unit) 
              
        
        context ={
            'query' :query,
            'register':register,            
        }
        # return redirect('employee_profile')
    return render(request,'inventory/mrn_awaiting_stock_location.html',context)
    

def quality_check(request, id):
    gate_entry_instance = get_object_or_404(Gate_Entry, id=id)    
    related_specifications = Standard_Quality_Specifications.objects.filter(item_cat=gate_entry_instance.item_cat)

    if request.method == "POST":
        form = QualityCheckForm(request.POST)
        if form.is_valid():
            try:
                # Save the form without committing, and add extra fields
                instance = form.save(commit=False)
                instance.created_by = request.user  # Use request.user directly
                instance.unit = gate_entry_instance.unit
                instance.transaction_type = Transaction_Type.objects.get(transaction_name='QC')
                instance.save()                
                messages.success(request, 'Quality update successful')
                Gate_Entry.objects.filter(id=id).update(is_quality_ok=True)
                gate_entry_instance.save()
                form = QualityCheckForm(initial={'gate_entry': gate_entry_instance})

                # Now check if all specifications for the selected item have an observed value
                remaining_specifications = related_specifications.exclude(
                    id__in=Quality_Check.objects.filter(
                        gate_entry=gate_entry_instance,
                        observed_value__isnull=False  # Make sure observed_value is not null
                    ).values_list('specification', flat=True)
                )

                # If no remaining specifications are missing observed values, redirect
                if not remaining_specifications.exists():
                    # Redirect to a success page or another view when all specifications are filled
                    return redirect('update_flag',id)  # Replace with the name of your success view

            except Exception as e:
                # Log the error and its type for more information
                print(f"Error type: {type(e)}, Error message: {str(e)}")
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            # Form validation error
            messages.error(request, 'Form validation failed. Please check the following errors:')
            print(form.errors)  # Print form errors to console for debugging
            messages.error(request, form.errors.as_text())  # Display form errors
    else:
        form = QualityCheckForm(initial={'gate_entry': gate_entry_instance})

    return render(request, 'inventory/forms/quality_check_form.html', {'form': form})

def update_flag(request,id):
    Gate_Entry.objects.filter(id=id).update(is_quality_ok=True)
    return redirect('employee_profile')




# @login_required
# def approve_quality_check(request,id):
#     gate_entry_instance = get_object_or_404(Gate_Entry, id=id)
#     if request.method == "POST":
#         form = QualityCheckApproveForm(request.POST,initial={'gate_entry': gate_entry_instance},user=request.user)
#         if form.is_valid():                        
#             instance = form.save(commit=False)
#             approval = form.cleaned_data['approval_number']            
#             instance.approver = User.objects.get(id= request.user.id)
#             instance.save()           
#             messages.success(request,'Quality update Successful')
#             approval.gate_entry.is_quality_ok = True
#         else:
#             messages.error(request,'Try Again')
            
#     else:
#         form = QualityCheckApproveForm(initial={'gate_entry': gate_entry_instance},user= request.user)
#     return render(request,'inventory/forms/quality_check_approve_form.html',{'form':form})

@login_required
def vehicle_unload(request,id):    
    gate_entry_instance = Gate_Entry.objects.get(id=id)
    if request.method =='POST':
        form = VehicleUnloadForm(request.POST,user=request.user,initial={'gate_entry': gate_entry_instance})
        if form.is_valid():
            # gate_entry = form.cleaned_data['gate_entry']
            instance = form.save(commit=False)
            instance.unit = gate_entry_instance.unit
            instance.transaction_type = Transaction_Type.objects.get(transaction_name='VUR')          
            instance.created_by= User.objects.get(id=request.user.id)
            instance.save()
            gate_entry_instance.is_unloaded = True
            gate_entry_instance.save(update_fields=['is_unloaded'])
            id = instance.id
            messages.success(request,'Vehicle unloading report generated Successfully')           
            return redirect('vehicle_unload_items',id)
        else:
            messages.error(request,'Something went wrong. Try again or contact admin')            
        
    else:
        form = VehicleUnloadForm(user=request.user,initial={'gate_entry': gate_entry_instance})
    return render(request,'inventory/forms/vehicleunloadform.html',{'form':form})

def vehicle_unload_items(request,id):
    unloading_instance = Vehicle_Unloading_Report.objects.get(id=id)
    if request.method =="POST":
        form = VehicleUnloadItemForm(request.POST)
        decision_form= AddItemForm(request.POST)        
        if form.is_valid() and decision_form.is_valid():
            instance=form.save(commit=False)
            instance.vur=unloading_instance
            instance.save()
            Gate_Entry.objects.filter(id=unloading_instance.gate_entry.id).update(is_unloaded=True)           
            response = decision_form.cleaned_data['add_item']
            if response == 'yes':
                return redirect('vehicle_unload_items', id)
            else:
                pass               
            return redirect('employee_profile')

    else:
        form = VehicleUnloadItemForm()
        decision_form=AddItemForm()
    return render(request,'inventory/forms/vehicle_unload_items.html',{'form':form,'decision_form':decision_form})
            
        
    

@login_required    
def vehicle_out_time(request, id):
    try:
        Gate_Entry.objects.filter(id=id).update(out_time=now())
        # time_to_update.out_time = timezone.now()
        # time_to_update.save(update_fields=['out_time'])  # Force update only the 'out_time' field
        # messages.success(request, f'Out_time successfully updated for vehicle {time_to_update.truck_number}')
    except Gate_Entry.DoesNotExist:
        messages.error(request, f'Vehicle with ID {id} not found')
    except Exception as e:
        messages.error(request, f'Something went wrong: {e}')
    return redirect('employee_profile') 

def receipts_pending_mrn(request):
    pending_mrn = Gate_Entry.objects.filter(is_mrn_made = False,unit= request.user.user_roles.unit)
    return render(request,'inventory/receipt_pending_mrn.html',{'pending':pending_mrn})

@login_required
def generate_mrn(request, id):        
    gate_entry = Gate_Entry.objects.select_for_update().get(id=id)
    unloading_instance = Vehicle_Unloading_Report.objects.select_for_update().get(gate_entry=gate_entry)    
    if request.method == 'POST':
        form = GenerateMrnForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with db_transaction.atomic():
                    transaction_type = form.cleaned_data['transaction_type']               
                    instance = form.save(commit=False)               
                    instance.created_by = request.user                
                    instance.gate_entry = gate_entry
                    instance.created = True
                    instance.unit = gate_entry.unit
                    instance.unload_report = unloading_instance
                    instance.save()
                    Gate_Entry.objects.filter(id=id).update(is_mrn_made=True)                
                    last_mrn = Material_Receipt_Note.objects.select_for_update().filter(created_by=request.user.id,unit=instance.unit).last()
                    Gate_Entry.objects.filter(id=id).update(mrn_no=str(last_mrn),mrn_date=last_mrn.mrn_date)
                    id = last_mrn.id 
                    if gate_entry.po.business.pk ==1:                
                        process_mrn(id)
                    else:
                        process_taxable_mrn(id)
                
            except Exception as e:
                if e:
                    raise db_transaction.TransactionManagementError(f"Rolling back as exception {e} has caused this error")
                            
            messages.success(request, 'MRN Successfully Generated')            #
    else:   
        form = GenerateMrnForm(user=request.user)
    return render(request,'inventory/forms/generate_mrn_form.html',{'form':form})         
               
                
def process_mrn(id):    
    mrn = Material_Receipt_Note.objects.get(id=id)    
    po= mrn.gate_entry.po
    # service_supplier = po.service.supplier
    # ic(service_supplier,721)
    unit = po.unit
    unload_report = mrn.unload_report
    # print(unload_report,694)    
    mrn_items = unload_report.unloaded_item.all()
    # print(mrn_items)   
    total_quantity_dict = unload_report.unloaded_item.values('item').aggregate(total_quantity=Sum('bill_quantity'))
    total_quantity = total_quantity_dict['total_quantity']  
    transaction_type = mrn.transaction_type    
    # if not transaction_number:
    transaction_number = generate_document_number(
        model_class= Inv_Transaction,
        transaction_type=transaction_type,
        unit=unit,
        number_field='transaction_number',
    )
    
    with db_transaction.atomic():
        landed_cost=credit_supplier=freight_provision=credit_custom=credit_excise = total_debits=total_credits=total_import_levies=total_excise_levies=0   
        for mrn_item in mrn_items:                
            billed_quantity = mrn_item.bill_quantity
            actual_quantity = mrn_item.actual_quantity 
            item = mrn_item.item                    
            po_item = Purchase_Order_Items.objects.select_for_update().get(quotation_item= mrn_item.item,purchase_order=po)
            rate= po_item.rate         
            unit = mrn.gate_entry.unit
    #         # lcr = Po_Lcr_Join.objects.get(po_id=mrn.gate_entry.po.id)
    
            value = Decimal(billed_quantity) * Decimal(rate) * Decimal(po.quotation.currency.conversion_rate) 
            inland_haulage = (Decimal(billed_quantity) * Decimal(po.quotation.misc_cost) * Decimal(po.quotation.currency.conversion_rate))
            custom_duty = 0 
            igst = 0               
            supplier_state= po.quotation.supplier.supplier_state
            custom_duty = excise_levies = clearance_charge = 0
            cgst = sgst = igst = cgst_freight = sgst_freight = igst_freight = 0  # initialize variables
            creditable = False            
            if po.quotation.supplier.location == 'Overseas':
    #             # Fetch all custom duties related to the item
                custom , igst = calculate_custom(inr_value=value,item=mrn_item.item)
                custom_duty = custom
                igst = igst                
                clearance_charge = value * Decimal('1.18') / Decimal('100')
                ic(value,custom_duty,igst,clearance_charge, 703)
            total_import_levies = 0                
            if mrn_item.item.item_tax_type == 'Non_GST':
                if po.quotation.supplier.supplier_state != unit.state:
                    import_levies = State_Excise_taxes_On_Goods.objects.filter(state=unit.state,incidence='Outward')                    
                    for levy in import_levies:
                        tax_name = levy.tax_name       
                        excise_rate = levy.rate
                        uom = levy.levy_unit
                        import_fee_account= levy.account
                        excise_amount = billed_quantity * excise_rate
                        total_import_levies += excise_amount 
                    
                #Calculate excise levies on export of goods
               
                excise_levies = State_Excise_taxes_On_Goods.objects.filter(state=po.quotation.supplier.supplier_state,incidence='Inward')
                total_excise_levies = 0
                for levies in excise_levies:
                    tax_name = levies.tax_name       
                    excise_rate = levies.rate
                    uom = levies.levy_unit
                    excise_amount = billed_quantity * excise_rate    
                    total_excise_levies += excise_amount 
                    

    #             # Calculate State taxes like VAT and CST
                    
                tax =calculate_tax(po=po,value=value+total_excise_levies,item=mrn_item.item,supplier_state=supplier_state)            
                vat = tax['VAT']
                cst = tax['CST']
                cgst = tax['CGST']
                sgst = tax['SGST']
                igst = tax['IGST']
                creditable = tax['creditable']            
            else:
                tax =calculate_tax(po=po,value=value+total_import_levies,item=mrn_item.item,supplier_state=supplier_state)            
                vat = tax['VAT']
                cst = tax['CST']
                cgst = tax['CGST']
                sgst = tax['SGST']
                igst = tax['IGST']
                creditable = tax['creditable']     
                    
    #                 # Calculate applicable freight
            if po.quotation.delivery_terms == 'Ex-Factory':
                transporter = po.freight.service.supplier                                
                freight = po.freight.freight
                toll_tax = po.freight.toll_tax
                freight = (freight + toll_tax)/(total_quantity)*mrn_item.bill_quantity          

                # Calculate tax on freight service
                if po.freight.service.supplier.supplier_state != po.unit.state:
                    igst_freight = freight * po.freight.service.service.gst_rate / 100
                    
                                        
                else:
                    cgst_freight = freight * po.freight.service.service.gst_rate / 200
                    sgst_freight = freight * po.freight.service.service.gst_rate / 200             
                    
            else:
                freight = 0
          
            mrn_item_instance=Mrn_Items(invoice_quantity=billed_quantity,actual_quantity=actual_quantity,value=value,vat=vat,cst=cst,cgst=cgst,sgst=sgst,igst=igst,freight=freight,cgst_freight=cgst_freight,sgst_freight=sgst_freight,igst_freight=igst_freight,custom_duty=custom_duty,excise_levies_import=total_import_levies,item=item,mrn=mrn,unit=unit,excise_levies_export=total_excise_levies,)
                        
            # Ensure billed_quantity is valid
            if billed_quantity is None or billed_quantity <= 0:
                raise ValueError("Invalid billed_quantity. Ensure it is properly calculated.")

            # Update balance quantities within a transaction
            with db_transaction.atomic():
                po.balance_quantity = F('balance_quantity') - billed_quantity
                po_item.balance_quantity = F('balance_quantity') - billed_quantity
                po_item.save()
                po.save()

            # Refresh from database to ensure updated values
            po.refresh_from_db()
            po_item.refresh_from_db()
            
            item = mrn_item.item
            if po.business.pk == 1:
                landed_cost=0
                if creditable:                                             
                    landed_cost += value + cst +freight + cgst_freight + sgst_freight + igst_freight + total_import_levies+custom_duty + igst + cgst + sgst + total_excise_levies + clearance_charge + inland_haulage
                else:
                    landed_cost += value + vat + cst + freight + cgst_freight + sgst_freight + igst_freight + total_import_levies+custom_duty + igst + cgst + sgst+total_excise_levies +clearance_charge + inland_haulage                                        
                credit_supplier += value + cst + vat + cgst + sgst + igst + inland_haulage + total_excise_levies
                ic(credit_supplier,inland_haulage) 
                freight_provision += freight + cgst_freight + sgst_freight + igst_freight
                credit_custom += custom_duty 
                credit_excise += total_import_levies          
                mrn_item_instance.landed_cost=landed_cost
                # clearance_charge = clearance_charge
                mrn_item_instance.save() 
                receipt_not_vouchered_supplier = Receipt_Not_Vouchered(
                transaction_number=transaction_number,
                transaction_type=transaction_type,
                transaction_date=mrn.mrn_date,
                unit=unit,
                supplier = po.quotation.supplier,
                invoice_number=mrn.gate_entry.invoice_no,
                invoice_date=mrn.gate_entry.invoice_date,
                invoice_value = credit_supplier,
                account= po.quotation.supplier.account,
                )
                receipt_not_vouchered_supplier.save()
                if freight > 0: 
                    receipt_not_vouchered_transporter = Receipt_Not_Vouchered(
                    transaction_number=transaction_number,
                    transaction_type=transaction_type,
                    transaction_date=mrn.mrn_date,
                    unit=unit,
                    supplier = transporter,
                    invoice_number=mrn.gate_entry.lorry_receipt_number,
                    invoice_date=mrn.gate_entry.lorry_receipt_date,
                    invoice_value = freight_provision,
                    account= transporter.account,
                    )
                    receipt_not_vouchered_transporter.save()
                if po.quotation.supplier.location == 'Overseas': 
                    receipt_not_vouchered_clearing_agent = Receipt_Not_Vouchered(
                    transaction_number=transaction_number,
                    transaction_type=transaction_type,
                    transaction_date=mrn.mrn_date,
                    unit=unit,
                    supplier = po.service.supplier,
                    invoice_number=mrn.gate_entry,
                    invoice_date=mrn.gate_entry.gate_entry_date,
                    invoice_value = clearance_charge,
                    account = po.service.supplier.account,                
                    )
                    receipt_not_vouchered_clearing_agent.save()        
                account_chart = Account_Chart.objects.select_for_update().get(id=item.account.id)
                debit_update =Inv_Transaction(
                    transaction_number = transaction_number,
                    transaction_type = transaction_type,
                    transaction_cat = 'Debit',
                    unit = unit,
                    debit_amount = landed_cost,
                    credit_amount = 0,
                    account_chart = account_chart,
                    reference = f"Debit toward reciept of {item} vide {mrn.gate_entry} mrn_no {mrn} date {mrn.mrn_date}"                            
                )
                debit_update.save()
                # print(debit_update,811)
                total_debits += landed_cost 
                  
                update_account_chart(id=account_chart.id,debit_amount=landed_cost,credit_amount=0)
                print(debit_update,852)
        
                
        account_chart = Account_Chart.objects.get(id=43)

        credit_update_supplier =Inv_Transaction(
        transaction_type =transaction_type,
        transaction_number = transaction_number,
        transaction_cat = 'Credit',
        unit =unit,
        debit_amount = 0,
        credit_amount = credit_supplier,
        account_chart = account_chart,
        reference = f"Credit entry toward supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}"
        )
        credit_update_supplier.save()
        print(credit_update_supplier)
        total_credits += credit_supplier
    
        update_account_chart(id=account_chart.id,debit_amount=0,credit_amount=credit_supplier)
    
        
        if freight > 0: 
            account_chart = Account_Chart.objects.get(id=po.freight.provision_account.id)            
            freight_update= Inv_Transaction(
            transaction_type =transaction_type,
            transaction_number = transaction_number,
            transaction_cat = 'Credit',
            unit =unit,
            debit_amount = 0,
            credit_amount = freight_provision,
            account_chart = account_chart,
            reference = f"freight entry toward supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}"
            )
            print(freight_update,846)
            freight_update.save()
            update_account_chart(id=account_chart.id,debit_amount=0,credit_amount=freight_provision)            
            total_credits += freight_provision
            
        if custom_duty > 0:
            account_chart = Account_Chart.objects.get(id=42)
            custom_update= Inv_Transaction(
            transaction_type =transaction_type,
            transaction_number = transaction_number,
            unit=unit,
            transaction_cat = 'Credit',
            debit_amount = 0,
            credit_amount = credit_custom,
            account_chart = account_chart,
            reference = f"Credit entry toward custom duty on supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}"
            )
            custom_update.save()
            update_account_chart(id=account_chart.id,credit_amount=credit_custom,debit_amount=0)
            total_credits += credit_custom
    
        if total_import_levies >0:
            account_chart=Account_Chart.objects.get(id=import_fee_account.id)              
            excise_update =Inv_Transaction(
            transaction_type =transaction_type,
            transaction_number = transaction_number,
            transaction_cat = 'Credit',
            unit =unit,
            debit_amount = 0,
            credit_amount = total_import_levies,
            account_chart = account_chart,
            reference = f"Credit entry toward advance excise levies on supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}"
            )
            excise_update.save()
            update_account_chart(id=account_chart.id,credit_amount=total_import_levies,debit_amount=0)
            ic(total_credits)
            total_credits += total_import_levies
            ic(total_import_levies,total_credits,971)
        if vat > 0:
                account_chart= Account_Chart.objects.get(id=49)
                vat_update=Inv_Transaction(
                transaction_type = transaction_type,
                transaction_number = transaction_number,
                unit = unit,
                transaction_cat = 'Debit',
                debit_amount = vat,
                credit_amount= 0,
                account_chart = account_chart,
                reference = f'ITC toward vat  on supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}'
                )
                vat_update.save()
                update_account_chart(id=account_chart.id,debit_amount=vat,credit_amount=0)
                total_debits += vat
        if clearance_charge > 0:
            account_chart= Account_Chart.objects.get(id=43)
            clearance_update=Inv_Transaction(
            transaction_type = transaction_type,
            unit = unit,
            transaction_number = transaction_number,
            transaction_cat = 'Credit',
            credit_amount = clearance_charge,
            debit_amount= 0,
            account_chart = account_chart,
            reference = f' clearance charge on supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}'
            )
            clearance_update.save()
            update_account_chart(id=account_chart.id,debit_amount=0,credit_amount=clearance_charge)
            total_credits += clearance_charge
        print(total_debits,total_credits,867)
        return redirect('employee_profile')
    
    if total_debits != total_credits:
        raise db_transaction.TransactionManagementError("Debit and credit amounts do not match, rolling back transaction.")
    

def process_taxable_mrn(id):
    pass  
    # mrn = Material_Receipt_Note.objects.get(id=id)    
    # po= mrn.gate_entry.po
    # unload_report = mrn.unload_report
    # # print(unload_report,694)    
    # mrn_items = unload_report.unloaded_item.all()
    # # print(mrn_items)   
    # total_quantity_dict = unload_report.unloaded_item.values('item').aggregate(total_quantity=Sum('bill_quantity'))
    # total_quantity = total_quantity_dict['total_quantity']  
    # transaction_type = mrn.transaction_type
    # new_transaction_no= generate_document_number(
    #     model_class=Inv_Transaction,
    #     transaction_type=transaction_type,
    #     unit=po.unit,
    #     number_field='transaction_number'
        
    # )
       
    # with db_transaction.atomic():
    #     landed_cost=credit_supplier=freight_provision=credit_custom=credit_excise=debit_cgst=debit_sgst=debit_igst = total_debits=total_credits=0   
    #     for mrn_item in mrn_items:                
    #         billed_quantity = mrn_item.bill_quantity
    #         actual_quantity = mrn_item.actual_quantity 
    #         item = mrn_item.item                    
    #         po_item = Purchase_Order_Items.objects.get(quotation_item= mrn_item.item)
    #         rate= po_item.rate         
    #         unit = mrn.gate_entry.unit
    # #         # lcr = Po_Lcr_Join.objects.get(po_id=mrn.gate_entry.po.id)
    
    #         value = (billed_quantity * rate *po.quotation.currency.conversion_rate) +(billed_quantity * po.quotation.misc_cost * po.quotation.currency.conversion_rate)              
    #         custom_duty = 0 
    #         igst = 0               
    #         supplier_state= po.quotation.supplier.supplier_state
    #         custom_duty = excise_levies = clearance_charge = 0
    #         cgst = sgst = igst = cgst_freight = sgst_freight = igst_freight = 0  # initialize variables
    #         creditable = False            
    #         if po.quotation.supplier.location == 'Overseas':
    # #             # Fetch all custom duties related to the item
    #             custom , igst = calculate_custom(inr_value=value,item=mrn_item.item)
    #             custom_duty = custom
    #             igst = igst                
    #             clearance_charge = 0                       
    #         if item.item_tax_type == 'Non_GST':                
    # #             # Calculate State taxes like VAT and CST                    
    #             tax =calculate_tax(po=po,value=value,item=mrn_item.item,supplier_state=supplier_state)            
    #             vat = tax['VAT']
    #             cst = tax['CST']
    #             cgst = tax['CGST']
    #             sgst = tax['SGST']
    #             igst = tax['IGST']
    #             creditable = tax['creditable']            
    #         else:
    #             tax =calculate_tax(po=po,value=value,item=mrn_item.item,supplier_state=supplier_state)            
    #             vat = tax['VAT']
    #             cst = tax['CST']
    #             cgst = tax['CGST']
    #             sgst = tax['SGST']
    #             igst = tax['IGST']
    #             creditable = tax['creditable']     
                    
    # #                 # Calculate applicable freight
    #         if po.quotation.delivery_terms == 'Ex-Factory':
    #             transporter = po.freight.service.supplier                                
    #             freight = po.freight.freight
    #             toll_tax = po.freight.toll_tax
    #             freight = (freight + toll_tax)/(total_quantity)*mrn_item.bill_quantity          

    #             # Calculate tax on freight service
    #             if po.freight.service.supplier.supplier_state != po.unit.state:
    #                 igst_freight = freight * po.freight.service.service.gst_rate / 100
                    
                                        
    #             else:
    #                 cgst_freight = freight * po.freight.service.service.gst_rate / 200
    #                 sgst_freight = freight * po.freight.service.service.gst_rate / 200             
                    
    #         else:
    #             freight = 0
          
    #         mrn_item_instance=Mrn_Items(invoice_quantity=billed_quantity,actual_quantity=actual_quantity,value=value,vat=vat,cst=cst,cgst=cgst,sgst=sgst,igst=igst,freight=freight,cgst_freight=cgst_freight,sgst_freight=sgst_freight,igst_freight=igst_freight,custom_duty=custom_duty,excise_levies=excise_levies,item=item,mrn=mrn,unit=unit)          
    #         po.balance_quantity -= billed_quantity
    #         po_item.balance_quantity -= billed_quantity       
    #         po_item.save()        
    #         po.save()
    #         landed_cost += value + freight        
    #         credit_supplier += value + cgst + sgst + igst 
    #         freight_provision += freight + cgst_freight + sgst_freight + igst_freight
    #         credit_custom += custom_duty
    #         credit_import_fee += total_import_levies
    #         debit_cgst += cgst
    #         debit_sgst += sgst
    #         debit_igst += igst
    #         mrn_item_instance.landed_cost =landed_cost
    #         mrn_item_instance.save()                  
    #         total_debits = total_credits = 0
        
    #         account_chart = Account_Chart.objects.select_for_update().get(id=item.account.id)
    
    #     Inv_Transaction.objects.create(
    #         transaction_number = new_transaction_no,
    #         transaction_type = transaction_type,
    #         transaction_cat = 'Debit',
    #         unit = unit,
    #         debit_amount = landed_cost,
    #         credit_amount = 0,
    #         account_chart = account_chart,
    #         reference = f"Debit toward reciept of {item} vide {mrn.gate_entry}"                            
    #         )
    #     update_chart = update_account_chart(id=account_chart.id,debit_amount=landed_cost,credit_amount=0)
    #     print(update_chart)
    #     total_debits += landed_cost
                
    # # account_chart=Account_Chart.objects.get(id=po.quotation.supplier.account.id),
    # Inv_Transaction.objects.create(
    #     transaction_type =transaction_type,
    #     transaction_number = new_transaction_no,
    #     transaction_cat = 'Credit',
    #     unit =unit,
    #     debit_amount = 0,
    #     credit_amount = credit_supplier,
    #     account_chart = Account_Chart.objects.get(id=po.quotation.supplier.account.id),
    #     reference = f"Credit entry toward supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}"
    # )       
    # # update_chart = update_account_chart(id=account_chart,debit_amount=0,credit_amount=credit_supplier)
    # total_credits += credit_supplier
    # # account_chart = Account_Chart.objects.get(id=3)
    # if freight > 0:
    #     Inv_Transaction.objects.create(
    #         transaction_type =transaction_type,
    #         transaction_number = new_transaction_no,
    #         transaction_cat = 'Credit',
    #         unit=unit,
    #         debit_amount = 0,
    #         credit_amount = freight_provision,
    #         account_chart = Account_Chart.objects.get(id=3),
    #         reference = f"Credit entry toward supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}"
    #     )
    #     print(freight_provision,942)
    #     # update_chart = update_account_chart(id=account_chart,debit_amount=0,credit_amount=freight_provision)
    #     total_credits += freight_provision
    # if custom_duty > 0:
    #     account_chart = Account_Chart.objects.get(id=13)
    #     Inv_Transaction.objects.create(
    #         transaction_type =transaction_type,
    #         transaction_number = new_transaction_no,
    #         transaction_cat = 'Credit',
    #         unit=unit,
    #         debit_amount = 0,
    #         credit_amount = credit_custom,
    #         account_chart = account_chart,
    #         reference = f"Credit entry toward custom duty on supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}"
    #     )
    #     update_chart = update_account_chart(id=account_chart,debit_amount=0,credit_amount=credit_custom)
    #     print(update_chart)
    #     total_credits += credit_custom

    # if excise_levies >0:
    #     account_chart = Account_Chart.objects.get(id=14)
    #     Inv_Transaction.objects.create(
    #         transaction_type =transaction_type,
    #         transaction_number = new_transaction_no,
    #         transaction_cat = 'Credit',
    #         unit=unit,
    #         debit_amount = 0,
    #         credit_amount = credit_excise,
    #         account_chart = account_chart,
    #         reference = f"Credit entry toward advaince excise levies on supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}"
    #     )
    #     update_chart = update_account_chart(id=account_chart,debit_amount=0,credit_amount=credit_excise)
    #     total_credits += credit_excise
    # if vat > 0:
    #     if creditable:
    #         account_chart = Account_Chart.objects.get(id=11)
    #         Inv_Transaction.objects.create(
    #             transaction_type = transaction_type,
    #             transaction_number = new_transaction_no,
    #             transaction_cat = 'Debit',
    #             unit = unit,
    #             debit_amount = vat,
    #             credit_amount= 0,
    #             account_chart = account_chart,
    #             reference = f'ITC toward vat  on supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}'
    #         )
    #     update_chart = update_account_chart(id=account_chart,debit_amount=vat,credit_amount=0)
    #     print(update_chart)
    #     total_debits += vat
        
    # if cgst > 0 and po.business.id == 1 or po.business.id ==3:
    #     account_chart = Account_Chart.objects.get(id=49)
    #     Inv_Transaction.objects.create(
    #         transaction_type = transaction_type,
    #         transaction_number = new_transaction_no,
    #         transaction_cat = 'Debit',
    #         unit = unit,
    #         debit_amount = mrn.cgst,
    #         credit_amount = 0,
    #         account_chart = account_chart,
    #         reference = f'ITC toward cgst  on supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}'
            
    #     )
    #     update_chart = update_account_chart(id=account_chart,debit_amount=mrn.cgst,credit_amount=0)
    #     print(update_chart)
    #     total_debits += debit_cgst
        
    # if sgst > 0 and po.business.id == 1 or po.business.id ==3:
    #     account_chart = Account_Chart.objects.get(id=49)
    #     Inv_Transaction.objects.create(
    #         transaction_type = transaction_type,
    #         transaction_number = new_transaction_no,
    #         transaction_cat = 'Debit',
    #         unit = unit,
    #         debit_amount = mrn.sgst,
    #         credit_amount = 0,
    #         account_chart = account_chart,
    #         reference = f'ITC toward sgst  on supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}'
            
    #     )
    #     update_chart = update_account_chart(id=account_chart,debit_amount=mrn.sgst,credit_amount=0)
    #     print(update_chart)
    #     total_debits += debit_sgst
    # if igst > 0 and po.business.id == 1 or po.business.id ==3:
    #     account_chart = Account_Chart.objects.get(id=49)
    #     Inv_Transaction.objects.create(
    #         transaction_type = transaction_type,
    #         transaction_number = new_transaction_no,
    #         transaction_cat = 'Debit',
    #         unit = unit,
    #         debit_amount = mrn.igst,
    #         credit_amount = 0,
    #         account_chart = account_chart,
    #         reference = f'ITC toward igst  on supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}'
            
    #     )
    #     update_chart= update_account_chart(id=account_chart,debit_amount=mrn.igst,credit_amount=0)
    #     print(update_chart)
    #     total_debits += debit_igst
    # if cgst_freight > 0 and po.business.id == 1 or po.business.id ==3:                
    #     Account_Chart.objects.get(id=50)                
    #     Inv_Transaction.objects.create(
    #         transaction_type = transaction_type,
    #         transaction_number = new_transaction_no,
    #         transaction_cat = 'Debit',
    #         unit = unit,
    #         debit_amount = mrn.cgst_freight,
    #         credit_amount = 0,
    #         account_chart = account_chart,
    #         reference = f'ITC toward gst on freight  on supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}'
            
    #     )
    #     update_chart = update_account_chart(id=account_chart,debit_amount=mrn.cgst_freight,credit_amount=0)
    #     print(update_chart)
    #     total_debits += cgst_freight
    # if sgst_freight > 0 and po.business.id == 1 or po.business.id ==3:
    #     account_chart = Account_Chart.objects.get(id=50)
    #     Inv_Transaction.objects.create(
    #         transaction_type = transaction_type,
    #         transaction_number = new_transaction_no,
    #         transaction_cat = 'Debit',
    #         unit = unit,
    #         debit_amount = sgst_freight,
    #         credit_amount = 0,
    #         account_chart = account_chart,
    #         reference = f'ITC toward gst on freight  on supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}'
            
    #     )
    #     update_chart = update_account_chart(id=account_chart,debit_amount=mrn.sgst_freight,credit_amount=0)
    #     print(update_chart)
    #     total_debits += sgst_freight
    # if igst_freight > 0 and po.business.id == 1 or po.business.id ==3:
    #     account_chart = Account_Chart.objects.get(id=50)
    #     Inv_Transaction.objects.create(
    #         transaction_type = transaction_type,
    #         transaction_number = new_transaction_no,
    #         transaction_cat = 'Debit',
    #         unit = unit,
    #         debit_amount = igst_freight,
    #         credit_amount = 0,
    #         account_chart = account_chart,
    #         reference = f'ITC toward gst on freight  on supply of {item} vide  {mrn.gate_entry.invoice_no} dated {mrn.gate_entry.invoice_date}'
            
    #     )
    #     update_chart = update_account_chart(id=account_chart,debit_amount=mrn.igst_freight,credit_amount=0)
        
    #     total_debits += igst_freight  
    #         # Check if debits and credits match
                
    #     print(total_debits,total_credits,867)
    #     if total_debits != total_credits:
    #             raise db_transaction.TransactionManagementError("Debit and credit amounts do not match, rolling back transaction.")
    
    # return redirect('employee_profile')          
    
            
                        
                
# def mrn_account_entry(Request,id):
#     mrn = Material_Receipt_Note.objects.get(id=id)
#     if mrn.gate_entry.po.business == 2:
#         item = mrn.gate_entry.po.quotation.item
#         creditable = State_Tax_on_Sale_Of_Goods.objects.filter(item=item)
#         for credit in creditable:
#             if creditable:
#         inv_account = item.account
#         inventory_account = Account_Chart.objects.get(id=inv_account)
#         supplier = mrn.gate_entry.po.quotation.supplier
#         sup_account = supplier.account
#         supplier_account = Account_Chart.objects.get(id=sup_account)
#         freight_provision_account = Account_Chart.objects.get(id=3)
#         value = mrn.value
#         vat = mrn.vat
#         cst = mrn.cst
#         cgst = mrn.cgst
#         sgst = mrn.sgst
#         igst = mrn.igst
#         freight = mrn.freight
#         cgst_freight = mrn.cgst_freight
#         sgst_freight = mrn.sgst_freight
#         igst_freight = mrn.igst_freight
#         custom_duty = mrn.custom_duty
#         excise_levies = mrn.excise_levies
#         custom_clearance = mrn.custom_clearance
#         mrn.landed_cost = value + vat + cst + cgst + sgst + igst + freight + cgst_freight +sgst_freight + igst_freight + custom_duty +custom_clearance + excise_levies
        
                    

import django_filters

class MRNFilter(django_filters.FilterSet):
    mrn_date = django_filters.DateFilter(
        field_name='mrn_date',
        lookup_expr='exact',
        label='Mrn Date',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    class Meta:
        model = Material_Receipt_Note
        fields = ['unit','mrn_date', 'quality_approval','form_c_issue_status']
        # {
        #     'unit': forms.Select(attrs={'class': 'form-control'}),
        #     'mrn_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        # }
        
        
def mrn_report_view(request):
    f = MRNFilter(request.GET, queryset=Material_Receipt_Note.objects.all())
    return render(request, 'inventory/mrn_report.html', {'filter': f})
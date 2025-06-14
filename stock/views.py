from django.shortcuts import render,redirect,get_object_or_404 
from django.db import transaction as db_transaction
from django.http import HttpResponseRedirect,HttpResponse
from accounts.models import Inv_Transaction
from masters.models import User,User_Roles,Transaction_Type,Account_Chart,Item,Unit_Sub_Location
from .models import Blend,Blend_Bom,Bom_Items,Material_Requisition,Stock_Ledger,Stock_Entry
from .forms import BomForm,BomItemsForm,BlendForm,Blend_Bom,MaterialRequisionForm,StockEntryForm,IssueForm
from .forms import DateRangeForm
from decimal import Decimal
# from production.models import Finished_Blend
from inventory.models import Material_Receipt_Note,Mrn_Items
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction as db_transaction
from django.utils import timezone
from inventory.functions import generate_document_number,update_stock_location,update_account_chart
from django.db.models import Sum
from django.core.exceptions import ValidationError
from icecream import ic


def stock_entry(request,id):
    '''This view record entry of material and allot the stock location after generation of MRN'''
    if request.method =='POST':
        form = StockEntryForm(request.POST,user=request.user)
        if form.is_valid():
            try:
                with db_transaction.atomic():  
                    mrn = form.cleaned_data['mrn']
                    transaction_type = form.cleaned_data['transaction_type']
                    unit_sub_loc = form.cleaned_data['stock_location']
                    instance = form.save(commit=False)  
                    instance.created_by = request.user
                    instance.unit = mrn.unit 
                    instance.item = mrn.item 
                    instance.quantity = mrn.actual_quantity
                    instance.value = mrn.landed_cost                             
                    instance.save()
                    # update stock location
                    update_location = update_stock_location(id=unit_sub_loc.id,receipt_quantity=mrn.actual_quantity,receipt_value=mrn.landed_cost,issue_quantity=0,issue_value=0,unit=mrn.unit,item=mrn.item)
                    update_location.save()
                    # update mrn flag for stock location
                    Mrn_Items.objects.filter(id=mrn.id).update(stock_location=unit_sub_loc.id)
                    messages.success(request,'Stock Entry Successfull')
                   # udpate stock ledger
                    update_stock_ledger(id=instance.id)
                    return redirect('employee_profile')
            except Exception as e:
                messages.error(request,f'Transaction Failed because of {e}')
                if e:
                    raise db_transaction.TransactionManagementError(f"Rolling back as exception {e} has caused this error")                                
    else:       
        form = StockEntryForm(user=request.user)
    return render(request,'stock/stock_entry_form.html',{'form':form})

def update_stock_ledger(id):
    stock_entry = Stock_Entry.objects.get(id=id)    
    stock_ledger = Stock_Ledger.objects.filter(item=stock_entry.item,unit=stock_entry.unit).last()
    if stock_ledger:
        opening_quantity = stock_ledger.closing_quantity        
        opening_value = stock_ledger.closing_value if opening_quantity > 0 else 0
        opening_rate = round(stock_ledger.closing_rate,4) if opening_quantity > 0 else 0    
        transaction_type = stock_entry.transaction_type
        transaction_number = stock_entry.transaction_number     
        transaction_date = stock_entry.transaction_date
        unit = stock_entry.unit
        item = stock_entry.item
    else:
        opening_quantity = 0
        opening_value = 0
        opening_rate = 0
        transaction_type = stock_entry.transaction_type
        transaction_number = stock_entry.transaction_number     
        transaction_date = stock_entry.transaction_date
        unit = stock_entry.unit
        item = stock_entry.item
    if stock_entry.transaction_cat == 'Receipt': 
        quantity = stock_entry.quantity
        value = stock_entry.value
        receipt_rate =Decimal(round(value/quantity,4))
        stock_ledger = Stock_Ledger(transaction_type=transaction_type,transaction_number=transaction_number,transaction_date=transaction_date,unit=unit,item=item,receipt_quantity=quantity,receipt_value=value,receipt_rate=receipt_rate,opening_quantity=opening_quantity,opening_value=opening_value,opening_rate=opening_rate,closing_quantity=opening_quantity+quantity,closing_value=opening_value+value,closing_rate=round((opening_value+value)/(opening_quantity+quantity),4),stock_entry=stock_entry)
    elif stock_entry.transaction_cat == 'Issue': 
        if opening_quantity > 0:
            quantity = stock_entry.issue_quantity       
            value = stock_entry.issue_value        
            issue_rate = round(value/quantity,4) if quantity != 0 else 0
            closing_quantity = opening_quantity - quantity if opening_quantity > 0 else quantity
            closing_value = opening_value - value if opening_value > 0 else value
            # ic(closing_quantity, closing_value, 264)
            closing_rate = round(closing_value / closing_quantity, 4) if closing_quantity != 0 else 0
        else:
            raise ValidationError('The no stock to issue for this item')

        stock_ledger = Stock_Ledger(transaction_type=transaction_type, transaction_number=transaction_number, transaction_date=transaction_date, unit=unit, item=item, issue_quantity=quantity, issue_value=value, issue_rate=issue_rate, opening_quantity=opening_quantity, opening_value=opening_value, opening_rate=opening_rate, closing_quantity=closing_quantity, closing_value=closing_value, closing_rate=closing_rate, stock_entry=Stock_Entry.objects.get(id=id))
    stock_ledger.save()
    # return redirect('employee_profile')    
       

def create_blend_bom(request):
    with db_transaction.atomic():
        if request.method == 'POST':
            form = BomForm(request.POST)
            if form.is_valid():
                brand = form.cleaned_data.get('brand')
                transaction_type = form.cleaned_data.get('transaction_type')
                unit = form.cleaned_data.get('unit')
                bom_date = timezone.now()
                created_by = request.user            
                bom_number = generate_document_number(
                model_class=Blend_Bom,
                unit= unit,
                transaction_type=transaction_type,
                number_field='bom_number'
                )
                bom=Blend_Bom.objects.create(transaction_type=transaction_type,bom_number=bom_number,bom_date=bom_date,brand=brand,created_by=created_by,unit=unit)
                messages.success(request,f'Bom Created successfully for {brand}')
                id = bom.id
                return redirect('bom_items',id)
        else:
            form = BomForm()
        return render(request,'stock/blend_bom_form.html',{'form':form})    

def bom_items(request,id):
    with db_transaction.atomic():
        bom = get_object_or_404(Blend_Bom, id=id) 
        if request.method == 'POST':
            form = BomItemsForm(request.POST)
            if form.is_valid():
                item = form.cleaned_data['item']
                bom_quantity = form.cleaned_data['bom_quantity']
                uom = form.cleaned_data['uom']
                Bom_Items.objects.create(bom=bom,item=item,bom_quantity=bom_quantity,uom=uom)
                messages.success(request,f'Bom item successfully saved for brand {bom.brand}')
        else:
            form = BomItemsForm()
        return render(request,'stock/bom_items_form.html',{'form':form})
            

@login_required
def create_blend(request):
    with db_transaction.atomic():
        if request.method == "POST":
            form = BlendForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.unit = request.user.user_roles.unit
                instance.created_by = request.user
                instance.save()
                messages.success(request,'Blend Successfully Saved')
                # id = instance.id
                return redirect('employee_profile')
        else:
            form = BlendForm()
        return render(request,'stock/blend_form.html',{'form':form})

@login_required
def material_requisition(request, id): 
    '''In this view requistion is created based on per unit consumption as per bom. This is used for wet goods requisition'''  
    with db_transaction.atomic():
        blend = Blend.objects.get(id=id)
        unit = blend.unit
        uom = blend.uom
        batch_quantity = blend.batch_quantity
        
        # Generate a unique requisition number once for the entire blend transaction
        transaction_type = Transaction_Type.objects.get(id=9)
        requisition_number = generate_document_number(
            model_class=Material_Requisition,
            unit=unit,
            transaction_type=transaction_type,
            number_field='requisition_number'
        )
        
        # Loop through BOM items and create individual requisitions
        bom_items = Bom_Items.objects.filter(bom=blend.bom.id)
        for bom in bom_items:
            quantity = bom.bom_quantity
            item = bom.item
            uom = bom.uom
            required_quantity = batch_quantity * quantity
            created_by = request.user

            # Create the Material Requisition
            Material_Requisition.objects.create(
                requisition_number=requisition_number,  # Use the generated requisition number
                required_quantity=required_quantity,
                blend=blend,
                bom=blend.bom,
                uom=uom,
                item=item,
                transaction_type=transaction_type,
                unit=unit,
                created_by=created_by
            )
         
        Blend.objects.filter(id=id).update(status='200') # Set the status to '200' to indicate that requisition for wet goods has been raised
        
        messages.success(request,f'Material Requisition for blend {blend.brand} raised succsessfully' )

    return redirect('employee_profile')

@login_required
def blend_awating_issue(request):
    blend_awaiting_issue = Material_Requisition.objects.filter(issue_slip__isnull = True)
    return render(request,'stock/blend_awaiting_issue.html',{'blend_awaiting_issue':blend_awaiting_issue})



@login_required
def issue_to_blend(request, id):
    '''This view is used to issue Dry Goods stock to blend based on the requisition raised'''    
    requisition = Material_Requisition.objects.get(id=id)    #Fetch the requisition based on the id
    bom = requisition.bom
    average_rate = Stock_Ledger.objects.filter(item=requisition.item,unit=requisition.unit).last().closing_rate #Fetch the average rate of the item from last stock ledger entry
    available_stock = Stock_Ledger.objects.filter(item=requisition.item,unit=requisition.unit).last().closing_quantity #Fetch the available stock of the item from last stock ledger entry
    blend_to_update = Blend.objects.get(id=requisition.blend.id) #Fetch the blend to update the status
    if request.method == "POST":
        form = IssueForm(request.POST, user=request.user)
        if form.is_valid():
            with db_transaction.atomic():
                # try:
                if requisition.required_quantity <= available_stock:
                    transaction_type = form.cleaned_data['transaction_type']
                    stock_location = form.cleaned_data['stock_location']
                    to_location = form.cleaned_data['to_location']
                    unit = requisition.blend.unit
                    blend = blend_to_update
                    item = requisition.item
                    issue_quantity = requisition.required_quantity
                    issue_value = round(issue_quantity * average_rate,4)
                    created_by = request.user
                    ic(item,unit,issue_quantity,issue_value,blend,stock_location,to_location,transaction_type,created_by, 180)

                    # Create and save the Stock_Entry instance
                    se =Stock_Entry.objects.create(
                        transaction_type=transaction_type,
                        bom=bom,
                        blend=blend,
                        requisition=requisition,
                        transaction_cat = 'Issue',
                        stock_location=stock_location,
                        to_location=to_location,
                        issue_quantity=issue_quantity,
                        issue_value=issue_value,                               
                        item=item,
                        unit=unit,
                        # account = account,
                        created_by=created_by
                    )               
                    messages.success(request, 'Stock successfully issued to blend')
                    #update stock ledger
                    update_stock_ledger(id=se.id)
                    # Update the stock location
                    upl =update_stock_location(id=stock_location.id,receipt_quantity=0,receipt_value=0,issue_quantity=issue_quantity,issue_value=issue_value,unit=unit,item=item)
                    upl.save()
                    # Update the `issue_slip` in Material_sRequisition                    
                  
                    Material_Requisition.objects.filter(id=id).update(issue_slip=se.id)                    
                    
                    # Check if all requisitions for the blend are fully issued
                    fully_issued = Material_Requisition.objects.filter(blend=blend, issue_slip__isnull=True)                    
                    if not fully_issued.exists():
                        Blend.objects.filter(id=requisition.blend.id).update(status=300) #WG 
                        
                        #Generate Account Entry                         
                        
                        account_entry(blend.id)
                        return redirect('employee_profile')  
                    else:
                        return redirect('blend_awaiting_issue')
                        
                else:
                    messages.error(request, f"Available Stock of {requisition.item} is less than Required Quantity")
                # except Exception as e:
                    # print(f"Error occurred: {e}")
    else:
            # Initial form to select `from_location` and `to_location`, user will select locations
        form = IssueForm(user=request.user)

    return render(request,'production/issue_to_blend.html', {'form': form})






@login_required
def stock_location_update(request):
    '''This view is used to update the opening stock, total receipt quantity, total issue quantity, and closing stock for an item from the stock ledger table'''

    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            from_date = form.cleaned_data['start_date']
            to_date = form.cleaned_data['end_date']
            unit = form.cleaned_data['unit']
            item = form.cleaned_data['item']

            if unit is not None and item is not None:
                stock_ledger = Stock_Ledger.objects.filter(unit=unit, item=item, transaction_date__range=[from_date, to_date]).select_related('item','unit')
            else:
                stock_ledger = Stock_Ledger.objects.filter(transaction_date__range=[from_date, to_date]).select_related('item','unit')

            # Aggregate the sums of receipt_quantity and issue_quantity for each item and unit
            aggregated_data = stock_ledger.values('item__item_name', 'unit__unit_name').annotate(
                total_receipt_quantity=Sum('receipt_quantity'),
                total_receipt_value=Sum('receipt_value'),
                total_issue_quantity=Sum('issue_quantity'),
                total_issue_value=Sum('issue_value')
            ).order_by('item', 'unit')

            context = {
                'form': form,
                'start_date': from_date,
                'end_date': to_date,
                'aggregated_data': []
            }

            for data in aggregated_data:
                item_name = data['item__item_name']
                unit = data['unit__unit_name']
                item_stock_ledger = stock_ledger.filter(item__item_name=item_name, unit__unit_name=unit)

                if item_stock_ledger.exists():
                    first_entry = item_stock_ledger.first()
                    last_entry = item_stock_ledger.last()
                    opening_quantity = first_entry.opening_quantity
                    opening_value = first_entry.opening_value
                    closing_quantity = last_entry.closing_quantity
                    closing_value = last_entry.closing_value if closing_quantity > 0 else 0
                else:
                    opening_quantity = opening_value = closing_quantity = closing_value = 0

                context['aggregated_data'].append({
                    'unit': unit,
                    'item_name': item_name,
                    'opening_quantity': round(opening_quantity, 2),
                    'opening_value': round(opening_value, 2),
                    'total_receipt_quantity': round(data['total_receipt_quantity'], 2),
                    'total_receipt_value': round(data['total_receipt_value'], 2),
                    'total_issue_quantity': round(data['total_issue_quantity'], 2),
                    'total_issue_value': round(data['total_issue_value'], 2),
                    'closing_quantity': round(closing_quantity, 2),
                    'closing_value': round(closing_value, 2),
                    'start_date': from_date,
                    'end_date': to_date
                    
                })
                
          

            return render(request, 'stock/stock_location_update.html', context)
        else:
            print('form is invalid')
    else:
        form = DateRangeForm()

    return render(request, 'stock/stock_location_update.html', {'form': form})    

    
    
    

def account_entry(blend):
    with db_transaction.atomic():
        stock_entry = Stock_Entry.objects.filter(blend=blend)
        debit_account = Account_Chart.objects.select_for_update().get(account_code='2302')
        
        for entry in stock_entry:
            transaction_type = entry.transaction_type
            transaction_number = entry.transaction_number
            value = entry.issue_value
            unit = entry.unit
            item = entry.item
            blend = entry.blend
            account = item.account
            
            Inv_Transaction.objects.create(
                transaction_type=transaction_type,
                transaction_number=transaction_number,
                transaction_cat = 'Debit',
                unit= unit,
                account_chart = debit_account,
                debit_amount = value,
                credit_amount = 0,
                reference = f"Debit_Entry Towards transfer of {item} for {blend}"
                
            )
            update_account_chart(id=debit_account.id,debit_amount=value,credit_amount=0)
            Inv_Transaction.objects.create(
                transaction_type=transaction_type,
                transaction_number = transaction_number,
                transaction_cat = 'Credit',
                unit= unit,
                account_chart = account,
                credit_amount = value,
                debit_amount = 0,
                reference = f"Credit Entry Towards transfer of {item} for {blend}"
                
            )
            update_account_chart(id=account.id,debit_amount=0,credit_amount=value)
    return redirect('employee_profile')

# def account_chart_update(request,id):
#     transaction = Inv_Transaction.objects.get(id=id)
#     account_chart = transaction.account_chart.id
#     debit_amount = transaction.debit_amount 
#     credit_amount = transaction.credit_amount
#     update_account_chart(id=account_chart,debit_amount=debit_amount,credit_amount=credit_amount)
#     return redirect('employee_profile')
    
    
        
def bottling_material_requisition(request,id):
    if request.method == 'POST':
        form = MaterialRequisionForm(request.POST)
        if form.is_valid():
            with db_transaction.atomic():
                try:
                    bottling_bom = form.cleaned_data['bom'] 
                    blend = form.cleaned_data['blend']
                    production = form.cleaned_data['production']
                    bottling_bom = Blend_Bom.objects.get(id=bottling_bom.id)
                    finished_blend = Finished_Blend_Stock_Ledger.objects.filter(id=id)
                    sku = bottling_bom.sku
                    unit = blend.unit
                    uom = blend.uom
                
                    
                    # Generate a unique requisition number once for the entire blend transaction
                    transaction_type = Transaction_Type.objects.get(id=19)                    
                    requisition_number = generate_document_number(
                        model_class=Material_Requisition,
                        unit=unit,
                        transaction_type=transaction_type,
                        number_field='requisition_number'
                    )
                    
                    # Loop through BOM items and create individual requisitions
                    bom_items = Bom_Items.objects.filter(bom=bottling_bom.id)
                    for bom in bom_items:
                        available_stock = Unit_Sub_Location.objects.get(item=bom.item,unit=blend.unit).closing_quantity 
                        quantity = bom.bom_quantity
                        print(available_stock,quantity)
                        item = bom.item
                        uom = bom.uom
                        required_quantity = production * quantity
                        if required_quantity > available_stock:
                            raise ValidationError(f'Available Stock of {item} is less than Required Quantity')
                        created_by = request.user

                        # Create the Material Requisition
                        Material_Requisition.objects.create(
                            requisition_number=requisition_number,  # Use the generated requisition number
                            required_quantity=required_quantity,
                            blend=blend,
                            bom=bottling_bom,                    
                            uom=uom,
                            item=item,
                            transaction_type=transaction_type,
                            unit=unit,
                            created_by=created_by
                        )
                    blend.is_dg_requistioned = True
                    blend.save()
                    messages.success(request,f'Material Requisition for blend {blend.brand} {sku} raised successfully' )
                except Exception as e:
                    messages.error(request,f"Transaction Failed because of e")
                    raise db_transaction.TransactionManagementError("Rolling back Transaction as {e} occured")                    

                return redirect('employee_profile')
    else:
        form = MaterialRequisionForm()
    return render(request,'stock/material_requisition_form.html',{'form':form})



                            
@login_required
def issue_for_bottling(request, id):
    if request.method == "POST":
        form = BottlingIssueForm(request.POST, user=request.user)
        if form.is_valid():
            with db_transaction.atomic():
                try:
                    transaction_type = form.cleaned_data['transaction_type']
                    blend = form.cleaned_data['blend']
                    requisition = form.cleaned_data['requisition']
                    mrn_ref = form.cleaned_data['mrn_ref']
                    from_location = form.cleaned_data['from_location']
                    to_location = form.cleaned_data['to_location']
                    item = form.cleaned_data['item']  # The current BOM item being transferred
                    issue_quantity = form.cleaned_data['issue_quantity']
                    unit = blend.unit
                    account = item.account
                    created_by = request.user

                    # Create and save the Stock_Entry instance
                    Stock_Entry.objects.create(
                        transaction_type=transaction_type,
                        blend=blend,
                        requisition=requisition,
                        mrn_ref=mrn_ref,
                        from_location=from_location,
                        to_location=to_location,
                        issue_quantity=issue_quantity,
                        item=item,
                        unit=unit,
                        account = account,
                        created_by=created_by
                    )
                    
                    messages.success(request, 'Stock successfully issued for Bottling')
                    # Update the `issue_slip` in Material_sRequisition
                    last_issued_entry = Stock_Entry.objects.select_for_update().filter(transaction_type=transaction_type,unit=unit).last()
                    requisition.issue_slip = last_issued_entry
                    requisition.save()

                    # Check if all requisitions for the blend are fully issued
                    fully_issued = Material_Requisition.objects.filter(blend=blend, issue_slip__isnull=False)
                    if not fully_issued.exists():
                        Blend.objects.filter(id=blend.id).update(is_dg_issued=True)
                        blend.save()
                        return redirect('employee_profile')                        
                    else:
                        return redirect('issue_to_bottling',blend.id)

                except Exception as e:                    
                    messages.error(request, f"Failed to issue stock: {e}")
                    db_transaction.TransactionManagementError(f'Rolling Back transaction because of error {e}')
    else:
        # Initial form to select `from_location` and `to_location`, users will select locations
        form = BottlingIssueForm(user=request.user)
    return render(request, 'stock/issue_to_bottling_form.html', {'form': form})

    

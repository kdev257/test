from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from masters.models import Account_Chart,Transaction_Type,Unit_Sub_Location,Brand
from .models import Blend_WIP,Daily_Production_Plan,Production_Plan_Line,Production_Report,Production_Report_Line,Map_Brand_SKU_Item,Overheads_Absorbed,Blend_Overhead_Absorbed
from inventory.forms import AddItemForm
from .forms import BlendWipForm,BlendWipIssueForm,DailyProductionPlanForm,DailyProductionPlanLineForm,UpdateDailyProductionPlanForm,ProductionReportForm,ProductionReportLineForm,RawMaterialConsumptionForm
from stock.models import Blend,Stock_Entry,Blend_Bom,Bom_Items, Stock_Ledger,Material_Requisition
from stock.forms import MaterialRequisionForm
from stock.views import update_stock_ledger
from accounts.models import Inv_Transaction
from django.db import transaction as db_transaction
from django.db.models import Sum
from inventory.functions import generate_document_number,update_stock_location,update_account_chart
from django.utils import timezone
from django.db.models import Q 
from decimal import Decimal
from django.forms import modelformset_factory
from icecream import ic

    # Create your views here.

def blend_awaiting_processing(request):
    '''This function is list all the blends where material issued to blend and proceesing of same is awaited, i.e. reduction ,adding color etc. is done while processing the blend '''
        
    issued_to_blend = Blend.objects.filter(status=300)
    return render(request,'production/blend_awaiting_processing.html',{'issue_to_blend':issued_to_blend})
    
def blend_awaiting_transfer(request):
    '''Here blend has been reduced to its drinking strength but is awaiting transfer to blend holding tank'''
    transfer_blend = Blend.objects.filter(status='400',unit=request.user.user_roles.unit)    
    return render(request,'production/blend_awaiting_transfer.html',{'transfer_blend':transfer_blend})

def receive_blend(request):
    '''receive blend from blending process tank after its finished'''
    receive_blend = Blend_WIP.objects.filter(is_issued= True,transaction_type = 11,unit=request.user.user_roles.unit).first()
    
    return render(request,'production/receive_blend.html',{'receive_blend':receive_blend})

def blend_awaiting_bottling(request):
    '''Blend is lying in blend holding Tank awating to be issued for bottling'''
    awaiting_bottling = Blend.objects.filter(is_bottled = False,unit=request.user.user_roles.unit)    
    return render(request,'production/blend_awaiting_bottling.html',{'awaiting_bottling':awaiting_bottling})


def blend_wip(request,id):
    '''The Blend is processed by reducing it to requisite strength here'''
    blend = Blend.objects.get(id=id)     
    if request.method == "POST":
        form = BlendWipForm(request.POST,user=request.user,blend=blend)
        if form.is_valid():
            with db_transaction.atomic():
                try:
                    transaction_type = form.cleaned_data['transaction_type']
                    blend = form.cleaned_data['blend']            
                    issue = Stock_Entry.objects.filter(blend=blend,transaction_type=7,unit=blend.unit).first()
                    water = form.cleaned_data['water']
                    issue_totals = Stock_Entry.objects.filter( Q(stock_location__item__item_class__class_name='Wet Goods'),
                    blend=blend).aggregate( total_issue_quantity=Sum('issue_quantity'),total_issue_value=Sum('issue_value'))
                    totals_non_spirits = Stock_Entry.objects.filter(blend=blend).exclude(stock_location__item__item_class__class_name='Wet Goods').aggregate(total_issue_value=Sum('issue_value'))

                    # Access the summed values
                    total_issue_value_non_spirits =totals_non_spirits['total_issue_value'] or 0
                    total_issue_quantity = issue_totals['total_issue_quantity']
                    total_issue_value_siprits = issue_totals['total_issue_value']
                    blend_quantity  = total_issue_quantity + Decimal(water)
                    stock_location = issue.to_location
                    requisition = issue.requisition
                    closing_quantity = blend_quantity                    
                    blend_value = total_issue_value_siprits+total_issue_value_non_spirits
                    closing_value = blend_value 
                    unit = blend.unit
                    created_by = request.user
                    # average_cost = blend_value / blend_quantity   
                    id = blend.id                                
                    se =Stock_Entry.objects.create(transaction_type=transaction_type,unit=unit,item=blend.brand.wip_blend_item,stock_location=stock_location,blend=blend,quantity = blend_quantity,value=blend_value,created_by=created_by,requisition=requisition)
                    update_stock_ledger(id=se.id)
                                                    
                    messages.success(request,'Blend WIP Entry Successfully made')
                    usl =update_stock_location(id=stock_location.id,receipt_quantity=blend_quantity,receipt_value=blend_value,issue_quantity=0,issue_value=0,unit=unit,item=blend.brand.wip_blend_item)
                    usl.save()
                    
                    
                    Blend.objects.filter(id=id).update(status='400')
                    wip_accounting_entry(id=se.id)
                except Exception as e:
                    messages.error(request,f'Transaction Failed because of {e}')
                    if e:
                        raise db_transaction.TransactionManagementError(f"Rolling back as exception {e} has caused this error")
    else:
        form = BlendWipForm(user=request.user,blend=blend)
    return render(request,'production/blend_wip_form.html',{'form':form})
                
def wip_accounting_entry(id):
    wip = Stock_Entry.objects.filter(id=id,transaction_type=13).last()
    blend = wip.blend
    contra_account   = Account_Chart.objects.select_for_update().get(account_code='2302')
    inventory_account = Account_Chart.objects.select_for_update().get(id=blend.brand.wip_blend_account.id)
    amount = wip.value    
    transaction_type = wip.transaction_type
    transaction_number = wip.transaction_number   
    transaction_date = wip.transaction_date 
    with db_transaction.atomic():
        total_debits = total_credits = 0
        Inv_Transaction.objects.create(
            transaction_type=transaction_type,
            transaction_number=transaction_number,
            transaction_date=transaction_date,
            transaction_cat = 'Debit',
            account_chart = inventory_account,
            debit_amount = amount,
            credit_amount = 0,
            reference = f'Entry for wip blend for blend {blend.brand} vide blend _number{blend.batch_number}'
            )
        update_account_chart(id=inventory_account.id,debit_amount=amount,credit_amount=0)
        total_debits += amount
        Inv_Transaction.objects.create(
            transaction_type=transaction_type,
            transaction_number=transaction_number,
            transaction_date= transaction_date,
            account_chart = contra_account,
            transaction_cat = 'credit',
            credit_amount = amount,
            debit_amount = 0,
            reference = f' Entry for issue of {blend.brand} vide blend _number{blend.batch_number}'
            )
        update_account_chart(id=contra_account.id,debit_amount=0,credit_amount=amount)
        total_credits += amount
        if total_debits != total_credits:
                raise db_transaction.TransactionManagementError("Debit and credit amounts do not match, rolling back transaction.")
        else:
            return redirect('employee_profile')          



def wip_issue(request,id):
    '''Once blend is finished in blend tank and transferred to Blend holidng Tank for resting before issue to bottling'''
    wip = Blend.objects.get(id=id)
    wip_to_issue= Stock_Entry.objects.filter(blend=id,transaction_type=13).last()
    # blend = Blend.objects.get(id=blend in wip for blend in wip)  
    if request.method == 'POST':
        form = BlendWipIssueForm(request.POST)
        if form.is_valid():
            try:
                with db_transaction.atomic():
                    transaction_type = form.cleaned_data['transaction_type']                
                    quantity = form.cleaned_data['quantity']                    
                    stock_location = form.cleaned_data['stock_location']                    
                    to_location = form.cleaned_data['to_location']
                    # average_cost = wip.average_cost
                    blend = wip_to_issue.blend
                    unit = wip_to_issue.blend.unit
                    wip_item = wip_to_issue.blend.brand.wip_blend_item
                    value = round(wip_to_issue.value/wip_to_issue.quantity * quantity,4)    
                    
                    #Create Stock Entry for WIP Blend Issue                
                    
                    se =Stock_Entry.objects.create(transaction_type=transaction_type,blend=blend,stock_location=stock_location,to_location=to_location,issue_quantity=quantity,issue_value=value,unit=unit,created_by=request.user,item=blend.brand.wip_blend_item,transaction_cat='Issue')
                    
                    #updte issueing stock location
                    
                    upl_issue=update_stock_location(id=stock_location.id,issue_quantity=quantity,issue_value=value,receipt_quantity=0,receipt_value=0,unit=unit,item=blend.brand.wip_blend_item)
                    upl_issue.save()     
                    
                    #update stock ledger for issued item
                                
                    update_stock_ledger(id=se.id)
                    
                    #create stock_entry for receiving location
                    
                    ser =Stock_Entry.objects.create(transaction_type=transaction_type,blend=blend,stock_location=stock_location,to_location=to_location,quantity=quantity,value=value,unit=unit,created_by=request.user,item=blend.brand.finished_blend_item,transaction_cat='Receipt')
                    
                    #update receiving stock location
                    upl_receopt = update_stock_location(id=to_location.id,receipt_quantity=quantity,receipt_value=value,issue_quantity=0,issue_value=0,unit=unit,item=wip_item)
                    upl_receopt.save()
                    
                    #update Blend status to 500
                    
                    Blend.objects.filter(id=blend.id).update(status='500')
                    
                    #update stock ledger for receiving item
                    
                    update_stock_ledger(id=ser.id)                       
                    messages.success(request,'WIP Blend issue Entry Successfully made')
                    
                    #Create Accounting Entry
                                        
                    wip_issue_accounting_entry(id)
            #Handle exceptions       
            except Exception as e:
                messages.error(request,f'Transaction Failed because of {e}')
                if e:
                    raise db_transaction.TransactionManagementError(f"Rolling back as exception {e} has caused this error")
    else:
        form = BlendWipIssueForm()
    return render(request,'production/blend_issue_form.html',{'form':form})
                            

def wip_issue_accounting_entry(id):  
    blend = Blend.objects.get(id=id)
    wip = Stock_Entry.objects.filter(blend=blend,transaction_type=14).last()  
    wip_account = Account_Chart.objects.select_for_update().get(id=wip.blend.brand.wip_blend_account.id)
    inventory_account = Account_Chart.objects.select_for_update().get(id=wip.blend.brand.finished_blend_account.id)      
    transaction_type = wip.transaction_type
    transaction_number = wip.transaction_number   
    transaction_date = wip.transaction_date 
    issue_value = wip.value
    #Generate Accounting Entries
    with db_transaction.atomic():
        total_debits = total_credits = 0
        Inv_Transaction.objects.create(
            transaction_type=transaction_type,
            transaction_number=transaction_number,
            transaction_date=transaction_date,
            transaction_cat = 'Debit',
            account_chart = inventory_account,
            debit_amount = issue_value,
            credit_amount = 0,
            reference = f'Entry for issue of wip blend for blend {blend.brand} vide blend _number{blend.batch_number}'
            )
        update_account_chart(id=inventory_account.id,debit_amount=issue_value,credit_amount=0)
        total_debits += issue_value
        Inv_Transaction.objects.create(
            transaction_type=transaction_type,
            transaction_number=transaction_number,
            transaction_date= transaction_date,
            account_chart = wip_account,
            transaction_cat = 'credit',
            credit_amount = issue_value,
            debit_amount = 0,
            reference = f' Entry for receipt of {blend.brand} vide blend _number{blend.batch_number}'
            )
        update_account_chart(id=wip_account.id,debit_amount=0,credit_amount=issue_value)
        total_credits += issue_value
        print(total_credits,total_debits)
        if total_debits != total_credits:
                raise db_transaction.TransactionManagementError("Debit and credit amounts do not match, rolling back transaction.")
        else:
            return redirect('employee_profile')          
                
                
def daily_production_plan(request):
    if request.method == 'POST':
        form = DailyProductionPlanForm(request.POST,user=request.user)
        if form.is_valid():
            instance =form.save(commit=False)
            instance.created_by= request.user 
            instance.unit = request.user.user_roles.unit
            instance.save()
            return redirect('daily_production_plan_line')
    else:
        form = DailyProductionPlanForm(user=request.user)
    return render(request,'production/daily_production_plan_form.html',{'form':form})

def daily_production_plan_line(request):   
    if request.method == 'POST':
        form = DailyProductionPlanLineForm(request.POST,user=request.user)
        decision_form = AddItemForm(request.POST)
        if form.is_valid() and decision_form.is_valid():
            instance =form.save(commit=False)
            instance.item = Map_Brand_SKU_Item.objects.get(brand=instance.brand,sku=instance.sku).item
            instance.unit = request.user.user_roles.unit
            instance.blend = instance.plan.blend
            instance.save()
            messages.success(request,'Daily Production  Successfully made')
            response = decision_form.cleaned_data['add_item']
            if response == 'yes':
                return redirect(daily_production_plan_line)
            else:                
                return redirect('employee_profile')
    else:
        form = DailyProductionPlanLineForm(user=request.user)
        decision_form = AddItemForm()
    return render(request,'production/daily_production_plan_line_form.html',{'form':form,'decision_form':decision_form})        
        
        
            
        
    
def daily_production_plan_list(request):
    list = Production_Plan_Line.objects.all()
    return render(request,'production/daily_production_plan_list.Html',{'list':list})


def update_daily_production_plan(request,id):
    pi = Production_Plan_Line.objects.get(id=id)
    if request.method =='POST':
        form = UpdateDailyProductionPlanForm(request.POST,instance=pi)
        if form.is_valid():
            form.save()
            messages.success(request,'Daily Production Plan Successfully updated')
        else:
            messages.error(request,'Something went Wrong Pls. Try again or contact system admin')
        return redirect('employee_profile')
            
    else:
        form = UpdateDailyProductionPlanForm(instance=pi)
    return render(request,'production/daily_production_plan_form.html',{'form':form})    
    

def blend_requisition(request,id):
    '''This view is used to make a requisition for issue to DG to Blend'''
    plan = Production_Plan_Line.objects.get(id=id) #Fetch the production plan 
    production = plan.production #Get the production quantity
    blend = plan.plan.blend  #Get the blend from related daily production plan
    brand = plan.brand  #Get the brand
    sku = plan.sku #Get the sku
    unit = plan.plan.unit    #Get the unit
    if request.method == 'POST':
        form = MaterialRequisionForm(request.POST)
        if form.is_valid():
            try:
                with db_transaction.atomic():            
                    transaction_type = form.cleaned_data['transaction_type']                    
                    bom = Blend_Bom.objects.get(brand=brand,bom_type='Bottling',sku=sku)
                    # ic(bom)
                    bom_items = Bom_Items.objects.filter(bom=bom.id)
                    success_flag = False
                    requisition_number = generate_document_number(
                        transaction_type=transaction_type,
                        model_class=Material_Requisition,
                        unit=unit,
                        number_field='requisition_number'                        
                    )
                    
                    for items in bom_items:                        
                        unit = unit
                        created_by = request.user
                        item = items.item
                        
                        # Check if available quantity is greater than required quantity
                    
                        available_quantity = Stock_Ledger.objects.filter(item=item).last().closing_quantity
                        required_quantity =round( production * items.bom_quantity,2)
                        #check if available quantity is greater than required quantity
                        if available_quantity >= required_quantity:
                            #create a material requisition object
                            Material_Requisition.objects.create(requisition_number=requisition_number,transaction_type=transaction_type,blend=blend,item=item,required_quantity=required_quantity,unit=unit,created_by=created_by,uom=item.item_unit,bom=bom)
                            #update the success flag
                            success_flag = True
                        else:
                            messages.error(request, f'Closing Quantity of {item} is less than required Quantity')
                            break
                                    
                    if success_flag:
                        messages.success(request,'Blend Requisition Successfully made')
                        Blend.objects.filter(id=blend.id).update(status='600')
                        return redirect('employee_profile')
                                
                    else:
                        messages.error(request, f'Closing Quantity of {item} is less than required Quantity') 
            except Exception as e:
                raise db_transaction.TransactionManagementError(f"Rolling back as exception {e} has caused this error")
    else:
        form = MaterialRequisionForm()
    return render(request,'production/blend_requisition_form.html',{'form':form})
            
@login_required
def bottling_requisition_awating_issue(request):
    bottling_requisition_awating_issue = Blend.objects.filter(status='600',unit=request.user.user_roles.unit)
    return render(request,'stock/bottling_material_awaiting_issue_form.html',{'bottling_material_awaiting_issue':bottling_requisition_awating_issue})

def open_production_plan(request): 
    """This view is used to list all the open production plan where production is yet to be made"""
    open_plan = Daily_Production_Plan.objects.filter(bottled=False,unit=request.user.user_roles.unit)    
    return render(request,'production/open_production_plan.html',{'open_plan':open_plan})

def production_entry(request,id):
    '''This view is used to make production entry at end of production line'''
    if request.method == 'POST':
        form = ProductionReportForm(request.POST,user=request.user)
        if form.is_valid():
            try:
                with db_transaction.atomic():
                    transaction_type = form.cleaned_data['transaction_type']
                    plan = form.cleaned_data['plan']
                    unit = request.user.user_roles.unit
                    created_by = request.user                    
                    Production_Report.objects.create(transaction_type=transaction_type,plan=plan,unit=unit,created_by=created_by)
                    messages.success(request,'Production Entry Successfully made')
                    return redirect('production_entry_line')
            except Exception as e:
                messages.error(request,f'{e}')
                
    else:
        form = ProductionReportForm(user=request.user)  
    return render(request,'production/production_report_form.html',{'form':form})


def production_entry_line(request):
    if request.method == 'POST':
        form = ProductionReportLineForm(request.POST,user=request.user)
        decision_form = AddItemForm(request.POST)
        if form.is_valid() and decision_form.is_valid():
            try:
                with db_transaction.atomic():
                    instance=form.save(commit=False)
                    instance.unit = request.user.user_roles.unit            
                    instance.item = Map_Brand_SKU_Item.objects.get(brand=instance.brand,sku=instance.sku).item
                    instance.blend = instance.report.plan.blend    
                    instance.save()    
                    messages.success(request,'Production Entry Successfully made')
                    Production_Report.objects.filter(id=instance.report.id).update(status=True)
                    id = instance.blend.id
                    response = decision_form.cleaned_data['add_item']
                    if response == 'yes':
                        return redirect(production_entry_line)
                    else:                
                        return redirect('rm_consumption',id=id)
            except Exception as e:
                messages.error(request,f'{e}')
    else:
        form = ProductionReportLineForm(user=request.user)
        decision_form = AddItemForm()
    return render(request,'production/production_report_line_form.html',{'form':form,'decision_form':decision_form})



def raw_material_consumption(request, id):
    # Fetch all stock entries related to the transaction
    stock_entries = Stock_Entry.objects.filter(Q(blend=id) & Q(bom__bom_type ='Bottling')) 
            
    StockEntryFormSet = modelformset_factory(Stock_Entry, form=RawMaterialConsumptionForm, extra=0)
    if request.method == 'POST':
        formset = StockEntryFormSet(request.POST, queryset=stock_entries)

        if formset.is_valid():  
            try:          
                for form, stock_entry in zip(formset, stock_entries):                
                    with db_transaction.atomic():
                        # Save form data into the object without committing                        
                        stock_entry = form.save(commit=False)
                        transaction_type= stock_entry.transaction_type
                        transaction_number = stock_entry.transaction_number
                        transaction_date =stock_entry.transaction_date
                        blend= stock_entry.blend
                        sku = stock_entry.bom.sku
                        issue_quantity = stock_entry.issue_quantity
                        issue_value = stock_entry.issue_value
                        return_quantity = stock_entry.return_quantity or 0  # Get return_quantity from the form

                        if issue_quantity == 0:
                            raise ValueError("Issued quantity cannot be zero.")

                        # Calculate and update the return_value
                        stock_entry.return_value = round(stock_entry.issue_value / issue_quantity,4) * return_quantity
                        stock_entry.issue_quantity = issue_quantity - return_quantity
                        stock_entry.issue_value = issue_value - stock_entry.return_value
                        # Save the updated object to the database
                        stock_entry.save()
                        update_location=update_stock_location(id=stock_entry.stock_location.id,receipt_quantity=0,receipt_value=0,issue_quantity=stock_entry.issue_quantity,issue_value=stock_entry.issue_value,unit=stock_entry.unit,item=stock_entry.item)
                        update_location.save()
                        update_stock_ledger(id=stock_entry.id)                           

                        total_debits=total_credits=0                               
                        account_map = Brand.objects.get(id=blend.brand.id)
                        if account_map:
                            wip_account = account_map.wip_account
                        else:
                            raise ValueError("Account mapping not found for the brand")
                            
                        inv_debit_transaction=Inv_Transaction(transaction_date=transaction_date,
                            transaction_type =transaction_type,
                            transaction_number=transaction_number,
                            transaction_cat='Debit',
                            debit_amount = stock_entry.issue_value,
                            credit_amount= 0 ,
                            account_chart=wip_account,
                            reference=f"RM  consumption for {blend} tfd to WIP Account" ,
                            unit = stock_entry.unit)
                        inv_debit_transaction.save()
                    
                            
                        total_debits += stock_entry.issue_value
                        
                            
                        update_account_chart(id=wip_account.id,debit_amount=stock_entry.issue_value,credit_amount=0)
                            
                        inv_credit_transaction =Inv_Transaction(transaction_date=transaction_date,transaction_type=transaction_type,transaction_number=transaction_number,transaction_cat='Credit',credit_amount=stock_entry.issue_value,debit_amount=0,account_chart=stock_entry.item.account,reference=f'Issue entry towards {stock_entry.blend}',unit=stock_entry.unit)
                        inv_credit_transaction.save()
                    
                            
                        total_credits += stock_entry.issue_value
                        
                        update_account_chart(id=stock_entry.item.account.id,debit_amount=0,credit_amount=stock_entry.issue_value)
                messages.success(request,'Transaction Successfull')
                
                plan = Daily_Production_Plan.objects.get(blend=blend)
                id = plan.id 
                return redirect('update_wip_overhead_cost',id)
            except Exception as e:
                messages.error(request,f"Transaction Failed becuase of: {e}")
                if e:
                    raise db_transaction.TransactionManagementError(f"Rolling back as exception {e} has caused this error")

        else:
            print('Formset is invalid.')
            print(formset.errors)

    else:
        formset = StockEntryFormSet(queryset=stock_entries)

    return render(request, 'production/dg_consumption.html', {'formset': formset})


def update_wip_overhead_cost(request,id):
    '''This view is used to update the WIP account with overhead cost'''
    with db_transaction.atomic():
        try:    
            plan = Daily_Production_Plan.objects.get(id=id)
            blend = plan.blend                
            finished_goods = Production_Report.objects.get(plan=plan)
            related_entries = finished_goods.production_report_line.all()
            rm_cost_dict =  Stock_Entry.objects.filter(Q(blend=blend) & Q(bom__bom_type ='Bottling')).aggregate(total_value=Sum('issue_value'))
            rm_cost = rm_cost_dict['total_value']
            absorbed_overheads = Overheads_Absorbed.objects.filter(unit=plan.unit)
            total_absorbed_amount = Decimal(0)  # Initialize as Decimal
            # absorbed_overhead=Decimal(0)
            transaction_type = Transaction_Type.objects.get(id=18)
            transaction_number = generate_document_number(
            model_class= Blend_Overhead_Absorbed,
            transaction_type=transaction_type,
            unit = plan.blend.unit,
            number_field='transaction_number'
            )
            if related_entries:
                for r in related_entries:               
                    production = r.production
                    sku = r.sku 
                    report = r.report  
                    item = r.item 
                    ic(production,sku,report,item)            
                    for overhead in absorbed_overheads:
                        try:                        
                            if overhead.is_active:
                                overhead_id = overhead.name                        
                                rate = Decimal(overhead.rate)
                                absorbed_amount = production * rate
                                overhead.amount = absorbed_amount
                                total_absorbed_amount += absorbed_amount
                                overhead.blend = plan.blend  
                                overhead.unit = plan.unit
                                r.production_value = rm_cost + total_absorbed_amount
                                r.average_cost = round(r.production_value/production,4)
                                r.save()
                                
                                
                                #Create absorbed overhead object
                                
                                absorbed_oh =Blend_Overhead_Absorbed(
                                    transaction_type=transaction_type,
                                    transaction_number = transaction_number,
                                    transaction_date = timezone.now(),
                                    report = report,
                                    blend = plan.blend,
                                    unit = plan.unit,
                                    overhead = Overheads_Absorbed.objects.get(id=overhead_id.id),
                                    amount = absorbed_amount                                
                                )
                                #save absorbed Overhead object
                                absorbed_oh.save()
                                #create accounting entry for absorbed overhead
                                credit_account = overhead_id.account
                                credit_transaction =Inv_Transaction(
                                    transaction_type = transaction_type,
                                    transaction_number=transaction_number,
                                    transaction_cat = 'Credit',
                                    debit_amount = 0,
                                    unit = plan.unit,
                                    credit_amount = absorbed_amount,
                                    account_chart = credit_account,
                                    reference = f'Overhead absorbed for {report}'
                                    
                                )
                                credit_transaction.save()
                                update_account_chart(id=credit_account.id,debit_amount=0,credit_amount=absorbed_amount)
                                sum_debit_amount = total_absorbed_amount 
                                # ic(sum_debit_amount)
                        except:
                            messages.error(request, 'Overhead Cost update failed')
                            raise db_transaction.TransactionManagementError('Rolling back the transaction')             
                        
                debit_account = blend.brand.wip_account.id
                account_chart = Account_Chart.objects.get(id=debit_account)
                ic(debit_account)
                debit_transaction =Inv_Transaction(
                    transaction_type=transaction_type,
                    transaction_number=transaction_number,
                    transaction_date= timezone.now(),
                    transaction_cat = 'Debit',
                    debit_amount = sum_debit_amount,
                    credit_amount = 0,
                    unit = plan.unit,
                    account_chart = account_chart,
                    reference = f'Overhead absorbed for {report}'
                
                )
                ic(debit_transaction)
                debit_transaction.save()
                update_account_chart(id=debit_account,debit_amount=sum_debit_amount,credit_amount=0) 
                
                #Create Stock Entry for finished goods item
                mapped_object = Map_Brand_SKU_Item.objects.get(brand=blend.brand,sku=sku)  
                stock_location = mapped_object.stock_location
                stock_receipt= Stock_Entry(
                    transaction_type=transaction_type,
                    transaction_number=transaction_number,
                    transaction_date = timezone.now(),
                    quantity = production,
                    value = r.production_value,
                    blend= blend,
                    item= r.item,
                    stock_location= Unit_Sub_Location.objects.get(id=stock_location.id),
                    unit = blend.unit,
                    transaction_cat ='Receipt'
                )
                stock_receipt.save()
                #fetch the id of the stock entry
                id = stock_receipt.pk 
                
                #update the stock location
                
                usl =update_stock_location(id=stock_location.id,receipt_quantity=production,receipt_value=r.production_value,issue_quantity=0,issue_value=0,unit=blend.unit,item=r.item)
                usl.save()
                #update the stock ledger
                update_stock_ledger(id)
                
                #Create Accounting Entry for finished goods item
                  
                finished_goods_account = mapped_object.account
                finished_goods_transaction= Inv_Transaction(
                    transaction_type=transaction_type,
                    transaction_number=transaction_number,
                    transaction_date = timezone.now(),
                    debit_amount = total_absorbed_amount + rm_cost,
                    credit_amount = 0,
                    unit = blend.unit,
                    account_chart = finished_goods_account,
                    transaction_cat = 'Debit',
                    reference = f"Amount trf to fg accounts from WIP account agaist {report}"
                )
                finished_goods_transaction.save()    
                
                update_account_chart(id=finished_goods_account.id,debit_amount=total_absorbed_amount + rm_cost,credit_amount=0)
                
                #Create Accounting Entry for WIP Account credit 
                
                wip_credit_transaction = Inv_Transaction(
                    transaction_type=transaction_type,
                    transaction_number=transaction_number,
                    transaction_date = timezone.now(),
                    transaction_cat ='Credit',
                    credit_amount = total_absorbed_amount + rm_cost,
                    account_chart = Account_Chart.objects.get(id=debit_account),
                    debit_amount = 0,
                    unit = blend.unit,
                    reference = f"Amount tfd to fg accounts from WIP account agaist {report}"
                    
                ) 
                wip_credit_transaction.save()
                
                #update the WIP Account
                
                update_account_chart(id=debit_account,debit_amount=0,credit_amount=total_absorbed_amount + rm_cost)      
            
                messages.success(request, 'Overhead Cost successfully updated in WIP Account')
                #Update the status of the production plan
                Daily_Production_Plan.objects.filter(id=plan.id).update(bottled=True) 
                #update the status of the blend
                Blend.objects.filter(id=blend.id).update(status='600')   
            else:
                messages.error(request, 'No related production line entries found')
        except Exception as e:
            messages.error(request, f'An error {e} caused this error, rolling back the transaction')
            if e:
                raise db_transaction.TransactionManagementError(
                f'An error {e} caused this error, rolling back the transaction'
            )
    
    return redirect('employee_profile')

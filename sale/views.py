from django.shortcuts import render
from django.utils import timezone
from django.core.exceptions import ValidationError
# Create your views here.
from django.shortcuts import render,redirect,HttpResponse
from masters.models import Case,State_Excise_levies,State,Customer,TCS,Account_Chart
from accounts.models import Inv_Transaction
from stock.models import Stock_Ledger,Stock_Entry
from .forms import Cost_Card_Form_Haryana,Cost_Card_Form_Punjab,Permit_Entry_Form,Permit_Item_Form,Vehicle_For_Loading_Form,Sale_Invoice_Form
from production.models import Map_Brand_SKU_Item
from inventory.forms import AddItemForm
from inventory.functions import update_account_chart,update_stock_location
from stock.views import update_stock_ledger
from .models import *
from django.template import loader
from django.http import HttpResponse
from django.db.models import Sum
from django.db.models import Q,Sum
from icecream import ic
from django.template import loader
from django.contrib.auth.decorators import login_required
from simpleeval import simple_eval
from django.db import transaction as db_transaction
from django.contrib import messages
from icecream import ic
from decimal import Decimal
# Create your views here.


def state_list(request):
    state_list = State.objects.all()    
    return render(request,'sale/state_list.html',{'list':state_list})
   


@login_required
def cost_card_form(request, id):
    if id == 1:
        header_info_list = []
        if request.method == 'POST':
            form = Cost_Card_Form_Haryana(request.POST)
            if form.is_valid():
                state = form.cleaned_data['state']
                brand = form.cleaned_data['brand']
                sku = form.cleaned_data['sku']
                edp = form.cleaned_data['edp']
                msp = form.cleaned_data['msp']
                valid_from = form.cleaned_data['valid_from']
                valid_till = form.cleaned_data['valid_till']
                # Extract Case information
                instance = form.save(commit=False)
                instance.created_by = request.user
                # instance.save()
                case = Case.objects.get(sku=sku)
                bottle = case.bottle
                bl = case.bl
                pl = case.pl
                al = case.al
                sku = case.sku                
                current_date = timezone.now().today()
                # Calculate Excise duty based on slab values
                cost_card_elements = State_Excise_Levies_Rate.objects.filter(state=state, valid_from = valid_from,valid_till=valid_till)
                merged_dict = {}
                excise_duty = 0  # Initialize excise_duty              
                excise_dict = {}
                for levy_element in cost_card_elements:                
                    if levy_element.slab:                        
                        duty_slab = Slabs.objects.get(Q(min_value__lte=edp) & Q(max_value__gte=edp))                       
        
                        # Define safe variable dictionary
                        duty_info_dict = {
                        'levy_name': str(duty_slab.levy_name),
                        'levy_rate': duty_slab.levy_rate,
                        'pl': pl,
                        'levy_formula': str(duty_slab.levy_formula)
                        }
                    
                        # Safely evaluate the formula using simple_eval
                        levy_name = duty_info_dict['levy_name']                                         
                        levy_amount= simple_eval(duty_info_dict['levy_formula'], names=duty_info_dict)                        
                        excise_dict[levy_name] = levy_amount                        
                        levy_element.levy_amount = levy_amount
                        State_Excise_Levies_Rate.objects.filter(levy_name=duty_slab.levy_name).update(levy_amount=levy_element.levy_amount)
                        
                    else:
                        pass
                
                    # duty_info_list.append(duty_info_dict)
                    duty_element_dict = {
                        'edp':edp,
                        'name': str(levy_element.levy_name),
                        'levy_rate': levy_element.levy_rate,
                        'pl': pl,                       
                        'formula': str(levy_element.levy_formula),
                        'bottling_fee':merged_dict.get('bottling_fee',0),
                        'excise_duty': excise_dict['excise_duty']
                        }
                
                   
                    # ic(duty_element_dict)
                    levy_name = duty_element_dict['name']                    
                    levy_amount = round(simple_eval(duty_element_dict['formula'], names=duty_element_dict), 2)
                    duty_element_dict[levy_name] = levy_amount
                    merged_dict[duty_element_dict['name']] = levy_amount
                    levy_element.levy_amount = levy_amount
                    levy_element.save()
                    State_Excise_Levies_Rate.objects.filter(levy_name=1).update(levy_amount=excise_dict.get('excise_duty'))
               
                    
                vat = merged_dict.get('vat-haryana')
                permit_fee = merged_dict.get('permit_fee')
                bottling_fee = merged_dict.get('bottling_fee')
                retail_permit_fee = merged_dict.get('retail_permit_fee')
                incidence_of_fl_2 = merged_dict.get('incidence_of_fl-2')
                excise_duty = excise_dict.get('excise_duty')
                # ic(vat)
                landed_to_wholesale = (edp + bottling_fee +excise_duty + vat + permit_fee)
                wholesale_margin = round(landed_to_wholesale * 10 /100,2)
                landed_to_retail = round(landed_to_wholesale + wholesale_margin + retail_permit_fee,2)
                retail_margin = msp - incidence_of_fl_2 - landed_to_retail
                consumer_price = landed_to_retail +retail_margin + incidence_of_fl_2
                ecp_per_bottle = round(consumer_price /  bottle)
                
                context ={
                    'brand':brand,
                    'sku': sku,
                    'bottle':bottle,
                    'bl' : bl,
                    'pl' : pl,
                    'al' :al,
                    'edp':edp,
                    'bottling_fee':bottling_fee,
                    'excise_duty':excise_duty,
                    'vat':vat,
                    'permit_fee':permit_fee,
                    'landed_to_wholesale':landed_to_wholesale,
                    'wholesale_margin':wholesale_margin,
                    'landed_to_retail':landed_to_retail,
                    'retail_permit_fee':retail_permit_fee,
                    'retail_margin':round(retail_margin,2),
                    'incidence_of_fl_2':incidence_of_fl_2,
                    'consumer_price':consumer_price,
                    'ecp' : ecp_per_bottle
                }                
                
                # Load the template and render it with the context
                template = loader.get_template('sale/cost_card.html')
                
                return HttpResponse(template.render(context, request))
        else:
            form = Cost_Card_Form_Haryana()
        return render(request, 'sale/cost_card_form.html', {'form': form, 'list': header_info_list})
    elif id == 6:
        if request.method == "POST":
            form = Cost_Card_Form_Punjab(request.POST)
            if form.is_valid():
                state = form.cleaned_data['state']
                brand = form.cleaned_data['brand']
                sku = form.cleaned_data['sku']
                edp = form.cleaned_data['edp']
                mop = form.cleaned_data['mop']
                form.save(commit=False)
                # Extract Case information
                case = Case.objects.get(sku=sku)
                bottle = case.bottle
                bl = case.bl
                pl = case.pl
                al = case.al
                sku = case.sku
                current_date =timezone.now().today()
                cost_card_elements = State_Excise_Levies_Rate.objects.filter(state=state, valid_from__lte = current_date,valid_till__gte=current_date)
                duty_info_list = []
                merged_dict = {}
                excise_duty = 0  # Initialize excise_duty
                for levy_element in cost_card_elements:                
                    if levy_element.slab:
                        duty_slab = Slabs.objects.get(Q(min_value__lte=edp) & Q(max_value__gte=edp))
                        duty_info_dict = {
                            'levy_name':duty_slab.levy_name,
                            'levy_rate': duty_slab.levy_rate,
                            'pl': pl, 
                            'levy_formula': str(duty_slab.levy_formula)}
                        
                        levy_amount = simple_eval(duty_info_dict['levy_formula'], names= duty_info_dict)
                    
                    
                    duty_element_dict = {
                        'edp':edp,
                        'name': str(levy_element.levy_name),
                        'levy_rate': levy_element.levy_rate,
                        'bl':bl,
                        'bottle':bottle,
                        'pl': pl,
                        'formula': str(levy_element.levy_formula)
                    }
                    # ic(duty_element_dict)
                        
                    levy_amount = round(eval(duty_element_dict['formula'],{},duty_element_dict), 2)
                        # ic(levy_amount)
                    levy_element.levy_amount = levy_amount
                    levy_element.save()
                    merged_dict[duty_element_dict['name']] = levy_amount
                    merged_dict['edp'] = edp
                                     
                additional_excise_fee = merged_dict.get('additional_license_fee')
                bottling_fee = merged_dict.get('bottling_fee')
                cctv_charges = merged_dict.get('cctv_charges')
                excise_develepment_cess = merged_dict.get('excise_development_cess')
                freight = merged_dict.get('freight')
                hologram_charges = merged_dict.get('hologram_charges')                
                permit_fee = merged_dict.get('permit_fee')
                special_license_fee = merged_dict.get('special_license_fee')
                track_trace_charges = merged_dict.get('track_and_trace_charges')
                
                wsp_without_excise_vat =round((edp + bottling_fee + additional_excise_fee + excise_develepment_cess + freight + hologram_charges + track_trace_charges + cctv_charges + permit_fee),2)                                
                l_1_margin = round(edp * 10 /100,2)
                excise_duty_l_1 = round((wsp_without_excise_vat + l_1_margin)*1/100,2)
                # ic(excise_duty_l_1)
                special_license_fee = merged_dict['special_license_fee']
                wsp_without_vat = wsp_without_excise_vat +excise_duty_l_1 + special_license_fee
                # ic(wsp_without_vat)
                vat_at_bond = round(wsp_without_vat * 1.1 / 100,2)
                # ic(vat_at_bond)
                l1_landed = wsp_without_vat + vat_at_bond
                # ic(l1_landed)
                l1_vat = (wsp_without_vat + l_1_margin) *1.1 /100
                ic(l1_vat)
                vat_credit = vat_at_bond
                l1_landed_after_vat_credit = l1_landed + l1_vat - vat_credit +l_1_margin + special_license_fee               
                # calculate msp
                if edp < 400:
                    msp = round(edp * 4 / bottle,0)
                elif edp > 400 and edp < 800:
                    msp = round(edp * 3.5 / bottle,0)
                elif edp > 800 and edp < 1200:
                    msp = round(edp * 3 / bottle,0)
                elif edp > 1200 and edp < 1600:
                    msp = round(edp * 2.5 / bottle,0)
                elif edp > 1600 and edp < 3000:
                    msp = round(edp * 2 / bottle,0)
                else:
                    msp = round(edp *1.75 /bottle,0)
                
                excise_duty_l2 = round((mop-msp) * bottle,0)
                landed_to_retail = l1_landed_after_vat_credit + excise_duty_l2
                retail_margin = (mop*bottle)-landed_to_retail
                context ={
                    'brand':brand,
                    'sku': sku,
                    'bottle':bottle,
                    'bl' : bl,
                    'pl' : pl,
                    'al' :al,
                    'edp':edp,
                    'bottling_fee':bottling_fee,
                    'excise_duty':excise_duty,
                    # 'vat':vat,
                    'permit_fee':permit_fee,
                    'landed_to_wholesale':l1_landed_after_vat_credit,
                    'wholesale_margin':l_1_margin,
                    'landed_to_retail':landed_to_retail,
                    # 'retail_permit_fee':retail_permit_fee,
                    'retail_margin':round(retail_margin,2),
                    # 'incidence_of_fl_2':incidence_of_fl_2,
                    # 'consumer_price':consumer_price,
                    'mop' : mop
                }                
                
                # Load the template and render it with the context
            template = loader.get_template('sale/cost_card.html')
               
            return HttpResponse(template.render(context, request))                
            
        else:
            form = Cost_Card_Form_Punjab()
        return render(request,'sale/cost_card.html',{'form':form})
            

def permit_entry(request):
    if request.method == "POST":
        with db_transaction.atomic():
            try:
                form = Permit_Entry_Form(request.POST)
                if form.is_valid():
                    instance =form.save(commit=False)
                    instance.created_by = request.user
                    instance.save()
                    messages.success(request,'Permit Entry Successful')
                else:
                    messages.error(request,f'Error in form submission: {form.errors}')
            except Exception as e:
                messages.error(e)
        return redirect('permit_item_entry')
    else:
        form = Permit_Entry_Form()
    return render(request,'sale/permit_entry_form.html',{'form':form})   

def permit_pending_sale_invoice(request):
    pending_permit = Permit.objects.filter(status=100)
    return render(request,'sale/pending_permit_list.html',{'pending_permit':pending_permit})
    
def permit_item_entry(request):
    if request.method == 'POST':        
        try:
            with db_transaction.atomic():
                form = Permit_Item_Form(request.POST)
                decision_form = AddItemForm(request.POST)
                if form.is_valid() and decision_form.is_valid():
                    # Extract data from form
                    permit = form.cleaned_data['permit']
                    product_item = form.cleaned_data['product_item']
                    brand = form.cleaned_data['brand']
                    sku = form.cleaned_data['sku']
                    quantity = form.cleaned_data['quantity']
                    uom = form.cleaned_data['uom']                   
                    permit_item = Permit_Item(permit=permit, product_item=product_item, brand=brand, sku=sku, quantity=quantity, uom=uom)
                    permit_item.save()                    
                    messages.success(request, f'{brand} successfully added to {permit}')
                    # Process the decision form
                    response = decision_form.cleaned_data['add_item']
                    if response == 'yes':
                        return redirect('permit_items')
                    else:                        
                        return redirect('employee_profile')
                else:
                    # Log form errors for debugging
                 
                    messages.error(request, f'{form.errors} -- {decision_form.errors}')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    else:
        form = Permit_Item_Form()
        decision_form = AddItemForm()
    return render(request, 'sale/permit_item_form.html', {'form': form, 'decision_form': decision_form})           

def vehicle_for_loading(request):
    if request.method == 'POST':
        form = Vehicle_For_Loading_Form(request.POST,user=request.user)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user            
            instance.save()
            vehicle_number = instance.vehicle_number
            messages.success(request,f'Entry for {vehicle_number} successfully made')
        else:
            messages.error(request,'Something went wrong Pls try againt or contact admins')
            
    else:
        form = Vehicle_For_Loading_Form(user=request.user)
    return render(request,'sale/vehicle_for_loading_form.html',{'form':form})


def sale_invoice(request,id):
    """
    View: sale_invoice
    This view handles the creation of a sales invoice based on a permit. It performs the following operations:
    1. Validates the permit's validity based on its expiration date.
    2. Creates a new sales invoice instance if the permit is valid.
    3. Iterates through the items in the permit to calculate costs, levies, and other charges.
    4. Saves the calculated levies and invoice items to the database.
    5. Updates the total invoice amount, including TCS (Tax Collected at Source).
    6. Updates the permit status upon successful invoice creation.
    Parameters:
    - request: The HTTP request object.
    - id (int): The ID of the permit to generate the sales invoice for.
    Returns:
    - Redirects to the 'permit_entry' page.
    Exceptions:
    - Rolls back the database transaction and displays an error message if any exception occurs during the process.
    Notes:
    - The view uses Django's `db_transaction.atomic()` to ensure atomicity of the database operations.
    - If the permit has expired, an error message is displayed, and the user is redirected to the 'permit_entry' page.
    """
    if request.method =='POST':
        form = Sale_Invoice_Form(request.POST)
        if form.is_valid():
            excise_pass = form.cleaned_data['excise_pass']
            excise_pass_date= form.cleaned_data['excise_pass_date']
            lr_number = form.cleaned_data['lr_number']
            lr_date = form.cleaned_data['lr_date']
            truck = form.cleaned_data['truck']
            truck_number = truck.vehicle_number
        
            #fetch permit against which invoice to created
            permit = Permit.objects.get(id=id,status=100)
            transaction_type = Transaction_Type.objects.get(id=20)
            tcs_rate = TCS.objects.get(transaction_type=transaction_type).rate
            permit_number = permit.permit_number
            permit_date = permit.permit_date
            valildy = permit.valid_till
            customer = permit.customer
            customer_account = permit.customer.account
            currend_date = timezone.datetime.now().date()        
            if valildy >= currend_date:
                with db_transaction.atomic():
                    try:
                        #save invoice headers
                        sale_invoice_instance = Sales_Invoice(transaction_type = transaction_type,permit=permit,created_by =request.user,excise_pass=excise_pass,excise_pass_date=excise_pass_date,lr_number=lr_number,lr_date=lr_date,truck=truck)
                        sale_invoice_instance.save()
                        transaction_number =sale_invoice_instance.invoice_number                
                        transaction_type =transaction_type
                        transaction_date = sale_invoice_instance.invoice_date
                        #Fetch permit items   
                        lines = Permit_Item.objects.filter(permit=permit)        
                        for line in lines:
                            quantity = line.quantity
                            item = line.product_item
                            item_account = line.product_item.account
                            brand = line.brand
                            sku = line.sku
                            currend_date = timezone.now().today()        
                            cost_card = Cost_Card.objects.get(brand=brand,sku=sku,state=customer.unit.state,valid_from__lte=currend_date,valid_till__gte= currend_date)
                            edp = Decimal(cost_card.edp)
                            basic_amount = edp * quantity                                        
                            levies = State_Excise_Levies_Rate.objects.filter(state=customer.unit.state,valid_from__lte=currend_date,valid_till__gte = currend_date,payee='Company')
                            levies_total = 0  
                            total_debits = total_credits = 0                  
                            for levy in levies:
                                levy_name = levy.levy_name.id
                                # ic(levy_name)
                                levy_rate = levy.levy_rate
                                levy_unit = levy.levy_unit
                                levy_account = levy.account
                                levy_amount = levy.levy_amount * quantity
                                levies_total += levy_amount
                                invoice_levies = Sale_Invoice_Levies(invoice=Sales_Invoice.objects.get(id = sale_invoice_instance.id),levy_name=State_Excise_Levies_Rate.objects.get(levy_name=levy_name,state=customer.unit.state),levy_amount=levy_amount)
                                invoice_levies.save()
                                
                                levy_entry = Inv_Transaction(
                                    transaction_number=transaction_number,
                                    transaction_type=transaction_type,
                                    transaction_date = transaction_date,
                                    transaction_cat = 'Credit',
                                    debit_amount = 0,
                                    credit_amount = levy_amount,
                                    account_chart = Account_Chart.objects.get(id=levy_account.id),
                                    reference = f'credit Entry towards sales of {quantity} case of {brand}--{sku} againt permit {permit.permit_number} dated {permit.permit_date}'
                                )
                                ic(levy_entry)
                                levy_entry.save()
                                update_account_chart(id=levy_account.id,debit_amount=0,credit_amount=levy_amount)
                                total_credits += levy_amount
                                ic(total_credits)
                            sale_invoice_item_instance=Sales_Invoice_Item(basic_amount=basic_amount,invoice_quantity = quantity,brand=brand,sku=sku,invoice= Sales_Invoice.objects.get(id=sale_invoice_instance.id),product_item = Permit_Item.objects.get(product_item= item,permit=permit),levies_amount=levies_total)
                            ic(sale_invoice_item_instance)
                            sale_invoice_item_instance.save()
                            
                            Sale_Invoice_Levies.objects.filter(invoice=sale_invoice_instance.id).update(invoice_line=sale_invoice_item_instance.id)                    
                        total_invoice_amount_without_tcs = basic_amount+levies_total                
                        tcs = total_invoice_amount_without_tcs * tcs_rate / 100                
                        total_invoice_amount= total_invoice_amount_without_tcs + tcs 
                        Sales_Invoice.objects.filter(id=sale_invoice_instance.id).update(basic_amount=basic_amount,levies_total=levies_total,total_invoice_amount=total_invoice_amount,tcs=tcs)
                        Permit.objects.filter(id=id).update(status='300')
                        #Create accounting Entry
                        mapping = Map_Brand_SKU_Item.objects.get(brand=brand,sku=sku)
                        sale_account = mapping.sale_account
                        cogs_account = mapping.cost_of_sale_account
                        finished_goods_account = mapping.account
                        stock_location = mapping.stock_location
                        customer_debit=Inv_Transaction(
                            transaction_number=transaction_number,
                            transaction_type=transaction_type,
                            transaction_date = transaction_date,
                            transaction_cat = 'Debit',
                            debit_amount = total_invoice_amount,
                            credit_amount = 0,
                            account_chart = Account_Chart.objects.get(id=customer_account.id),
                            unit = customer.unit,
                            reference = f"Debit Entry towards sales of {quantity} case of {brand}--{sku} againt permit {permit.permit_number} dated {permit.permit_date}"
                        )
                        customer_debit.save()
                        update_account_chart(id=customer_account.id,debit_amount=total_invoice_amount,credit_amount=0)
                        ic(customer_debit)
                        total_debits += total_invoice_amount
                        
                    
                        sale_credit =Inv_Transaction(
                            transaction_number=transaction_number,
                            transaction_type=transaction_type,
                            transaction_date = transaction_date,
                            transaction_cat = 'Credit',
                            credit_amount = basic_amount,
                            debit_amount = 0,
                            account_chart = Account_Chart.objects.get(id=sale_account.id),
                            unit = customer.unit,
                            reference = f"Sale Entry towards sales of {quantity} case of {brand}--{sku} againt permit {permit.permit_number} dated {permit.permit_date} to {customer}"
                        )
                        sale_credit.save()
                        update_account_chart(id=sale_account.id,debit_amount=0,credit_amount=basic_amount)
                        ic(sale_credit)
                        total_credits += basic_amount
                        tcs_entry =Inv_Transaction(
                            transaction_number=transaction_number,
                            transaction_type=transaction_type,
                            transaction_date = transaction_date,
                            transaction_cat = 'Credit',
                            credit_amount = tcs,
                            debit_amount = 0,
                            account_chart = Account_Chart.objects.get(id=74),
                            unit = customer.unit,
                            reference = f"tcs towards sales of {quantity} case of {brand}--{sku} againt permit {permit.permit_number} dated {permit.permit_date} to {customer}"
                        )
                        tcs_entry.save()
                        update_account_chart(id=74,debit_amount=0,credit_amount=tcs)
                        ic(tcs_entry)
                        total_credits += tcs
                        ic(total_debits,total_credits)
                        if not total_debits == total_credits:                    
                            raise ValidationError('Debit and Credit do not match. rolling backs')
                            
                        # Booking cost of sale Entry
                        stock_ledger_instance = Stock_Ledger.objects.filter(item=item,unit=customer.unit).last()
                        closing_stock = stock_ledger_instance.closing_quantity
                        closing_value = stock_ledger_instance.closing_value
                        rate = Decimal(round(closing_value / closing_stock, 4)) if closing_stock > 0 else Decimal(0)
                        cost_of_sale = Decimal(round(quantity * rate,4)) if rate > 0 else Decimal(0)
                        stock_entry =Stock_Entry(
                            transaction_number =transaction_number,
                            transaction_date = transaction_date,
                            transaction_type =transaction_type,
                            transaction_cat = 'Issue',
                            issue_quantity = quantity,
                            issue_value = cost_of_sale,
                            item = item,
                            # requisition = permit,
                            stock_location = stock_location,
                            unit = customer.unit,
                            
                        )
                        stock_entry.save()
                        usl =update_stock_ledger(stock_entry.id)
                        ic(usl)
                        us =update_stock_location(stock_location.id,item=item,receipt_quantity=0,receipt_value=0,issue_quantity=quantity,issue_value=cost_of_sale,unit=customer.unit)
                        us.save()
                        ic(us)
                        cogs_entry =Inv_Transaction(
                            transaction_type=transaction_type,
                            transaction_number=transaction_number,
                            transaction_date=transaction_date,
                            transaction_cat = 'Debit',
                            unit = customer.unit,
                            debit_amount = cost_of_sale,
                            credit_amount = 0,
                            account_chart = Account_Chart.objects.get(id = cogs_account.id),
                            reference = f"Cogs towards sales of {quantity} case of {brand}--{sku} againt permit {permit.permit_number} dated {permit.permit_date} to {customer}"
                            
                        )
                        cogs_entry.save()
                        update_account_chart(id=cogs_account.id,debit_amount=cost_of_sale,credit_amount=0)                    
                        inventory_entry =Inv_Transaction(
                            transaction_type=transaction_type,
                            transaction_number=transaction_number,
                            transaction_date=transaction_date,
                            transaction_cat = 'Credit',
                            unit = customer.unit,
                            debit_amount = 0,
                            credit_amount = cost_of_sale,
                            account_chart = Account_Chart.objects.get(id = finished_goods_account.id),
                            reference = f"Cogs towards sales of {quantity} case of {brand}--{sku} againt permit {permit.permit_number} dated {permit.permit_date} to {customer}"
                            
                        )
                        inventory_entry.save()
                        update_account_chart(id=finished_goods_account.id,debit_amount=0,credit_amount=cost_of_sale)                        
                        return redirect('employee_profile')
                                
                    except Exception as e:
                        db_transaction.rollback()
                        messages.error(request,{e})
            else:
                messages.error(request, 'Permit has expired')
                return redirect('employee_profile')
    else:
        form =Sale_Invoice_Form()
    return render(request,'sale/sale_invoice_form.html',{'form':form})
   
        
    
    
        
    

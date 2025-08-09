from django.db import transaction as db_transaction
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction as db_transaction

from django.contrib import messages
# functions.py or utils.py
from django.db.models import Max
from masters.models import *

# from accounts.models import Inv_Transaction  # Import your model
from django.db.models import Q
# from yourapp.models import State_Tax_on_Sale_Of_Goods, Gst_On_Goods

from django.db import models
from django.shortcuts import render
# from stock.models import Stock_Entry,Stock_Ledger,Unit_Sub_Location
def update_stock_ledger(id,model_class1,model_class2):
    stock_entry = model_class1.objects.get(id=id)
    stock_ledger=model_class2.objects.filter(item=stock_entry.item,unit=stock_entry.unit).last()
    if stock_ledger:
        opening_quantity = stock_ledger.closing_quantity
        opening_value = stock_ledger.closing_value
        opening_rate = round(stock_ledger.closing_rate,4)    
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
    if transaction_type.transaction_name == 'MRN':
        quantity = stock_entry.quantity
        value = stock_entry.value
        receipt_rate =round(value/quantity,4)
        stock_ledger = model_class2.objects.create(transaction_type=transaction_type,transaction_number=transaction_number,transaction_date=transaction_date,unit=unit,item=item,receipt_quantity=quantity,receipt_value=value,receipt_rate=receipt_rate,opening_quantity=opening_quantity,opening_value=opening_value,opening_rate=opening_rate,closing_quantity=opening_quantity+quantity,closing_value=opening_value+value,closing_rate=round((opening_value+value)/(opening_quantity+quantity),4),stock_entry=stock_entry)
    elif transaction_type.transaction_name == 'Issue':
        quantity = stock_entry.issue_quantity
        value = stock_entry.issue_value
        issue_rate = round(value/quantity,4)
        stock_ledger = model_class2.objects.create(transaction_type=transaction_type,transaction_number=transaction_number,transaction_date=transaction_date,unit=unit,item=item,issue_quantity=quantity,issue_value=value,issue_rate=issue_rate,opening_quantity=opening_quantity,opening_value=opening_value,opening_rate=opening_rate,closing_quantity=opening_quantity-quantity,closing_value=opening_value-value,closing_rate=round((opening_value-value)/(opening_quantity-quantity),4),stock_entry=stock_entry)
    # elif transaction_type.transaction_name == 'return':
    #     quantity = stock_entry.return_quantity  
    #     value = stock_entry.return_value
    #     return_rate = round(value/quantity,4)
    #     stock_ledger = Stock_Ledger.objects.create(transaction_type=transaction_type,transaction_number=transaction_number,transaction_date=transaction_date,unit=unit,item=item,return_quantity=quantity,return_value=value,return_rate_rate=return_rate,opening_stock=opening_stock,opening_value=opening_value,opening_rate=opening_rate,closing_quantity=opening_stock+quantity,closing_value=opening_value+value,closing_rate=round((opening_value-value)/(opening_stock-quantity),4))


def update_account_chart(id,debit_amount,credit_amount):    
    account = Account_Chart.objects.get(id=id)    
    sub_category = account.sub_category
    category = sub_category.category
    sub_class = category.sub_class
    account_class = sub_class.account_class
    account.debit_amount += debit_amount
    account.credit_amount += credit_amount
    account.closing_balance = account.opening_balance + account.debit_amount - account.credit_amount

    account.save()
    #update sub_category
    sub_category.debit_amount += debit_amount
    sub_category.credit_amount += credit_amount
    sub_category.closing_balance = sub_category.opening_balance + sub_category.debit_amount - sub_category.credit_amount
    sub_category.save()
    # update categroy
    category.debit_amount += debit_amount
    category.credit_amount += credit_amount
    category.closing_balance = category.opening_balance + category.debit_amount - category.credit_amount
    category.save()
    # update sub_class
    sub_class.debit_amount += debit_amount
    sub_class.credit_amount += credit_amount
    sub_class.closing_balance = sub_class.opening_balance +sub_class.debit_amount - sub_class.credit_amount
    sub_class.save()
    
    # update class
    
    account_class.debit_amount += debit_amount
    account_class.credit_amount += credit_amount
    account_class.closing_balance = account_class.opening_balance + account_class.debit_amount - account_class.credit_amount
    account_class.save()
    return account,sub_category,category,sub_class,account_class
        



def update_stock_location(id,item,receipt_quantity,receipt_value,issue_quantity,issue_value,unit ):    
    location = Unit_Sub_Location.objects.get(id= id,unit=unit)
    if location:
        item = item
        location.receipt_quantity = location.receipt_quantity + receipt_quantity        
        location.receipt_value += receipt_value
        location.issued_quantity += issue_quantity
        location.issue_value += issue_value
        location.closing_quantity = location.opening_quantity + location.receipt_quantity - location.issued_quantity
        location.closing_value = location.opening_value + location.receipt_value - location.issue_value
        location.average_rate = round((location.opening_value+location.receipt_value-location.issue_value)/(location.opening_quantity+ location.receipt_quantity-location.issued_quantity),4) if location.closing_quantity > 0 else 0 
        # location.save()
        
        unit_stock_location = location.unit_stock_location 
        item = item       
        unit_stock_location.receipt_quantity += receipt_quantity
        unit_stock_location.receipt_value += receipt_value
        unit_stock_location.issued_quantity += issue_quantity
        unit_stock_location.issue_value += issue_value
        unit_stock_location.closing_quantity = location.opening_quantity + location.receipt_quantity - location.issued_quantity
        unit_stock_location.closing_value = location.opening_value + location.receipt_value - location.issue_value
        unit_stock_location.average_rate = round(unit_stock_location.closing_value/unit_stock_location.closing_quantity,4) if unit_stock_location.closing_quantity > 0 else 0
        # unit_stock_location.save()  
        
        stock_location = unit_stock_location.stock_location
        item = item        
        stock_location.receipt_quantity += receipt_quantity
        stock_location.receipt_value += receipt_value
        stock_location.issued_quantity += issue_quantity
        stock_location.issue_value += issue_value
        stock_location.closing_quantity = location.opening_quantity + location.receipt_quantity - location.issued_quantity
        # location.save()
    else:
        print('Location not found')
    return location
              
  





def generate_unique_transaction_number(model_class,transaction_type, unit):
    """
    Generates a new transaction number based on the last transaction's number.
    
    Args:
        transaction_type (str): The type of the transaction.
        unit (str): The unit associated with the transaction.
        
    Returns:
        str: A new transaction number.
    """
    # Fetch the last transaction for the given unit
    last_transaction = model_class.objects.select_for_update().filter(unit=unit).order_by('-id').first()
    
    if last_transaction and last_transaction.transaction_no:
        # Extract the last number and increment it
        last_number = int(last_transaction.transaction_no.split('/')[-1])
        new_number = last_number + 1
    else:
        # Start from 1 if no previous transaction exists
        new_number = 1
    
    # Format the new transaction number
    return f'{transaction_type}/{unit}/{str(new_number).zfill(5)}'

def gst_on_service(po, value, service, supplier_state):
    cgst=sgst=igst=0
    if po.business == 'Exempt':
        creditable = False
    else:
        creditable = True
    total_tax = 0       
    # Intra-state transaction
    tax_rate = Service.objects.get(id=service.id).gst_rate
    if not tax_rate:
        raise ValidationError('No Rate has been defined for this item')
    tax_amount = value * tax_rate / 100
    if supplier_state != po.unit.state:
        igst = tax_amount
    else:
        cgst = tax_amount / 2
        sgst = tax_amount / 2
    return {'CGST':cgst, 'SGST':sgst, 'IGST':igst, 'creditable':creditable, }


def calculate_tax(po, value,item, supplier_state):
    # Initialize tax variables
    creditable = False
    vat = cst = cgst = sgst = igst = 0
    total_tax = 0
    
    # Check if the item is non-GST
    if item.item_tax_type == 'Non_GST':                
        # Non-GST Tax Calculation
        if supplier_state == po.quotation.unit.state:
            # Apply VAT for intra-state transactions
            taxes = State_Tax_on_Sale_Of_Goods.objects.filter(state=supplier_state).exclude(tax_name='CST')
            if not taxes.exists():
                raise ValidationError('No Rate has been defined for this item')
            for tax in taxes:
                rate = tax.rate
                creditable = tax.creditable
                tax_amount = value * rate / 100
                total_tax += tax_amount
                vat += tax_amount  # Accumulate VAT
        else:
            # Apply CST for inter-state transactions
            taxes = State_Tax_on_Sale_Of_Goods.objects.filter(state=supplier_state).exclude(tax_name='VAT')
            if not taxes.exists():
                raise ValidationError('No Rate has been defined for this item')
            for tax in taxes:
                rate = tax.rate
                creditable = tax.creditable
                tax_amount = value * rate / 100
                total_tax += tax_amount
                cst += tax_amount  # Accumulate CST
    # For GST-based transactions
    else:
        if po.quotation.supplier.supplier_state == po.unit.state:
                # Apply CGST and SGST for intra-state transactions
            taxes = Gst_On_Goods.objects.filter(item=item).exclude(tax_name='IGST')
            if not taxes.exists():
                raise ValidationError('No Rate has been defined for this item')
            for tax in taxes:
                rate = tax.rate
                tax_amount = value * rate / 100
                total_tax += tax_amount
            # Divide equally for CGST and SGST
            cgst = sgst = total_tax / 2
        else:            
            # Apply IGST for inter-state transactions
            taxes = Gst_On_Goods.objects.filter(item=item).exclude(Q(tax_name='CGST') | Q(tax_name='SGST'))
            if not taxes.exists():
                raise ValidationError('No Rate has been defined for this item')
            for tax in taxes:
                rate = tax.rate
                tax_amount = value * rate / 100
                total_tax += tax_amount
                igst += tax_amount
                
    
    return {'VAT':vat, 'CST':cst, 'CGST':cgst, 'SGST':sgst, 'IGST':igst, 'creditable':creditable}

def assign_approver_services(transaction_type, inr_value, unit,cost_center):
    """
    Assign an approver to the Purchase Order (PO) based on the defined levels and monetary limit.
    
    Args:
    - transaction_type: The type of transaction (e.g., PO)
    - inr_value: The monetary value of the transaction
    - unit: The unit for which the approver is being assigned
    
    Returns:
    - The approver user instance if found, otherwise None
    """
    # Find approvers based on transaction type and monetary limit
    approvers = DOA.objects.filter(
        transaction_type=transaction_type,
        monetary_limit__gte=inr_value,
        cost_center=cost_center,
        
    ).order_by('monetary_limit')
    if not approvers.exists():
        messages.error("Error: No approver found for the given transaction type, value, and cost center.")

    # Loop through the approvers to find the correct one
    for approver in approvers:
        if 'Unit Head' in approver.level:
            # Check if there's a unit head approver
            selected_unit = User_Roles.objects.filter(
                unit=unit,
                can_approve=True,
                user_id=approver.user  #  `user` is a ForeignKey in DOA pointing to a `User`
            ).first()

            if selected_unit:
                return selected_unit.user_id  # Return the User instance once assigned

        else:
            # For non-Unit Head approvers, return the User directly
            return approver.user  # Ensure this is returning a `User` instance

    return None  # No approver was assigned


def assign_approver(transaction_type, inr_value, unit):
    """
    Assign an approver to the Purchase Order (PO) based on the defined levels and monetary limit.
    
    Args:
    - transaction_type: The type of transaction (e.g., PO)
    - inr_value: The monetary value of the transaction
    - unit: The unit for which the approver is being assigned
    
    Returns:
    - The approver user instance if found, otherwise None
    """
    # Find approvers based on transaction type and monetary limit
    approvers = DOA.objects.filter(
        transaction_type=transaction_type,
        monetary_limit__gte=inr_value,        
        
    ).order_by('monetary_limit')

    # Loop through the approvers to find the correct one
    for approver in approvers:
        if 'Unit Head' in approver.level:
            # Check if there's a unit head approver
            selected_unit = User_Roles.objects.filter(
                unit=unit,
                can_approve=True,
                user_id=approver.user  #  `user` is a ForeignKey in DOA pointing to a `User`
            ).first()

            if selected_unit:
                return selected_unit.user_id  # Return the User instance once assigned

        else:
            # For non-Unit Head approvers, return the User directly
            return approver.user  # Ensure this is returning a `User` instance

    return None  # No approver was assigned



def calculate_state_tax(po, taxes):
    total_tax = 0
    for tax in taxes:
        rate = tax.rate
        creditable = tax.creditable
        tax_amount = po.inr_value * rate / 100
        total_tax += tax_amount
    return total_tax,creditable

def calculate_gst(po, taxes, intra_state):
    cgst = 0
    sgst = 0
    igst = 0
    
    for tax in taxes:
        rate = tax.rate
        if intra_state:
            cgst += po.inr_value * rate / 100
            sgst += po.po_value * rate / 100
        else:
            igst += po.po_value * rate / 100
    
    return (cgst, sgst) if intra_state else igst
    


def calculate_tds(supplier,service_classification,inr_value):
    # Check if the supplier has a lower TDS rate defined
    
    supplier_exists = Lower_TDS.objects.filter(supplier=supplier).exists()
    tds_amount = 0
    if supplier_exists:
        # If the supplier has a lower TDS rate, use that rate        
        tds_rate = Lower_TDS.objects.get(supplier=supplier).rate
        tds_amount = inr_value * tds_rate / 100
    else:      
    
        if not service_classification:
            raise ValidationError('Service Classification not found')
    
        tds = TDS.objects.filter(service_classification=service_classification)
        tds_amount = 0
        if tds.exists():
            for t in tds:
                rate = t.rate
                tds_amount += inr_value * rate / 100
        else:    
            raise  ValidationError('No TDS Rate has been defined for this item')     
        
    return tds_amount

def calculate_custom(inr_value,item):
    igst =0
    custom = 0
    # Fetch all custom duties related to the item
    custom_duty_entries = Custom_Duty.objects.filter(item=item)

    named_dict = {}

    # Loop through each duty entry to handle multiple taxes
    for custom_duty in custom_duty_entries:
        tax_name = custom_duty.tax_name
        rate = custom_duty.rate
        levy_amount = inr_value * rate / 100
        
        # Add the tax name and levy amount to the dictionary
        named_dict[tax_name] = levy_amount
    if 'IGST' in named_dict.keys():
        custom = named_dict['Custom Duty']
        igst = named_dict['IGST']
    else:
        custom = named_dict['Custom Duty']
        igst = 0   
        
    print(custom,igst)
    return custom,igst



def generate_transaction_no(unit, transaction_type,model):
    """
    Generate a unique transaction number in the format unit+transaction_type/000001.
    If a previous transaction exists for the given unit and transaction type, increment the number.
    Otherwise, start from 1.
    
    Args:
        unit (str): The unit of the transaction (e.g., department or branch).
        transaction_type (str): The type of the transaction (e.g., 'Debit' or 'Credit').

    Returns:
        str: The generated transaction number.
    """
    # Get the latest transaction_no for the given unit and transaction_type
    latest_transaction = model.objects.filter(
        unit=unit,
        transaction_type=transaction_type
    ).aggregate(Max('transaction_no'))  # Find the max transaction_no
    
    # Extract the latest number (if available)
    latest_no = latest_transaction['transaction_no__max']
    
    if latest_no:
        # Increment the number from the latest transaction_no
        number = int(latest_no.split('/')[-1]) + 1
    else:
        # Start from 1 if no previous transaction exists
        number = 1

    # Format the new transaction_no as unit+transaction_type/000001
    transaction_no = f"{unit}{transaction_type}/{str(number).zfill(6)}"
    
    return transaction_no



def generate_document_number(model_class, transaction_type, unit, number_field):
    """
    Generate a new document number for the specified model, document type, and unit.
    :param model_class: The Django model class to query
    :param transaction_type: The type of transaction (e.g., 'po', 'mrn')
    :param unit: The unit related to the document
    :param number_field: The field in the model that holds the document number
    :return: The new document number
    """
    if not isinstance(number_field, str) or not number_field:
        raise ValueError("The number_field must be a valid non-empty string")

    try:
        with db_transaction.atomic():
            # Fetch the last document ordered by the document number
            last_document = model_class.objects.filter(unit=unit,transaction_type=transaction_type).order_by(number_field).last()
            
            if last_document and getattr(last_document, number_field):
                last_number_str = getattr(last_document, number_field)

                # Determine if the last number has a prefix or is in old format
                last_document.id = last_document
                if '/' in last_number_str:
                    # New format with prefix (e.g., unit/transaction_type/xxxx)
                    last_number = int(last_number_str.split('/')[-1])
                    new_document_number = f'{unit}/{transaction_type}/{str(last_number + 1).zfill(4)}'
                else:
                    # Old format without prefix, assume numeric only
                    last_number = int(last_number_str)
                    new_document_number = f'{unit}/{transaction_type}/{str(last_number + 1).zfill(4)}'
            else:
                # Start with 0001 if no last document exists
                new_document_number = f'{unit}/{transaction_type}/0001'

            return new_document_number

    except Exception as e:
        # Handle any other unforeseen errors
        raise ValueError(f"Error generating document number: {str(e)}")



def determine_supply_nature(supplier_state, recipient_location, is_imported, is_sez, supply_type):
    """
    Determines the nature of supply: Inter-State or Intra-State based on the location of the supplier and the recipient.

    :param supplier_location: (str) Location of the supplier (state or union territory)
    :param recipient_location: (str) Location of the recipient (state or union territory)
    :param is_imported: (bool) Whether the goods/services are imported into India (default is False)
    :param is_sez: (bool) Whether the supply involves an SEZ (default is False)
    :param supply_type: (str) Type of supply: "goods" or "services" (default is "goods")
    
    :return: (str) Nature of the supply - either "Inter-State" or "Intra-State"
    """

    # Inter-State supply conditions
    if supplier_state != recipient_location:
        return "Inter-State"

    if is_imported:
        return "Inter-State"

    if is_sez:
        return "Inter-State"

    # Special cases for goods and services
    if supply_type == "goods":
        if supplier_state == recipient_location and not is_sez:
            return "Intra-State"
    elif supply_type == "services":
        if supplier_state == recipient_location and not is_sez:
            return "Intra-State"

    # Default case, intra-state supply
    return "Intra-State"

# def place_of_supply_goods(movement,bill_ship,)


class PlaceOfSupplyServices:
    def __init__(self, service_type, recipient_registered, recipient_location=None, supplier_location=None, performance_location=None, immovable_property_location=None, event_location=None, transportation_destination=None, export=False):
        self.service_type = service_type
        self.recipient_registered = recipient_registered  # Boolean: True if recipient is registered
        self.recipient_location = recipient_location
        self.supplier_location = supplier_location
        self.performance_location = performance_location
        self.immovable_property_location = immovable_property_location
        self.event_location = event_location
        self.transportation_destination = transportation_destination
        self.export = export

    def determine_place_of_supply(self):
        # Section 12: Within India
        if not self.export:
            # 1. General Rule: If recipient is registered, use recipient's location; if not, use supplier's location
            if self.recipient_registered:
                return self.recipient_location
            else:
                return self.supplier_location

            # 2. Services requiring physical performance (e.g., training, repairs, etc.)
        if self.service_type == "performance" and self.performance_location:
                return self.performance_location

            # 3. Services related to immovable property (e.g., construction, renting)
        if self.service_type == "immovable_property" and self.immovable_property_location:
                return self.immovable_property_location

            # 4. Services related to an event (e.g., cultural or sports events)
        if self.service_type == "event" and self.event_location:
                return self.event_location

        # Section 13: Outside India (Export of services)
        else:
            # 1. General Rule: Location of the recipient (for exports)
            if self.recipient_location:
                return self.recipient_location

            # 2. Performance-based services outside India (e.g., physical services performed outside India)
            if self.service_type == "performance" and self.performance_location:
                return self.performance_location

            # 3. Services related to immovable property outside India
            if self.service_type == "immovable_property" and self.immovable_property_location:
                return self.immovable_property_location

            # 4. Transportation of goods outside India
            if self.service_type == "transportation" and self.transportation_destination:
                return self.transportation_destination

        return "Cannot determine place of supply"

# Example usage:

# Section 12: Within India, recipient is registered
# pos1 = PlaceOfSupplyServices(service_type="general", recipient_registered=True, recipient_location="Bangalore", supplier_location="Chennai").determine_place_of_supply()
# print(f"Place of Supply (Within India - Registered Recipient): {pos1}")

# # Section 12: Within India, recipient is unregistered
# pos2 = PlaceOfSupplyServices(service_type="general", recipient_registered=False, supplier_location="Chennai").determine_place_of_supply()
# print(f"Place of Supply (Within India - Unregistered Recipient): {pos2}")

# # Section 12: Within India - Immovable property-related services
# pos3 = PlaceOfSupplyServices(service_type="immovable_property", recipient_registered=True, immovable_property_location="Goa").determine_place_of_supply()
# print(f"Place of Supply (Within India - Immovable Property): {pos3}")

# # Section 13: Outside India (Export of services, performance-based service)
# pos4 = PlaceOfSupplyServices(service_type="performance", recipient_registered=True,recipient_location="New York", export=True, performance_location="Paris").determine_place_of_supply()
# print(f"Place of Supply (Outside India - Performance): {pos4}")

# # Section 13: Outside India (Export of services, transportation of goods)
# pos5 = PlaceOfSupplyServices(service_type="transportation",recipient_registered=True, transportation_destination="Canada", export=True).determine_place_of_supply()
# print(f"Place of Supply (Outside India - Transportation): {pos5}")

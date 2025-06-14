import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testinv.settings')
django.setup()

from inventory.models import Purchase_Order ,Po_Lcr_Join,Service,Gate_Entry,Material_Receipt_Note,Quotation
from inventory.forms import GenerateMrnForm,Po_Lcr_Join
from masters.models import Custom_Duty,User,State_Excise_taxes_On_Goods,State_Tax_on_Sale_Of_Goods,Gst_On_Goods,Account_Chart,DOA,User,User_Roles,Item
from stock.models import Stock_Entry,Blend,Stock_Ledger,Stock_Entry
from django.db.models import Q 
from django.core.exceptions import ValidationError
from .functions import update_stock_location,update_stock_ledger
from accounts.models import Inv_Transaction
from django.db import transaction as db_transaction
from inventory.views import generate_mrn
from django.http import request
from icecream import ic
from stock.models import Stock_Entry,Stock_Ledger

# id = Stock_Entry.objects.get(id=14)
stock_ledger =update_stock_ledger(id=14,model_class1=Stock_Entry, model_class2=Stock_Ledger)
ic(stock_ledger)
# generate_mrn(10,user=request.user)

# update_stock_location(id=1,receipt_quantity=3000,receipt_value=30000,issue_quantity=0,issue_value=0)

# def account_entry(blend):
#     if blend == blend:
#         wip_account = Account_Chart.objects.get(id=35)
#         credit_ena = Account_Chart.objects.get(id=1)
#         credit_cab = Account_Chart.objects.get(id=2)
#         issued_items = Stock_Entry.objects.filter(blend= blend)
#         issue_list= []
#         for item in issued_items:
#             issue_dict ={
#             'item' : item.item,
#             'issue': item.issue_value                    
#             }            
#             issue_list.append(issue_dict)
#         for items  in issue_list:
#             item = items['item']
#             issue = items['issue']
#         account = Item.objects.get(account=credit_ena)
      
      

# account_entry(1)
    
        # wip_debit = blend_value
        # with db_transaction.atomic():
        #     total_debits =0
        #     total_credit =0
                                
            # Inv_Transaction.objects.create(
            #     account_chart = credit_ena,
            #     credit_amount = issue_dict['issue'],
            #     debit_amount = 0,
            #     reference = f'Towards issue of {item} in blend id {blend}'                           
                
            # )
            # total_credit += credit_ena
            
            # Inv_Transaction.objects.create(               
            #     account_chart = cab_credit,
            #     credit_amount = credit_cab,
            #     debit_amount = 0,
            #     reference = f'Towards issue of {item} in blend id {self.blend}'                           
                
            # )
            # total_credit += credit_cab
            # Inv_Transaction.objects.create(
            #     transaction_type = self.transaction_type,
            #     transaction_cat = 'Debit',
            #     unit = self.unit,
            #     account_chart = wip_account,
            #     debit_amount = wip_debit,
            #     credit_amount = 0,
            #     reference = f'WIP Entry for {self.blend}'                           
                
            # )
            # total_debits += wip_debit
            # if total_debits != total_credit:
            #     print('Debit and credit donot match')


# def calculate_tax(po, lcr, supplier_state):
#     # Fetch the latest Po_Lcr_Join and Purchase_Order objects
#     lcr = Po_Lcr_Join.objects.filter(lcr_id=lcr).last()    
#     po = Purchase_Order.objects.filter(id=po).last()    

#     # Initialize tax variables
#     creditable = False
#     vat = cst = cgst = sgst = igst = 0
#     total_tax = 0

#     # Check if the item is non-GST
#     if lcr.lcr.item.item_tax_type == 'Non_GST':        
#         # Non-GST Tax Calculation
#         if supplier_state == lcr.lcr.unit.state:
#             # Apply VAT for intra-state transactions
#             taxes = State_Tax_on_Sale_Of_Goods.objects.filter(state=supplier_state).exclude(tax_name='CST')
#             if taxes is None:
#                 raise ValidationError('No Rate has been defined for this item')
#             for tax in taxes:
#                 rate = tax.rate
#                 creditable = tax.creditable
#                 tax_amount = po.inr_value * rate / 100
#                 total_tax += tax_amount
#                 vat += tax_amount  # Accumulate VAT
#                 print(38,vat)

#         else:
#             # Apply CST for inter-state transactions
#             taxes = State_Tax_on_Sale_Of_Goods.objects.filter(state=supplier_state).exclude(tax_name='VAT')
#             if taxes is None:
#                 raise ValidationError('No Rate has been defined for this item')
#             for tax in taxes:
#                 rate = tax.rate
#                 creditable = tax.creditable
#                 tax_amount = po.inr_value * rate / 100
#                 total_tax += tax_amount
#                 cst += tax_amount  # Accumulate CST
#                 print(cst)

#     # For GST-based transactions
#     else:
#         if lcr.lcr.supplier.supplier_state == po.unit.state:
#             # Apply CGST and SGST for intra-state transactions
#             taxes = Gst_On_Goods.objects.filter(item=po.quotation.item).exclude(tax_name='IGST')
#             if taxes is None:
#                 raise ValidationError('No Rate has been defined for this item')
#             for tax in taxes:
#                 rate = tax.rate
#                 tax_amount = po.inr_value * rate / 100
#                 total_tax += tax_amount

#             # Divide equally for CGST and SGST
#             cgst = sgst = total_tax / 2
#             print(61,cgst,sgst)

#         else:
#             print(67,True)
#             # Apply IGST for inter-state transactions
#             taxes = Gst_On_Goods.objects.filter(item=po.quotation.item).exclude(Q(tax_name='CGST') | Q(tax_name='SGST'))
#             if taxes is None:
#                 raise ValidationError('No Rate has been defined for this item')
#             for tax in taxes:
#                 rate = tax.rate
#                 tax_amount = po.inr_value * rate / 100
#                 total_tax += tax_amount
#                 igst += tax_amount
#                 print(70,igst) 
    
#     return vat, cst, cgst, sgst, igst, creditable

# calculate_tax(28,3,'Maharashtra')


# def calculate_custom(inr_value,item):
#     igst =0
#     custom = 0
#     # Fetch all custom duties related to the item
#     custom_duty_entries = Custom_Duty.objects.filter(item=item)

#     named_dict = {}

#     # Loop through each duty entry to handle multiple taxes
#     for custom_duty in custom_duty_entries:
#         tax_name = custom_duty.tax_name
#         rate = custom_duty.rate
#         levy_amount = inr_value * rate / 100
        
#         # Add the tax name and levy amount to the dictionary
#         named_dict[tax_name] = levy_amount
#     custom = named_dict['Custom Duty']
#     igst = named_dict['IGST']
        
#     print(custom,igst)
#     return custom,igst

# calculate_custom(6090000,4)



# def assign_approver(transaction_type, inr_value,unit):
#     """
#     Assign an approver to the Purchase Order (PO) based on the defined levels and monetary limit.
    
#     Args:
#     - po: The purchase order instance
#     - po_value: The monetary value of the PO
#     - request: Optional request object to send error messages (required if using Django messages)
    
#     Returns:
#     - The approver user if found, otherwise None
#     """
#     # Find approvers based on transaction type and monetary limit
#     approvers = DOA.objects.filter(
#         transaction_type=transaction_type,
#         monetary_limit__gte= inr_value
#     ).order_by('monetary_limit')
    
#     # Loop through the approvers to find the correct one
#     for approver in approvers:
#         if 'Unit Head' in approver.level:
#             # Check if there's a unit head approver
#             selected_unit = User_Roles.objects.filter(
#                 unit=unit,
#                 can_approve=True,
#                 user_id=approver.user
#             ).first()

#             if selected_unit:
#                approver = selected_unit.user_id               
#                return selected_unit.user_id  # Return the user ID once assigned
#             break
              
#         else:
#             approver = approver.user           
#             return approver # Return the user ID once assigned
        

#     return None  # No approver was assigned

# assign_approver(2,6090000,1)



# def calculate_custom(base_value, item):
#     total_levy = 0
#     custom_list = []  # Use a list to hold all custom duty details
#     custom_duty = Custom_Duty.objects.filter(item=item)    
    
#     for customs in custom_duty:
#         name = customs.tax_name
#         rate = customs.rate
#         levy_amount = base_value * rate / 100
#         total_levy += levy_amount
        
#         # Append a dictionary for each tax name and its corresponding details
#         custom_list.append({
#             'name': name,
#             'rate': rate,
#             'levy_amount': levy_amount,                   
#         }) 
    
#     return custom_list, total_levy  # Return the list and total levy


# # calculate_custom(100,4)
# custom_duties, total_levy = calculate_custom(100,4)
# for duty in custom_duties:
#     tax_name = duty['name']
#     levy_amount = duty['levy_amount']
#     specific_dict={
#         tax_name :levy_amount
#     }                  
#     print(specific_dict)


# def calculate_freight(po,lcr):
#     po = Purchase_Order.objects.get(id=po)
#     lcr = Po_Lcr_Join.objects.get(id=lcr)    
#     if po.quotation.delivery_terms == 'Ex-Factory':
#                     freight = lcr.freight.freight
#                     toll_tax = lcr.freight.toll_tax
#                     totafreight = freight + toll_tax
                    

#                     # Calculate tax on freight service
#                     if lcr.freight.service.supplier.supplier_state != po.unit.state:
#                         igst_freight = freight * lcr.freight.service.service.gst_rate / 100
#                         print(igst_freight)
                                        
#                     else:
#                         cgst_freight = freight * lcr.freight.service.service.gst_rate / 200
#                         sgst_freight = freight * lcr.freight.service.service.gst_rate / 200             
#                         print(cgst_freight,sgst_freight)
         
# calculate_freight(8,6)



# def calculate_custom(item):
#     base_value = 6264000
#     total_levy = 0
#     custom_duty = Custom_Duty.objects.filter(item=item)
#     custom_duty_list = []
#     for custom in custom_duty:        
#         name = custom.tax_name
#         rate = custom.rate
#         levy_amount = base_value * rate / 100
#         total_levy += levy_amount
#     handling_charges = (base_value +total_levy) *1 /100       
#     custom_dir = {
#         'name': name,
#         'rate': rate,
#         'total_levy': total_levy,
#         'handling_charges': handling_charges
        
#     }
#     custom_duty_list.append(custom_dir)

#     inventory_debit_amount = base_value +total_levy+handling_charges
#     supplier_credit_amount = base_value
#     custom_duty_credit_amount = total_levy + handling_charges
    
#     return custom_duty_list, inventory_debit_amount,supplier_credit_amount,custom_duty_credit_amount

# calculate_custom(4)



# def freight_purchase_order(id):   
#     #  calculate applicable freight
#     po = Purchase_Order.objects.get(id=id) 
#     transaction_type = 'FPO'
#     business =po.business
#     unit_state = po.unit.state
#     lcr = Po_Lcr_Join.objects.get(po_id=po)
#     lcr_freight = lcr.freight.freight
#     lcr_mode = lcr.freight.mode
#     lcr_service = lcr.freight.service.service.id    
#     lcr_transporter = lcr.freight.service.supplier
#     supplier_state = lcr_transporter.supplier_state
#     service = Service.objects.get(id=lcr_service)
#     sac = service.sac_code
#     service_name = service.service_name
#     service_type = service.service_type
#     rate = service.gst_rate
#     mode= service.payment_mode
#     gst_amount = lcr_freight * rate / 100
#     # created_by= request.user
#     cgst=sgst=igst=0
#     if unit_state == supplier_state:
#         cgst = gst_amount / 2 or 0
#         sgst = gst_amount / 2 or 0
#     else:
#         igst = gst_amount or 0
    
    
    
#     print(business,lcr_freight,lcr_mode,lcr_service,lcr_transporter,rate,cgst,sgst,igst,service_name,service_type,sac,mode)
    
# freight_purchase_order(6)
    
# service_purchase_order(6)
    # if po.quotation.delivery_terms =='Ex-Factory':
    #     freight = lcr.
    #     # Calculate tax on freight service
    #     if service.tras   supplier_state != po.unit.state:
    #         taxes = Service.objects.get(tax_name = 'IGST')
    #         tax_name = 'IGST'
    #         igst_freight = freight * lcr.freight.freight_gst_rate / 100
    #     else:
    #         cgst_freight = freight* lcr.freight.freight_gst_rate / 200
    #         sgst_freight = freight * lcr.freight.freight_gst_rate / 200
    #     tax_on_freight = cgst_freight + sgst_freight + igst_freight
    # else:
    #     freight =0



# def calculate_tds(state):
#     cha_charges = Supplier_Service.objects.filter(service=1)   
#     total_charges = 0
#     for charges in cha_charges:            
#         ass_type= charges.supplier.assessee_type   
#         service = charges.service_id
#         print(service)
#         supplier_state = charges.supplier.supplier_state
#         gst_rate = charges.service.gst_rate
#         lower_rate = charges.lower_rate
#         fee_name = charges.fee_name
#         fee_rate = charges.rate
#         total_charges += fee_rate    
#     cha_gst = total_charges*gst_rate / 100
#     if supplier_state == state:
#         cgst = cha_gst/2
#         sgst = cha_gst /2
#     else:
#         igst = cha_gst   
        
#     if charges.lower_rate:
#         pass
#     else:
#         if  ass_type == 'Individual' or ass_type == 'HUF':       
#             tds = TDS.objects.get(service_classification = service)
#             rate = tds.rate
#             tds_amount = total_charges * rate / 100
#         else:
#             tds = TDS.objects.filter(service_classification = service).first()
#             rate = tds.rate
#             tds_amount = total_charges * rate / 100
#     return tds_amount
        


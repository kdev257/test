from django.shortcuts import render,redirect 
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth import login,logout,authenticate
from masters.models import User,User_Roles,Supplier_Profile,User_Roles
from stock.models import Blend,Material_Requisition
from sale.models import Permit
from production.models import Blend_WIP
from service.models import Service_Quotation,Service_Quotation_Items,Service_Order,Service_Order_Items
from django.db import transaction as db_transaction
from django.contrib import messages
from inventory.forms import *
from inventory.models import Mrn_Items
from .forms import UserRoleForm , CustomAuthenticationForm, SupplierProfileForm, Registrationform
from django.db.models import Q
from icecream import ic
from django.contrib.auth.decorators import login_required


# Create your views here.

def userloginview(request):
    with db_transaction.atomic():
        if request.method=='POST':
            fm = CustomAuthenticationForm(request=request,data=request.POST)
            if fm.is_valid():
                name = fm.cleaned_data['username']
                pw =fm.cleaned_data['password']
                user=authenticate(username=name,password=pw)
                if user is not None:
                    login(request,user)
                    messages.success(request,(f'Login Successful...Welcome {user}'))
                    if user.user_type == 'Goods_Supplier' or user.user_type == 'Service_Provider' or user.user_type == 'Transporter':
                        supplier=Supplier_Profile.objects.filter(user=user).exists()
                        if supplier:
                            return redirect('view_supplier_profile')
                        else:  
                            pass                          
                            return redirect('supplier_profile')
                    elif user.user_type == 'Employee':
                        emp = User_Roles.objects.filter(user_id=user).exists()
                        if emp:
                            return redirect('employee_profile')
                        else:
                            return redirect('user_roles')  
                    
        else:
            fm=CustomAuthenticationForm()
        return render(request,'registration/login.html',{'form':fm}) 

def supplier_profile(request):
    with db_transaction.atomic():
        if request.method=='POST':        
            form = SupplierProfileForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.created_by= User.objects.get(id=request.user.id)                
                instance.save()                
                messages.success(request,'Your profile has been created successfully')
                return redirect('view_supplier_profile')
            else:
                messages.error(request,'Your profile could not be created, pls try again or contact admin') 
           
        else:
            form = SupplierProfileForm()
        return render(request,'login/supplierprofile.html',{'form':form})    

def view_supplier_profile(request):
    profile = Supplier_Profile.objects.get(user=request.user.id)
    return render(request,'login/view_profile_page.html',{'profile':profile})



def employee_workspace_page(request):    
    profile = User_Roles.objects.get(user_id=request.user.id)
    unit = profile.unit 

    if profile:
        # Combine filtering logic for created_by and approver
        quote_queryset = Quotation.objects.filter(
            Q(created_by=request.user.id) | Q(approver=request.user.id, approved=False)
        )
        po_queryset = Purchase_Order.objects.filter(
            Q(created_by=request.user.id,) | Q(approver=request.user.id, approved=False)
        )
        # blend_queryset = Blend.objects.filter(created_by=request.user.id)
        ge_queryset = Gate_Entry.objects.filter(Q(created_by=request.user.id),Q(out_time__isnull=True))
        quality_queryset = Gate_Entry.objects.filter(is_quality_ok=False)
        awaiting_queryset = Gate_Entry.objects.filter(is_unloaded=False).count()
        awaiting_quality_queryset = Gate_Entry.objects.filter(is_quality_ok=False).count()
        mrn_queryset = Gate_Entry.objects.filter(is_unloaded=True,is_quality_ok=True,is_mrn_made=False)
        mrn_count = Gate_Entry.objects.filter(is_unloaded=True,is_quality_ok=True,is_mrn_made=False).count()
        mrn_awaiting_stock_location = Mrn_Items.objects.filter(stock_location__isnull = True).count()
        #blend created by user        
        blend_produced_pending_wg_requisition = Blend.objects.filter(status = '100') #Awaiting requisition of WG
        blend_produced_pending_wg_requisition_count = Blend.objects.filter(status = '100').count() #Awaiting requisition of WG
        reqisition_made_pending_wg_issue = Blend.objects.filter(status = '200').count() #WG requisition made, pending issue
        wg_issued_pending_processing = Blend.objects.filter(status = '300').count()
        blend_processed_pending_transfer = Blend.objects.filter(status = '400').count()
        finished_blend_pending_bottling_requistion = Blend.objects.filter(status = '500').count()
        bottling_requisition_made_pending_issue = Blend.objects.filter(status = '600').count()
        dg_issued_pending_bottling = Blend.objects.filter(status = '700').count()
        fg_pending_transfer_fg_area = Blend.objects.filter(status = '800').count()
        blend_bottled = Blend.objects.filter(status=900).count()
        #sale View
        pending_permit_count = Permit.objects.filter(status=100).count() 
        total_quotations = Service_Quotation.objects.filter(Q(created_by=request.user) | Q(approver=request.user)).count()
        total_orders = Service_Order.objects.filter(Q(created_by=request.user) | Q(approver=request.user)).count()
        pending_orders = Service_Order.objects.filter(Q(created_by=request.user)  & Q(status='Pending') | Q(approver=request.user) & Q(status='Pending')).count()
        approved_orders = Service_Order.objects.filter(Q(created_by=request.user)  &  Q(status='Approved') | Q(approver=request.user) & Q(status='Approved')).count()
        ic(approved_orders)
        closed_orders = Service_Order.objects.filter(Q(created_by=request.user) & Q(status='Closed') | Q(approver=request.user) & Q(status='Closed')).count()

    else:
        quote_queryset = None
        po_queryset = None
        ge_queryset = None
        quality_queryset=None
        awaiting_queryset = None
        awaiting_quality_queryset = None
        mrn_count = None
        mrn_awaiting_stock_location = None
        blend_produced_pending_wg_requisition_count =None
        reqisition_made_pending_wg_issue = None
        wg_issued_pending_processing = None
        blend_processed_pending_transfer = None
        finished_blend_pending_bottling_requistion = None
        bottling_requisition_made_pending_issue = None
        dg_issued_pending_bottling = None
        fg_pending_transfer_fg_area = None
        blend_bottled = None
        pending_permit_count = None
        total_quotations = None
        total_orders = None,
        pending_orders = None,
        approved_orders = None,
        closed_orders = None
        

    context = {
        'profile': profile,
        'quote_queryset': quote_queryset,
        'po_queryset' : po_queryset,
        'ge_queryset' : ge_queryset,
        'count' : awaiting_queryset,
        'count_quality':awaiting_quality_queryset,
        'quality_queryset':quality_queryset,
        "mrn_count" :mrn_count,
        'mrn_queryset': mrn_queryset,
        'stock_location': mrn_awaiting_stock_location,
        'blend' : blend_produced_pending_wg_requisition,
        'blend_count':blend_produced_pending_wg_requisition_count,        
        'blend_awaiting_issue':reqisition_made_pending_wg_issue,
        'issued_to_blend' : wg_issued_pending_processing,
        'transfer_blend' : blend_processed_pending_transfer,
        'blend_pending_bottling_requisition':finished_blend_pending_bottling_requistion,
        'bottling_requisition_made':bottling_requisition_made_pending_issue,
        'dg_issued_pending_bottling':dg_issued_pending_bottling,
        'fg_pending_transfer_to_fg_area':fg_pending_transfer_fg_area,
        'blend_bottled':blend_bottled,
        'permit_count': pending_permit_count,
        'total_quotations': total_quotations,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'approved_orders': approved_orders,
        'closed_orders': closed_orders,
    
        
        
                
        
    }
    
    return render(request, 'login/employee_workspace.html', context)


def user_roles(request):
    '''Use this view to define user roles for employees'''
    with db_transaction.atomic():
        if request.method == "POST":
            form = UserRoleForm(request.POST)            
            if form.is_valid():
                form.save()
                messages.success(request,'Your role has created Successfully')
                return redirect('employee_profile')
            else:
                messages.error(request,'Your role cannot created, pls try again of contact admin')
                return redirect(userloginview)
        else:
            form = UserRoleForm()
        return render(request,'login/userrolesform.html',{'form':form})

def landingpage(request):
    return render(request,'login/landingpage.html')

def home(request):
    if  request.user.user_type != "Owner":
        return render(request,'login/home.html')
    else:
        return HttpResponse('<h1>You are not authorised to view this resource</h1>')

def registration(request):
    with db_transaction.atomic():
        if request.method =='POST':
            form = Registrationform(request.POST)        
            if form.is_valid():           
                form.save()
                messages.success(request,'Your registration was successful')
                return redirect('userloginview')
            else:
                messages.error(request,'Your Registration Could not be Completed.Pls Contact Admin')
                
        else:
            form = Registrationform()
        return render(request,'registration/sign-up.html',{'form':form})

def suppiler_details(request):
    with db_transaction.atomic():
        if request.method == 'POST':
            form = SupplierProfileForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request,'Your profile has been created successfully')
            else:
                messages.error(request,'Your profile could not be created,pls try again or contact admin')
        else:
            form = SupplierProfileForm()
        return render(request,'login/supplierprofile.html',{'form':form})

# def order_payment(request,pk): 
#     pk = Maintenance.objects.get(id=pk)
#     client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))

#     DATA = {
#         "amount": pk.bill_amount*100,
#         "currency": "INR",
#         "payment_capture" : 1
#     }
#     payment_order = client.order.create(data=DATA) 
#     payment_order_id = payment_order['id']   
#     context ={'amount':pk.bill_amount,'api_key':settings.RAZORPAY_KEY_ID,'order_id':payment_order_id}
#     return render(request, "login/payment.html",context)


def userlogout(request):
    logout(request)
    return redirect('/')
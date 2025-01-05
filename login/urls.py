from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
path('accounts/',include('django.contrib.auth.urls')),
path('',userloginview, name='userloginview'),
path('landingpage/',landingpage,name='landingpage'),
path('supplier_profile/', supplier_profile, name='supplier_profile'),
path('view_supplier_profile/', view_supplier_profile, name='view_supplier_profile'),
path('employee_profile/', employee_workspace_page, name='employee_profile'),
path('userroles/',user_roles,name='user_roles'),
# path('home/',home,name='home'),
path('register/',registration,name='registration'),
# path('profilcreate/',userprofile,name='profilecreate'), 
# path('updateprofile/<int:pk>',updateuserprofile,name='updateprofile'), 
# path('accounts/profile/',userprofileview,name = 'profile'),
# path('approveowner/<int:pk>',approveflatownerdetail,name='approveowner'),
# path("payment/<int:pk>", order_payment, name="payment"),
path('logout/',userlogout,name = 'logout'),
# path('book_purchase/',book_purchase_bill,name='book_purchase_bill')

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django import forms
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm,PasswordResetForm,AuthenticationForm
from inventory.models import Supplier
from masters.models import Supplier_Profile,User,User_Roles,Company, Unit

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'style': 'font-size: 25px; height: 50px; border: solid 2px;',
        })
        self.fields['password'].widget.attrs.update({
            'style': 'font-size: 25px; height: 50px;border: solid 2px;',
        })
        for field_name, field in self.fields.items():
            field.widget.attrs['style'] += ' font-size: 25px;'

class SupplierProfileForm(forms.ModelForm):
    class Meta:
        model = Supplier_Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'style': 'border: 1px solid #000; padding: 5px;'
            })

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = User_Roles
        fields = '__all__'
    

class Registrationform(UserCreationForm):
    class Meta:
        model = User        
        fields =['username','password1','password2','email','company','user_type']
    
# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = User_Profile
#         fields =['id','username','first_name','last_name','email','user_type','phone_no','address','city','state','pincode','image']
#         Widget={
#             'address': forms.Textarea(attrs={'row':4})
#         }


from django import forms
from .models import Blend_WIP,Daily_Production_Plan,Production_Plan_Line,Production_Report,Production_Report_Line
from masters.models import User_Roles,Transaction_Type
from stock.models import Blend,Stock_Entry


class BlendWipForm(forms.ModelForm):
    class Meta:
        model = Blend_WIP
        fields = 'transaction_type','blend','water'
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        blend = kwargs.pop('blend',None)              
        super(BlendWipForm, self).__init__(*args, **kwargs)
        if blend:
            blend=blend
        if user:
            try:
                user_unit = user.user_roles.unit
            except User_Roles.DoesNotExist:
                user_unit = None

            # Filtering the Purchase Orders based on user unit and approval status
            self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(transaction_name='BWIPR')
            self.fields['blend'].queryset = Blend.objects.filter(unit=user_unit,status=300)
            # self.fields['issue'].queryset = Stock_Entry.objects.filter(unit=user_unit,transaction_type=7,blend=blend)
           

class BlendWipIssueForm(forms.ModelForm):
    '''form to issue blend from process tank to holding tank'''
    class Meta:
        model = Stock_Entry
        fields = 'transaction_type','stock_location','quantity','to_location'
        def __init__(self, *args, **kwargs):
            user = kwargs.pop('user', None)
            blend = kwargs.pop('blend',None)              
            super(BlendWipIssueForm, self).__init__(*args, **kwargs)
            if blend:
             blend=blend
            if user:
                try:
                    user_unit = user.user_roles.unit
                except User_Roles.DoesNotExist:
                    user_unit = None

                # Filtering the Purchase Orders based on user unit and approval status
                self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(transaction_name='Transfer')
             
    
            
class DailyProductionPlanForm(forms.ModelForm):
    class Meta:
        model = Daily_Production_Plan
        fields = 'transaction_type','blend'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(DailyProductionPlanForm, self).__init__(*args, **kwargs)
        if user:
            try:
                user_unit = user.user_roles.unit
            except User_Roles.DoesNotExist:
                user_unit = None

            self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(transaction_name='DPP')
            self.fields['blend'].queryset = Blend.objects.filter(status ='500',unit=user_unit)
                
class DailyProductionPlanLineForm(forms.ModelForm):
    class Meta:
        model = Production_Plan_Line
        fields = 'plan','brand','sku','production','state','line'
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(DailyProductionPlanLineForm, self).__init__(*args, **kwargs)
        if user:
            try:
                user_unit = user.user_roles.unit
            except User_Roles.DoesNotExist:
                user_unit = None

            self.fields['plan'].queryset = Daily_Production_Plan.objects.filter(unit=user_unit,bottled=False)

class UpdateDailyProductionPlanForm(forms.ModelForm):
    class Meta:
        model = Production_Plan_Line
        fields = '__all__'
        # exclude = 'transaction_number',
        
        widgets = {
            'transaction_date': forms.DateInput(attrs={'type': 'date'}),
            'created': forms.DateInput(attrs={'type': 'date'}),
            'modified': forms.DateInput(attrs={'type': 'date'})
        }
        



class ProductionReportForm(forms.ModelForm):
    class Meta:
        model = Production_Report
        fields = 'transaction_type','plan'
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        # blend = kwargs.pop('blend',None)              
        super(ProductionReportForm, self).__init__(*args, **kwargs)
        # if blend:
        #     blend=blend
        if user:
            try:
                unit = user.user_roles.unit
            except User_Roles.DoesNotExist:
                unit = None

            # Filtering the Purchase Orders based on user unit and approval status
            self.fields['transaction_type'].queryset = Transaction_Type.objects.filter(transaction_name='PROD')
            self.fields['plan'].queryset = Daily_Production_Plan.objects.filter(bottled=False,unit=unit)
            
class ProductionReportLineForm(forms.ModelForm):
    class Meta:
        model = Production_Report_Line
        fields = 'report','brand','sku','production','state','line'
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProductionReportLineForm, self).__init__(*args, **kwargs)
        if user:
            try:
                unit = user.user_roles.unit
            except User_Roles.DoesNotExist:
                unit = None

            self.fields['report'].queryset = Production_Report.objects.filter(unit=unit,status = False)

class RawMaterialConsumptionForm(forms.ModelForm):
    class Meta: 
        model= Stock_Entry
        fields = 'id','transaction_type','item','issue_quantity','return_quantity'
        
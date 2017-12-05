from django.forms import ModelForm, Textarea
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import SKU, Invoice, InvoiceItem, Payment, PaymentInvoice, Customer, Branch
from django.db.models import Q
from django.forms.models import BaseModelFormSet
        
class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",  "password1", "password2", 'first_name', 'last_name',"email")

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    

class SKUForm(forms.ModelForm):                                      
    class Meta:
        model = SKU
        fields = ('sku_code', 'description', 'couriervendor', 'product_type', 'zone_type',
                  'zone', 'weight_start', 'weight_end', 'tax_code', 'corporate_price',
                  'walkin_special_price', 'walkin_price')
    def __init__(self, *args, **kwargs):
        super(SKUForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.sku_code:
            self.fields['sku_code'].widget.attrs['readonly'] = True

    def clean_sku_code(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.sku_code
        else:
            return self.cleaned_data['sku_code']
    def clean(self):
        cleaned_data = super(SKUForm, self).clean()
        if cleaned_data['weight_start'] > cleaned_data['weight_end']:
            raise forms.ValidationError("Weight end must be larger than weight start")
        try:
            weightstart = cleaned_data.get('weight_start')
            weightend = cleaned_data.get('weight_end')
            overlap1 = SKU.objects.filter(couriervendor=self.cleaned_data['couriervendor'],
                                        product_type=self.cleaned_data['product_type'],
                                        zone=self.cleaned_data['zone'],
                                        weight_start__lte=weightstart,
                                        weight_end__gte=weightstart ).exclude(sku_code=self.cleaned_data['sku_code'])
            overlap2 = SKU.objects.filter(couriervendor=self.cleaned_data['couriervendor'],
                                        product_type=self.cleaned_data['product_type'],
                                        zone=self.cleaned_data['zone'],
                                        weight_start__lte=weightend,
                                        weight_end__gte=weightend ).exclude(sku_code=self.cleaned_data['sku_code'])
            if overlap1 or overlap2:
                raise forms.ValidationError("SKU with same courier, prouct type, zone and weight range exist already!")
        except SKU.DoesNotExist:
          #because we didn't get a match
            pass
        return cleaned_data

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ( "name", 'owner', 'contact', 'email', 'address', 'registrationno', 'gstno', 'payment_bank', 'payment_acc','fax', 'tollfree', 'website')
        widgets = {
            'address': Textarea(attrs={'cols': 33, 'rows': 4})
        }
class DateInput(forms.DateInput):
    input_type = 'date'
      
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ( "invoice_date", "invoicetype",  "customer", "remarks", 'discount', "payment", 'payment_type')
        widgets = {
            'remarks': Textarea(attrs={'cols': 25, 'rows': 3}),
            "invoice_date": DateInput()
        }
    def clean_customer(self):
        return self.cleaned_data['customer'] or None
    def __init__(self, branchid, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(branch__id=branchid)
        self.fields['discount'].widget.attrs\
            .update({
                'oninput': 'UpdateTotal()'
            })
            
        self.fields['payment'].widget.attrs\
            .update({
                'oninput': 'UpdateTotal()'
            })
        self.fields['invoicetype'].widget.attrs\
            .update({
                'onchange': 'HideShowCashType()'
            })
    
class InvoiceItemForm(forms.ModelForm):
    #sku = forms.ModelChoiceField(queryset=SKU.objects.all())
    class Meta: 
        model = InvoiceItem
        fields = ("tracking_code", 'zone_type', "producttype", 'sku', 'skudescription',"courier", 'zone', 'weight',"height", 'length', 'width',  "dimension_weight", 'price','gst')
        exclude = ('id',)
        widgets = {'gst': forms.HiddenInput()}
 
    def clean_postcode(self):
        return self.cleaned_data['postcode'] or ''
    def clean_height(self):
        return self.cleaned_data['height'] or 0
    def clean_length(self):
        return self.cleaned_data['length'] or 0
    def clean_width(self):
        return self.cleaned_data['width'] or 0
    def __init__(self, *args, **kwargs):
        super(InvoiceItemForm, self).__init__(*args, **kwargs)
        self.fields['tracking_code'].widget.attrs\
            .update({
                'oninput': 'ValidateTrackingCode(this.id)',
                'class': "validateFieldTC"
            })   
        self.fields['sku'].widget.attrs\
            .update({
                'class': 'sku-autocomplete',
                'onchange' : 'AutoCompleteSKUDetail(this.id)',
                'onblur' : 'AutoCompleteSKUDetail(this.id)',
            })
        self.fields['courier'].widget.attrs\
            .update({
                'onchange': 'AutoCompleteWeight(this.id);AutoCompleteSKU(this.id);ValidateTrackingCode(this.id)'
            })
        self.fields['zone_type'].widget.attrs\
            .update({
                'onchange': 'DefaultProductType(this.id);AutoCompleteSKU(this.id);ValidateTrackingCode(this.id);SetDescriptionAvailability(this.id)'
            })
        self.fields['zone'].widget.attrs\
            .update({
                'onchange': 'AutoCompleteSKU(this.id);AutoCompleteZone(this.id)'
            })
        self.fields['producttype'].widget.attrs\
            .update({
                'onchange': 'AutoCompleteZone(this.id);AutoCompleteSKU(this.id)',
            })

        self.fields['weight'].widget.attrs\
        .update({
            'onchange': 'AutoCompleteSKU(this.id)',
            'class': "validateFieldWeight"
        })
        self.fields['dimension_weight'].widget.attrs\
        .update({
            'oninput': 'AutoCompleteSKU(this.id)',
            'ondblclick': 'editDimensionalWeight(this.id)',
            'class': 'lastInput'
        })
        self.fields['height'].widget.attrs\
            .update({
                'onchange': 'AutoCompleteWeight(this.id)',
                'class': "dimensioninput",
            })
        self.fields['length'].widget.attrs\
            .update({
                'onchange': 'AutoCompleteWeight(this.id)',
                'class': "dimensioninput",
            })
        self.fields['width'].widget.attrs\
            .update({
                'onchange': 'AutoCompleteWeight(this.id)',
                'class': "dimensioninput",
                
            })

        self.fields['price'].widget.attrs\
            .update({
                'readOnly': 'True',
                'class': 'toAdd',
                'onchange': 'UpdateTotal()',
                'tabindex':'-1'
            })
        self.fields['gst'].widget.attrs\
            .update({
                'readOnly': 'True',
                'class' : 'toAddGST',
                'onchange': 'UpdateTotal()',
                'tabindex':'-1'
            })
        self.fields['skudescription'].widget.attrs\
            .update({
                'readOnly': 'True'
            })
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ( "customer", "payment_paymenttype")
        exclude = ("total", "createtimestamp", "updatetimestamp", "created_by",)
    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['customer'].widget.attrs\
            .update({
                'readOnly': 'True'
            })   
class PaymentInvoiceForm(forms.ModelForm):
    class Meta: 
        model = PaymentInvoice
        fields = ('paidamount',)
        exclude = ('previousamount',)

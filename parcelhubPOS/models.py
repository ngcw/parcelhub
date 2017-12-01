from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from unittest.util import _MAX_LENGTH
class UserExtend(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact = models.CharField(max_length=25)

class Branch(models.Model):
    name = models.CharField(max_length=50)
    owner = models.CharField(max_length=50)
    contact = models.CharField(max_length=25)
    email = models.EmailField(max_length=254)
    address = models.CharField(max_length=254)
    registrationno = models.CharField(max_length=50, verbose_name='Registration no')
    gstno = models.CharField(max_length=50, verbose_name='GST no')
    fax = models.CharField(max_length=25, blank=True, null=True)
    tollfree = models.CharField(max_length=25,verbose_name='Toll-free', blank=True, null=True)
    website = models.CharField(max_length=254, blank=True, null=True)
    payment_bank = models.CharField(max_length=254, blank=True, null=True)
    payment_acc = models.CharField(max_length=254, blank=True, null=True)
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class UserBranchAccess(models.Model):
    user = models.ForeignKey(User, blank=False, null=False,on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, blank=False, null=False, on_delete=models.CASCADE)
    masterdata_auth = models.CharField(max_length=20, verbose_name='Master data')
    branch_auth = models.CharField(max_length=20, verbose_name='Branch')
    user_auth = models.CharField(max_length=20, verbose_name='User')
    skupricing_auth = models.CharField(max_length=20, verbose_name='SKU price' )
    transaction_auth = models.CharField(max_length=20, verbose_name='Invoice')
    custacc_auth = models.CharField(max_length=20, verbose_name='Cust acc')
    report_auth = models.CharField(max_length=20, verbose_name='Report',)

class ZoneType(models.Model):
    name = models.CharField(max_length=50, primary_key=True, unique=True)  
    isother = models.BooleanField()
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']   

class ProductType(models.Model):
    name = models.CharField(max_length=50, primary_key=True, unique=True) 
    isdocument = models.BooleanField()
    ismerchandise = models.BooleanField() 
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name'] 
        
class CourierVendor(models.Model):
    name = models.CharField(max_length=50)
    zone_type = models.ForeignKey(ZoneType)
    formula = models.CharField(max_length=254)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        #unique_together = ["user", "branch"]

class ZoneDomestic(models.Model):
    state = models.CharField(max_length=25)
    postcode_start = models.CharField(max_length=25)
    postcode_end = models.CharField(max_length=25)
    zone = models.PositiveIntegerField()


    class Meta:
        ordering = ['zone']
        unique_together = ["state", "postcode_start", "postcode_end"]
        
class ZoneInternational(models.Model):
    couriervendor = models.ForeignKey(CourierVendor, on_delete=models.CASCADE, verbose_name='Courier')
    country = models.CharField(max_length=50, unique=True)
    zone_doc = models.PositiveIntegerField( verbose_name= 'Zone document' )
    zone_mer = models.PositiveIntegerField( verbose_name= 'Zone merchandise' )

    def __str__(self):
        return self.country

    class Meta:
        ordering = ['country']


class Tax(models.Model):
    tax_code = models.CharField(max_length=25)
    gst = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return self.tax_code

    class Meta:
        ordering = ['tax_code']
        
class SKU(models.Model):
    sku_code = models.CharField(max_length=20,  unique=True, verbose_name='SKU')
    description = models.CharField(max_length=254)
    couriervendor = models.ForeignKey(CourierVendor, on_delete=models.CASCADE, verbose_name='Courier')
    product_type = models.ForeignKey(ProductType)
    zone_type = models.ForeignKey(ZoneType)
    zone = models.IntegerField()
    weight_start = models.DecimalField(max_digits=30, decimal_places=3)
    weight_end = models.DecimalField(max_digits=30, decimal_places=3)
    tax_code = models.ForeignKey(Tax)
    corporate_price = models.DecimalField(max_digits=30, decimal_places=2)
    walkin_special_price = models.DecimalField(max_digits=30, decimal_places=2)
    walkin_price = models.DecimalField(max_digits=30, decimal_places=2)
    updatetimestamp = models.DateTimeField('master update time', auto_now=True)

    def __str__(self):
        return self.sku_code
        
    class Meta:
        ordering = ['sku_code']

class CustomerType(models.Model):
    name = models.CharField(max_length=50, primary_key=True, unique=True)  
    iscorporate = models.BooleanField()
    iswalkinspecial = models.BooleanField()
    iswalkin = models.BooleanField()
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']   
             
class Customer(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    contact = models.CharField(max_length=25)
    fax = models.CharField(max_length=25)
    email = models.EmailField(max_length=254)
    identificationno = models.CharField(max_length=50, verbose_name='Registration/IC No')
    customertype = models.ForeignKey(CustomerType, models.SET_NULL, blank=True, null=True, verbose_name='Type')
    addressline1 = models.CharField(max_length=254, verbose_name="Address line 1", blank=True, null=True)
    addressline2 = models.CharField(max_length=254, verbose_name="line 2", blank=True, null=True)
    addressline3 = models.CharField(max_length=254, verbose_name="line 3", blank=True, null=True)
    addressline4 = models.CharField(max_length=254, verbose_name="line 4", blank=True, null=True)
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['branch', 'name']
    
class SKUBranch(models.Model):
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, models.SET_NULL, blank=True, null=True)
    corporate_override = models.DecimalField(max_digits=30, decimal_places=2,blank=True, null=True)
    walkin_special_override = models.DecimalField(max_digits=30, decimal_places=2,blank=True, null=True)
    walkin_override = models.DecimalField(max_digits=30, decimal_places=2,blank=True, null=True)
    updatetimestamp = models.DateTimeField('last update timestamp', auto_now=True)
    class Meta:
        unique_together = (("sku", "branch", "customer"),)

class InvoiceType(models.Model):
    name = models.CharField(max_length=50, primary_key=True, unique=True)  
    iscustomer = models.BooleanField()
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class PaymentType(models.Model):
    name = models.CharField(max_length=50, primary_key=True, unique=True)  
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']        
class Invoice(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    invoiceno = models.CharField(max_length=25, verbose_name='Invoice No.')
    invoice_date = models.DateField(blank=True, null=True)
    invoicetype =models.ForeignKey(InvoiceType, verbose_name='Type')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    remarks = models.CharField(max_length=254,blank=True, null=True)
    subtotal = models.DecimalField(max_digits=30, decimal_places=2)
    discount = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    discountmode = models.CharField(max_length=25, verbose_name='Discount mode', blank=True, null=True)
    gst = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='GST')
    total = models.DecimalField(max_digits=30, decimal_places=2)
    payment = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    payment_type = models.ForeignKey(PaymentType)
    createtimestamp = models.DateTimeField(default=timezone.now, verbose_name='Created datetime')
    updatetimestamp = models.DateTimeField(blank=True, null=True, verbose_name='Update datetime')
    created_by = models.ForeignKey(User)
    def __str__(self):
        return self.invoiceno
    class Meta:
        unique_together = (("branch", "invoiceno"),)
        
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    tracking_code = models.CharField(max_length=100, verbose_name='Track code', blank=True, null=True)
    courier = models.ForeignKey(CourierVendor, models.SET_NULL, blank=True, null=True)
    producttype = models.ForeignKey(ProductType, verbose_name='Product type')
    skudescription = models.CharField(max_length=255, verbose_name='Description')
    zone_type = models.ForeignKey(ZoneType)
    zone = models.CharField(max_length=100)
    weight = models.DecimalField(max_digits=25, decimal_places=3, verbose_name='Weight(kg)')
    dimension_weight = models.DecimalField(max_digits=25, decimal_places=3,blank=True, null=True,  verbose_name='Dim wt(kg)')
    height = models.DecimalField(max_digits=25, decimal_places=3,blank=True, null=True, verbose_name='Height(mm)')
    length = models.DecimalField(max_digits=25, decimal_places=3,blank=True, null=True, verbose_name='Length(mm)')
    width = models.DecimalField(max_digits=25, decimal_places=3,blank=True, null=True, verbose_name='Width(mm)')
    sku = models.CharField(max_length=100)
    gst = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='GST')
    price = models.DecimalField(max_digits=30, decimal_places=2)
    
class Payment(models.Model):
    customer = models.ForeignKey(Customer)
    total = models.DecimalField(max_digits=30, decimal_places=3,blank=True, null=True)
    payment_paymenttype = models.ForeignKey(PaymentType,blank=True, null=True, verbose_name="Payment method")
    createtimestamp = models.DateTimeField('create timestamp', default=timezone.now)
    updatetimestamp = models.DateTimeField('update timestamp',blank=True, null=True)
    created_by = models.ForeignKey(User)

class PaymentInvoice(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    remainder = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='Remainder',blank=True, null=True)
    prevamount = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='Previous amount',blank=True, null=True)
    paidamount = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='Paid amount',blank=True, null=True)
    
class VendorReport(models.Model):
    vendor = models.ForeignKey(CourierVendor, on_delete=models.CASCADE)
    datefrom = models.DateField()
    dateto = models.DateField()
    itemcount = models.PositiveIntegerField()
    createtimestamp = models.DateTimeField('create timestamp', default=timezone.now)
    created_by = models.ForeignKey(User)
    
class CashUpReport(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    datefrom = models.DateField()
    dateto = models.DateField()
    cashremaining = models.DecimalField(max_digits=30, decimal_places=2)
    createtimestamp = models.DateTimeField('create timestamp', default=timezone.now)
    created_by = models.ForeignKey(User)
    
class AccountReport(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    datefrom = models.DateField()
    dateto = models.DateField()
    createtimestamp = models.DateTimeField('create timestamp', default=timezone.now)
    created_by = models.ForeignKey(User)

class StatementOfAccount(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    datefrom = models.DateField('Date from')
    dateto = models.DateField('Date to')
    totalamount = models.DecimalField(max_digits=30, decimal_places=2,verbose_name='Total amt', blank=True, null=True )
    paidamount = models.DecimalField(max_digits=30, decimal_places=2,verbose_name='Paid amt', blank=True, null=True)
    outstandindamount = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='Outstanding amt', blank=True, null=True)
    created_by = models.ForeignKey(User)
    createtimestamp = models.DateTimeField('create timestamp', default=timezone.now())
    
    def get_month(self):
        return self.createtimestamp.month
    def get_year(self):
        return self.createtimestamp.year
class StatementOfAccountInvoice(models.Model):
    soa = models.ForeignKey(StatementOfAccount, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

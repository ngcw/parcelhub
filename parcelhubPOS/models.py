from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from unittest.util import _MAX_LENGTH
class UserExtend(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact = models.CharField(max_length=25)

class Branch(models.Model):
    name = models.CharField(max_length=50, verbose_name='*Name' )
    branch_code = models.CharField(max_length=10, verbose_name='*Branch code')
    owner = models.CharField(max_length=50, verbose_name='*Owner')
    contact = models.CharField(max_length=25, verbose_name='*Contact')
    email = models.EmailField(max_length=254, verbose_name='*Email')
    address = models.CharField(max_length=254, verbose_name='*Address')
    registrationno = models.CharField(max_length=50, verbose_name='*Registration no')
    gstno = models.CharField(max_length=50, verbose_name='*GST no')
    fax = models.CharField(max_length=25, blank=True, null=True)
    tollfree = models.CharField(max_length=25,verbose_name='Toll-free', blank=True, null=True)
    website = models.CharField(max_length=254, blank=True, null=True)
    payment_bank = models.CharField(max_length=254, blank=True, null=True)
    payment_acc = models.CharField(max_length=254, blank=True, null=True)
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Terminal(models.Model):
    name = models.CharField(max_length=50, verbose_name='*Name')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    float = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    isactive = models.BooleanField()
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
class UserBranchAccess(models.Model):
    id = models.CharField(max_length=50, primary_key=True, unique=True)  
    user = models.ForeignKey(User, blank=False, null=False,on_delete=models.CASCADE, verbose_name='*User')
    branch = models.ForeignKey(Branch, blank=False, null=False, on_delete=models.CASCADE, verbose_name='*Branch')
    access_level = models.CharField(max_length=20, verbose_name='*Access level')

class ZoneType(models.Model):
    name = models.CharField(max_length=50, primary_key=True, unique=True)  
    isother = models.BooleanField()
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']   

class CourierVendor(models.Model):
    id = models.CharField(max_length=50, verbose_name='*Name', primary_key=True)
    zone_type = models.ForeignKey(ZoneType, verbose_name='*Zone type')
    formula = models.CharField(max_length=254, verbose_name='*Formula')
    
    def __str__(self):
        return self.id

    class Meta:
        ordering = ['id']
        #unique_together = ["user", "branch"]
        
class ProductType(models.Model):
    name = models.CharField(max_length=50, primary_key=True, unique=True, verbose_name='*Name') 
    isdocument = models.BooleanField()
    ismerchandise = models.BooleanField() 
    default_zonetype = models.ForeignKey(ZoneType, verbose_name='Default zone type', blank=True, null=True)
    default_courier = models.ForeignKey(CourierVendor, verbose_name='Default courier', blank=True, null=True)
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name'] 
        


class ZoneDomestic(models.Model):
    state = models.CharField(max_length=25, verbose_name='*State')
    postcode_start = models.CharField(max_length=25, verbose_name='*Postcode start')
    postcode_end = models.CharField(max_length=25, verbose_name='*Postcode end')
    zone = models.PositiveIntegerField(verbose_name='*Zone')


    class Meta:
        ordering = ['zone']
        unique_together = ["state", "postcode_start", "postcode_end"]
        
class ZoneInternational(models.Model):
    couriervendor = models.ForeignKey(CourierVendor, on_delete=models.CASCADE, verbose_name='*Courier')
    country = models.CharField(max_length=50, unique=True, verbose_name='*Country')
    zone_doc = models.PositiveIntegerField( verbose_name= '*Zone document' )
    zone_mer = models.PositiveIntegerField( verbose_name= '*Zone merchandise' )

    def __str__(self):
        return self.country

    class Meta:
        ordering = ['country']


class Tax(models.Model):
    id = models.CharField(max_length=25, verbose_name='*Tax code', primary_key=True)
    gst = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='*GST(%)')

    def __str__(self):
        return self.id

    class Meta:
        ordering = ['id']
        
class SKU(models.Model):
    sku_code = models.CharField(max_length=20,  unique=True, verbose_name='*SKU')
    description = models.CharField(max_length=254, verbose_name='*Description')
    couriervendor = models.ForeignKey(CourierVendor, on_delete=models.CASCADE, verbose_name='*Courier', blank=True, null=True)
    product_type = models.ForeignKey(ProductType, verbose_name='*Product type')
    zone_type = models.ForeignKey(ZoneType, verbose_name='*Zone type', blank=True, null=True)
    zone = models.IntegerField(verbose_name='*Zone', blank=True, null=True)
    weight_start = models.DecimalField(max_digits=30, decimal_places=3, verbose_name='*Weight start(kg)', blank=True, null=True)
    weight_end = models.DecimalField(max_digits=30, decimal_places=3, verbose_name='*Weight end(kg)', blank=True, null=True)
    tax_code = models.ForeignKey(Tax, verbose_name='*Tax code')
    is_gst_inclusive = models.BooleanField('GST inclusive', default=False)
    corporate_price = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='*Corporate price')
    walkin_special_price = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='*Walk in special price')
    walkin_price = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='*Walk in price')
    updatetimestamp = models.DateTimeField('master update time', auto_now=True)

    def __str__(self):
        return self.sku_code
        
    class Meta:
        ordering = ['sku_code']

class CustomerType(models.Model):
    name = models.CharField(max_length=50, primary_key=True, unique=True, verbose_name='*Name')  
    iscorporate = models.BooleanField()
    iswalkinspecial = models.BooleanField()
    iswalkin = models.BooleanField()
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']   
             
class Customer(models.Model):
    id = models.CharField(max_length=100, primary_key=True, unique=True)  
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name='*Branch')
    name = models.CharField(max_length=50, verbose_name='*Name')
    contact = models.CharField(max_length=25, verbose_name='*Contact')
    fax = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(max_length=254, verbose_name='*Email' , blank=True, null=True)
    identificationno = models.CharField(max_length=50, verbose_name='*Registration/IC No')
    customertype = models.ForeignKey(CustomerType, verbose_name='*Type')
    addressline1 = models.CharField(max_length=254, verbose_name="Address line 1", blank=True, null=True)
    addressline2 = models.CharField(max_length=254, verbose_name="line 2", blank=True, null=True)
    addressline3 = models.CharField(max_length=254, verbose_name="line 3", blank=True, null=True)
    addressline4 = models.CharField(max_length=254, verbose_name="line 4", blank=True, null=True)
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['branch', 'name']
        unique_together = (('branch', 'identificationno'),)
class SKUBranch(models.Model):
    id = models.CharField(max_length=100, primary_key=True, unique=True)  
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='*SKU')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name='*Branch')
    customer = models.ForeignKey(Customer, models.SET_NULL, blank=True, null=True)
    corporate_override = models.DecimalField(max_digits=30, decimal_places=2,blank=True, null=True)
    walkin_special_override = models.DecimalField(max_digits=30, decimal_places=2,blank=True, null=True)
    walkin_override = models.DecimalField(max_digits=30, decimal_places=2,blank=True, null=True)
    updatetimestamp = models.DateTimeField('last update timestamp', auto_now=True)
    class Meta:
        unique_together = (("sku", "branch", "customer"),)

class InvoiceType(models.Model):
    name = models.CharField(max_length=50, primary_key=True, unique=True, verbose_name='*Name')  
    iscustomer = models.BooleanField()
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class PaymentType(models.Model):
    name = models.CharField(max_length=50, primary_key=True, unique=True, verbose_name='*Name')  
    legend = models.CharField(max_length=5, verbose_name='*Legend',blank=True, null=True)  
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']        
class Invoice(models.Model):
    id = models.CharField(max_length=100, primary_key=True, unique=True)  
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
    invoiceno = models.CharField(max_length=25, verbose_name='Invoice No.')
    invoicetype =models.ForeignKey(InvoiceType, verbose_name='*Type')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    remarks = models.CharField(max_length=254,blank=True, null=True)
    subtotal = models.DecimalField(max_digits=30, decimal_places=2)
    discount = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    discountvalue = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True, verbose_name='Discount (RM)')
    discountmode = models.CharField(max_length=25, verbose_name='Discount mode', blank=True, null=True)
    gst = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='GST')
    total = models.DecimalField(max_digits=30, decimal_places=2)
    payment = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    payment_type = models.ForeignKey(PaymentType)
    createtimestamp = models.DateTimeField(default=timezone.now, verbose_name='*Invoice datetime', blank=True, null=True)
    updatetimestamp = models.DateTimeField(blank=True, null=True, verbose_name='Update datetime')
    created_by = models.ForeignKey(User)
    def __str__(self):
        return self.invoiceno
    class Meta:
        unique_together = (("branch", "invoiceno"),)
        
class InvoiceItem(models.Model):
    id = models.CharField(max_length=100, primary_key=True, unique=True)  
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    tracking_code = models.CharField(max_length=100, verbose_name='Track code', blank=True, null=True)
    courier = models.ForeignKey(CourierVendor, models.SET_NULL, blank=True, null=True)
    producttype = models.ForeignKey(ProductType, verbose_name='*Product type')
    skudescription = models.CharField(max_length=255, verbose_name='*Description')
    zone_type = models.ForeignKey(ZoneType, verbose_name='Zone type', blank=True, null=True)
    zone = models.CharField(max_length=100, verbose_name='Zone',blank=True, null=True)
    weight = models.DecimalField(max_digits=25, decimal_places=3, verbose_name='Weight(kg)',blank=True, null=True)
    dimension_weight = models.DecimalField(max_digits=25, decimal_places=3,blank=True, null=True,  verbose_name='Dim wt(kg)')
    height = models.DecimalField(max_digits=25, decimal_places=3,blank=True, null=True, verbose_name='Height(cm)')
    length = models.DecimalField(max_digits=25, decimal_places=3,blank=True, null=True, verbose_name='Length(cm)')
    width = models.DecimalField(max_digits=25, decimal_places=3,blank=True, null=True, verbose_name='Width(cm)')
    sku = models.CharField(max_length=100, verbose_name='*SKU')
    gst = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='GST')
    price = models.DecimalField(max_digits=30, decimal_places=2)
    
class Payment(models.Model):
    id = models.CharField(max_length=200, primary_key=True, unique=True)  
    customer = models.ForeignKey(Customer, verbose_name='*Customer')
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE, verbose_name='*Terminal')
    total = models.DecimalField(max_digits=30, decimal_places=2,blank=True, null=True)
    payment_paymenttype = models.ForeignKey(PaymentType,blank=True, null=True, verbose_name="Payment method")
    createtimestamp = models.DateTimeField('create timestamp', default=timezone.now)
    created_by = models.ForeignKey(User,blank=True, null=True)

class PaymentInvoice(models.Model):
    id = models.CharField(max_length=200, primary_key=True, unique=True)  
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    remainder = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='Remainder',blank=True, null=True)
    paidamount = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='Paid amount',blank=True, null=True, default=0.00)
    
    
class CashUpReport(models.Model):
    id = models.CharField(max_length=100, primary_key=True, unique=True)  
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=30, decimal_places=2,blank=True, null=True)
    sessiontimestamp = models.DateTimeField('session timestamp')
    invoicenofrom = models.CharField(max_length=100, verbose_name='Invoice from',blank=True, null=True)
    invoicenoto = models.CharField(max_length=100, verbose_name='Invoice to',blank=True, null=True)
    createtimestamp = models.DateTimeField('create timestamp', default=timezone.now)
    created_by = models.ForeignKey(User)
    
class CashUpReportPaymentType(models.Model):
    id = models.CharField(max_length=100, primary_key=True, unique=True)  
    cashupreport = models.ForeignKey(CashUpReport, on_delete=models.CASCADE)
    payment_type  = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=30, decimal_places=2)
    percentage = models.DecimalField(max_digits=30, decimal_places=2)
    count = models.IntegerField()
    
class StatementOfAccount(models.Model):
    id = models.CharField(max_length=100, primary_key=True, unique=True)  
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='*Customer', blank=True, null=True)
    datefrom = models.DateField('Date from', blank=True, null=True)
    dateto = models.DateField('*Date to')
    totalamount = models.DecimalField(max_digits=30, decimal_places=2,verbose_name='Total amt', blank=True, null=True )
    paidamount = models.DecimalField(max_digits=30, decimal_places=2,verbose_name='Paid amt', blank=True, null=True)
    outstandindamount = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='Balance', blank=True, null=True)
    created_by = models.ForeignKey(User)
    createtimestamp = models.DateTimeField('create timestamp')
    
    def get_month(self):
        return self.createtimestamp.month
    def get_year(self):
        return self.createtimestamp.year
class StatementOfAccountInvoice(models.Model):
    id = models.CharField(max_length=100, primary_key=True, unique=True)  
    soa = models.ForeignKey(StatementOfAccount, on_delete=models.CASCADE)
    date = models.DateField('Date from')
    reference = models.CharField(max_length=250,blank=True, null=True) 
    description = models.CharField(max_length=254, verbose_name='Description',blank=True, null=True)
    debit = models.DecimalField(max_digits=30, decimal_places=2,blank=True, null=True)
    credit = models.DecimalField(max_digits=30, decimal_places=2,blank=True, null=True)

class GlobalParameter(models.Model):
    invoice_lockin_date = models.DateField('*Invoice lock in date' )
    

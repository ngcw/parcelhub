import django_tables2 as tables
from .models import *

deletelinkinvoice = '''<a href="/parcelhubPOS/invoice/deleteinvoice?dinvoiceid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete this?')">Delete</a>'''
editlinkinvoice = '''{% if record.createtimestamp >= deadlinetime or issuperuser %}
                    <a href="/parcelhubPOS/invoice/editinvoice?invoiceid={{record.id}}">Edit</a>
                    {% else%}
                    Edit
                    {% endif %}'''
class InvoiceTable(tables.Table):
    edit = tables.TemplateColumn(editlinkinvoice,
                                      orderable=False)
    delete = tables.TemplateColumn( deletelinkinvoice,
                                    orderable = False );
    class Meta:
        model = Invoice
        fields = ('invoiceno', 'invoice_date','invoicetype', 'customer','remarks', 'subtotal', 'discount', 'discountmode', 'gst', 'total', 'payment','createtimestamp', 'updatetimestamp', 'edit', 'delete' )
        attrs = {'class': 'paleblue'
                 }
        empty_text = "There are no invoice matching the search criteria..."

deletelinksku = '''<a href="/parcelhubPOS/sku/deletesku?dskucode={{record.sku_code}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete this?')">Delete</a>'''
editlinksku = '<a href="/parcelhubPOS/sku/editsku?skucode={{record.sku_code}}">Edit</a>'
class SKUTable(tables.Table):
    edit = tables.TemplateColumn(editlinksku,
                                orderable = False)
    delete = tables.TemplateColumn( deletelinksku,
                                    orderable = False );
    class Meta:
        model = SKU
        attrs = {'class': 'paleblue'
                 }
        sequence = ('sku_code', 'description', 'couriervendor', 'product_type', 'zone_type',
                       'zone', 'weight_start', 'weight_end', 'tax_code', 'corporate_price',
                       'walkin_special_price', 'walkin_price','edit', 'delete')
        exclude = {'id'}
        empty_text = "There are no SKU matching the search criteria..."

deletelinkbranch = '''<a href="/parcelhubPOS/branch/deletebranch?dbranchid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete this?')">Delete</a>'''
editlinkbranch = '<a href="/parcelhubPOS/branch/editbranch?ebranchid={{record.id}}">Edit</a>'
class BranchTable(tables.Table):
    edit = tables.TemplateColumn(editlinkbranch,
                                      orderable=False)
    delete = tables.TemplateColumn( deletelinkbranch,
                                    orderable = False );
    class Meta:
        model = Branch
        attrs = {'class': 'paleblue'
                 }
        sequence = ('name', 'owner', 'contact', 'email', 'address', 'registrationno', 'gstno','edit', 'delete')
        exclude = {'id', 'fax', 'tollfree', 'payment_bank', 'payment_acc', 'website'}
            
deletelinkuser = '''<a href="/parcelhubPOS/user/deleteuser?duser_id={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete this?')">Delete</a>'''
editlinkuser = '<a href="/parcelhubPOS/user/userbranchaccess?user_id={{record.id}}">Edit</a>'
class UserTable(tables.Table):
    edit = tables.TemplateColumn(editlinkuser,
                                    orderable = False)
    delete = tables.TemplateColumn( deletelinkuser,
                                    orderable = False );
    contact = tables.Column(accessor='userextend.contact')
    class Meta:
        model = User
        attrs = {'class': 'paleblue'}
        fields = ('username', 'first_name', 'last_name', 'email', 'last_login', 'date_joined'  )
        sequence = ('username', 'first_name', 'last_name', 'email', 'contact' ,'last_login', 'date_joined','edit', 'delete')
        empty_text = "There are no User matching the search criteria..."
        
edituserbranchaccess = '''<a href="/parcelhubPOS/user/userbranchaccess/edituba?userbranch_id={{record.id }}_{{ record.user.id }}">Edit</a>'''
deleteuserbranchaccess = '''<a href="/parcelhubPOS/user/userbranchaccess/deleteuba?duserbranch_id={{record.id}}_{{ record.user.id }}" class="deletebutton" onclick="return confirm('Are you sure you want to delete this?')">Delete</a>'''
class UserBranchAccessTable(tables.Table):
    edit = tables.TemplateColumn(edituserbranchaccess,
                               orderable = False)
    delete = tables.TemplateColumn( deleteuserbranchaccess,
                                    orderable = False );
    class Meta:
        model = User
        attrs = {'class': 'paleblue'}
        fields = ('user', 'branch', 'masterdata_auth', 'branch_auth',
                  'user_auth', 'skupricing_auth', 'transaction_auth', 
                  'custacc_auth', 'report_auth' )
        sequence = ('user', 'branch', 'masterdata_auth', 'branch_auth',
                  'user_auth', 'skupricing_auth', 'transaction_auth', 
                  'custacc_auth', 'report_auth','edit', 'delete')
        exclude = {'id'}
        empty_text = "There are no assigned access to user"
        
deletelinkvendor = '''<a href="/parcelhubPOS/vendor/deletevendor?dvendorid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete this?')">Delete</a>'''
editlinkvendor = '<a href="/parcelhubPOS/vendor/editvendor?vendorid={{record.id}}">Edit</a>'
class VendorTable(tables.Table):
    edit = tables.TemplateColumn(editlinkvendor,
                                      orderable = False)
    delete = tables.TemplateColumn( deletelinkvendor,
                                    orderable = False );
    class Meta:
        model = CourierVendor
        attrs = {'class': 'paleblue'
                 }
        sequence = ('name', 'zone_type', 'formula' ,'edit','delete')
        exclude = {'id'}
        empty_text = "There are no Vendor matching the search criteria..."
        
deletelinktax = '''<a href="/parcelhubPOS/tax/deletetax?dtaxid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete this?')">Delete</a>'''
editlinktax = '<a href="/parcelhubPOS/tax/edittax?taxid={{record.id}}">Edit</a>'
class TaxTable(tables.Table):
    edit = tables.TemplateColumn(editlinktax,
                                      orderable = False)
    delete = tables.TemplateColumn( deletelinktax,
                                    orderable = False );
    class Meta:
        model = Tax
        attrs = {'class': 'paleblue'
                 }
        sequence = ('tax_code', 'gst','edit','delete')
        exclude = {'id'}
        empty_text = "There are no Tax matching the search criteria..."
        
deletelinkzonedomestic = '''<a href="/parcelhubPOS/zonedomestic/deletezonedomestic?dzonedomesticid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete this?')">Delete</a>'''
editlinkzonedomestic = '<a href="/parcelhubPOS/zonedomestic/editzonedomestic?zonedomesticid={{record.id}}">Edit</a>'
class ZoneDomesticTable(tables.Table):
    edit = tables.TemplateColumn(editlinkzonedomestic,
                                      orderable = False)
    delete = tables.TemplateColumn( deletelinkzonedomestic,
                                    orderable = False );
    class Meta:
        model = ZoneDomestic
        attrs = {'class': 'paleblue'
                 }
        sequence = ('state', 'postcode_start', 'postcode_end','zone','edit', 'delete')
        exclude = {'id'}
        empty_text = "There are no Zone matching the search criteria..."

deletelinkzoneinternational = '''<a href="/parcelhubPOS/zoneinternational/deletezoneinternational?dzoneinternationalid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete this?')">Delete</a>'''
editlinkzoneinternational = '<a href="/parcelhubPOS/zoneinternational/editzoneinternational?zoneinternationalid={{record.id}}">Edit</a>'
class ZoneInternationalTable(tables.Table):
    edit = tables.TemplateColumn(editlinkzoneinternational,
                                      orderable = False)
    delete = tables.TemplateColumn( deletelinkzoneinternational,
                                    orderable = False );
    class Meta:
        model = ZoneInternational
        attrs = {'class': 'paleblue'
                 }
        sequence = ( 'couriervendor','country', 'zone_doc', 'zone_mer','edit','delete')
        exclude = {'id'}
        empty_text = "There are no Zone matching the search criteria..."
        
deletelinkskubranch = '''<a href="/parcelhubPOS/skubranch/deleteskubranch?dskubranchid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete this?')">Delete</a>'''
editlinkskubranch = '<a href="/parcelhubPOS/skubranch/editskubranch?skubranchid={{record.id}}">Edit</a>'
class SKUBranchTable(tables.Table):
    edit = tables.TemplateColumn(editlinkskubranch,
                                           orderable = False)
    corporate_price = tables.Column(accessor='sku.corporate_price')
    walkin_special_price = tables.Column(accessor='sku.walkin_special_price')
    walkin_price = tables.Column(accessor='sku.walkin_price')
    vendor = tables.Column(accessor='sku.couriervendor')
    zone = tables.Column(accessor='sku.zone')
    weight_start = tables.Column(accessor='sku.weight_start')
    weight_end = tables.Column(accessor='sku.weight_end')
    master_last_update = tables.Column(accessor='sku.updatetimestamp')
    delete = tables.TemplateColumn( deletelinkskubranch,
                                    orderable = False );
    class Meta:
        model = SKUBranch
        attrs = {'class': 'paleblue'
                 }
        sequence = ('sku', 'branch', 'customer', 'vendor', 'zone', 'weight_start', 'weight_end',
                    'walkin_price', 'walkin_override','walkin_special_price', 'walkin_special_override', 'corporate_price', 'corporate_override',
                    'master_last_update','updatetimestamp','edit','delete')
        exclude = {'id', 'iswalkinspecial_override', 'iscorporate_override', 'iswalkin_override'}
        empty_text = "There are no SKU matching the search criteria..."

deletelinkcustomer = '''<a href="/parcelhubPOS/customer/deletecustomer?dcustomerid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete this?')">Delete</a>'''
editlinkcustomer = '<a href="/parcelhubPOS/customer/editcustomer?customerid={{record.id}}">Edit</a>'
customertypeimg = '''{% if record.customertype.iscorporate %}
                        <img src="/static/img/company.png" alt="company" title="company" width="20" height="20"/>
                    {% elif  record.customertype.iswalkinspecial %}
                        <img src="/static/img/individual_special.png" alt="individual special" title="individual special" width="20" height="20"/>
                    {% else %}
                        <img src="/static/img/individual.png" alt="individual" title="individual" width="20" height="20"/>
                    {% endif %}'''
class CustomerTable(tables.Table):
    edit = tables.TemplateColumn(editlinkcustomer,
                                      orderable = False)
    
    type = tables.TemplateColumn( customertypeimg,
                                          orderable = False)
    delete = tables.TemplateColumn( deletelinkcustomer,
                                    orderable = False );
    class Meta:
        model = Customer
        attrs = {'class': 'paleblue'
                 }
        sequence = ('type', 'name', 'contact','email', 'fax', 'identificationno', "addressline1","addressline2", "addressline3","addressline4",'edit', 'delete')
        exclude = {'id', 'customertype',}
        empty_text = "There are no Customer matching the search criteria..."

deletelinkpayment = '''<a href="/parcelhubPOS/payment/deletepayment?dpaymentid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete this?')">Delete</a>'''
editlinkpayment = '<a href="/parcelhubPOS/payment/editpayment?paymentid={{record.id}}">Edit</a>'
class PaymentTable(tables.Table):
    edit = tables.TemplateColumn(editlinkpayment,
                                      orderable = False)
    delete = tables.TemplateColumn( deletelinkpayment,
                                    orderable = False );
    class Meta:
        model = Payment
        attrs = {'class': 'paleblue'
                 }
        sequence = ('customer', 'total', 'payment_paymenttype','createtimestamp', 'updatetimestamp', 'created_by', 'edit', 'delete')
        exclude = {'id'}
        empty_text = "There are no Payment matching the search criteria..."
        
deletelinksoa = '''<a href="/parcelhubPOS/statementofaccount/deletesoa?dsoaid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete this?')">Delete</a>'''
viewlinksoa = '<a href="/parcelhubPOS/statementofaccount/viewsoa?soaid={{record.id}}">View</a>'
class StatementOfAccountTable(tables.Table):
    view = tables.TemplateColumn(viewlinksoa,
                                      orderable = False)
    delete = tables.TemplateColumn( deletelinksoa,
                                    orderable = False );
    class Meta:
        model = StatementOfAccount
        attrs = {'class': 'paleblue'
                 }
        sequence = ('customer', 'datefrom', 'dateto','totalamount', 'paidamount', 'outstandindamount', 'createtimestamp', 'view', 'delete')
        exclude = {'id', 'created_by'}
        empty_text = "There are no statement of account matching the search criteria..."

import django_tables2 as tables
from .models import *


editlinkinvoice = '''<a href="/parcelhubPOS/invoice/editinvoice?invoiceid={{record.id}}">{{record.invoiceno}}</a>
                    {% if record.createtimestamp.date >= deadlinetime.date and  record.createtimestamp.time >= deadlinetime.time and isedit %}
                    
                    {% endif %}'''
class InvoiceTable(tables.Table):
    invoiceno = tables.TemplateColumn(editlinkinvoice,
                                      orderable=False)
    customer = tables.Column(default='Cash')
    class Meta:
        model = Invoice
        fields = ('createtimestamp', 'invoiceno', 'customer','remarks', 'subtotal', 'discountvalue', 'gst', 'total', 'payment','updatetimestamp' )
        attrs = {'class': 'paleblue'
                 }
        exclude = {'invoicetype', 'discount'}
        empty_text = "There are no invoice matching the search criteria..."

class InvoiceTable2(tables.Table):
    invoiceno = tables.TemplateColumn(editlinkinvoice,
                                      orderable=False)
    customer = tables.Column(default='Cash')
    class Meta:
        model = Invoice
        fields = ('createtimestamp', 'branch', 'invoiceno', 'customer','remarks', 'subtotal', 'discountvalue', 'gst', 'total', 'payment','updatetimestamp' )
        attrs = {'class': 'paleblue'
                 }
        exclude = {'invoicetype', 'discount'}
        empty_text = "There are no invoice matching the search criteria..."
        
deletelinksku = '''{% if isedit %}
                    <a href="/parcelhubPOS/sku/deletesku?dskucode={{record.sku_code}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete SKU {{ record.sku_code}}?')">Delete</a>

                    {% endif %}'''
editlinksku = '''{% if isedit %}<a href="/parcelhubPOS/sku/editsku?skucode={{record.sku_code}}">Edit</a>
                    {% endif %}'''
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
                       'zone', 'weight_start', 'weight_end', 'tax_code', 'is_gst_inclusive', 'corporate_price',
                       'walkin_special_price', 'walkin_price','updatetimestamp','edit', 'delete')
        exclude = {'id'}
        empty_text = "There are no SKU matching the search criteria..."

deletelinkbranch = '''{% if isedit and record.invoice_set.count <= 0 %}<a href="/parcelhubPOS/branch/deletebranch?dbranchid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete branch {{ record.name }}?')">Delete</a>
                        {% endif %}'''
editlinkbranch = '''{% if isedit %}<a href="/parcelhubPOS/branch/editbranch?ebranchid={{record.id}}">Edit</a>
                    {% endif %}'''
class BranchTable(tables.Table):
    edit = tables.TemplateColumn(editlinkbranch,
                                      orderable=False)
    delete = tables.TemplateColumn( deletelinkbranch,
                                    orderable = False );
    class Meta:
        model = Branch
        attrs = {'class': 'paleblue'
                 }
        sequence = ('branch_code', 'name', 'owner', 'contact', 'email', 'address', 'registrationno', 'gstno','edit', 'delete')
        exclude = {'id', 'fax', 'tollfree', 'payment_bank', 'payment_acc', 'website'}
            
deletelinkuser = '''{% if isedit %}<a href="/parcelhubPOS/user/deleteuser?duser_id={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete user {{ user.username}}?')">Delete</a>
                        {% endif %}'''
editlinkuser = '''{% if isedit %}<a href="/parcelhubPOS/user/edituser/?user_id={{record.id}}">Edit</a>
                    {% endif %}'''
editbranchaccesslinkuser = '''{% if isedit %}<a href="/parcelhubPOS/user/userbranchaccess?user_id={{record.id}}">Grant access</a>
                    {% endif %}'''
class UserTable(tables.Table):
    edit = tables.TemplateColumn(editlinkuser,
                                    orderable = False)
    grant_access = tables.TemplateColumn(editbranchaccesslinkuser,
                                    orderable = False)
    delete = tables.TemplateColumn( deletelinkuser,
                                    orderable = False );
    contact = tables.Column(accessor='userextend.contact')
    class Meta:
        model = User
        attrs = {'class': 'paleblue'}
        fields = ('username', 'first_name', 'last_name', 'email', 'last_login', 'date_joined'  )
        sequence = ('username', 'first_name', 'last_name', 'email', 'contact' ,'last_login', 'date_joined','edit', 'grant_access','delete')
        empty_text = "There are no User matching the search criteria..."

class UserTable2(tables.Table):
    edit = tables.TemplateColumn(editlinkuser,
                                    orderable = False)
    grant_access = tables.TemplateColumn(editbranchaccesslinkuser,
                                    orderable = False)
    delete = tables.TemplateColumn( deletelinkuser,
                                    orderable = False );
    contact = tables.Column(accessor='userextend.contact')
    class Meta:
        model = User
        attrs = {'class': 'paleblue'}
        fields = ('branch', 'username', 'first_name', 'last_name', 'email', 'last_login', 'date_joined'  )
        sequence = ('branch','username', 'first_name', 'last_name', 'email', 'contact' ,'last_login', 'date_joined','edit', 'grant_access','delete')
        empty_text = "There are no User matching the search criteria..."
                
edituserbranchaccess = '''{% if isedit %}<a href="/parcelhubPOS/user/userbranchaccess/edituba?userbranch_id={{record.id }}_{{ record.user.id }}">Edit</a>
                    {% endif %}'''
deleteuserbranchaccess = '''{% if isedit %}<a href="/parcelhubPOS/user/userbranchaccess/deleteuba?duserbranch_id={{record.id}}_{{ record.user.id }}" class="deletebutton" onclick="return confirm('Are you sure you want to delete user access for {{ record.branch }}?')">Delete</a>
                        {% endif %}'''
class UserBranchAccessTable(tables.Table):
    edit = tables.TemplateColumn(edituserbranchaccess,
                               orderable = False)
    delete = tables.TemplateColumn( deleteuserbranchaccess,
                                    orderable = False );
    class Meta:
        model = User
        attrs = {'class': 'paleblue'}
        fields = ('user', 'branch', 'access_level' )
        sequence = ('user', 'branch', 'access_level', 'edit', 'delete')
        exclude = {'id'}
        empty_text = "There are no assigned access to user"
        
deletelinkvendor = '''{% if isedit and record.invoiceitem_set.count <= 0 %}<a href="/parcelhubPOS/vendor/deletevendor?dvendorid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete vendor {{ record.name }}?')">Delete</a>
                        {% endif %}'''
editlinkvendor = '''{% if isedit %}<a href="/parcelhubPOS/vendor/editvendor?vendorid={{record.id}}">Edit</a>
                    {% endif %}'''
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
        empty_text = "There are no courier vendor matching the search criteria..."
        
deletelinktax = '''{% if isedit and record.sku_set.count <= 0%}<a href="/parcelhubPOS/tax/deletetax?dtaxid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete tax {{record.tax_code}}?')">Delete</a>
                        {% endif %}'''
editlinktax = '''{% if isedit %}<a href="/parcelhubPOS/tax/edittax?taxid={{record.id}}">Edit</a>
                    {% endif %}'''
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
        empty_text = "There are no tax matching the search criteria..."
        
deletelinkzonedomestic = '''{% if isedit %}<a href="/parcelhubPOS/zonedomestic/deletezonedomestic?dzonedomesticid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete domestic zone for state {{ record.state }} from {{ record.postcode_start}} to {{ record.postcode_end}}?')">Delete</a>
                        {% endif %}'''
editlinkzonedomestic = '''{% if isedit %}<a href="/parcelhubPOS/zonedomestic/editzonedomestic?zonedomesticid={{record.id}}">Edit</a>
                    {% endif %}'''
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
        empty_text = "There are no domestic zone matching the search criteria..."

deletelinkzoneinternational = '''{% if isedit %}<a href="/parcelhubPOS/zoneinternational/deletezoneinternational?dzoneinternationalid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete international zone for {{record.couriervendor}} at {{record.country}}?')">Delete</a>
                        {% endif %}'''
editlinkzoneinternational = '''{% if isedit %}<a href="/parcelhubPOS/zoneinternational/editzoneinternational?zoneinternationalid={{record.id}}">Edit</a>
                    {% endif %}'''
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
        empty_text = "There are no international zone matching the search criteria..."
        
deletelinkskubranch = '''{% if isedit %}<a href="/parcelhubPOS/skubranch/deleteskubranch?dskubranchid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete SKU pricing for {{ record.sku}}?')">Delete</a>
                        {% endif %}'''
editlinkskubranch = '''{% if isedit %}<a href="/parcelhubPOS/skubranch/editskubranch?skubranchid={{record.id}}">Edit</a>
                    {% endif %}'''
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
    GST_inclusive = tables.BooleanColumn(accessor='sku.is_gst_inclusive')
    master_last_update = tables.Column(accessor='sku.updatetimestamp')
    delete = tables.TemplateColumn( deletelinkskubranch,
                                    orderable = False );
    class Meta:
        model = SKUBranch
        attrs = {'class': 'paleblue'
                 }
        sequence = ('sku', 'branch', 'customer', 'vendor', 'zone', 'weight_start', 'weight_end', 'GST_inclusive',
                    'walkin_price', 'walkin_override','walkin_special_price', 'walkin_special_override', 'corporate_price', 'corporate_override',
                    'master_last_update','updatetimestamp','edit','delete')
        exclude = {'id', 'iswalkinspecial_override', 'iscorporate_override', 'iswalkin_override'}
        empty_text = "There are no SKU pricing matching the search criteria..."


deletelinkcustomer = '''{% if isedit and record.invoice_set.count <= 0 %}<a href="/parcelhubPOS/customer/deletecustomer?dcustomerid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete customer {{record.name}}?')">Delete</a>
                        {% else %}
                                                {% endif %}'''
editlinkcustomer = '''{% if isedit %}<a href="/parcelhubPOS/customer/editcustomer?customerid={{record.id}}">Edit</a>
                    {% endif %}'''
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
        exclude = {'id', 'customertype', 'branch'}
        empty_text = "There are no customer matching the search criteria..."

class CustomerTable2(tables.Table):
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
        sequence = ('branch','type', 'name', 'contact','email', 'fax', 'identificationno', "addressline1","addressline2", "addressline3","addressline4",'edit', 'delete')
        exclude = {'id', 'customertype'}
        empty_text = "There are no customer matching the search criteria..."


editlinkpayment = '''<a href="/parcelhubPOS/payment/editpayment?paymentid={{record.id}}">View</a>'''
class PaymentTable(tables.Table):
    view = tables.TemplateColumn(editlinkpayment,
                                      orderable = False)
    branch = tables.Column(accessor='customer.branch')
    class Meta:
        model = Payment
        attrs = {'class': 'paleblue'
                 }
        sequence = ('createtimestamp','customer', 'branch','total', 'payment_paymenttype', 'created_by', 'view')
        exclude = {'id'}
        empty_text = "There are no payment matching the search criteria..."
        
deletelinksoa = '''{% if isedit %}<a href="/parcelhubPOS/statementofaccount/deletesoa?dsoaid={{record.id}}" class="deletebutton" onclick="return confirm('Are you sure you want to delete statement of account for {{record.customer}} from {{ record.datefrom}} to {{record.dateto}}?')">Delete</a>
                        {% endif %}'''
viewlinksoa = '<a href="/parcelhubPOS/statementofaccount/viewsoa?soaid={{record.id}}">View</a>'
class StatementOfAccountTable(tables.Table):
    view = tables.TemplateColumn(viewlinksoa,
                                      orderable = False)
    delete = tables.TemplateColumn( deletelinksoa,
                                    orderable = False );
    branch = tables.Column(accessor='customer.branch')
    class Meta:
        model = StatementOfAccount
        attrs = {'class': 'paleblue'
                 }
        sequence = ('createtimestamp', 'customer', 'branch','datefrom', 'dateto','totalamount', 'paidamount', 'outstandindamount', 'view', 'delete')
        exclude = {'id', 'created_by'}
        empty_text = "There are no statement of account matching the search criteria..."


viewlinksoa = '<a href="/parcelhubPOS/cashupreport/viewcur?curid={{record.id}}" target="_blank">View</a>'
class CashUpReportTable(tables.Table):
    view = tables.TemplateColumn(viewlinksoa,
                                      orderable = False)

    class Meta:
        model = CashUpReport
        attrs = {'class': 'paleblue'
                 }
        sequence = ('sessiontimestamp', 'createtimestamp', 'branch','invoicenofrom', 'invoicenoto','total', 'view')
        exclude = {'id', 'created_by'}
        empty_text = "There are no cash up report generate yet..."
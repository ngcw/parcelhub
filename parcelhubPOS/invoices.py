from .models import *
from .tables import InvoiceTable, InvoiceTable2
from .commons import *
from .forms import InvoiceForm, InvoiceItemForm, CustomerForm
from datetime import timedelta, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django_tables2 import RequestConfig
from django.template.context_processors import request
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms import modelformset_factory
from django.utils import timezone
import json
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from .invoiceprint import *
from io import StringIO
@login_required
def invoice(request):
    loguser = User.objects.get(id=request.session.get('userid'))
    branchaccess = UserBranchAccess.objects.filter(user=loguser).first()
    if loguser.is_superuser or branchaccess:
        return retrieveInvoice(request)
    else:
        return HttpResponse("No branch access configured for user")

# method to retrieve invoices
@login_required
def retrieveInvoice(request):
    loggedusers = userselection(request)
    try: 
        globalparameter = GlobalParameter.objects.filter().first()
        deadlinedatetime = datetime.combine(globalparameter.invoice_lockin_date, datetime.min.time())
    except:
        deadlinedatetime = timezone.now() - timedelta(days=1); 
    
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    loguser = User.objects.get(id=request.session.get('userid'))
    branchid = request.session.get(CONST_branchid)
    if branchid == "-1":
        invoice_list = Invoice.objects.all();
    else:
        invoice_list = Invoice.objects.filter(branch_id=branchid )
    formdata = {'invoicenumber':'',
                'fromdate':'',
                'todate':'',
                'customer':'',
                'trackingcode':'',
                'remark': ''}
    if request.method == "GET":
        submitted_trackingcode = request.GET.get('trackingcode') 
        if submitted_trackingcode:
            formdata['trackingcode'] = submitted_trackingcode;
            invoiceitem_invoiceid = InvoiceItem.objects.filter(tracking_code__icontains=submitted_trackingcode).values_list('invoice_id', flat=True)

            invoice_list =  invoice_list.filter(id__in=invoiceitem_invoiceid)

        submitted_invoiceno = request.GET.get('invoicenumber') 
        if submitted_invoiceno:
            formdata['invoicenumber'] = submitted_invoiceno;
            invoice_list =  invoice_list.filter(invoiceno__icontains=submitted_invoiceno)
        submitted_remark = request.GET.get('remark') 
        if submitted_remark:
            formdata['remark'] = submitted_remark;
            invoice_list =  invoice_list.filter(remarks__icontains=submitted_remark)
        submitted_fromdate = request.GET.get('fromdate') 
        submitted_todate = request.GET.get('todate') ;
        if submitted_fromdate and submitted_todate:
            submitted_todate = datetime.strptime(submitted_todate, '%Y-%m-%d')
            submitted_todate = submitted_todate + timedelta(days=1) - timedelta(seconds=1);
            submitted_fromdate = datetime.strptime(submitted_fromdate, '%Y-%m-%d')
            formdata['fromdate'] = request.GET.get('fromdate') ;
            formdata['todate'] = request.GET.get('todate') 
            invoice_list =  invoice_list.filter(createtimestamp__gte=submitted_fromdate,
                                                createtimestamp__lte= submitted_todate )
        submitted_customer = request.GET.get('customer')
        if submitted_customer:
            formdata['customer'] = submitted_customer;
            invoice_list = invoice_list.filter( customer__name__icontains=submitted_customer)
        
    if branchid == "-1":
        final_invoice_table = InvoiceTable2(invoice_list.order_by('-createtimestamp'))
    else:
        final_invoice_table = InvoiceTable(invoice_list.order_by('-createtimestamp'))     
    
    issearchempty = True
    searchmsg = 'There no invoice matching the search criteria...'
    try:
        if invoice_list or (not submitted_trackingcode and not submitted_invoiceno and not submitted_remark and not submitted_fromdate and not submitted_todate and not submitted_customer):
            issearchempty = False
    except:
        issearchempty = False
    #template = loader.get_template('invoice.html')
    RequestConfig(request, paginate={'per_page': 25}).configure(final_invoice_table)
    
    context = {
                'invoice': final_invoice_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'branchselectionaction': '/parcelhubPOS/invoice/',
                'formdata' : formdata,
                'deadlinetime': deadlinedatetime,
                'title' : 'Invoice',
                'isedit' : True,
                'isall': branchid != '-1',
                'statusmsg' : request.GET.get('msg'),
                'header': 'Invoice list',
                'issearchempty': issearchempty,
                'searchmsg': searchmsg,
                'titleid': 'invoicelisttitle'
                }
    return render(request, 'invoice.html', context)

def gen_invoice_number(request):
    branchid = request.session.get(CONST_branchid)
    branch = Branch.objects.filter(id=branchid).first()
    last_invoice = Invoice.objects.filter(branch_id=branchid).order_by('invoiceno').last()
    if not last_invoice:
         return branch.branch_code + '000001'
    invoiceno = last_invoice.invoiceno
    invoice_int = int(invoiceno.split(branch.branch_code)[-1])
    new_invoice_int = invoice_int + 1
    length_int = len(str(new_invoice_int))
    paddingnumber = max([6,length_int])
    paddingstr = '%0' + str(paddingnumber) +'d'
    new_invoice_no = branch.branch_code + paddingstr % new_invoice_int
    return new_invoice_no

def round_to(n, precision):
    n = float ( n )
    correction = 0.5 if n >= 0 else -0.5
    return int( n/precision+correction ) * precision

def round_to_05(n):
    return round_to(n, 0.05)

@login_required
def editInvoice(request, invoiceid):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    invoiceid = request.GET.get('invoiceid')
    title = 'New invoice'
    if invoiceid:
        title = "Edit invoice"
    branchid = request.session.get(CONST_branchid)
    if branchid == '-1':
        sel_branch = Branch.objects.all().first()
    else:
        sel_branch = Branch.objects.filter(id=branchid).first()
    user = User.objects.get(id = request.session.get('userid'))
    if invoiceid:
        InvoiceItemFormSet = modelformset_factory(InvoiceItem, form = InvoiceItemForm, extra=0)
        invoicequeryset = Invoice.objects.get(id=invoiceid)
        invoiceitemqueryset = InvoiceItem.objects.filter(invoice=invoicequeryset)
        invoice_form = InvoiceForm(invoicequeryset.branch.id, instance=invoicequeryset)
        
        invoice = invoicequeryset
        haspayment = invoice.paymentinvoice_set.count() > 0
    else:
        InvoiceItemFormSet = modelformset_factory(InvoiceItem, form = InvoiceItemForm, extra=1)
        invoicequeryset = None;
        invoiceitemqueryset = InvoiceItem.objects.none()

        invoice_form = InvoiceForm(branchid, instance=invoicequeryset, initial={'discount': 0, 
                                                                                  'invoice_date': timezone.now().date(),
                                                                                  'invoicetype': 'Cash',
                                                                                  'payment_type': 'Cash',
                                                                                  'branch': sel_branch.id,}
                                   )
        
        invoice = None;
        haspayment = False
    defaultproduct = ProductType.objects.filter(name = 'Parcel').first()
    defaultzonetype = ''
    defaultcourier = ''
    if defaultproduct:
        if defaultproduct.default_zonetype:
            defaultzonetype = defaultproduct.default_zonetype
        if defaultproduct.default_courier:
            defaultcourier = defaultproduct.default_courier
    invoice_item_formset = InvoiceItemFormSet(queryset=invoiceitemqueryset, initial=[{'producttype':defaultproduct,'zone_type': defaultzonetype, 'courier': defaultcourier}])
    
    #printing
    if request.method == 'POST':
        invoicebranch = branchid
        if invoicequeryset:
            invoicebranch = invoicequeryset.branch.id
        invoice_form = InvoiceForm(branchid, request.POST, instance=invoicequeryset) # A form bound to the POST data
        invoicebranch
        # Create a formset from the submitted data
        invoice_item_formset = InvoiceItemFormSet(request.POST, request.FILES)
        postaction = ''
        if invoice_form.is_valid() and invoice_item_formset.is_valid():
            subtotal = 0;
            invoice = invoice_form.save(commit=False)
            formdatainvoice = invoice_form.cleaned_data
            gsttotal = 0;
            #calculation only
            discountval = formdatainvoice.get('discount')
            
            invoice.discount = discountval
            discountmode = request.POST["discountoption"]
            invoice.discountmode = discountmode
            if discountmode == '%':
                discount = 0;
            else:
                discount = discountval;
            for form in invoice_item_formset.forms:
                invoice_item = form.save(commit=False)
                formdata = form.cleaned_data
                invoice_item.list = invoice
                invoice_item.invoice = invoice
                price = formdata.get('price') 
                gstvalue = formdata.get('gst') 
                gsttotal = gsttotal + gstvalue
                skucode = formdata.get('sku')
                sku = SKU.objects.filter(sku_code=skucode).first()
                if sku:
                    if sku.is_gst_inclusive:
                        subtotal = subtotal + price - gstvalue
                    else:
                        subtotal = subtotal + price
                if discountmode == '%':
                    if sku:
                        if sku.is_gst_inclusive:
                            discount = discount + ( ( discountval / 100 ) * (subtotal ) )
                        else:
                            discount = discount + ( ( discountval / 100 ) * (subtotal + gsttotal) )
            if not invoice_form.instance.id:
                invoice.invoiceno = gen_invoice_number(request)
                invoice.createtimestamp = timezone.now()
            invoice.updatetimestamp = timezone.now()
            invoice.subtotal = subtotal
            invoice.created_by = user
            
            invoice.discountvalue = discount
            invoice.total = round_to_05(subtotal + gsttotal - discount)
            payment = formdatainvoice.get('payment')
            if not payment:
                payment = 0;
            invoice.payment = payment
            invoice.gst = gsttotal
            invoice.save()
            
            # save invoice item
            trackingcodes = []
            for form in invoice_item_formset.forms:
                invoice_item = form.save(commit=False)
                formdata = form.cleaned_data
                
                invoice_item.list = invoice
                invoice_item.invoice = invoice
                price = formdata.get('price') 
                invoice_item.save()
                trackingcodes.append(invoice_item.tracking_code)
            itemstodelete = InvoiceItem.objects.filter(invoice__id=invoice.id).exclude(tracking_code__in=trackingcodes)
            for item in itemstodelete:
                item.delete()
                
            if 'action' in request.POST and request.POST['action'] == 'Print delivery order':
                doprint = deliveryorder_pdf(request, invoice.id)
                return HttpResponse(doprint, content_type='application/pdf')
            elif 'action' in request.POST and request.POST['action'] == 'Preview':
                if invoice.invoicetype.name == 'Cash':
                    invoiceprint = invoice_thermal(request, invoice.id)
                else:
                    invoiceprint = invoice_pdf(request, invoice.id) 
                return HttpResponse(invoiceprint, content_type='application/pdf')
            else:
                if invoice.invoicetype.name == 'Cash':
                    invoiceprint = invoice_thermal(request, invoice.id)
                else:
                    invoiceprint = invoice_pdf(request, invoice.id) 
                return HttpResponse(invoiceprint, content_type='application/pdf')#HttpResponseRedirect("/parcelhubPOS/invoice/editinvoice/?invoiceid=" + str( invoice_list.id ) ) # Redirect to a 'success' page
            
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/
    globalparam = GlobalParameter.objects.all().first();
    isnotlocked = True;
    if invoicequeryset and globalparam:
         isnotlocked = invoicequeryset.createtimestamp.date() >= globalparam.invoice_lockin_date
    isedit = isnotlocked and not haspayment
    context = {'invoice_form': invoice_form,
                 'invoice_item_formset': invoice_item_formset,
                 'headerselectiondisabled' : True,
                 'nav_bar' : sorted(menubar.items()),
                 'loggedusers' : loggedusers,
                 'branchselection': branchselectlist,
                 'invoice': invoice,
                 'invoicetitle': title,
                 'isedit' : isedit,
                 'haspayment': haspayment,
                 'isall': branchid == '-1',
                 'header': 'Sales invoice',
                 'sel_branch': sel_branch,
                 }
    return render(request, 'editinvoice.html', context)

def CustomerCreatePopup(request):
    branchid = request.session.get(CONST_branchid)
    form = CustomerForm(request.POST or None, initial={'branch': branchid})

    if form.is_valid():
        instance = form.save()

        ## Change the value of the "#id_author". This is the element id in the form
        
        return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_customer");</script>' % (instance.pk, instance))
    
    return render(request, "addcustomer.html", {"form" : form})

@csrf_exempt
def get_customer_id(request):
    if request.is_ajax():
        customer_name = request.GET['form-0-name']
        customer_id = Customer.objects.get(name = customer_name).id
        data = {'customer_id':customer_id,}
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")

@login_required
def deleteinvoice(request, dinvoiceid ):
    dinvoiceid = request.GET.get('dinvoiceid')
    invoice = Invoice.objects.filter(id = dinvoiceid )
    msg = 'Invoice "%s" have been deleted successfully.' % invoice.first().invoiceno
    if invoice:
        invoice.delete()
    return HttpResponseRedirect("/parcelhubPOS/invoice/?msg=%s" %msg)

def getskulist(request):
    branchid = request.session.get(CONST_branchid)
    skubranch_list = SKUBranch.objects.filter(branch_id = branchid )
    results = []
    skucode_list = []
    zonetypename = request.GET.get('zonetypename');
    prodtypename = request.GET.get('prodtypename');
    courierid = request.GET.get('courierid');
    zoneinput = request.GET.get('zoneinput');
    weightinput = request.GET.get('weightinput');
    customerid = request.GET.get('customerid');
    if zonetypename:
        skubranch_list = skubranch_list.filter(sku__zone_type__name = zonetypename)
    if prodtypename:
        skubranch_list = skubranch_list.filter(sku__product_type__name = prodtypename)
    if courierid:
        skubranch_list = skubranch_list.filter(sku__couriervendor__id = courierid)
    if zoneinput:
        try:
            skubranch_list = skubranch_list.filter(sku__zone = zoneinput)
        except:
            pass
    if weightinput:
        skubranch_list = skubranch_list.filter(sku__weight_start__lte=weightinput,sku__weight_end__gt=weightinput )
    if customerid:
        skubranch_list = skubranch_list.filter(customer__id = customerid)
    for skubranch in skubranch_list:
        sku_json = {}
        sku = skubranch.sku
        sku_json['id'] = sku.sku_code
        sku_json['label'] = sku.sku_code
        sku_json['value'] = sku.sku_code
        skucode_list.append(sku.sku_code)
        results.append(sku_json)
    sku_list = SKU.objects.all().exclude(sku_code__in=skucode_list)
    if zonetypename:
        sku_list = sku_list.filter(zone_type__name = zonetypename)
    if prodtypename:
        sku_list = sku_list.filter(product_type__name = prodtypename)
    if courierid:
        sku_list = sku_list.filter(couriervendor__id = courierid)
    if zoneinput:
        try:
            sku_list = sku_list.filter(zone = zoneinput)
        except:
            pass
    if weightinput:
        sku_list = sku_list.filter(weight_start__lt=weightinput,weight_end__gte=weightinput )
    for sku in sku_list:
        sku_json = {}
        sku_json['id'] = sku.sku_code
        sku_json['label'] = sku.sku_code
        sku_json['value'] = sku.sku_code
        results.append(sku_json)
    return results;

def autocompletesku(request):
    
    results = getskulist(request)
    data = json.dumps(results)

    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

@csrf_exempt
def autocompleteskufield(request):
    results = getskulist(request)
    data = json.dumps(results)
    return JsonResponse(data, safe=False)

@csrf_exempt
def autocompleteskudetail(request):
    branchid = request.session.get(CONST_branchid)
    skucode =request.GET.get('sku_code')
    invoicetype =request.GET.get('invoicetype')
    skubranch_list = SKUBranch.objects.filter(branch_id = branchid, sku__sku_code = skucode)
    results = []
    skucode_list = []
    iswalkinspecial = False;
    iscorporate = False;
    customerid = request.GET.get('customerid') ;
    if invoicetype != 'Cash' and customerid:
        try:
            customersel = Customer.objects.get(id=customerid)
            if customersel:
                iswalkinspecial = customersel.customertype.iswalkinspecial
                iscorporate = customersel.customertype.iscorporate
                skubranch_list = skubranch_list.filter(Q(customer__isnull=True) | Q(customer__name=customersel.name) )
        except:
            pass
    skubranch = skubranch_list.first()
    if invoicetype != 'Cash' and skubranch:
        try:
            sku_json = {}
            sku = skubranch.sku
            sku_json['skucode'] = sku.sku_code
            sku_json['producttype'] = sku.product_type.name
            
            sku_json['tax'] = sku.tax_code.id
            sku_json['description'] = sku.description
            try:
                sku_json['zonetype'] = sku.zone_type.name
                sku_json['couriervendor'] = sku.couriervendor.id
                sku_json['zone'] = sku.zone
            except:
                pass
            skuprice = 0.0
            if iswalkinspecial:
                skuprice = skubranch.walkin_special_override
            elif iscorporate:
                skuprice = skubranch.corporate_override
            else:
                skuprice = skubranch.walkin_override
            gstpercentage = (sku.tax_code.gst / 100 )
            if sku.is_gst_inclusive:
                gst = skuprice - (skuprice/(1+gstpercentage))
                pricewithgst = skuprice
            else:
                gst = (skuprice * gstpercentage)
                pricewithgst = skuprice + gst
            sku_json['price'] = "%.2f" % pricewithgst
            sku_json['gst'] = "%.2f" % gst
            skucode_list.append(sku.sku_code)
            results.append(sku_json)
        except: 
            pass
    else:
        try:
            sku = SKU.objects.get(sku_code = skucode)
    
            sku_json = {}
            sku_json['skucode'] = sku.sku_code
            sku_json['producttype'] = sku.product_type.name
            sku_json['tax'] = sku.tax_code.id
            sku_json['description'] = sku.description
            try:
                sku_json['zonetype'] = sku.zone_type.name
                sku_json['couriervendor'] = sku.couriervendor.id
                sku_json['zone'] = sku.zone
            except:
                pass
            skuprice = 0.0
            if iswalkinspecial:
                skuprice = sku.walkin_special_price
            elif iscorporate:
                skuprice = sku.corporate_price
            else:
                skuprice = sku.walkin_price
            gstpercentage = (sku.tax_code.gst / 100 )
            if sku.is_gst_inclusive:
                gst = skuprice - (skuprice/(1+gstpercentage))
                pricewithgst = skuprice
            else:
                gst = (skuprice * gstpercentage)
                pricewithgst = skuprice + gst
            sku_json['price'] = "%.2f" % pricewithgst
            sku_json['gst'] = "%.2f" % gst
            results.append(sku_json)
        except:
            pass
    data = json.dumps(results)
    return JsonResponse(data, safe=False)

@csrf_exempt
def autocompletezone(request):
    results = []
    
    zone_list = None
    zonetype = request.GET.get('zonetypename');
    postcode_country = request.GET.get('postcode_country') ;
    prodtypename = request.GET.get('prodtypename');
    courier = request.GET.get('courier');
    if zonetype:
        if zonetype == 'International':
            zone_list = ZoneInternational.objects.filter(couriervendor__id = courier)
        else:
            zone_list = ZoneDomestic.objects.all()
    if postcode_country:
        if zonetype == 'Domestic':
            if len(postcode_country) > 3:
                zone_list =  zone_list.filter(postcode_start__lte=postcode_country,postcode_end__gte=postcode_country)
            else:
                try:
                    zone_list =  zone_list.filter(zone = postcode_country)
                except:
                    zone_list =  zone_list.filter(zone= -1)
        elif zonetype == 'International':
            zone_list = zone_list.filter(country = postcode_country)
    if zone_list:
        for zone in zone_list:
            zone_json = {}
            if zonetype == 'International':
                if prodtypename:
                    prodtype = ProductType.objects.get(name=prodtypename);
                    if prodtype:
                        if prodtype.isdocument:
                            zone_json['zone'] = str(zone.zone_doc);
                        elif prodtype.ismerchandise:
                            zone_json['zone'] = str(zone.zone_mer);
            elif zonetype == 'Domestic':
                zone_json['zone'] = str(zone.zone);
            results.append(zone_json)
    data = json.dumps(results)
    return JsonResponse(data, safe=False)

@csrf_exempt
def autocompleteweight(request):
    results = []
    courierid = request.GET.get('courier');
    height = request.GET.get('height') ;
    length = request.GET.get('length');
    width = request.GET.get('width');
    if courierid:
        courier = CourierVendor.objects.get(id=courierid)
        if courier and height and length and width:
            formula = courier.formula.upper();
            formula = formula.replace('H', height ).replace('W', width).replace('L', length);
            weight_json = {}
            weightvalue = eval(formula)
            weight_json['weight'] = weightvalue;
            results.append(weight_json)
    data = json.dumps(results)
    return JsonResponse(data, safe=False)

@csrf_exempt
def hideshowcustomer(request):
    results = []
    invoicetypename = request.GET.get('invoicetype');
    weight_json = {}
    weight_json['invoicetype'] = True;
    if invoicetypename:
        invoicetype = InvoiceType.objects.get(name=invoicetypename)
        if invoicetype:
            weight_json['invoicetype'] = invoicetype.iscustomer;
    results.append(weight_json)
    data = json.dumps(results)
    return JsonResponse(data, safe=False)

@csrf_exempt
def setdefaultforproduct(request):
    results = []
    producttypename = request.GET.get('producttype');
    default_json = {}
    default_json['zonetype'] = '';
    default_json['courier'] = '';
    if producttypename:
        producttype = ProductType.objects.get(name=producttypename)
        if producttype:
            if producttype.default_zonetype:
                default_json['zonetype'] = producttype.default_zonetype.name;
            if producttype.default_courier:
                default_json['courier'] = producttype.default_courier.id;
    results.append(default_json)
    data = json.dumps(results)
    return JsonResponse(data, safe=False)
    
@csrf_exempt
def validatetrackingcode(request):
    results = []
    trackingcode = request.GET.get('trackcode');
    courier = request.GET.get('courier')
    trackingcode_json = {}
    trackingcode_json['trackcode'] = False;
    invoicesel = None;
    if 'invoiceid' in request.GET:
        invoiceid = request.GET.get('invoiceid')
        invoicesel = Invoice.objects.get(id=invoiceid)
    if courier != '':
        if trackingcode:
            try:
                invoiceitem = InvoiceItem.objects.filter(tracking_code=trackingcode).exclude(invoice = invoicesel)
                if invoiceitem:
                    trackingcode_json['trackcode'] = True;
            except:
                pass
        else:
            trackingcode_json['trackcode'] = True;
    results.append(trackingcode_json)
    data = json.dumps(results)
    return JsonResponse(data, safe=False)

@csrf_exempt
def validateweightrange(request):
    results = []
    weight = request.GET.get('weight');
    skucode = request.GET.get('skucode');
    weight_json = {}
    weight_json['weight'] = False;
    if weight and skucode:
        try:
            sku = SKU.objects.get(sku_code=skucode)
            weightvalue = float(weight)
            if sku and float(sku.weight_start) <= weightvalue and float(sku.weight_end) >= weightvalue:
                weight_json['weight'] = True;
        except:
            pass
    results.append(weight_json)
    data = json.dumps(results)
    return JsonResponse(data, safe=False)
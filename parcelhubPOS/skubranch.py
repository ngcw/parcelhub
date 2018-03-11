from django_tables2 import RequestConfig
from django.shortcuts import render
from django.forms import modelformset_factory
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .tables import SKUBranchTable
from .commons import *
from .models import SKUBranch, SKU, Customer, UserBranchAccess
from django.http import HttpResponseRedirect
CONST_branchid = 'branchid'
#method to retrieve skuoverride list
@login_required
def skubranchlist(request):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    branchid = request.session.get(CONST_branchid)
    if branchid == '-1':
        isedit = True
    else:
        branchaccess = UserBranchAccess.objects.get(user__id=request.session.get('userid'), branch__id = request.session.get(CONST_branchid))
        isedit = branchaccess.access_level != 'Cashier'
    loguser = User.objects.get(id=request.session.get('userid'))
    if branchid == "-1":
        skubranch_list = SKUBranch.objects.all()
    else:
        skubranch_list = SKUBranch.objects.filter(branch__id=branchid)
    
    formdata = {'skucode':'',
                'branchname':'',
                'customername':''}
    if request.method == "GET":
        submitted_skucode = request.GET.get('skucode') 
        if submitted_skucode:
            formdata['skucode'] = submitted_skucode;
            skubranch_list =  skubranch_list.filter(sku__sku_code__icontains=submitted_skucode)
        submitted_branchname = request.GET.get('branchname') 
        if submitted_branchname:
            formdata['branchname'] = submitted_branchname;
            skubranch_list =  skubranch_list.filter(branch__name__icontains=submitted_branchname)
        submitted_customername = request.GET.get('customername') 
        if submitted_customername:
            formdata['customername'] = submitted_customername;
            skubranch_list =  skubranch_list.filter(customer__name__icontains=submitted_customername)
    final_SKUBranch_table = SKUBranchTable(skubranch_list)
    
    RequestConfig(request, paginate={'per_page': 25}).configure(final_SKUBranch_table)
    issearchempty = True
    searchmsg = 'There no SKU pricing matching the search criteria...'
    try:
        if skubranch_list or (not submitted_skucode and not submitted_branchname and not submitted_customername):
            issearchempty = False
    except:
        issearchempty = False
    context = {
                'skubranch': final_SKUBranch_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'formdata' : formdata,
                'title': 'SKU per branch',
                'isedit' : isedit,
                'issuperuser' : loguser.is_superuser,
                'isall': branchid == '-1',
                'statusmsg' : request.GET.get('msg'),
                'header': "SKU branch",
                'issearchempty': issearchempty,
                'searchmsg': searchmsg
            }
    return render(request, 'skubranch.html', context)

@login_required
def editskubranch(request, skubranchid):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    branchid = request.session.get(CONST_branchid)
    branch = Branch.objects.get(id=branchid)
    sku_list = SKU.objects.all()
    customer_list = Customer.objects.filter(branch__id = branchid)
    errortext = ''
    title = "New SKU branch"
    try:
        skubranchid = request.GET.get('skubranchid')
        if skubranchid:
            title = "Edit SKU branch"
        skubranch = SKUBranch.objects.get(id=skubranchid)
        coverride = skubranch.corporate_override
        wsoverride = skubranch.walkin_special_override
        woverride = skubranch.walkin_override
    except:
        skubranch = None
        coverride = 0
        wsoverride = 0
        woverride = 0
    try:
        skuselected = skubranch.sku
        customerselected = skubranch.customer
    except:
        skuselected = sku_list.first()
        customerselected = None
    
    if request.method == "POST":
        if 'skuselected' in request.POST:
            skucodeselected = request.POST['skuselected']
            skuselected = SKU.objects.get(sku_code=skucodeselected)
        if 'customerselected' in request.POST:
            try:
                customeridselected = request.POST['customerselected']
                customeridselected = int("0" + customeridselected)
                customerselected = Customer.objects.get(id=customeridselected)
            except:
                customeridselected = ''
                customerselected = None
        if 'corporate' in request.POST:
            coverride = request.POST['corporate']
        if 'walkinspecial' in request.POST:
            wsoverride = request.POST['walkinspecial']
        if 'walkin' in request.POST:
            woverride = request.POST['walkin']
        if 'save' in request.POST:
            if skubranch:
                skubranch.sku = skuselected
                skubranch.customer = customerselected
                skubranch.corporate_override = coverride
                skubranch.walkin_special_override = wsoverride
                skubranch.walkin_override = woverride
            else:
                skubranch = SKUBranch( sku = skuselected,
                                       customer = customerselected,
                                       branch = branch,
                                       corporate_override = coverride,
                                       walkin_special_override = wsoverride,
                                       walkin_override = woverride )
            
            skubranchexist = SKUBranch.objects.filter(sku = skuselected, branch = branch, customer = customerselected).exclude(id=skubranchid)
            if skubranchexist:
                try:
                    customererror = ' and customer (' + customerselected.name + ')'
                except:
                    customererror = ''
                
                errortext = 'SKU pricing for SKU(' + skucodeselected + ')' + customererror + ' already exist.'
                
            else:
                sku_code = request.POST['skuselected'] 
                try:
                    customername = customerselected.name
                    customernamemsg = ' and customer "' + customername + '"'
                except:
                    customername = ''
                    customernamemsg = ''
                if title == 'New SKU branch':
                    msg = 'SKU override for "%s"%s have been created successfully.' % (sku_code, customernamemsg )
                else:
                    msg = 'SKU override for "%s"%s have been updated successfully.' % (sku_code, customernamemsg )
                skubranch.id = str(branchid) + '_' + sku_code + '_' + customername
                skubranch.save()
                return HttpResponseRedirect("/parcelhubPOS/skubranch/?msg=%s" % msg)#
    skucodeselected = skuselected.sku_code
    isgstinclusive = skuselected.is_gst_inclusive
    try:
        customeridselected = customerselected.id
    except:
        customeridselected = ''
    iscorporate = True;
    iswalkinspecial = True;
    iswalkin = True;
    corporatevalue = skuselected.corporate_price
    walkinspecialvalue = skuselected.walkin_special_price
    walkinvalue = skuselected.walkin_price
    if customerselected:
        iscorporate = False;
        iswalkinspecial = False;
        iswalkin = False;
        if customerselected.customertype.iscorporate:
            iscorporate = True
        elif customerselected.customertype.iswalkinspecial:
            iswalkinspecial = True
        elif customerselected.customertype.iswalkin:
            iswalkin = True
    formdata = {'corporate': [iscorporate, 'corporate', coverride, corporatevalue], 
                'walkinspecial':[iswalkinspecial, 'walkinspecial', wsoverride, walkinspecialvalue], 
                'walkin':[iswalkin, 'walkin',woverride, walkinvalue],
                'selectedsku' : skucodeselected,
                'selectedcustomer' : customeridselected,
                'isgstinclusive' : isgstinclusive
                 }
    context = {
                'headerselectiondisabled' : True,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'formdata' : formdata,
                'sku_list': sku_list,
                'customer_list': customer_list,
                'branch': branch,
                'errortext' : errortext,
                'title' : title,
                'header': title
                }
    return render(request, 'editskubranch.html', context)

@login_required
def deleteskubranch(request, dskubranchid ):
    dskubranchid = request.GET.get('dskubranchid')
    skubranch = SKUBranch.objects.filter(id = dskubranchid )
    msg = 'SKU override for "%s" and customer "%s" have been deleted successfully.' % (skubranch.first().sku.sku_code, skubranch.first().customer.name )
    if skubranch:
        skubranch.delete()
    return HttpResponseRedirect("/parcelhubPOS/skubranch/?msg=%s" % msg)
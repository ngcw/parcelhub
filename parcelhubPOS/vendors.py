from django_tables2 import RequestConfig
from django.shortcuts import render
from django.forms import modelformset_factory
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .tables import VendorTable
from .commons import *
from .models import CourierVendor, ZoneType, UserBranchAccess
from django.http import HttpResponseRedirect

CONST_branchid = 'branchid'
#method to retrieve Courier vendor list
@login_required
def vendorlist(request):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    branchid = request.session.get(CONST_branchid)
    branchaccess = UserBranchAccess.objects.get(user__id=request.session.get('userid'), branch__id = request.session.get(CONST_branchid))
    vendor_list = CourierVendor.objects.all()
    zonetype_list = ZoneType.objects.all()
    formdata = {'name':'',
                'zonetype':''}
    if request.method == "GET":
        submitted_name = request.GET.get('name') 
        if submitted_name:
            formdata['name'] = submitted_name;
            vendor_list =  vendor_list.filter(name__icontains=submitted_name)
        
        submitted_zonetype = request.GET.get('zonetype') 
        if submitted_zonetype:
            formdata['zonetype'] = submitted_zonetype;
            vendor_list =  vendor_list.filter(zone_type__name__icontains=submitted_zonetype )
    final_Vendor_table = VendorTable(vendor_list)
    
    RequestConfig(request, paginate={'per_page': 25}).configure(final_Vendor_table)
    
    context = {
                'vendor': final_Vendor_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'zonetype_list' : zonetype_list,
                'formdata' : formdata,
                'title': "Courier vendor",
                'isedit' : branchaccess.masterdata_auth == 'edit',
                'statusmsg' : request.GET.get('msg'),
                }
    return render(request, 'vendor.html', context)

@login_required
def editvendor(request, vendorid):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    vendorid = request.GET.get('vendorid')
    title = "New vendor"
    if vendorid:
        title = "Edit vendor"
    vendorqueryset = CourierVendor.objects.filter(id=vendorid)
    
    VendorFormSet = modelformset_factory(CourierVendor, fields=('name', 'zone_type', 'formula'), max_num=1)
    if request.method == "POST":
        formset = VendorFormSet(request.POST, request.FILES,
                             queryset=vendorqueryset)
        if formset.is_valid():
            name = request.POST['form-0-name'] 
            if title == 'New vendor':
                msg = 'Courier vendor "%s" have been created successfully.' % name
            else:
                msg = 'Courier vendor "%s" have been updated successfully.' % name
            formset.save()
            return HttpResponseRedirect("/parcelhubPOS/vendor/?msg=%s" % msg)
    else:
        formset = VendorFormSet(queryset=vendorqueryset)
    
    context = {
                'formset': formset,
                'headerselectiondisabled' : True,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'title' : title
                }
    return render(request, 'editvendor.html', context)

@login_required
def deletevendor(request, dvendorid ):
    dvendorid = request.GET.get('dvendorid')
    vendor = CourierVendor.objects.filter(id = dvendorid )
    msg = 'Tax "%s" have been deleted successfully.' % vendor.first().name
    if vendor:
        vendor.delete()
    return HttpResponseRedirect("/parcelhubPOS/vendor/?msg=%s" % msg)
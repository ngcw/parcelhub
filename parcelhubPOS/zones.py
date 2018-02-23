from django_tables2 import RequestConfig
from django.shortcuts import render
from django.forms import modelformset_factory
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .tables import ZoneDomesticTable, ZoneInternationalTable
from .commons import *
from .models import ZoneDomestic, ZoneInternational, UserBranchAccess, CourierVendor
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
CONST_branchid = 'branchid'
#method to retrieve Courier zonedomestic list
@login_required
def zonedomesticlist(request):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    branchid = request.session.get(CONST_branchid)
    zonedomestic_list = ZoneDomestic.objects.all()
    formdata = {'state':'',
                'postcode':'',
                'zone':''}
    if request.method == "GET":
        submitted_state = request.GET.get('state') 
        if submitted_state:
            formdata['state'] = submitted_state
            zonedomestic_list =  zonedomestic_list.filter(state__icontains=submitted_state)
        submitted_zone = request.GET.get('zone') 
        if submitted_zone:
            formdata['zone'] = submitted_zone
            zonedomestic_list =  zonedomestic_list.filter(zone=submitted_zone)
        submitted_postcode = request.GET.get('postcode') 
        if submitted_postcode:
            submitted_postcode = int('0' + submitted_postcode ) 
            formdata['postcode'] = submitted_postcode
            zonedomestic_list =  zonedomestic_list.filter(postcode_start__lte=submitted_postcode,postcode_end__gte=submitted_postcode)
         
    final_ZoneDomestic_table = ZoneDomesticTable(zonedomestic_list)
    
    RequestConfig(request, paginate={'per_page': 25}).configure(final_ZoneDomestic_table)
    loguser = User.objects.get(id=request.session.get('userid'))
    issearchempty = True
    searchmsg = 'There no domestic zone matching the search criteria...'
    try:
        if zonedomestic_list or (not submitted_state and not submitted_zone and not submitted_postcode):
            issearchempty = False
    except:
        issearchempty = False
    context = {
                'zonedomestic': final_ZoneDomestic_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'formdata' : formdata,
                'title': 'Domestic zone',
                'isedit' : loguser.is_superuser,
                'isall': branchid == '-1',
                'issuperuser' : loguser.is_superuser,
                'statusmsg' : request.GET.get('msg'),
                'header': "Domestic zone",
                'issearchempty': issearchempty,
                'searchmsg': searchmsg
                }
    return render(request, 'zonedomestic.html', context)

@login_required
def editzonedomestic(request, zonedomesticid):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    zonedomesticid = request.GET.get('zonedomesticid')
    title = "New domestic zone"
    if zonedomesticid:
        title = "Edit domestic zone"
    zonedomesticqueryset = ZoneDomestic.objects.filter(id=zonedomesticid)
    
    ZoneDomesticFormSet = modelformset_factory(ZoneDomestic, fields=('state', 'postcode_start', 'postcode_end','zone'), max_num=1)
    if request.method == "POST":
        formset = ZoneDomesticFormSet(request.POST, request.FILES,
                             queryset=zonedomesticqueryset)
        if formset.is_valid():
            zone_state = request.POST['form-0-state'] 
            if title == 'New domestic zone':
                msg = 'Zone "%s" have been created successfully.' % zone_state
            else:
                msg = 'Zone "%s" have been updated successfully.' % zone_state
            formset.save()
            return HttpResponseRedirect("/parcelhubPOS/zonedomestic/?msg=%s" % msg)
    else:
        formset = ZoneDomesticFormSet(queryset=zonedomesticqueryset)
    
    context = {
                'formset': formset,
                'headerselectiondisabled' : True,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'title': title,
                'header': title
                }
    return render(request, 'editzonedomestic.html', context)

@login_required
def deletezonedomestic(request, dzonedomesticid ):
    dzonedomesticid = request.GET.get('dzonedomesticid')
    zonedomestic = ZoneDomestic.objects.filter(id = dzonedomesticid )
    msg = 'Zone "%s" have been deleted successfully.' % zonedomestic.first().state
    if zonedomestic:
        zonedomestic.delete()
    return HttpResponseRedirect("/parcelhubPOS/zonedomestic/?msg=%s" % msg)

@login_required
def zoneinternationallist(request):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    branchid = request.session.get(CONST_branchid)
    zoneinternational_list = ZoneInternational.objects.all()
    formdata = {'country':'',
                'zonedoc':'',
                'zonemer':'',
                'courier':''}
    if request.method == "GET":
        submitted_courier = request.GET.get('courier') 
        if submitted_courier:
            formdata['courier'] = submitted_courier;
            zoneinternational_list =  zoneinternational_list.filter(couriervendor__name__icontains=submitted_courier)
        submitted_country = request.GET.get('country') 
        if submitted_country:
            formdata['country'] = submitted_country
            zoneinternational_list =  zoneinternational_list.filter(country__icontains=submitted_country)
        submitted_zonedoc = request.GET.get('zonedoc') 
        if submitted_zonedoc:
            submitted_zonedoc = int('0' + submitted_zonedoc ) 
            formdata['zonedoc'] = submitted_zonedoc
            zoneinternational_list =  zoneinternational_list.filter(zone_doc=submitted_zonedoc)
        submitted_zonemer = request.GET.get('zonemer') 
        if submitted_zonemer:
            submitted_zonemer = int('0' + submitted_zonemer ) 
            formdata['zonemer'] = submitted_zonemer
            zoneinternational_list =  zoneinternational_list.filter(zone_mer=submitted_zonemer)
    final_ZoneInternational_table = ZoneInternationalTable(zoneinternational_list)
    
    RequestConfig(request, paginate={'per_page': 25}).configure(final_ZoneInternational_table)
    loguser = User.objects.get(id=request.session.get('userid'))
    issearchempty = True
    searchmsg = 'There no international zone matching the search criteria...'
    try:
        if zoneinternational_list or (not submitted_country and not submitted_courier and not submitted_zonedoc and not submitted_zonemer):
            issearchempty = False
    except:
        issearchempty = False
    context = {
                'zoneinternational': final_ZoneInternational_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'formdata' : formdata,
                'title': "International zone",
                'isedit' : loguser.is_superuser,
                'isall': branchid == '-1',
                'issuperuser' : loguser.is_superuser,
                'statusmsg' : request.GET.get('msg'),
                'header': "International zone",
                'issearchempty': issearchempty,
                'searchmsg': searchmsg
                }
    return render(request, 'zoneinternational.html', context)

@login_required
def editzoneinternational(request, zoneinternationalid):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    zoneinternationalid = request.GET.get('zoneinternationalid')
    title = "New international zone"
    if zoneinternationalid:
        title = "Edit international zone"
    zoneinternationalqueryset = ZoneInternational.objects.filter(id=zoneinternationalid)
    
    ZoneInternationalFormSet = modelformset_factory(ZoneInternational, fields=('couriervendor', 'country', 'zone_doc', 'zone_mer'), max_num=1)
    if request.method == "POST":
        formset = ZoneInternationalFormSet(request.POST, request.FILES,
                             queryset=zoneinternationalqueryset)
        if formset.is_valid():
            vendorid = request.POST['form-0-couriervendor'] 
            courier = CourierVendor.objects.get(id=vendorid)
            if title == 'New international zone':
                msg = 'Zone for courier "%s" and country "%s" have been created successfully.' % (courier.name, request.POST['form-0-country'] )
            else:
                msg = 'Zone for courier "%s" and country "%s" have been updated successfully.' % (courier.name, request.POST['form-0-country'] )
            formset.save()
            return HttpResponseRedirect("/parcelhubPOS/zoneinternational/?msg=%s" % msg)
    else:
        formset = ZoneInternationalFormSet(queryset=zoneinternationalqueryset)
    
    context = {
                'formset': formset,
                'headerselectiondisabled' : True,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'title': title,
                'header': title
                }
    return render(request, 'editzoneinternational.html', context)

@login_required
def deletezoneinternational(request, dzoneinternationalid ):
    dzoneinternationalid = request.GET.get('dzoneinternationalid')
    zoneinternational = ZoneInternational.objects.filter(id = dzoneinternationalid )
    msg = 'Zone for courier "%s" and country "%s" have been deleted successfully.' % (zoneinternational.first().couriervendor.name, zoneinternational.first().country )
    if zoneinternational:
        zoneinternational.delete()
    return HttpResponseRedirect("/parcelhubPOS/zoneinternational/?msg=%s" % msg)
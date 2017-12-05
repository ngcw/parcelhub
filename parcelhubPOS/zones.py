from django_tables2 import RequestConfig
from django.shortcuts import render
from django.forms import modelformset_factory
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .tables import ZoneDomesticTable, ZoneInternationalTable
from .commons import *
from .models import ZoneDomestic, ZoneInternational
from django.http import HttpResponseRedirect
CONST_branchid = 'branchid'
#method to retrieve Courier zonedomestic list
@login_required
def zonedomesticlist(request):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
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
    
    context = {
                'zonedomestic': final_ZoneDomestic_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'formdata' : formdata,
                'title': 'Domestic zone'
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
            formset.save()
            return HttpResponseRedirect("/parcelhubPOS/zonedomestic")
    else:
        formset = ZoneDomesticFormSet(queryset=zonedomesticqueryset)
    
    context = {
                'formset': formset,
                'headerselectiondisabled' : True,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'title': title
                }
    return render(request, 'editzonedomestic.html', context)

@login_required
def deletezonedomestic(request, dzonedomesticid ):
    dzonedomesticid = request.GET.get('dzonedomesticid')
    zonedomestic = ZoneDomestic.objects.filter(id = dzonedomesticid )
    if zonedomestic:
        zonedomestic.delete()
    return zonedomesticlist(request)

@login_required
def zoneinternationallist(request):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
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
    
    context = {
                'zoneinternational': final_ZoneInternational_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'formdata' : formdata,
                'title': "International zone"
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
            formset.save()
            return HttpResponseRedirect("/parcelhubPOS/zoneinternational")
    else:
        formset = ZoneInternationalFormSet(queryset=zoneinternationalqueryset)
    
    context = {
                'formset': formset,
                'headerselectiondisabled' : True,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'title': title
                }
    return render(request, 'editzoneinternational.html', context)

@login_required
def deletezoneinternational(request, dzoneinternationalid ):
    dzoneinternationalid = request.GET.get('dzoneinternationalid')
    zoneinternational = ZoneInternational.objects.filter(id = dzoneinternationalid )
    if zoneinternational:
        zoneinternational.delete()
    return zoneinternationallist(request)
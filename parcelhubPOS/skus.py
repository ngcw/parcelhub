from django_tables2 import RequestConfig
from django.shortcuts import render
from django.forms import modelformset_factory
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .tables import SKUTable
from .commons import *
from .models import SKU, ZoneType, ProductType
from .forms import SKUForm
from django.http import HttpResponseRedirect
CONST_branchid = 'branchid'
#method to retrieve SKU list
@login_required
def SKUlist(request):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    sku_list = SKU.objects.all()
    zonetype_list = ZoneType.objects.all()
    producttype_list = ProductType.objects.all()
    formdata = {'skucode':'',
                'producttype':'',
                'courier':'',
                'weight':'',
                'zonetype':'',
                'zone':''}
    if request.method == "GET":
        submitted_skucode = request.GET.get('skucode') 
        if submitted_skucode:
            formdata['skucode'] = submitted_skucode;
            sku_list =  sku_list.filter(sku_code__icontains=submitted_skucode)
        submitted_producttype = request.GET.get('producttype') 
        if submitted_producttype:
            formdata['producttype'] = submitted_producttype;
            sku_list =  sku_list.filter(product_type__name__icontains=submitted_producttype )
        submitted_courier = request.GET.get('courier')
        if submitted_courier:
            formdata['courier'] = submitted_courier;
            sku_list = sku_list.filter( couriervendor__name__icontains=submitted_courier)
        submitted_weight = request.GET.get('weight') 
        if submitted_weight:
            submitted_weight = int('0' + submitted_weight ) 
            formdata['weight'] = submitted_weight;
            sku_list =  sku_list.filter(weight_start__lte=submitted_weight,weight_end__gt=submitted_weight )
        submitted_zonetype = request.GET.get('zonetype') 
        if submitted_zonetype:
            formdata['zonetype'] = submitted_zonetype;
            sku_list =  sku_list.filter(zone_type__name__icontains = submitted_zonetype )
        submitted_zone = request.GET.get('zone')
        if submitted_zone:
            submitted_zone = int('0' + submitted_zone ) 
            formdata['zone'] = submitted_zone;
            sku_list =  sku_list.filter(zone = submitted_zone )
    final_SKU_table = SKUTable(sku_list)
    
    RequestConfig(request, paginate={'per_page': 25}).configure(final_SKU_table)
    
    context = {
                'sku': final_SKU_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'zonetype_list' :zonetype_list,
                'producttype_list' : producttype_list,
                'formdata': formdata,
                'title': "SKU"
                }
    return render(request, 'sku.html', context)

@login_required
def editSKU(request, skucode):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    skucode = request.GET.get('skucode')
    title = "New SKU"
    if skucode:
        title = "Edit SKU"
    try:
        skuqueryset = SKU.objects.get(sku_code=skucode)
    except:
        skuqueryset = None
    isedit = False;
    if skucode:
        isedit = True;
    if request.method == "POST":
        formset = SKUForm(request.POST, instance=skuqueryset)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect("/parcelhubPOS/sku")
    else:
        formset = SKUForm(instance=skuqueryset)
    
    context = {
                'formset': formset,
                'headerselectiondisabled' : True,
                'isedit' : isedit,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                }
    return render(request, 'editsku.html', context)

@login_required
def deleteSKU(request, dskucode ):
    dskucode = request.GET.get('dskucode')
    sku = SKU.objects.filter(sku_code = dskucode )
    if sku:
        sku.delete()
    return SKUlist(request)


from django_tables2 import RequestConfig
from django.shortcuts import render
from django.forms import modelformset_factory
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .tables import CustomerTable
from .commons import *
from .models import Customer


CONST_branchid = 'branchid'
#method to retrieve Courier skuoverride list
@login_required
def customerlist(request):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    branchid = request.session.get(CONST_branchid)
    customer_list = Customer.objects.filter(branch__id=branchid)
    formdata = {'name':'',
                'contact':'',
                'email':'',
                'icno':''}
    if request.method == "GET":
        submitted_name = request.GET.get('name') 
        if submitted_name:
            formdata['name'] = submitted_name;
            customer_list =  customer_list.filter(name__icontains=submitted_name)
        submitted_contact = request.GET.get('contact') 
        if submitted_contact:
            formdata['contact'] = submitted_contact;
            customer_list =  customer_list.filter(contact__icontains=submitted_contact)
        submitted_email = request.GET.get('email') 
        if submitted_email:
            formdata['email'] = submitted_email;
            customer_list =  customer_list.filter(email__icontains=submitted_email)
        submitted_icno = request.GET.get('icno') 
        if submitted_icno:
            formdata['icno'] = submitted_icno;
            customer_list =  customer_list.filter(identificationno__icontains=submitted_icno)
        
    final_Customer_table = CustomerTable(customer_list)
    
    RequestConfig(request, paginate={'per_page': 25}).configure(final_Customer_table)
    
    context = {
                'customer': final_Customer_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'formdata' : formdata,
                'title' : 'Customer'
            }
    return render(request, 'customer.html', context)

@login_required
def editcustomer(request, customerid):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    branchid = request.session.get(CONST_branchid)
    customerid = request.GET.get('customerid')
    title = "New customer"
    if customerid:
        title = "Edit customer"
    customerqueryset = Customer.objects.filter(id=customerid)
    CustomerFormSet = modelformset_factory(Customer, fields=('branch', 'name', 'contact', 'email', 'fax', 'customertype', 'identificationno', 'addressline1', 'addressline2', 'addressline3', 'addressline4'), 
                                            max_num=1,
                                            exclude= ('id',)) 
    if request.method == "POST":
        formset = CustomerFormSet(request.POST, request.FILES,
                                   queryset=customerqueryset,
                                   initial=[{'branch': branchid}])
        if formset.is_valid():
            formset.save()

            return HttpResponseRedirect("/parcelhubPOS/customer")#customerlist(request)
    else:
        formset = CustomerFormSet(queryset=customerqueryset,
                                   initial=[{'branch': branchid}])
    
    context = {
                'formset': formset,
                'headerselectiondisabled' : True,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                }
    return render(request, 'editcustomer.html', context)

@login_required
def deletecustomer(request, dcustomerid ):
    dcustomerid = request.GET.get('dcustomerid')
    customer = Customer.objects.filter(id = dcustomerid )
    if customer:
        customer.delete()
    return customerlist(request)
from django_tables2 import RequestConfig
from django.shortcuts import render, redirect
from django.forms import modelformset_factory, inlineformset_factory
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .tables import PaymentTable
from .commons import *
from .models import Payment, ZoneType, Customer, Invoice, PaymentInvoice, UserBranchAccess
from django.http import HttpResponseRedirect
from django.db import models
from .forms import PaymentForm, PaymentInvoiceForm
from django.utils import timezone
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()
@register.filter(name='minus')
def minus(value, arg):
    return value - arg
CONST_branchid = 'branchid'
#method to retrieve Courier payment list
@login_required
def paymentlist(request, custid):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    branchid = request.session.get(CONST_branchid)
    branchaccess = UserBranchAccess.objects.get(user__id=request.session.get('userid'), branch__id = request.session.get(CONST_branchid))
    custid = request.GET.get('custid')
    customerlist = Customer.objects.filter(branch__id=branchid)
    try:
        payment_list = Payment.objects.filter(customer__id=custid, customer__branch__id=branchid)
    except:
        payment_list = Payment.objects.all()
    formdata = {'customername':'',
                'date':''}
    if request.method == "GET":
        submitted_name = request.GET.get('customername') 
        if submitted_name:
            formdata['customername'] = submitted_name;
            payment_list =  payment_list.filter(customer__name__icontains=submitted_name)
        submitted_date = request.GET.get('date') 
        if submitted_date:
            formdata['date'] = submitted_date;
            payment_list =  payment_list.filter(createtimestamp__lte=submitted_date, createtimestamp__gte=submitted_date )
    final_Payment_table = PaymentTable(payment_list)
    
    RequestConfig(request, paginate={'per_page': 25}).configure(final_Payment_table)
    
    context = {
                'payment': final_Payment_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'formdata' : formdata,
                'customerlist':customerlist,
                'title': 'Payment',
                'isedit' : branchaccess.custacc_auth == 'edit',
                'statusmsg' : request.GET.get('msg'),
                }
    return render(request, 'payment.html', context)



@login_required
def editpayment(request, paymentid):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    user = User.objects.get(id = request.session.get('userid'))
    paymentid = request.GET.get('paymentid')
    title = "New payment"
    if paymentid:
        title = "Edit payment"
        paymentqueryset = Payment.objects.get(id=paymentid)
        payment_form = PaymentForm(instance=paymentqueryset)
        payment = paymentqueryset
    elif request.method == "GET" and 'customerinput' in request.GET:
        customerid = request.GET.get('customerinput')
        date_from = request.GET.get('datefrom')
        date_to = request.GET.get('dateto')
        paymentoption = request.GET.get('paymentoptioninput')
        selectedcustomer =  Customer.objects.get(id=customerid)
        invoicetopay = Invoice.objects.filter(customer__id = customerid)
        if date_from:
            invoicetopay = invoicetopay.filter(invoice_date__gte = date_from)
        if date_to:
            invoicetopay = invoicetopay.filter(invoice_date__lte = date_to)
        if paymentoption == 'Unpaid':
            invoicetopay = invoicetopay.filter(payment__lt=models.F('total'))
        paymentqueryset = Payment(customer=selectedcustomer, created_by=user, updatetimestamp=timezone.now() );
        paymentqueryset.save()
        payment_form = PaymentForm(instance=paymentqueryset)
        for inv in invoicetopay:
            remainding = float(inv.total);
            if inv.total and inv.payment:
                remainding = float(inv.total) - float(inv.payment)
            paymentinv = PaymentInvoice(payment=paymentqueryset, invoice=inv, remainder = remainding)
            paymentinv.save()
        
    else:
        paymentqueryset = None;
        payment_form = PaymentForm(instance=paymentqueryset)
        
    PaymentInvoiceFormSet = modelformset_factory(PaymentInvoice, form = PaymentInvoiceForm, extra=0)
    paymentitemqueryset = PaymentInvoice.objects.filter(payment=paymentqueryset)
    payment_item_formset = PaymentInvoiceFormSet(queryset=paymentitemqueryset )
    if request.method == "POST":
        if request.POST['action'] == 'Confirm':

            payment_form = PaymentForm(request.POST, instance=paymentqueryset) # A form bound to the POST data
            # Create a formset from the submitted data
            payment_item_formset = PaymentInvoiceFormSet(request.POST, request.FILES)
            if payment_form.is_valid() and payment_item_formset.is_valid():
                total = 0;
                payment = payment_form.save(commit=False)
                paymentformdata = payment_form.cleaned_data
                payment.updatetimestamp = timezone.now()
                payment.created_by = user
                payment.customer = paymentformdata.get('customer')
                for form in payment_item_formset:
                    paymentinvoice = form.save(commit=False)
                    formdata = form.cleaned_data
                    paidamount = formdata.get('paidamount') 
                    if paidamount == None:
                        paidamount = 0;
                    else:
                        paidamount = float(paidamount)
                        
                    invoicetoupdate = paymentinvoice.invoice
                    prevamount = 0;
                    if paymentinvoice.prevamount:
                        prevamount = float(paymentinvoice.prevamount);
                    paymentamt = 0;
                    if invoicetoupdate.payment:
                        paymentamt = float(invoicetoupdate.payment)
                    invoicetoupdate.payment = paymentamt - prevamount + paidamount;
                    paymentinvoice.remainder = float(invoicetoupdate.total) - paymentamt - prevamount + paidamount
                    invoicetoupdate.save()
                    paymentinvoice.prevamount = paidamount
                    
                    total = total + paidamount 
                    paymentinvoice.save()
                payment.total = total;
                customername = request.POST['customer'] 
                if title == 'New payment':
                    msg = 'Payment for "%s" have been created successfully.' % customername
                else:
                    msg = 'Payment for "%s" have been updated successfully.' % customername
                payment.save()
                return HttpResponseRedirect('/parcelhubPOS/payment?custid=""&msg=%s' %msg)
        elif request.POST['action'] == 'Cancel payment':
            return HttpResponseRedirect("/parcelhubPOS/statementofaccount/deletesoa?dsoaid=%s"% paymentqueryset.id)
    context = {'payment_form': payment_form,
                'payment_item_formset': payment_item_formset,
                'headerselectiondisabled' : True,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'paymentid': paymentqueryset.id,
                'title': title
                }
    return render(request, 'editpayment.html', context)

@login_required
def deletepayment(request, dpaymentid ):
    dpaymentid = request.GET.get('dpaymentid')
    payment = Payment.objects.filter(id = dpaymentid )
    paymentinvoice = PaymentInvoice.objects.filter(payment = payment)
    msg = 'Payment for customer "%s" have been deleted successfully.' % payment.first().customer.name
    for paymentinv in paymentinvoice:
        invoice = paymentinv.invoice
        paymentamt = 0;
        if invoice.payment:
            paymentamt = float(invoice.payment)
        paymenttoremove = 0;
        if paymentinv.paidamount:
            paymenttoremove = float( paymentinv.paidamount )
        
        invoice.payment = paymentamt - paymenttoremove
        invoice.save()
    if payment:
        payment.delete()
    return HttpResponseRedirect('/parcelhubPOS/payment?custid=""&msg=%s' %msg)
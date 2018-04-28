from django_tables2 import RequestConfig
from django.shortcuts import render, redirect
from django.forms import modelformset_factory, inlineformset_factory
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from .tables import PaymentTable
from .commons import *
from .models import Payment, ZoneType, Customer, Invoice, PaymentInvoice, UserBranchAccess, Terminal, PaymentType
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
CONST_terminalid = 'terminalid'
#method to retrieve Courier payment list
@login_required
def paymentlist(request, custid):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    terminallist = terminalselection(request)
    menubar = navbar(request)
    branchid = request.session.get(CONST_branchid)
    terminalid = request.session.get(CONST_terminalid)
    custid = request.GET.get('custid')
    loguser = User.objects.get(id=request.session.get('userid'))
    if branchid == '-1':
        payment_list = Payment.objects.all()
    else:
        if terminalid:
            if terminalid == '-1':
                payment_list = Payment.objects.filter(customer__branch__id=branchid)
            else:    
                payment_list = Payment.objects.filter(customer__branch__id=branchid, terminal__id = terminalid)
        else:
            payment_list = Payment.objects.filter(customer__branch__id=branchid)
    formdata = {'customername':'',
                'date':'',
                'invoiceno': ''}
    if request.method == "GET":
        submitted_name = request.GET.get('customername') 
        if submitted_name:
            formdata['customername'] = submitted_name;
            payment_list =  payment_list.filter(customer__name__icontains=submitted_name)
        submitted_date = request.GET.get('date') 
        if submitted_date:
            formdata['date'] = submitted_date;
            payment_list =  payment_list.filter(createtimestamp__lte=submitted_date, createtimestamp__gte=submitted_date )
        submitted_invoiceno = request.GET.get('invoiceno') 
        if submitted_invoiceno:
            formdata['invoiceno'] = submitted_invoiceno;
            paymentitem_paymentid = PaymentInvoice.objects.filter(invoice__invoiceno__icontains=submitted_invoiceno).values_list('payment_id', flat=True)

            payment_list =  payment_list.filter(id__in=paymentitem_paymentid)
    final_Payment_table = PaymentTable(payment_list.order_by('-createtimestamp'))
    
    RequestConfig(request, paginate={'per_page': 25}).configure(final_Payment_table)
    issearchempty = True
    searchmsg = 'There no payment matching the search criteria...'
    try:
        if payment_list or (not submitted_name and not submitted_date):
            issearchempty = False
    except:
        issearchempty = False
    context = {
                'payment': final_Payment_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'terminalselection': terminallist, 
                'loggedusers' : loggedusers,
                'formdata' : formdata,
                'title': 'Payment overview',
                'isedit' : True,
                'issuperuser' : loguser.is_superuser,
                'isall': branchid == '-1',
                'statusmsg' : request.GET.get('msg'),
                'header': 'Payment overview',
                'issearchempty': issearchempty,
                'searchmsg': searchmsg,
                'titleid': 'paymentlisttile'
                }
    return render(request, 'payment.html', context)

@login_required
def paymentreceive(request):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    terminallist = terminalselection(request)
    menubar = navbar(request)
    branchid = request.session.get(CONST_branchid)
    loguser = User.objects.get(id=request.session.get('userid'))
    if branchid == '-1':
        customerlist = Customer.objects.all()
    else:
        customerlist = Customer.objects.filter(branch__id=branchid)
    context = {
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'terminalselection': terminallist, 
                'loggedusers' : loggedusers,
                'customerlist':customerlist,
                'title': 'Payment receive',
                'isedit' : True,
                'issuperuser' : loguser.is_superuser,
                'isall': branchid == '-1',
                'header': 'Payment receive',
                'statusmsg' : request.GET.get('msg'),
                'titleid': 'paymentedittitle'
                }
    return render(request, 'paymentreceive.html', context)

def gen_payment_number(terminalid,customerselected):
    branch = customerselected.branch
    last_payment = Payment.objects.filter(terminal__branch=branch).order_by('id').last()
    paymentcode = branch.branch_code + 'P'
    if not last_payment:
         return  paymentcode + '000001'
    paymentid = last_payment.id
    payment_int = int(paymentid.split(paymentcode)[-1])
    new_payment_int = payment_int + 1
    length_int = len(str(new_payment_int))
    paddingnumber = max([6,length_int])
    paddingstr = '%0' + str(paddingnumber) +'d'
    new_payment_no = paymentcode + paddingstr % new_payment_int
    return new_payment_no

@login_required
def editpayment(request, paymentid):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    terminallist = terminalselection(request)
    menubar = navbar(request)
    user = User.objects.get(id = request.session.get('userid'))
    paymentid = request.GET.get('paymentid')
    terminalid = request.session.get(CONST_terminalid)
    title = "New payment"
    if paymentid:
        title = "View payment"
        paymentqueryset = Payment.objects.get(id=paymentid)
        payment_form = PaymentForm(instance=paymentqueryset)
        payment = paymentqueryset
    elif request.method == "GET" and 'customerinput' in request.GET:
        customerid = request.GET.get('customerinput')
        date_from = request.GET.get('datefrom')
        date_to = request.GET.get('dateto')
        paymentoption = request.GET.get('paymentoptioninput')
        selectedcustomer =  Customer.objects.get(id=customerid)
        invoicetopay = Invoice.objects.filter(customer = selectedcustomer)
        if date_from:
            invoicetopay = invoicetopay.filter(createtimestamp__gte = date_from)
        if date_to:
            invoicetopay = invoicetopay.filter(createtimestamp__lte = date_to)
        if paymentoption == 'Unpaid':
            invoicetopay = invoicetopay.filter(payment__lt=models.F('total'))
        if invoicetopay:
            selectedterminal = Terminal.objects.get(id=terminalid)
            paymenttype = PaymentType.objects.all().first()
            paymentqueryset = Payment(customer=selectedcustomer, created_by=user, terminal= selectedterminal, payment_paymenttype=paymenttype);
            paymentqueryset.id = gen_payment_number(terminalid, selectedcustomer)
            paymentqueryset.save()
            payment_form = PaymentForm(instance=paymentqueryset)
            for inv in invoicetopay:
                remainding = float(inv.total);
                if inv.total and inv.payment:
                    remainding = float(inv.total) - float(inv.payment)
                paymentinv = PaymentInvoice(payment=paymentqueryset, invoice=inv, remainder = remainding, id=paymentqueryset.id + '_' + inv.invoiceno)
                paymentinv.save()
        else:
            msg = 'There are no available invoice to be paid for customer "%s".' % selectedcustomer.name
            return HttpResponseRedirect('/parcelhubPOS/makepayment?msg=%s' %msg)
        
        
    else:
        paymentqueryset = None;
        payment_form = PaymentForm(instance=paymentqueryset)
        
    PaymentInvoiceFormSet = modelformset_factory(PaymentInvoice, form = PaymentInvoiceForm, extra=0)
    paymentitemqueryset = PaymentInvoice.objects.filter(payment=paymentqueryset).order_by('invoice')
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
                    invoicepayments = PaymentInvoice.objects.filter(invoice=invoicetoupdate)
                    paymentupdate = 0;
                    for invoicepayment in invoicepayments:
                        invoicepaid = invoicepayment.paidamount
                        if invoicepaid == None:
                            invoicepaid = 0;
                        else:
                            invoicepaid = float(invoicepaid)
                        paymentupdate = paymentupdate + invoicepaid
                    invoicetoupdate.payment = paymentupdate + paidamount
                    paymentinvoice.remainder = float(invoicetoupdate.total) - float(invoicetoupdate.payment)
                    
                    total = total + paidamount 
                    paymentinvoice.save()
                    invoicetoupdate.save()
                payment.total = total;
                
                customername = request.POST['customer'] 
                customer = Customer.objects.get(id=customername)
                if title == 'New payment':
                    msg = 'Payment for "%s" have been created successfully.' % customer.name
                else:
                    msg = 'Payment for "%s" have been updated successfully.' % customer.name
                payment.save()
                return HttpResponseRedirect('/parcelhubPOS/payment?custid=""&msg=%s' %msg)
        elif request.POST['action'] == 'Cancel payment':
            return HttpResponseRedirect("/parcelhubPOS/payment/deletepayment?dpaymentid=%s"% paymentqueryset.id)
    totalamt = 0;
    if paymentqueryset.total:
        totalamt = '%.2f'% paymentqueryset.total
    
    context = {'payment_form': payment_form,
                'payment_item_formset': payment_item_formset,
                'headerselectiondisabled' : True,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'terminalselection': terminallist, 
                'loggedusers' : loggedusers,
                'paymentid': paymentqueryset.id,
                'title': title,
                'header': title,
                'isview': title == 'View payment',
                'isedit':  title == 'View payment',
                'totalamt': totalamt,
                'titleid': 'paymentedittitle'
                }
    return render(request, 'editpayment.html', context)

@csrf_exempt
def deletepayment(request, dpaymentid ):
    dpaymentid = request.GET.get('dpaymentid')
    payment = Payment.objects.filter(id = dpaymentid )
    paymentinvoice = PaymentInvoice.objects.filter(payment = payment)
    msg = 'Payment for customer "%s" have been cancelled successfully.' % payment.first().customer.name
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
    return HttpResponseRedirect('/parcelhubPOS/makepayment?msg=%s' %msg)
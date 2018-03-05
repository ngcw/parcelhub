from django_tables2 import RequestConfig
from django.shortcuts import render
from django.forms import modelformset_factory
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .tables import CashUpReportTable
from .commons import *
from .models import Invoice, PaymentType, CashUpReport, CashUpReportPaymentType, Branch, Payment, PaymentInvoice, Terminal
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.http import HttpResponseRedirect, HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics  
from reportlab.pdfbase.ttfonts import TTFont 
import os  
import reportlab
import ctypes
from io import BytesIO
from decimal import Decimal
from textwrap import wrap
from django.utils import timezone
from num2words import num2words
CONST_branchid = 'branchid'
CONST_font = 'Helvetica'
CONST_fontbold = CONST_font + '-Bold'
#method to retrieve Courier statementofacc list
@login_required
def cashuplist(request):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    branchid = request.session.get(CONST_branchid)
    loguser = User.objects.get(id=request.session.get('userid'))
    if branchid == '-1':
        cashupreport_list = CashUpReport.objects.all()
    else:
        cashupreport_list = CashUpReport.objects.filter(branch__id=branchid)

    final_CashUpReport_table = CashUpReportTable(cashupreport_list)
    
    RequestConfig(request, paginate={'per_page': 25}).configure(final_CashUpReport_table)
    context = {
                'cashupreport': final_CashUpReport_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'title': "Cash up report",
                'isedit' : True,
                'issuperuser' : loguser.is_superuser,
                'isall': branchid == '-1',
                'statusmsg' : request.GET.get('msg'),
                'header': "Cash up report",
                }
    return render(request, 'cashup.html', context)

@login_required
def viewcashupreport(request):
    branchid = request.session.get(CONST_branchid)
    selectedbranch = Branch.objects.get(id=branchid)
    loguser = User.objects.get(id=request.session.get('userid'))
    terminal = Terminal.objects.filter(branch=selectedbranch, isactive=True).first()
    try:
        curid = request.GET.get('curid')
        cureport = CashUpReport.objects.get(id=curid)
    except:
        cureport = None;
    if cureport:
        pass
    elif request.method == "POST":

        latestcashupreport = CashUpReport.objects.filter(branch__id=branchid).order_by('-createtimestamp').first()
        if latestcashupreport:
            invoicelist = Invoice.objects.filter(branch__id = branchid, createtimestamp__gte = latestcashupreport.createtimestamp, invoicetype__name="Cash")
            paymentlist = Payment.objects.filter(customer__branch__id = branchid, createtimestamp__gte = latestcashupreport.createtimestamp)
            paymentinvoicelist = PaymentInvoice.objects.filter(payment__in=paymentlist) 
            sessionstart = latestcashupreport.createtimestamp
        else:
            invoicelist = Invoice.objects.filter(branch__id = branchid, invoicetype__name="Cash")
            paymentlist = Payment.objects.filter(customer__branch__id = branchid)
            paymentinvoicelist = PaymentInvoice.objects.filter(payment__in=paymentlist) 
            sessionstart = invoicelist.order_by('createtimestamp').first().createtimestamp
            
        if invoicelist or paymentinvoicelist:
            earliestinvoice = invoicelist.order_by('invoiceno').first().invoiceno
            try:
                epaymentinvoiceid = paymentinvoicelist.order_by('invoice').first().invoice.invoiceno
                if epaymentinvoiceid < earliestinvoice:
                    earliestinvoice = epaymentinvoiceid
            except:
                pass
            latestinvoice = invoicelist.order_by('-invoiceno').first().invoiceno
            try:
                lpaymentinvoiceid = paymentinvoicelist.order_by('-invoice').first().invoice.invoiceno
                if lpaymentinvoiceid > latestinvoice:
                    latestinvoice = lpaymentinvoiceid
            except:
                pass
            totalpaymentinvoice = invoicelist.aggregate(Sum('payment')).get('payment__sum', 0.00)
            totalpaymentpayment = paymentlist.aggregate(Sum('total')).get('total__sum', 0.00)
            
            totalamt = 0; 
            if totalpaymentinvoice:
                totalamt = totalamt + totalpaymentinvoice 
            if totalpaymentpayment:
                totalamt = totalamt + totalpaymentpayment 
            if terminal and terminal.float:
                totalamt = totalamt + terminal.float
            cureport = CashUpReport(branch=selectedbranch, created_by = loguser,
                                     sessiontimestamp = sessionstart, createtimestamp = timezone.now(), 
                                     invoicenofrom=earliestinvoice, invoicenoto=latestinvoice,
                                     total = totalamt)
            cureport.save()
            paymenttypes = PaymentType.objects.all()
            totalfrominvoice = totalamt - terminal.float
            for paymenttype in paymenttypes:
                invoicepaymenttype = invoicelist.filter(payment_type=paymenttype)
                paymentpaymenttype = paymentlist.filter(payment_paymenttype=paymenttype)
                if invoicepaymenttype or paymentpaymenttype:
                    totalpayment = 0
                    if invoicepaymenttype:
                        totalpayment = totalpayment + invoicepaymenttype.aggregate(Sum('payment')).get('payment__sum', 0.00)
                    if paymentpaymenttype:
                        totalpayment = totalpayment +  paymentpaymenttype.aggregate(Sum('total')).get('total__sum', 0.00)
                    totalcount = invoicepaymenttype.count() + paymentpaymenttype.count()
                    percentagept = (float(totalpayment) / float(totalfrominvoice)) * 100
                    cashupreportpt = CashUpReportPaymentType(cashupreport=cureport,
                                                             payment_type=paymenttype,
                                                             total = totalpayment,
                                                             percentage = percentagept,
                                                             count = totalcount)
                    cashupreportpt.save()
        else:
            cureport = CashUpReport(branch=selectedbranch, created_by = loguser,
                                     sessiontimestamp = timezone.now(), createtimestamp = timezone.now(),
                                     total = terminal.float)
            cureport.save()
    cur_pdf = cashup_pdf(request, cureport)
    return HttpResponse(cur_pdf, content_type='application/pdf')

def cashup_pdf(request, cashupreport):
    response = HttpResponse(content_type='application/pdf')
    filename = 'CashUp_' + cashupreport.sessiontimestamp.strftime('%Y-%m-%d')  + '_' + cashupreport.createtimestamp.strftime('%Y-%m-%d') 
    response['Content-Disposition'] = 'attachment; filename="'+filename+'.pdf"'
    cashupreportpaymenttype = CashUpReportPaymentType.objects.filter(cashupreport=cashupreport).order_by('payment_type__legend')
    
    margin = 25;
    totalwidth = 590;
    totalheight = 820;
    center = totalwidth / 2.0
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont(CONST_fontbold, 14)
    # header
    branch = cashupreport.branch
    topmargin = 20;
    headerstring = branch.owner.upper() 
    linecount = 12;
    p.drawCentredString(center, totalheight - topmargin, headerstring)
    p.setFont(CONST_font, 8)
    datestring = cashupreport.createtimestamp.strftime('%d/%m/%Y')
    datewidth = p.stringWidth(datestring, CONST_font, 8)
    p.drawString(totalwidth-margin-datewidth, totalheight - topmargin, datestring)
    
    p.setLineWidth(1)
    lineheight = totalheight - topmargin- (linecount * 0.5)
    p.line(margin, lineheight, totalwidth-margin, lineheight)
    
    line2string = 'B/N: ' + branch.registrationno + ' GST No:' + branch.gstno + ' ' + branch.address
    p.drawCentredString(center, totalheight - topmargin - (linecount * 1.2), line2string)
    contactinfo = "Tel: " + branch.contact + " Fax: " + branch.fax
    p.drawCentredString(center, totalheight - topmargin- (linecount * 2), contactinfo)
    
    p.setFont(CONST_fontbold, 14)
    p.drawCentredString(center, totalheight - topmargin- (linecount * 4) - topmargin, "Cash Up Report")
    p.setFont(CONST_fontbold, 9)
    p.drawString(margin, totalheight - topmargin- (linecount * 9), "Drawer")
    p.drawString(margin, totalheight - topmargin- (linecount * 10), "Transactions")
    p.drawString(margin, totalheight - topmargin- (linecount * 11), "Session Opened")
    p.drawString(margin, totalheight - topmargin- (linecount * 12), "Report Run")
    
    terminal = Terminal.objects.filter(branch=branch, isactive=True).first()
    p.setFont(CONST_font, 9)
    p.drawString(margin+ 100, totalheight - topmargin- (linecount * 9), terminal.name)
    invoicerange = ''
    if cashupreport.invoicenofrom and cashupreport.invoicenoto:
        invoicefrom = cashupreport.invoicenofrom.split(branch.branch_code)[-1]
        invoiceto = cashupreport.invoicenoto.split(branch.branch_code)[-1]
        invoicerange = branch.branch_code + ' ' + str(int(invoicefrom)) + ' - ' + str(int(invoiceto))
    p.drawString(margin+100, totalheight - topmargin- (linecount * 10), invoicerange)
    p.drawString(margin+100, totalheight - topmargin- (linecount * 11), cashupreport.sessiontimestamp.strftime('%d/%m/%Y @%H:%M:%S%p'))
    p.drawString(margin+100, totalheight - topmargin- (linecount * 12), cashupreport.createtimestamp.strftime('%d/%m/%Y @%H:%M:%S%p'))
    p.setLineWidth(1)
    linecount = 15
    boxheight = linecount * (cashupreportpaymenttype.count() + 2 )
    p.rect(margin, totalheight - topmargin- (linecount * 12) - boxheight, totalwidth-(margin*2), boxheight, stroke=True, fill=False )
    p.line(margin, totalheight - topmargin- linecount * 13, totalwidth-margin, totalheight - topmargin- linecount * 13)
    p.setFont(CONST_fontbold, 9)
    tableheaderheight = totalheight - topmargin- (linecount * 12.7)
    p.drawString(margin*2, tableheaderheight, "Legend")
    p.drawString((margin*2)+60, tableheaderheight, "Payment Type")
    p.drawString((margin*2)+340, tableheaderheight, "Expected RM")
    p.drawString((margin*2)+430, tableheaderheight, "%")
    p.drawString((margin*2)+470, tableheaderheight, "Count")
    p.setFont(CONST_font, 9)
    count = 1;
    for cashup in cashupreportpaymenttype:
        legend = cashup.payment_type.legend
        paymenttype = cashup.payment_type.name
        p.drawCentredString((margin*2)+15, tableheaderheight - (linecount * count), legend)
        p.drawString((margin*2)+60, tableheaderheight - (linecount * count), paymenttype)
        totalstring = "%.2f" % cashup.total
        totalstringwidth = p.stringWidth(totalstring, CONST_font, 9)
        p.drawString((margin*2)+395-totalstringwidth, tableheaderheight - (linecount * count), totalstring)
        percentagestring = "%.2f" % cashup.percentage
        p.drawCentredString((margin*2)+435, tableheaderheight - (linecount * count), percentagestring)
        p.drawCentredString((margin*2)+485, tableheaderheight - (linecount * count), str(cashup.count))
        count += 1;
    
    p.drawCentredString((margin*2)+15, tableheaderheight - (linecount * count), '00')
    p.drawString((margin*2)+60, tableheaderheight - (linecount * count), 'Float')
    totalstring = "%.2f" % terminal.float
    totalstringwidth = p.stringWidth(totalstring, CONST_font, 9)
    p.drawString((margin*2)+395-totalstringwidth, tableheaderheight - (linecount * count), totalstring)
    
    p.setFont(CONST_fontbold, 9)
    p.drawString((margin*2)+60, tableheaderheight - (linecount * (count+1)), 'Total')
    totalstring = "%.2f" % cashupreport.total
    totalstringwidth = p.stringWidth(totalstring, CONST_font, 9)
    p.drawString((margin*2)+395-totalstringwidth, tableheaderheight - (linecount * (count+1)), totalstring)
    p.showPage()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = p.getpdfdata()
    buffer.close()
    return pdf


@login_required
def deletecashupreport(request, dcurid ):
    dcurid = request.GET.get('dcurid')
    cashupreport = CashUpReport.objects.filter(id = dcurid )
    msg = 'Cash up report from %s to %s have been deleted successfully.' % (cashupreport.first().sessiontimestamp.strftime('%d/%m/%Y @%H:%M:%S%p'), cashupreport.first().createtimestamp.strftime('%d/%m/%Y @%H:%M:%S%p') )
    if cashupreport:
        cashupreport.delete()
    return HttpResponseRedirect("/parcelhubPOS/cashupreport/?msg=%s" % msg)
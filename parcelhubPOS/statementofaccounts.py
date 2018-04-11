from django_tables2 import RequestConfig
from django.shortcuts import render
from django.forms import modelformset_factory
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .tables import StatementOfAccountTable
from .commons import *
from .models import StatementOfAccount, StatementOfAccountInvoice, Invoice, Customer, UserBranchAccess, Branch
from django.contrib.auth.models import User
from django.db import models
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
from datetime import timedelta, datetime
CONST_branchid = 'branchid'
CONST_font = 'Helvetica'
CONST_fontbold = CONST_font + '-Bold'
#method to retrieve Courier statementofacc list
@login_required
def statementofacclist(request):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    branchid = request.session.get(CONST_branchid)
    loguser = User.objects.get(id=request.session.get('userid'))
    if branchid == '-1':
        statementofacc_list = StatementOfAccount.objects.all()
    else:
        statementofacc_list = StatementOfAccount.objects.filter(customer__branch__id=branchid)
    formdata = {'customerinput':'',
                'date': ''
                }
    if request.method == "GET":
        submitted_customer = request.GET.get('customerinput') 
        if submitted_customer:
            formdata['customerinput'] = submitted_customer
            statementofacc_list =  statementofacc_list.filter(customer__name__icontains=submitted_customer)
        submitted_date = request.GET.get('date') 
        if submitted_date:
            formdata['date'] = submitted_date
            statementofacc_list =  statementofacc_list.filter(datefrom__lte=submitted_date,dateto__gt=submitted_date)
    final_StatementOfAccount_table = StatementOfAccountTable(statementofacc_list)
    
    RequestConfig(request, paginate={'per_page': 25}).configure(final_StatementOfAccount_table)
    issearchempty = True
    searchmsg = 'There no statement of account matching the search criteria...'
    try:
        if statementofacc_list or (not submitted_customer and not submitted_date):
            issearchempty = False
    except:
        issearchempty = False
    context = {
                'statementofacc': final_StatementOfAccount_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'formdata' : formdata,
                'title': "Statement of account",
                'isedit' : True,
                'issuperuser' : loguser.is_superuser,
                'isall': branchid == '-1',
                'statusmsg' : request.GET.get('msg'),
                'header': "Statement of account",
                'issearchempty': issearchempty,
                'searchmsg': searchmsg
                }
    return render(request, 'statementofaccount.html', context)

@login_required
def statementofaccnew(request):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
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
                'loggedusers' : loggedusers,
                'customerlist':customerlist,
                'title': "Generate statement of account",
                'isedit' : True,
                'issuperuser' : loguser.is_superuser,
                'isall': branchid != '-1',
                'header': "Generate statement of account",
                }
    return render(request, 'statementofaccount_new.html', context)
@login_required
def viewstatementofacc(request):
    try:
        soaid = request.GET.get('soaid')
        statementofacc = StatementOfAccount.objects.get(id=soaid)
    except:
        statementofacc = None;
    if statementofacc:
        pass
    elif request.method == "GET" and 'customerinput' in request.GET:
        customerid = request.GET.get('customerinput')
        date_from = request.GET.get('datefrom')
        date_to = request.GET.get('dateto')
        date_to = datetime.strptime(date_to, '%Y-%m-%d')
        date_to = date_to + timedelta(days=1) - timedelta(seconds=1);
        statementoption = request.GET.get('soaoptioninput')

        selectedcustomer =  Customer.objects.get(id=customerid)
        newcustid = customerid
        invoicelist = Invoice.objects.filter(customer__id = customerid, createtimestamp__gte = date_from, createtimestamp__lte=date_to)
        if statementoption == 'unpaid':
            invoicelist = invoicelist.filter(payment__gte=models.F('total'))      
        user = User.objects.get(id = request.session.get('userid'))
        statementofacc = StatementOfAccount(customer=selectedcustomer, datefrom = date_from, dateto=date_to, created_by=user, createtimestamp=timezone.now())
        statementofacc.id = newcustid + '_' + timezone.now().strftime("%d/%m/%Y %H:%M%p")  
        branchid = request.session.get(CONST_branchid)

        if branchid == '-1':
            pass
        else:
            selectedbranch = Branch.objects.get(id=branchid)
            statementofacc.branch = selectedbranch
        statementofacc.save()
        totalamt = 0.0;
        paidamt = 0.0;
        
        for inv in invoicelist:
            totalamt = totalamt + float(inv.total)
            
            try:
                payment = float(inv.payment)
            except:
                payment = 0.0;
            paidamt = paidamt + max( [payment, totalamt] )
            soainv = StatementOfAccountInvoice(soa=statementofacc, invoice=inv)
            soainv.id = statementofacc.id + '_' + inv.invoiceno
            soainv.save()
        outstandingamt = totalamt - paidamt;
        statementofacc.totalamount = totalamt
        statementofacc.paidamount = paidamt
        statementofacc.outstandindamount = outstandingamt
        statementofacc.save(update_fields=["totalamount", 'paidamount', 'outstandindamount']) 
    soa_pdf = statementofacc_pdf(request, statementofacc)
    return HttpResponse(soa_pdf, content_type='application/pdf')

def statementofacc_pdf(request, statementofacc):
    response = HttpResponse(content_type='application/pdf')
    customername = statementofacc.customer.name
    filename = 'Statement_' + customername + '_' + statementofacc.createtimestamp.strftime('%Y-%m-%d') 
    response['Content-Disposition'] = 'attachment; filename="'+filename+'.pdf"'
    soaitem = StatementOfAccountInvoice.objects.filter(soa=statementofacc).order_by('invoice')
    
    
        
    margin = 25;
    totalwidth = 590;
    totalheight = 820;
    center = totalwidth / 2.0
    
    customer = statementofacc.customer
    addresstokenize = []
    if customer.addressline1:
        addresstokenize.append(customer.addressline1)
    if customer.addressline2:
        addresstokenize.append(customer.addressline2)
    if customer.addressline3:
        addresstokenize.append(customer.addressline3)
    if customer.addressline4:
        addresstokenize.append(customer.addressline4)
    
    addressline = 4;
    
        
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont(CONST_fontbold, 12)
    # header
    branch = statementofacc.customer.branch
    topmargin = 20;
    headerstring = branch.owner.upper() + "("+ branch.registrationno+") |  (GST No: " + branch.gstno + ")"
    linecount = 12;
    p.drawCentredString(center, totalheight - topmargin, headerstring)
    p.setFont(CONST_font, 9)
    p.drawCentredString(center, totalheight - topmargin - (linecount * 1), branch.address)
    contactinfo = "Tel: " + branch.contact + " | Fax: " + branch.fax + " | " + branch.website 
    p.drawCentredString(center, totalheight - topmargin- (linecount * 2), contactinfo)
    
    p.setLineWidth(1)
    lineheight = totalheight - topmargin- (linecount * 6)
    p.line(margin, lineheight, totalwidth-margin, lineheight)
    p.setFont(CONST_font, 8)
    margin = margin + 2
    heightafterline = totalheight - topmargin- (linecount * 7)
    p.drawString(margin, heightafterline, "Customer")
    p.setFont(CONST_fontbold, 12)
    linecount = 12;
    heightcustaddress = heightafterline - ( linecount * 1.5 )
    p.drawString(margin, heightcustaddress, customer.name.upper())
    p.setFont(CONST_font, 12)
    addresslinedrawcount = 0;
    for line in addresstokenize:
        addresslinedrawcount = addresslinedrawcount + 1;
        p.drawString(margin, heightcustaddress - ( linecount * addresslinedrawcount ), line.lstrip())
    heightafteraddress = heightcustaddress - ( linecount * addressline )
    contactlineheight = 15;
    p.drawString(margin, heightafteraddress - (contactlineheight * 1), "Tel        " + customer.contact)
    customerfax = '';
    if customer.fax:
        customerfax = customer.fax
    p.drawString(margin, heightafteraddress - (contactlineheight * 2), "Fax        " + customerfax)
    lineheight = heightafteraddress - (contactlineheight * 2) - 5
    p.line(margin, lineheight, totalwidth-margin, lineheight)
    # Body
    p.setFont(CONST_font, 8)
    p.drawString( margin, lineheight - (linecount * 1), "Customer Account")
    p.drawString( margin + 150, lineheight - (linecount * 1), "Attendant")
    p.drawString( margin + 200, lineheight - (linecount * 1), "Currency")
    p.drawString( margin + 300, lineheight - (linecount * 1), "Page No")
    p.drawString( margin + 400, lineheight - (linecount * 1), "Terms")
    p.drawString( margin + 520, lineheight - (linecount * 1), "Date")
    p.setFont(CONST_fontbold, 11)
    custacc = customer.branch.branch_code + customer.identificationno
    p.drawString( margin, lineheight - (linecount * 2), custacc)
    
    username = statementofacc.created_by.last_name + ' ' +statementofacc.created_by.first_name
    usernamewidth = p.stringWidth(username, CONST_fontbold, 11)
    attendantstringwidth = p.stringWidth("Attendant", CONST_font, 8)
    p.drawString( margin + 150 + attendantstringwidth - usernamewidth, lineheight - (linecount * 2), username)
    currencywidth = p.stringWidth("Currency", CONST_font, 8)
    p.drawString( margin + 200 + currencywidth - 15, lineheight - (linecount * 2), "RM")
    pageno = "1/1"
    pagenowidth = p.stringWidth(pageno, CONST_fontbold, 11)
    pagenostringwidth = p.stringWidth("Page No", CONST_font, 8)
    p.drawString( margin + 300 + pagenostringwidth - pagenowidth, lineheight - (linecount * 2), pageno)
    terms = "30 days"
    termswidth = p.stringWidth(terms, CONST_fontbold, 11)
    termsstringwidth = p.stringWidth("Terms", CONST_font, 8)
    p.drawString( margin + 400 + termsstringwidth - termswidth, lineheight - (linecount * 2), terms)
    datestring = statementofacc.createtimestamp.strftime("%d/%m/%Y")
    datestringwidth = p.stringWidth(datestring, CONST_fontbold, 11)
    p.drawString( totalwidth - margin - datestringwidth, lineheight - (linecount * 2), datestring)
    
    lineheight = lineheight - (linecount * 2) - 7
    p.line(margin, lineheight, totalwidth-margin, lineheight)
    
    p.setFont(CONST_font, 8)
    p.drawString( margin, lineheight - (linecount * 1), "Date")
    p.drawString( margin + 70, lineheight - (linecount * 1), "Reference")
    p.drawString( margin + 160, lineheight - (linecount * 1), "Transaction Description")
    p.drawString( margin + 350, lineheight - (linecount * 1), "Debit")
    p.drawString( margin + 425, lineheight - (linecount * 1), "Credit")
    p.drawString( margin + 500, lineheight - (linecount * 1), "Balance")
    p.setFont(CONST_font, 11)
    itemheight = lineheight - (linecount * 2)
    itemcount = 0;
    cummulativedebit = 0.00;
    cummulativecredit = 0.00;
    creditcount = 0;
    cummulativebalance = 0.00;
    for item in soaitem:
        invoiceitem = item.invoice
        p.drawString( margin, itemheight - (linecount * itemcount), invoiceitem.createtimestamp.strftime("%d/%m/%Y"))
        p.drawString( margin + 70, itemheight - (linecount * itemcount), invoiceitem.invoiceno)
        if invoiceitem.remarks:
            remarks = invoiceitem.remarks
        else:
            remarks = ''
        p.drawString( margin + 160, itemheight - (linecount * itemcount), remarks)
        debitvalue = round(float(invoiceitem.total), 2 )
        debit = "{:,.2f}".format(debitvalue)
        cummulativedebit = cummulativedebit + debitvalue
        debitwidth = p.stringWidth(debit, CONST_font, 11)
        debitstringwidth = p.stringWidth("Debit", CONST_font, 8)
        p.drawString( margin + 350 + debitstringwidth - debitwidth, itemheight - (linecount * itemcount), debit)
        try:
            payment = float(invoiceitem.payment)
        except:
            payment = 0.00;
        creditvalue = round(payment, 2 )
        
        cummulativecredit = cummulativecredit + creditvalue
        credit = "{:,.2f}".format(creditvalue)
        if creditvalue > 0.00:
            creditcount += 1;
        else:
            credit = ''
        creditwidth = p.stringWidth(credit, CONST_font, 11)
        creditstringwidth = p.stringWidth("Credit", CONST_font, 8)
        p.drawString( margin + 425 + creditstringwidth - creditwidth, itemheight - (linecount * itemcount), credit)
        
        balancevalue = float(invoiceitem.total) - payment
        
        
        
        cummulativebalance = cummulativebalance + balancevalue
        balance = "{:,.2f}".format(round(cummulativebalance, 2 ))
        balancewidth = p.stringWidth(balance, CONST_font, 11)
        balancestringwidth = p.stringWidth("Balance", CONST_font, 8)
        p.drawString( margin + 500 + balancestringwidth - balancewidth, itemheight - (linecount * itemcount), balance)
        itemcount += 1;
    #Footer
    btmmargin = 40;
    
    #inflecteng = inflect.engine()
    #cummulativestring = inflecteng.number_to_words(cummulativebalance).upper()
    cummulativestring = num2words(cummulativebalance).upper()
    cummulativestring = cummulativestring.replace("POINT", " RINGGIT POINT")
    cummulativestring = 'RINGGIT MALAYSIA : ' + cummulativestring + " CENTS ONLY"
    valuestringcount = 0;
    for line in wrap(cummulativestring, 60):
        valuestringcount += 1;
    lineheight = btmmargin + (linecount * (8 + valuestringcount ))
    p.line(margin, lineheight, totalwidth-margin, lineheight)
    
    count = 1;
    for line in wrap(cummulativestring, 60):
        p.drawString(40, lineheight - (linecount * count ), line)
        count  += 1;
    
    p.drawString( totalwidth - 140, lineheight - linecount, "RM:")
    balance = "{:,.2f}".format(round(cummulativebalance, 2 ))
    balancewidth = p.stringWidth(balance, CONST_font, 11)
    balancestringwidth = p.stringWidth("Balance", CONST_font, 8)
    p.drawString( margin + 500 + balancestringwidth - balancewidth, lineheight - linecount, balance)
    p.setFont(CONST_font, 8)
    p.drawString(50, btmmargin + (linecount * 2), "We shall be grateful if you will let us have payment as soon as possible. Any discrepancy in this statement must be reported to us in writing")
    p.drawString(50, btmmargin + (linecount * 1), "within 10 days.")
    
    #Statement of account box
    height = heightafteraddress - (contactlineheight * 2) + 10
    p.rect(totalwidth - 250,height, 220, 90, stroke=True, fill=False) 
    
    p.setFont(CONST_font, 16)
    soatextheight = height + 75 ;
    centerbox = totalwidth - 250 + 110
    p.drawCentredString(centerbox, soatextheight, "Statement of Account")
    p.line(totalwidth - 250, soatextheight - 7, totalwidth - 30, soatextheight - 7)
    p.setFont(CONST_font, 11)
    p.drawString(totalwidth - 240, soatextheight - (linecount * 2.5 ), 'Total Debit (%d)' % itemcount)
    debitstring = "{:,.2f}".format(round(cummulativedebit, 2 ))
    debitstringwidth = p.stringWidth(debitstring, CONST_font, 11)
    p.drawString(totalwidth - 35 - debitstringwidth, soatextheight - (linecount * 2.5 ), debitstring)
    
    creditstring = "{:,.2f}".format(round(cummulativecredit, 2 ))
    creditstringwidth = p.stringWidth(creditstring, CONST_font, 11)
    p.drawString(totalwidth - 35 - creditstringwidth, soatextheight - (linecount * 3.5 ), creditstring)
    p.drawString(totalwidth - 240, soatextheight - (linecount * 3.5 ), 'Total Credit (%d)' % creditcount)
    p.setLineWidth(3)
    p.line( totalwidth - 245, soatextheight - (linecount * 4 ), totalwidth - 35, soatextheight - (linecount * 4 ))
    
    balancestring = "{:,.2f}".format(round(cummulativebalance, 2 ))
    balancestringwidth = p.stringWidth(balancestring, CONST_font, 11)
    p.drawString(totalwidth - 35 - balancestringwidth, soatextheight - (linecount * 5.5 ), balancestring)
    p.drawString(totalwidth - 240, soatextheight - (linecount * 5.5 ), 'Closing Balance')
    
    # Monthly summary box
    p.setLineWidth(1)
    p.setFont(CONST_font, 9)
    boxmargin = 70;
    boxwidth = 75
    boxytop = btmmargin + (linecount * 3)
    
    p.rect(boxmargin ,btmmargin + (linecount * 3) + 15, boxwidth, 15, stroke=True, fill=False) 
    p.drawRightString( boxmargin + (boxwidth * 1 ) - 2, boxytop + 18, 'Current Mth')
    p.rect(boxmargin + (boxwidth * 1 ) ,boxytop + 15, boxwidth, 15, stroke=True, fill=False)
    p.drawRightString( boxmargin + (boxwidth * 2 ) - 2, boxytop + 18, '1 Month')
    p.rect(boxmargin + (boxwidth * 2 ) ,boxytop + 15, boxwidth, 15, stroke=True, fill=False)
    p.drawRightString( boxmargin + (boxwidth * 3 ) - 2, boxytop + 18, '2 Month')
    p.rect(boxmargin + (boxwidth * 3 ) ,boxytop + 15, boxwidth, 15, stroke=True, fill=False)
    p.drawRightString( boxmargin + (boxwidth * 4 ) - 2, boxytop + 18, '3 Month')
    p.rect(boxmargin + (boxwidth * 4 ) ,boxytop + 15, boxwidth, 15, stroke=True, fill=False)
    p.drawRightString( boxmargin + (boxwidth * 5 ) - 2, boxytop + 18, '4 Month')
    p.rect(boxmargin + (boxwidth * 5 ) ,boxytop + 15, boxwidth, 15, stroke=True, fill=False)
    p.drawRightString( boxmargin + (boxwidth * 6 ) - 2, boxytop + 18, '5 Month+')
    
    p.rect(boxmargin, boxytop, boxwidth, 15, stroke=True, fill=False) 
    
    p.rect(boxmargin + (boxwidth * 1 ), boxytop, boxwidth, 15, stroke=True, fill=False) 
    p.rect(boxmargin + (boxwidth * 2 ) ,boxytop, boxwidth, 15, stroke=True, fill=False) 
    p.rect(boxmargin + (boxwidth * 3 ) ,boxytop, boxwidth, 15, stroke=True, fill=False) 
    p.rect(boxmargin + (boxwidth * 4 ) ,boxytop, boxwidth, 15, stroke=True, fill=False) 
    p.rect(boxmargin + (boxwidth * 5 ) ,boxytop, boxwidth, 15, stroke=True, fill=False) 
    
    currentmonthitem = soaitem.filter(invoice__createtimestamp__month = statementofacc.get_month(),
                                      invoice__createtimestamp__year = statementofacc.get_year())
    currentmonthbalance = calculate_soabalance(currentmonthitem)
    p.drawRightString( boxmargin + (boxwidth * 1 ) - 2, boxytop + 3, str(round(currentmonthbalance, 2)))
    
    month1 = get_month_year_value(statementofacc.get_month(), statementofacc.get_year(), 1)
    month1item = soaitem.filter(invoice__createtimestamp__month = month1[0],
                                invoice__createtimestamp__year =  month1[1])
    month1balance = calculate_soabalance(month1item)
    p.drawRightString( boxmargin + (boxwidth * 2 ) - 2, boxytop + 3, str(round(month1balance, 2)))
    
    month2 = get_month_year_value(statementofacc.get_month(), statementofacc.get_year(), 2)
    month2item = soaitem.filter(invoice__createtimestamp__month = month2[0],
                                invoice__createtimestamp__year =  month2[1])
    month2balance = calculate_soabalance(month2item)
    p.drawRightString( boxmargin + (boxwidth * 3 ) - 2, boxytop + 3, str(round(month2balance, 2)))
    
    month3 = get_month_year_value(statementofacc.get_month(), statementofacc.get_year(), 3)
    month3item = soaitem.filter(invoice__createtimestamp__month = month3[0],
                                invoice__createtimestamp__year =  month3[1])
    month3balance = calculate_soabalance(month3item)
    p.drawRightString( boxmargin + (boxwidth * 4 ) - 2, boxytop + 3, str(round(month3balance, 2)))
    
    month4 = get_month_year_value(statementofacc.get_month(), statementofacc.get_year(), 4)
    month4item = soaitem.filter(invoice__createtimestamp__month = month4[0],
                                invoice__createtimestamp__year =  month4[1])
    month4balance = calculate_soabalance(month4item)
    p.drawRightString( boxmargin + (boxwidth * 5 ) - 2, boxytop + 3, str(round(month4balance, 2)))
    
    month5balance = cummulativebalance - currentmonthbalance - month1balance - month2balance - month3balance - month4balance
    p.drawRightString( boxmargin + (boxwidth * 6 ) - 2, boxytop + 3, str(round(month5balance, 2)))
    p.showPage()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = p.getpdfdata()
    buffer.close()
    return pdf
def get_month_year_value(month, year, offsetmonth):
    monthafteroffset = month - offsetmonth;
    outputyear = year
    if monthafteroffset <= 0:
        outputyear = year - 1
        monthafteroffset = 12 + monthafteroffset
    return (monthafteroffset, year)
def calculate_soabalance(soaitem):
    balance = 0.00;
    
    for item in soaitem:
        invoiceitem = item.invoice
        try:
            payment = float(invoiceitem.payment)
        except:
            payment = 0.00
        balancevalue = float(invoiceitem.total) - payment
        balance = balance + balancevalue
    return balance
@login_required
def deletestatementofacc(request, dsoaid ):
    dsoaid = request.GET.get('dsoaid')
    statementofacc = StatementOfAccount.objects.filter(id = dsoaid )
    msg = 'Statement of account for customer "%s" from %s to %s have been deleted successfully.' % (statementofacc.first().customer.name, str(statementofacc.first().datefrom), str(statementofacc.first().dateto) )
    if statementofacc:
        statementofacc.delete()
    return HttpResponseRedirect("/parcelhubPOS/statementofaccount/?msg=%s" % msg)
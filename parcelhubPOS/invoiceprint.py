from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics  
from reportlab.pdfbase.ttfonts import TTFont
from datetime import timedelta 
from django.utils import timezone
from django.db.models import Sum
import os  
import reportlab
import ctypes
from io import BytesIO, StringIO
from django.http import HttpResponse
from .models import Invoice, InvoiceItem, SKU, Branch, Tax
from decimal import Decimal
from textwrap import wrap
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_URL = '/static/'

folder = PROJECT_ROOT + STATIC_URL + 'fonts'    
ttfFile = os.path.join(folder, 'DejaVuSansMono.ttf')     
pdfmetrics.registerFont(TTFont("DejaVuSansMono", ttfFile)) 
ttfFilebold = os.path.join(folder, 'DejaVuSansMono-Bold.ttf')     
pdfmetrics.registerFont(TTFont("DejaVuSansMono-Bold", ttfFilebold)) 
# Constants
CONST_font = 'Helvetica'
CONST_fontbold = CONST_font + '-Bold'

def invoice_pdf(request, invoiceid):
    # Create the HttpResponse object with the appropriate PDF headers.
    invoice = Invoice.objects.get(id=invoiceid)
    response = HttpResponse(content_type='application/pdf')
    filename = invoice.invoiceno
    response['Content-Disposition'] = 'attachment; filename="'+filename+'.pdf"'
    invoiceitem = InvoiceItem.objects.filter(invoice=invoice).order_by('sku', 'tracking_code')
    finaldict = {}
    invoiceitemdict = []
    currentsku = ''
    itemdict = {}
    itemcount = 0;
    page = 1;
    currentpage = page;
    remainingitem = invoiceitem.count();
    for item in invoiceitem:
        itemcount += 1
        remainingitem -= 1
        if currentsku != item.skudescription or currentpage != page:
            itemcount += 1
            itemdict = {}
            if currentsku != item.sku:
                skuselected = SKU.objects.get(sku_code=item.sku)
                itemdict['sku'] = item.sku
                itemdict['tax'] = skuselected.tax_code.id
                itemdict['price'] = item.price
                itemdict['qty'] = item.unit
                if skuselected.product_type.name == 'Services' or skuselected.product_type.name == 'Packaging':
                    itemdict['shipping'] = 'false'
                else:
                    itemdict['shipping'] = 'true'
            if currentpage != page:
                currentpage = page
            currentsku = item.skudescription
            itemdict['items'] = []
            itemdict['description'] = item.skudescription 
            invoiceitemdict.append(itemdict)
        itemdict['items'].append(item.tracking_code) 
        if (page == 1 and itemcount == 40 and remainingitem == 0) or (page == 1 and itemcount == 53) or itemcount == 72 or remainingitem == 0:
            finaldict[page]=invoiceitemdict
            invoiceitemdict = []
            page += 1;
            itemcount = 0;
    buffer = BytesIO()
    
    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont(CONST_fontbold, 16)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    owner = invoice.branch.owner
    marginleft = 25;
    p.drawString(marginleft, 800, owner.upper())
    p.setLineWidth(1)
    p.line(marginleft, 790, 570, 790)
    p.setFont(CONST_font, 8)
    gstno = ''
    if invoice.branch.gstno:
        gstno = invoice.branch.gstno
    p.drawString(marginleft, 780, 'Co Reg No: ' + invoice.branch.registrationno +'            GST No: '+ gstno) 
    p.drawString(marginleft, 770, invoice.branch.address)
    p.drawString(marginleft, 760, 'Phone: '+invoice.branch.contact)
    tollfree = '-'
    if invoice.branch.tollfree:
        tollfree = invoice.branch.tollfree
    website = '-'
    if invoice.branch.website:
        website = invoice.branch.website
    p.drawString(marginleft, 750, 'Toll Free: ' + tollfree +'            Website: '+ website)
    p.setFont( CONST_fontbold, 24)
    p.drawString(marginleft, 720, 'Tax Invoice')
    p.setFont(CONST_font, 10)
    p.setFillColorRGB(0.5, 0.5, 0.5 )
    p.setStrokeColorRGB(0.5, 0.5, 0.5 )
    # Invoice number box
    p.rect(marginleft,690,70,15, stroke=True, fill=True)
    p.rect(95,690,100,15, stroke=True, fill=False)
    # Date box
    p.rect(205,690,50,15, stroke=True, fill=True)
    p.rect(255,690,120,15, stroke=True, fill=False)
    
    
    p.setFillColorRGB(0, 0, 0 )
    # Invoice no text
    p.drawString(38,693, 'Invoice no')
    p.drawString(110,693, invoice.invoiceno)
    # Date text
    p.drawString(220,693, 'Date')
    p.drawString(270,693, invoice.createtimestamp.strftime("%d/%m/%Y %H:%M%p") )
    customername = ''
    if invoice.customer:
        customername = invoice.customer.name
    p.drawString(30, 670, 'Invoice to: ' + customername)
    
    # Invoice to
    p.rect(marginleft,630, 550, 50, stroke=True, fill=False)
    # Invoice items
    pagenum = 1;
    for each in finaldict:
        pageitemdict = finaldict[each]
        p.setFont(CONST_fontbold, 10)
        if (pagenum == 1 and invoiceitem.count() <= 40 ):
            headery = 613
            headerboxy = 610
            boxy = 200
            boxheight = 405
            y = 595
        elif (pagenum == 1 and invoiceitem.count() > 53 ):
            headery = 613
            headerboxy = 610
            boxy = 50
            boxheight = 555
            y = 595
        elif (pagenum  == len(finaldict) ):
            headery = 783
            headerboxy = 780
            boxy = 200
            boxheight = 580
            y = 765
        else:
            headery = 783
            headerboxy = 780
            boxy = 50
            boxheight = 730
            y = 765
        # Invoice item title
        p.setStrokeColorRGB(0.5, 0.5, 0.5 )
        p.setFillColorRGB(0.5, 0.5, 0.5 )
        p.rect(marginleft,headerboxy, 550, 15, stroke=True, fill=True)  
        p.setFillColorRGB(0, 0, 0 )   
        p.drawString(30, headery, 'SKU code                       Description                                                         Tax             Price RM         Qty             Total RM')
        p.setFont(CONST_font, 10)
        p.rect(marginleft,boxy, 115, boxheight, stroke=True, fill=False) # SKU code
        p.rect(140,boxy, 195, boxheight, stroke=True, fill=False) # Description
        p.rect(335,boxy, 40, boxheight, stroke=True, fill=False) # Tax
        p.rect(375,boxy, 80, boxheight, stroke=True, fill=False) # Price
        p.rect(455,boxy, 40, boxheight, stroke=True, fill=False) # Quantity
        p.rect(495,boxy, 80, boxheight, stroke=True, fill=False) #Total RM
        count = 0;
        itemcount = 0;
        topy = y;
        for item in pageitemdict:
            y = topy - (count * 10) 
            if 'sku' in item:
                p.drawString(30, y, item['sku'])
                p.drawString(145, y, item['description'])
                # tax string
                taxwidth = p.stringWidth(item['tax'], CONST_font, 10)
                p.drawString(370-taxwidth, y, item['tax'])
                # price string
                pricestring = str(item['price'])
                pricewidth = p.stringWidth(pricestring, CONST_font, 10)
                p.drawString(450-pricewidth, y, pricestring)
                # qty string
                if item['shipping'] == 'true':
                    qty = len(item['items']);
                else:
                    qty = item['qty'];
                    itemcount += qty
                qtywidth = p.stringWidth(str(qty), CONST_font, 10)
                p.drawString(490-qtywidth, y, str(qty))
                # total string
                total = item['price'] * qty
                totalwidth = p.stringWidth(str(total), CONST_font, 10)
                p.drawString(570-totalwidth, y, str(total))
                count +=1
            # item details
            for trackcode in item['items']:
                if trackcode:
                    itemcount += 1;
                    
                    dy = topy - (count * 10)
                    if trackcode:
                        p.drawString(155, dy, 'S/No: ' + trackcode )
                    else:
                        p.drawString(155, dy, 'S/No: ' + '-' )
                    count += 1
            
        
        totalitem = 'No. of items (%d)' % itemcount
        totalitemwidth = p.stringWidth(totalitem, CONST_font, 10)
        p.drawString(490-totalitemwidth, boxy-10, totalitem)
        if (pagenum  != len(finaldict) ):
            pagenumstr =str(pagenum)+ '/' + str(len(finaldict))
            p.drawString(560, 10, pagenumstr)
            p.showPage()
            pagenum += 1
    
    
    # Bottom titles and details
    p.setFont(CONST_fontbold, 10)
    p.setFillColorRGB(0.5, 0.5, 0.5 )
    p.rect(marginleft,165, 273, 15, stroke=True, fill=True) #Invoice details title
    p.rect(305,165, 270, 15, stroke=True, fill=True) #Invoice totals title
    
    p.setFillColorRGB(0, 0, 0 )
    p.drawString(90, 168, 'Invoice & Attendant details')
    p.drawString(410, 168, 'Invoice Totals (RM)')
    p.setFont(CONST_font, 10)
    p.drawString(30, 153, 'Invoice no')
    p.drawString(130, 153, invoice.invoiceno)
    p.drawString(30, 138, 'Payment due')
    paymentduedate = invoice.createtimestamp + timedelta(days=30)
    p.drawString(130, 138, paymentduedate.strftime("%d/%m/%Y") )
    username = invoice.created_by.last_name + ' ' +invoice.created_by.first_name
    p.drawString(30, 123, 'Attendant')
    p.drawString(130, 123, username)
    # Payment rules
    p.drawString(35, 100, 'All cheque must be crossed & made payable to')
    p.drawString(35, 85, owner.upper())
    paymentbank = ''
    if invoice.branch.payment_bank:
        paymentbank = invoice.branch.payment_bank
    bankacc = ''
    if invoice.branch.payment_acc:
        bankacc = invoice.branch.payment_acc
    p.drawString(35, 70, paymentbank + ' A/C No: '+ bankacc)
    # Invoice total titles
    end = 570
    p.drawString(310, 153, 'Subtotal')
    subtotal = "%.2f" % invoice.subtotal
    subtotalwidth = p.stringWidth(subtotal, CONST_font, 10)
    p.drawString(end - subtotalwidth, 153, subtotal)
    p.drawString(310, 138, 'Discount')
    discount = '0.00'
    if invoice.discountvalue and invoice.discountvalue > 0.00:
        discount = "-%.2f" % invoice.discountvalue
    discountwidth = p.stringWidth(discount, CONST_font, 10)
    p.drawString(end - discountwidth, 138, discount)
    p.drawString(310, 123, 'GST')
    gst = "%.2f" % invoice.gst
    gstwidth = p.stringWidth(gst, CONST_font, 10)
    p.drawString(end - gstwidth, 123, gst)
    p.drawString(310, 108, 'Rounding')
    roundingvalue = float(invoice.total) - (float(invoice.subtotal) - float(invoice.discountvalue) + float(invoice.gst))
    rounding = "%.2f" % roundingvalue
    if rounding == "-0.00":
        rounding = "0.00"
    roundingwidth = p.stringWidth(rounding, CONST_font, 10)
    p.drawString(end - roundingwidth, 108, rounding)
    p.drawString(310, 55, 'TOTAL inc GST')
    total = "%.2f" % invoice.total
    totalwidth = p.stringWidth(total, CONST_font, 10)
    p.drawString(end - totalwidth, 55, total)
    # bottom boxes
    p.rect(marginleft,50, 273, 115, stroke=True, fill=False) #Invoice details
    p.rect(marginleft,150, 100, 15, stroke=True, fill=False) #Invoice no
    p.rect(125,150, 173, 15, stroke=True, fill=False) #Invoice no info
    p.rect(marginleft,135, 100, 15, stroke=True, fill=False) #Payment due
    p.rect(125,135, 173, 15, stroke=True, fill=False) #Payment due info
    p.rect(marginleft,120, 100, 15, stroke=True, fill=False) #Attendant due
    p.rect(125,120, 173, 15, stroke=True, fill=False) #Attendant due info
    p.rect(305,50, 270, 115, stroke=True, fill=False) #Invoice totals
    p.rect(305,50, 120, 115, stroke=True, fill=False) #Invoice totals titles
    p.drawString(280, 40, 'Thank you')
    pagenumstr = str(pagenum)+ '/' + str(len(finaldict))
    p.drawString(560, 10, pagenumstr)
    p.showPage()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = p.getpdfdata()
    buffer.close()
    return pdf


CONST_fontr = 'DejaVuSansMono'
CONST_fontrbold = CONST_fontr + '-Bold'
def invoice_thermal(request, invoiceid):
    invoice = Invoice.objects.get(id=invoiceid)
    response = HttpResponse(content_type='application/pdf')
    filename = invoice.invoiceno
    response['Content-Disposition'] = 'attachment; filename="'+filename+'_receipt.pdf"'
    invoiceitem = InvoiceItem.objects.filter(invoice=invoice).order_by('skudescription', 'tracking_code')
    invoiceitemdict = []
    currentsku = ''
    itemdict = {}
    linecount = 0;
    for item in invoiceitem:
        linecount += 1
        if currentsku != item.skudescription:
            skuselected = SKU.objects.get(sku_code=item.sku)
            linecount += 2
            itemdict = {}
            currentsku = item.skudescription
            itemdict['items'] = []
            itemdict['sku'] = currentsku
            itemdict['price'] = item.price
            itemdict['description'] = item.skudescription
            itemdict['qty'] = item.unit
            if skuselected.product_type.name == 'Services' or skuselected.product_type.name == 'Packaging':
                itemdict['shipping'] = 'false'
            else:
                itemdict['shipping'] = 'true'
            invoiceitemdict.append(itemdict)
        itemdict['items'].append(item.tracking_code)
    buffer = BytesIO()
    
    # Create the PDF object, using the BytesIO object as its "file."
    
    
    p = canvas.Canvas(buffer)
    totalwidth = 80 * mm
    marginleft = 15
    topmargin = 40
    center = totalwidth / 2.0
    addresstxt = invoice.branch.address
    addressline = 0;
    addressallowedwith = 35
    for line in wrap(addresstxt, addressallowedwith ):
        addressline += 1;
    # GST summary
    gstsummary = {}
    taxcode = ''
    gstvalue = 0.0;
    for item in invoiceitem:
        sku = SKU.objects.get(sku_code = item.sku)
        tax = sku.tax_code
        gsttitletxt = ''
        if tax:
            gstvalue = tax.gst
            gstvaluetxt =  "%.0f" % gstvalue
            gsttitletxt = tax.id + ' @ ' + gstvaluetxt + '%'
        if gsttitletxt != '' and gsttitletxt not in gstsummary:
            gstsummary[gsttitletxt] = [0.0, 0.0]
        gstsummary[gsttitletxt][0] = gstsummary[gsttitletxt][0] + float(item.price) - float(item.gst)
        gstsummary[gsttitletxt][1] = gstsummary[gsttitletxt][1] + float(item.gst)

    linespace = 11
    topsize = (19 + addressline) * linespace
    middlesize = linecount * linespace
    btmsize = ( 17 + (len(gstsummary) + 1) ) * linespace
    totallength = topsize + middlesize + btmsize
    
    p.setPageSize((totalwidth, totallength))
    p.setFont(CONST_fontrbold, 8)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    owner = invoice.branch.owner
    
    p.drawCentredString(center, totallength - topmargin, owner.upper())
    p.setFont(CONST_fontr, 8)
    regnotext = 'Co Reg No: ' + invoice.branch.registrationno
    p.drawCentredString(center, totallength - topmargin - linespace, regnotext ) 
    gsttext = 'GST No: '+ invoice.branch.gstno
    p.drawCentredString(center, totallength - topmargin - ( linespace * 2 ), gsttext ) 
    addresslinedrawcount = 2;
    for line in wrap(addresstxt, addressallowedwith ):
        addresslinedrawcount += 1;
        p.drawCentredString(center, totallength - topmargin - ( linespace * addresslinedrawcount ), line)
        
    contacttxt = 'Phone: '+invoice.branch.contact
    p.drawCentredString(center, totallength - topmargin - ( linespace * ( addresslinedrawcount + 1 )  ), contacttxt)
    tollfreetxt = 'Toll Free: ' + invoice.branch.tollfree
    p.drawCentredString(center, totallength - topmargin - ( linespace * ( addresslinedrawcount + 2 ) ), tollfreetxt )
    websitetxt = 'Website: '+ invoice.branch.website
    p.drawCentredString(center, totallength - topmargin - ( linespace * ( addresslinedrawcount + 3 ) ),websitetxt)
    
    p.drawCentredString(center, totallength - topmargin - (( linespace * ( addresslinedrawcount + 4 ) ) + 3 ), 'Tax Invoice')

    # Invoice no text
    p.drawString(marginleft,totallength - topmargin - ( linespace * ( addresslinedrawcount + 6 ) ), 'Invoice no  : ' + invoice.invoiceno)
    username = invoice.created_by.last_name + ' ' +invoice.created_by.first_name
    p.drawString(marginleft,totallength - topmargin - ( linespace * ( addresslinedrawcount + 7 ) ),'Served by   : ' + username)
    # Date text
    p.drawString(marginleft,totallength - topmargin - ( linespace * ( addresslinedrawcount + 8 ) ),'Date        : ' + invoice.createtimestamp.strftime("%d/%m/%Y %I:%M%p"))
    p.drawString(marginleft,totallength - topmargin - ( linespace * ( addresslinedrawcount + 9 ) ),'Sold to     : Cash' )
    
    # Invoice items 
    p.setFillColorRGB(0, 0, 0 ) 
    p.setFont(CONST_fontrbold, 8)
    p.drawString(marginleft, totallength - topmargin - ( linespace * ( addresslinedrawcount + 12 ) ), 'Description')  
    p.drawString(marginleft, totallength - topmargin - ( linespace * ( addresslinedrawcount + 13 ) ), 'SKU            Price RM   Qty   Total RM')
    headerliney = totallength - topmargin - ( (linespace * ( addresslinedrawcount + 13 ) ) + 5) 
    p.line( marginleft, headerliney, totalwidth - marginleft, headerliney )
    p.setFont(CONST_fontr, 8)
    topy = totallength - topmargin - ( (linespace * ( addresslinedrawcount + 14 ) ) + 5) ;
    count = 0
    for item in invoiceitemdict:
        y = topy - (count * linespace) 
        p.drawString(marginleft, y, item['description'])
        count += 1
        # item details
        for trackcode in item['items']:
            if trackcode:
                count += 1
                dy = topy - (count * linespace)
                trackcodeval = trackcode
                p.drawString(marginleft, dy, ' S/No. ' + trackcodeval )
        # price string
        pricestring = str(item['price'])
        pricewidth = p.stringWidth(pricestring, CONST_fontr, 9)
        p.drawString(130-pricewidth, y - linespace, pricestring)
        # qty string
        if item['shipping'] == 'true':
            qty = len(item['items']);
        else:
            qty = item['qty'];
        qtywidth = p.stringWidth(str(qty), CONST_fontr, 9)
        p.drawString(155-qtywidth, y - linespace , str(qty))
        # total string
        total = item['price'] * qty
        totalpricewidth = p.stringWidth(str(total), CONST_fontr, 9)
        p.drawString(totalwidth - marginleft -totalpricewidth, y - linespace, str(total))
        count += 1
    # totals details
    footerliney = topy - ( (linespace *  (count -1 )) + 5) 
    p.line( marginleft, footerliney, totalwidth - marginleft, footerliney )
    # Sub total title
    subtotaly = footerliney - (linespace  )
    p.setFont(CONST_fontrbold, 8)
    p.drawString( marginleft + 40, subtotaly , 'Sub Total')
    
    # GST total title
    gsttitletxt = 'GST'
    try:
        tax = Tax.objects.get(gst__gt = Decimal('0.00'))
        if tax:
            gstvalue = tax.gst
            gstvaluetxt =  "%.0f" % gstvalue
            gsttitletxt = 'GST' + '@' + gstvaluetxt + '%'
    except:
        pass
    gsty = footerliney - (linespace * 2)
    p.drawString( marginleft + 40, gsty, gsttitletxt)
    # Discount title
    discounty = footerliney - (linespace * 3 )
    p.setFont(CONST_fontrbold, 8)
    p.drawString( marginleft + 40, discounty , 'Discount')
    # total title
    totaly = footerliney - (linespace * 4)
    p.drawString( marginleft + 40, totaly , 'Total inc GST')
    # Payment details
    paymenttitley = footerliney - ((linespace * 7) )
    p.drawString( marginleft, paymenttitley, 'Payment Details  -  ' + invoice.payment_type.name)
    
    paymentreceivedy = footerliney - ((linespace * 8) + 5)
    p.drawString( marginleft + 40, paymentreceivedy, 'Received: ')
    changey = footerliney - ((linespace * 9) + 5)
    p.drawString( marginleft + 40, changey, 'Change: ')
    p.setFont(CONST_fontr, 8)
    
    currencymargin = 80
    # Subtotal
    subtotaltxt = str(invoice.subtotal)
    subtotalwidth = p.stringWidth(subtotaltxt, CONST_fontr, 9)
    p.drawString( totalwidth - marginleft - subtotalwidth, subtotaly, subtotaltxt )
    p.drawString( totalwidth - currencymargin, subtotaly, 'RM' )
     # Discount
    discounttxt = str(invoice.discountvalue)
    discountwidth = p.stringWidth(discounttxt, CONST_fontr, 9)
    p.drawString( totalwidth - marginleft - discountwidth, discounty, discounttxt )
    p.drawString( totalwidth - currencymargin, discounty, 'RM' )
    # GST
    gsttxt = str(invoice.gst)
    gstwidth = p.stringWidth(gsttxt, CONST_fontr, 9)
    p.drawString( totalwidth - marginleft - gstwidth, gsty, gsttxt )
    p.drawString( totalwidth - currencymargin, gsty, 'RM' )
    # Total
    totaltxt = str(invoice.total)
    finaltotalwidth = p.stringWidth(totaltxt, CONST_fontr, 9)
    p.drawString( totalwidth - marginleft - finaltotalwidth, totaly, totaltxt )
    p.drawString( totalwidth - currencymargin, totaly, 'RM' )
    # Received
    receivedtxt = str(invoice.payment)
    receivedwidth = p.stringWidth(receivedtxt, CONST_fontr, 9)
    p.drawString( totalwidth - marginleft - receivedwidth, paymentreceivedy, receivedtxt )
    p.drawString( totalwidth - currencymargin, paymentreceivedy, 'RM' )
    # Change
    changetxt = '%.2f' %(invoice.payment-invoice.total)
    changewidth = p.stringWidth(changetxt, CONST_fontr, 9)
    p.drawString( totalwidth - marginleft - changewidth, changey, changetxt )
    p.drawString( totalwidth - currencymargin, changey, 'RM' )
    btmmargin = 10;
    
    # Payment
    p.setStrokeColorRGB(0.5, 0.5, 0.5 )
    headerboxy = btmmargin + ( linespace + 5)
    p.rect(marginleft,footerliney - ((linespace * 10)+5), (totalwidth - marginleft * 2), linespace * 3, stroke=True, fill=False)  
    
    
    p.setFont(CONST_fontrbold, 8)
    p.drawString(marginleft, btmmargin + ( (len(gstsummary)+2) * linespace ), "GST Summary:     Amount(RM)       Tax(RM)")   
    gstcount = 0;
    for key, value in sorted(gstsummary.items()):
        p.drawCentredString(marginleft + 30, btmmargin + ( (len(gstsummary) + 1 - gstcount ) * linespace ), key)
        amount = '%.2f' %(value[0])
        amount = '%.2f' %(value[1])
        p.drawCentredString(marginleft + 110, btmmargin + ( (len(gstsummary) + 1 - gstcount ) * linespace ), amount)
        p.drawCentredString(marginleft + 183, btmmargin + ( (len(gstsummary) + 1- gstcount ) * linespace ), amount)
        gstcount = gstcount + 1;
    # thank you 
    p.drawCentredString(center, btmmargin, 'Thank you')
    p.showPage()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = p.getpdfdata()
    buffer.close()
    return pdf

def deliveryorder_pdf(request, invoiceid):
    # Create the HttpResponse object with the appropriate PDF headers.
    invoice = Invoice.objects.get(id=invoiceid)
    response = HttpResponse(content_type='application/pdf')
    filename = invoice.invoiceno
    response['Content-Disposition'] = 'attachment; filename="do_'+filename+'.pdf"'
    invoiceitem = InvoiceItem.objects.filter(invoice=invoice).order_by('sku', 'tracking_code')
    finaldict = {}
    invoiceitemdict = []
    currentsku = ''
    itemdict = {}
    itemcount = 0;
    page = 1;
    currentpage = page;
    remainingitem = invoiceitem.count();
    for item in invoiceitem:
        itemcount += 1
        remainingitem -= 1
        if currentsku != item.sku or currentpage != page:
            itemcount += 1
            itemdict = {}
            if currentsku != item.sku:
                itemdict['sku'] = item.sku
            if currentpage != page:
                currentpage = page
            currentsku = item.sku
            itemdict['items'] = []
            
            
            try:
                sku = SKU.objects.get(sku_code=currentsku)
                itemdict['description'] = sku.description 
            except:
                pass
            invoiceitemdict.append(itemdict)
        itemdict['items'].append(item.tracking_code) 
        if (page == 1 and itemcount == 25 and remainingitem == 0) or (page == 1 and itemcount == 38) or itemcount == 72 or remainingitem == 0:
            finaldict[page]=invoiceitemdict
            invoiceitemdict = []
            page += 1;
            itemcount = 0;
    buffer = BytesIO()
    
    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont(CONST_fontbold, 16)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    owner = invoice.branch.owner
    marginleft = 25;
    top = 800
    linesize = 10;
    p.drawString(marginleft, top, owner.upper())
    p.setLineWidth(1)
    p.line(marginleft, top - (linesize), 570, 790)
    p.setFont(CONST_font, 8)
    p.drawString(marginleft, top - (linesize * 2), 'Co Reg No: ' + invoice.branch.registrationno +'            GST No: '+ invoice.branch.gstno) 
    p.drawString(marginleft, top - (linesize * 3), invoice.branch.address)
    p.drawString(marginleft, top - (linesize * 4), 'Phone: '+invoice.branch.contact)
    p.drawString(marginleft, top - (linesize * 5), 'Toll Free: ' + invoice.branch.tollfree +'            Website: '+ invoice.branch.website)
    p.setFont( CONST_fontbold, 24)
    p.drawString(marginleft+30, top - (linesize * 11), 'Delivery Note')
    p.setFont(CONST_fontbold, 10)
    
    # Transaction details
    p.setFillColorRGB(0.75, 0.75, 0.75 )
    p.setStrokeColorRGB(0.75, 0.75, 0.75 )
    p.setFillColorRGB(0, 0, 0 )
    p.roundRect(marginleft+280,top - (linesize * 11), 273, 45, 4,stroke=True, fill=False)
    p.line(marginleft+280, top - (linesize * 8), marginleft+553, top - (linesize * 8) )
    p.line(marginleft+280, top - (linesize * 10) + 5, marginleft+553, top - (linesize * 10) + 5)
    p.line(marginleft+380, top - (linesize * 11)+45 , marginleft+380, top - (linesize * 11))
    p.roundRect(marginleft+280,top - (linesize * 14) - 5, 273, 30, 4,stroke=True, fill=False)
    p.line(marginleft+280, top - (linesize * 13), marginleft+553, top - (linesize * 13))
    p.line(marginleft+380, top - (linesize * 14)+25 , marginleft+380, top - (linesize * 14)-5)
    p.drawString(marginleft+285, top - (linesize * 6), "Transaction details" )
    p.drawString(marginleft+285, top - (linesize * 7) - 5, "Type:" )
    p.drawString(marginleft+285, top - (linesize * 9) , "Number:" )
    p.drawString(marginleft+285, top - (linesize * 10) - 5, "Date:" )
    
    p.drawString(marginleft+285, top - (linesize * 12) - 5 , "Printed date:" )
    p.drawString(marginleft+285, top - (linesize * 14) , "Served by:" )
    p.setFont(CONST_font, 10)
    p.drawString(marginleft+385, top - (linesize * 7) - 5, "Account sale" )
    p.drawString(marginleft+385, top - (linesize * 9) , filename )
    p.drawString(marginleft+385, top - (linesize * 10) - 5, invoice.createtimestamp.strftime("%d/%m/%Y") )

    p.drawString(marginleft+385, top - (linesize * 12) - 5 , timezone.now().date().strftime("%d/%m/%Y") )
    username = invoice.created_by.last_name + ' ' +invoice.created_by.first_name
    p.drawString(marginleft+385, top - (linesize * 14) , username )
    # DO to
    p.roundRect(marginleft,top - (linesize * 23) - 5, 550, 80, 4,stroke=True, fill=False)
    cust = invoice.customer
    customername = ''
    if cust:
        customername = cust.name
        if cust.addressline1: 
            p.drawString(marginleft + 5, top - (linesize * 18) - 5, "                  " + cust.addressline1)
        if cust.addressline2:
            p.drawString(marginleft + 5, top - (linesize * 20), "                  " +cust.addressline2)
        if cust.addressline3:
            p.drawString(marginleft + 5, top - (linesize * 21) - 5, "                  " +cust.addressline3)
        if cust.addressline4:
            p.drawString(marginleft + 5, top - (linesize * 23), "                  " +cust.addressline4)
    p.drawString(marginleft + 5, top - (linesize * 17), "Customer: " + customername)
    # Invoice items
    pagenum = 1;
    for each in finaldict:
        pageitemdict = finaldict[each]
        p.setFont(CONST_fontbold, 10)
        if (pagenum == 1 and invoiceitem.count() <= 25 ):
            headery = top - (linesize * 27) + 3
            headerboxy = top - (linesize * 27)
            boxy = 180
            boxheight = 350
            y = top - (linesize * 29) + 5
        elif (pagenum == 1 and invoiceitem.count() > 38 ):
            headery = top - (linesize * 29) + 3
            headerboxy = top - (linesize * 29)
            boxy = 50
            boxheight = 555
            y = top - (linesize * 31) + 5
        elif (pagenum  == len(finaldict) ):
            headery = top - (linesize * 7 ) + 3
            headerboxy = top - (linesize * 7)
            boxy = 180
            boxheight = top - (linesize * 28)
            y = top - (linesize * 9) + 5
        else:
            headery = top - (linesize * 7 ) + 3
            headerboxy = top - (linesize * 7)
            boxy = 50
            boxheight = top - (linesize * 12)
            y = top - (linesize * 9) + 5
        # Invoice item title
        p.setStrokeColorRGB(0.75, 0.75, 0.75 )
        p.setFillColorRGB(0.75, 0.75, 0.75 )
        p.rect(marginleft,headerboxy, 550, 27, stroke=True, fill=True)  
        p.setFillColorRGB(0, 0, 0 )   
        p.drawString(480, headery + 13, 'Quantity' );
        p.drawString(30, headery, 'SKU code                       Description                                                                                            Ordered          Delivered')
        p.setFont(CONST_font, 10)
        p.rect(marginleft,boxy, 115, boxheight, stroke=True, fill=False) # SKU code
        p.rect(140,boxy, 295, boxheight, stroke=True, fill=False) # Description
        p.rect(435,boxy, 70, boxheight, stroke=True, fill=False) # Quantity
        p.rect(505,boxy, 70, boxheight, stroke=True, fill=False) #Total RM
        count = 0;
        itemcount = 0;
        topy = y;
        for item in pageitemdict:
            y = topy - (count * 12) 
            if 'sku' in item:
                p.drawString(30, y, item['sku'])
                p.drawString(145, y, item['description'])
                # qty string
                qty = len(item['items']);
                p.drawCentredString(470, y, str(qty))
                p.drawCentredString(540, y, str(qty))
                count += 1;
                # item details
            for trackcode in item['items']:
                itemcount += 1;
                
                dy = topy - (count * 12)
                p.drawString(155, dy, 'S/No: ' + trackcode )
                count += 1
        totalitem = 'No. of items (%d)' % itemcount
        totalitemwidth = p.stringWidth(totalitem, CONST_font, 10)
        p.drawString(500-totalitemwidth, boxy-10, totalitem)
        if (pagenum  != len(finaldict) ):
            pagenumstr =str(pagenum)+ '/' + str(len(finaldict))
            p.drawString(560, 10, pagenumstr)
            p.showPage()
            pagenum += 1
    
    
    # Bottom titles and details
    p.setFont(CONST_fontbold, 10)
    p.setFillColorRGB(0, 0, 0 )
    
    # page number
    pagenumstr = str(pagenum)+ '/' + str(len(finaldict))
    p.drawString(560, 10, pagenumstr)
    # bottom boxes
    p.setFillColorRGB(0.75, 0.75, 0.75 )
    p.rect(marginleft,50, 550, 60, stroke=True, fill=False) #Invoice details
    p.rect(marginleft,110, 250, 15, stroke=True, fill=True) #Invoice no
    # Instruction title
    p.setFillColorRGB(0, 0, 0 )
    p.drawString(marginleft+5, 140, "Received by")
    p.drawString(400, 140, "Received on")
    p.line(marginleft+70, 140, marginleft+370, 140)
    p.line(470, 140, 470+100, 140)
    
    
    p.drawString(marginleft+5, 115, 'Instructions:')
    p.setFont(CONST_fontbold, 7)
    p.drawString(marginleft+85, 135, "Name")
    p.drawString(marginleft+300, 135, "Signature")
    p.drawString(475, 135, "Date")
    p.showPage()

    pdf = p.getpdfdata()
    buffer.close()
    return pdf

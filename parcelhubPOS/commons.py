from .models import User, Branch, UserBranchAccess
from django.http.response import HttpResponse
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib.auth import login
CONST_branchid = 'branchid'
CONST_username = 'Username'
CONST_invoice = '1Invoice'
CONST_masterdata = '3Master Data'
CONST_custacc = '2Customer Account'
CONST_report = '4Report'
CONST_system = '5System'

def userselection(request):
    sessiondict = []
    if 'loggedusers' in request.session:
        sessiondict = request.session['loggedusers']
    try:
        selectedbranch = request.session[CONST_branchid]
    except:
        selectedbranch = ''
    if request.method == "POST":
        selecteduser = request.POST.get('userselection') 
        if selecteduser:
            loguser = User.objects.get(id=selecteduser)
            if loguser is not None:
                login(request, loguser)
                request.session['userid'] = loguser.id 
                name = "%s %s"%(loguser.last_name, loguser.first_name )
                request.session[CONST_username] = name
                request.session['loggedusers'] = sessiondict
                
        selectedbranch = request.POST.get('branchselection') 
    request.session[CONST_branchid] = selectedbranch
    allloggedusers = User.objects.filter(id__in=request.session['loggedusers'])
    return allloggedusers

def branchselection(request):
    loguser = User.objects.get(id=request.session.get('userid'))
    allbranchaccess = UserBranchAccess.objects.filter(user=loguser)
    selectedbranch = request.session.get(CONST_branchid)
    if not selectedbranch :
        branchaccess = allbranchaccess.first()
        if branchaccess:
            branchid = branchaccess.branch.id 
            request.session[CONST_branchid] = branchid 
    if request.method == "POST":
        selectedbranch = request.POST.get('branchselection') 
        if selectedbranch:
            request.session[CONST_branchid] = selectedbranch
    
    
    return allbranchaccess
    

def navbar(request):
    loguser = User.objects.get(id=request.session.get('userid'))
    branchid = request.session.get(CONST_branchid)
    sel_branch = Branch.objects.filter(id=branchid)
    branchaccess = UserBranchAccess.objects.filter(user=loguser, branch=sel_branch).first()
    menudict = {}
    if branchaccess or loguser.is_superuser:
        if loguser.is_superuser or branchaccess.transaction_auth != 'n/a' :
            menudict[CONST_invoice] =[('Invoice list','/parcelhubPOS/invoice'),
                                      ('New invoice','/parcelhubPOS/invoice/editinvoice/?invoiceid=')]
        menudict[CONST_masterdata] = []
        if loguser.is_superuser or branchaccess.masterdata_auth != 'n/a':
            menudict[CONST_masterdata].append(('Vendor','/parcelhubPOS/vendor'))
            menudict[CONST_masterdata].append(('Tax','/parcelhubPOS/tax') )
            menudict[CONST_masterdata].append(('Zone domestic','/parcelhubPOS/zonedomestic') )
            menudict[CONST_masterdata].append(('Zone international','/parcelhubPOS/zoneinternational') )
            menudict[CONST_masterdata].append(('SKU','/parcelhubPOS/sku'))
            menudict[CONST_system] =[('Synchronize data','/parcelhubPOS/masterdata')]
        if loguser.is_superuser or branchaccess.skupricing_auth != 'n/a':
            menudict[CONST_masterdata].append(('SKU pricing','/parcelhubPOS/skubranch'))                            
        if loguser.is_superuser or branchaccess.branch_auth != 'n/a':
            menudict[CONST_masterdata].append(('Branch','/parcelhubPOS/branch'))
        if loguser.is_superuser or branchaccess.user_auth != 'n/a':
            menudict[CONST_masterdata].append(('User','/parcelhubPOS/user'))
        
        if len(menudict[CONST_masterdata]) == 0:
            menudict.pop(CONST_masterdata)
        
        if loguser.is_superuser or branchaccess.custacc_auth != 'n/a':
            menudict[CONST_custacc] =[('Customer account','/parcelhubPOS/customer'),
                                      ('Statement of account','/parcelhubPOS/statementofaccount'),
                                      ('Payment','/parcelhubPOS/payment/?custid=""')]
        #if loguser.is_superuser or branchaccess.report_auth != 'n/a':
        #    menudict[CONST_report] =[('Customer report','/parcelhubPOS/custreport'),
        #                        ('Vendor report','/parcelhubPOS/vendorreport'),
        #                        ('Account report','/parcelhubPOS/accreport')]
    return menudict
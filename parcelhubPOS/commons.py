from .models import User, Branch, UserBranchAccess, Terminal
from django.http.response import HttpResponse
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib.auth import login
CONST_branchid = 'branchid'
CONST_terminalid = 'terminalid'
CONST_username = 'Username'
CONST_invoice = '1Invoice'
CONST_custacc = '2Customer Account'
CONST_payment = '3Payment'
CONST_soa = '4Statement Of Account'
CONST_masterdata = '5Information'
CONST_reporting = '6Report'
CONST_system = '7System'
def userselection(request):
    sessiondict = []
    if 'loggedusers' in request.session:
        sessiondict = request.session['loggedusers']

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
                request.session['issuperuser'] = loguser.is_superuser
    allloggedusers = User.objects.filter(id__in=request.session['loggedusers'])
    return allloggedusers

def branchselection(request):
    loguser = User.objects.get(id=request.session.get('userid'))
    if loguser.is_superuser:
        branches = Branch.objects.all()
    else:
        allbranchaccess = UserBranchAccess.objects.filter(user=loguser)
        branchidlist = allbranchaccess.values_list('branch_id', flat=True)
        branches = Branch.objects.filter(id__in=branchidlist)
    selectedbranch = request.session.get(CONST_branchid)
    if not selectedbranch:
        branchaccess = branches.first()
        if branchaccess:
            branchid = branchaccess.id 
            request.session[CONST_branchid] = branchid 
    if request.method == "POST" and 'branchselection' in request.POST:
        selectedbranch = request.POST.get('branchselection') 
        if selectedbranch:
            request.session[CONST_branchid] = selectedbranch
    return branches
    
def terminalselection(request):
    selectedbranch = request.session.get(CONST_branchid)
    selectedterminal = request.session.get(CONST_terminalid)
    if selectedbranch == '-1':
        terminals = None
        request.session[CONST_terminalid] = '-1'
    else:
        branch = Branch.objects.get(id=selectedbranch)
        terminals = Terminal.objects.filter(branch=branch)
        if not selectedterminal:
            terminal = terminals.first()
            if terminal:
                terminalid = terminal.id 
                request.session[CONST_terminalid] = terminalid 
            else:
                request.session[CONST_terminalid] = '-1'
        else:
            terminal = Terminal.objects.filter(branch=branch,id=selectedterminal)
            if terminal:
                pass
            else:
                if terminal:
                    terminalid = terminal.id 
                    request.session[CONST_terminalid] = terminalid 
                else:
                    request.session[CONST_terminalid] = '-1'
        if request.method == "POST" and 'terminalselection' in request.POST:
            selectedterminal = request.POST.get('terminalselection') 
            if selectedterminal:
                request.session[CONST_terminalid] = selectedterminal
        
    return terminals

def navbar(request):
    loguser = User.objects.get(id=request.session.get('userid'))
    branchid = request.session.get(CONST_branchid)
    terminalid = request.session.get(CONST_terminalid)
    sel_branch = Branch.objects.filter(id=branchid)
    branchaccess = UserBranchAccess.objects.filter(user=loguser, branch=sel_branch).first()
    menudict = {}
    if loguser.is_superuser or branchaccess:
        #Everyone access feature
        if branchid == '-1' or terminalid == '-1':
            menudict[CONST_invoice] =[('New invoice (F9)',''),('Invoice list','/parcelhubPOS/invoice')]
        else:
            menudict[CONST_invoice] =[('New invoice (F9)','/parcelhubPOS/invoice/editinvoice/?invoiceid='),('Invoice list','/parcelhubPOS/invoice')]
        menudict[CONST_custacc] =[]
        if terminalid and terminalid != '-1' :
            menudict[CONST_payment] =[('Payment overview','/parcelhubPOS/payment/?custid=""'),
                                        ('Payment receive','/parcelhubPOS/makepayment'),
                                          ]   
        else:
            menudict[CONST_payment] =[('Payment overview','/parcelhubPOS/payment/?custid=""'),
                                      ('Payment receive',''),
                                          ]   
        menudict[CONST_soa] =[
                                  ('New statement of account','/parcelhubPOS/statementofaccount_new'),
                                      ]   
        menudict[CONST_reporting] =[('Cash up report','/parcelhubPOS/cashupreport'),
                                      ]     
        menudict[CONST_masterdata] = []
        #Super admin and branch admin only feature
        if loguser.is_superuser:
            menudict[CONST_masterdata].append(('Vendor','/parcelhubPOS/vendor'))
            menudict[CONST_masterdata].append(('Tax','/parcelhubPOS/tax') )
            menudict[CONST_masterdata].append(('Zone domestic','/parcelhubPOS/zonedomestic') )
            menudict[CONST_masterdata].append(('Zone international','/parcelhubPOS/zoneinternational') )
            menudict[CONST_masterdata].append(('SKU','/parcelhubPOS/sku'))
            menudict[CONST_masterdata].append(('SKU pricing','/parcelhubPOS/skubranch'))
            menudict[CONST_masterdata].append(('User','/parcelhubPOS/user'))
        elif branchaccess.access_level == 'Branch admin':
            menudict[CONST_masterdata].append(('Vendor','/parcelhubPOS/vendor'))
            menudict[CONST_masterdata].append(('Tax','/parcelhubPOS/tax') )
            menudict[CONST_masterdata].append(('Zone domestic','/parcelhubPOS/zonedomestic') )
            menudict[CONST_masterdata].append(('Zone international','/parcelhubPOS/zoneinternational') )
            menudict[CONST_masterdata].append(('SKU','/parcelhubPOS/sku'))
            menudict[CONST_masterdata].append(('SKU pricing','/parcelhubPOS/skubranch'))
            menudict[CONST_masterdata].append(('User',''))
        else:
            menudict[CONST_masterdata].append(('Vendor',''))
            menudict[CONST_masterdata].append(('Tax','') )
            menudict[CONST_masterdata].append(('Zone domestic','') )
            menudict[CONST_masterdata].append(('Zone international','') )
            menudict[CONST_masterdata].append(('SKU',''))
            menudict[CONST_masterdata].append(('SKU pricing',''))
            menudict[CONST_masterdata].append(('User',''))
            
        #Super admin only feature
        if loguser.is_superuser:
            menudict[CONST_masterdata].append(('Branch','/parcelhubPOS/branch'))
            menudict[CONST_system] =[('Global parameters','/parcelhubPOS/globalparameter')]
        else:
            menudict[CONST_masterdata].append(('Branch',''))
            menudict[CONST_system] =[('Global parameters','')]
        if len(menudict[CONST_masterdata]) == 0:
            menudict.pop(CONST_masterdata)
        
    return menudict
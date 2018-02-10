from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth import authenticate
from .models import *
from .forms import GlobalParameterForm

from .tables import *
from .skus import *
from .commons import *
from .users import *
from .branchs import *
from .vendors import *
from .tax import *
from .zones import *
from .skubranch import *
from .customers import *
from .invoices import *
from .payments import *
from .statementofaccounts import *
from .reporting import *
# Constants
CONST_branchid = 'branchid'
CONST_username = 'Username'
CONST_loginhtml = 'login.html'

# Create your views here.
# login POST request
def loginuser(request):
    if request.method != "POST":
        return render(request, CONST_loginhtml)
    if CONST_username in request.POST:
        Submitted_User = request.POST[CONST_username] 
        Submitted_Pas = request.POST['Password']          
        sessiondict = []
        
        if 'loggedusers' in request.session:
            sessiondict = request.session['loggedusers']
        loguser = authenticate(username=Submitted_User, password=Submitted_Pas)
        
        if loguser is not None:
            branchaccess = UserBranchAccess.objects.filter(user=loguser)
            if branchaccess.count() == 0:
                return render(request, CONST_loginhtml, {'branchaccess_error': '1'})
            login(request, loguser)
            request.session['userid'] = loguser.id 
            name = "%s %s"%(loguser.last_name, loguser.first_name )
            request.session[CONST_username] = name
            request.session['issuperuser'] = loguser.is_superuser
            sessiondict.append(loguser.id)
            request.session['loggedusers'] = sessiondict
            
            if loguser.is_superuser:
                return dashboard(request)
            else:
                return HttpResponseRedirect("/parcelhubPOS/invoice/editinvoice/?")  
        else:
            return render(request, CONST_loginhtml, {'match_error': '1'})
        return render(request, CONST_loginhtml, {'match_error': '1'})


# admin login method
@login_required
def dashboard(request):
    loggedusers = userselection(request)
    loguser = User.objects.get(id=request.session.get('userid'))
    branchaccess = UserBranchAccess.objects.filter(user=loguser).first()
    if request.method == "POST" and 'branchselection' in request.POST:
        branchlist = branchselection(request)
        menubar = navbar(request)
        
        context = {
                    'nav_bar' : sorted(menubar.items()),
                    'branchselection': branchlist,
                    'loggedusers' : loggedusers,
                    'branchselectionaction': '/parcelhubPOS/dashboard/',
                    'issuperuser': loguser.is_superuser
                    }
        return render(request, 'dashboard.html', context)#HttpResponseRedirect('/parcelhubPOS/invoice/')#
    elif branchaccess or loguser.is_superuser:
        try:
            branchid = branchaccess.branch.id 
            user = branchaccess.user
            request.session[CONST_branchid] = branchid 
        except:
            pass
        menubar = navbar(request)
        branchlist = branchselection(request)
        context = {
                    'nav_bar' : sorted(menubar.items()),
                    'branchselection': branchlist,
                    'loggedusers' : loggedusers,
                    'branchselectionaction': '/parcelhubPOS/dashboard/',
                    'issuperuser': loguser.is_superuser
                    }
        return render(request, 'dashboard.html', context)#HttpResponseRedirect('/parcelhubPOS/invoice/')#
    else:
        return HttpResponse("No branch access configured for user")
    
@login_required
def globalparameter(request):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    
    title = "Update global parameter"
    loguser = User.objects.get(id=request.session.get('userid'))
    gpqueryset = GlobalParameter.objects.filter().first()
    
    if request.method == "POST":
        formset = GlobalParameterForm(request.POST, request.FILES,
                             instance=gpqueryset)
        if formset.is_valid():
            msg = 'Global parameter have been updated successfully.'
            formset.save()
            return HttpResponseRedirect("/parcelhubPOS/globalparameter/?msg=%s" % msg)
    else:
        formset = GlobalParameterForm(instance=gpqueryset)
    
    context = {
                'formset': formset,
                'headerselectiondisabled' : True,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'issuperuser' : loguser.is_superuser,
                'title' : title,
                'header' : title,
                'statusmsg' : request.GET.get('msg'),
                }
    return render(request, 'globalparameter.html', context)



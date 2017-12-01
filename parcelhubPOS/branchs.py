from django_tables2 import RequestConfig
from django.shortcuts import render
from django.forms import modelformset_factory
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .tables import BranchTable
from .commons import *
from .models import Branch, UserBranchAccess
from django.db.models import Q
from django.http import HttpResponseRedirect
CONST_branchid = 'branchid'
#method to retrieve branch list
@login_required
def branchlist(request):
    loggedusers = userselection(request)
    branchselectlist = branchselection(request)
    menubar = navbar(request)
    branch_list = Branch.objects.all()
    
    final_branch_table = BranchTable(branch_list)
    RequestConfig(request, paginate={'per_page': 25}).configure(final_branch_table)
    context = {
                'branch': final_branch_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'title': 'Branch'
                }
    return render(request, 'branch.html', context)

@login_required
def editbranch(request, ebranchid):
    loggedusers = userselection(request)
    menubar = navbar(request)
    branchselectlist = branchselection(request)
    ebranchid = request.GET.get('ebranchid')
    title = "New branch"
    if ebranchid:
        title = 'Edit branch'
    branchqueryset = Branch.objects.filter(id=ebranchid)
    
    branchFormSet = modelformset_factory(Branch, fields=('name', 
                                                        'owner', 
                                                        'contact', 
                                                        'email', 
                                                        'address',
                                                        'registrationno',
                                                        'gstno',
                                                        'payment_bank',
                                                        'payment_acc',
                                                        'fax',
                                                        'tollfree',
                                                        'website'), max_num=1)
    if request.method == "POST":
        formset = branchFormSet(request.POST, request.FILES,
                             queryset=branchqueryset)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect("/parcelhubPOS/branch")
    else:
        formset = branchFormSet(queryset=branchqueryset)
    context = {
                'formset': formset,
                'headerselectiondisabled' : True,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchselectlist,
                'loggedusers' : loggedusers,
                'title': title
                }
    return render(request, 'editbranch.html', context)

@login_required
def deletebranch(request, dbranchid ):
    dbranchid = request.GET.get('dbranchid')
    branch = Branch.objects.filter(id = dbranchid )
    currentbranchid = request.session.get(CONST_branchid)
    
    if branch:
        branch.delete()
    if currentbranchid == dbranchid:
        nextselectedbranch = UserBranchAccess.objects.filter(user__id=request.session.get('userid')).first()
        request.session[CONST_branchid] = nextselectedbranch.branch.id
    return branchlist(request)
from django.shortcuts import render
from django_tables2 import RequestConfig
from django.forms import modelformset_factory
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .tables import UserTable, UserBranchAccessTable
from .commons import *
from django.contrib.auth.models import User
from .forms import UserCreateForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserBranchAccess, User, Branch
from django.http import HttpResponse, HttpResponseRedirect
CONST_branchid = 'branchid'
CONST_username = 'Username'

@login_required
def userlist(request):
    loggedusers = userselection(request)
    branchlist = branchselection(request)
    menubar = navbar(request)
    user_list = User.objects.all()
    formdata = {'firstname':'',
                'lastname':'',
                'username':'',
                'email':''}
    if request.method == "GET":
        submitted_firstname = request.GET.get('firstname') 
        if submitted_firstname:
            formdata['firstname'] = submitted_firstname;
            user_list =  user_list.filter(first_name__icontains=submitted_firstname)
        submitted_lastname = request.GET.get('lastname') 
        if submitted_lastname:
            formdata['lastname'] = submitted_lastname;
            user_list =  user_list.filter(last_name__icontains=submitted_lastname)
        submitted_username = request.GET.get('username') 
        if submitted_username:
            formdata['username'] = submitted_username;
            user_list =  user_list.filter(username__icontains=submitted_username)
        submitted_email = request.GET.get('email')
        if submitted_email:
            formdata['email'] = submitted_email;
            user_list =  user_list.filter(email__icontains=submitted_email)
            
    final_user_table = UserTable(user_list)
    RequestConfig(request, paginate={'per_page': 25}).configure(final_user_table)
    context = {
                'userlist': final_user_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchlist,
                'loggedusers' : loggedusers,
                'formdata' :formdata,
                'title': "User"
                }
    return render(request, 'user.html', context)

@login_required
def edituser(request, user_id):
    loggedusers = userselection(request)
    branchlist = branchselection(request)
    menubar = navbar(request)
    user_id = request.GET.get('user_id')
    title = "Edit user"
    # Show user info
    userqueryset = User.objects.filter(id=user_id)
    UserFormSet = modelformset_factory(User, fields=('username', 'first_name', 'last_name', 'email'), max_num=1,
                                       exclude= ('id',))
    isedit = False;
    if user_id:
        isedit = True;
        
    if request.method == "POST":
        formset = UserFormSet(request.POST, request.FILES,
                             queryset=userqueryset)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect("/parcelhubPOS/user")
    else:
        formset = UserFormSet(queryset=userqueryset)
    context = {
                'formset': formset,
                'headerselectiondisabled' : True,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchlist,
                'loggedusers' : loggedusers,
                'user_id': user_id,
                'title' : title
                }
    return render(request, 'edituser.html', context)

@login_required
def change_password(request, user_id):
    loggedusers = userselection(request)
    branchlist = branchselection(request)
    menubar = navbar(request)
    user_id = request.GET.get('user_id')
    userqueryset = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = PasswordChangeForm(userqueryset, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return userlist(request)
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    context = {
                'formset': form,
                'headerselectiondisabled' : True,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchlist,
                'loggedusers' : loggedusers,
                'title': "Change password"
                }
    return render(request, 'change_password.html', context)

@login_required
def adduser(request):
    loggedusers = userselection(request)
    branchlist = branchselection(request)
    menubar = navbar(request)
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'New user successfully created!')
            return HttpResponseRedirect("/parcelhubPOS/user")
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserCreateForm()
    context = {
                'formset': form,
                'headerselectiondisabled' : True,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchlist,
                'loggedusers' : loggedusers,
                'title': "New user"
                }
    return render(request, 'adduser.html', context)

@login_required
def deleteuser(request, duser_id ):
    duser_id = request.GET.get('duser_id')
    user = User.objects.filter(id = duser_id )
    if user:
        user.delete()
    return userlist(request)

@login_required
def userbranchaccess( request, user_id):
    loggedusers = userselection(request)
    branchlist = branchselection(request)
    menubar = navbar(request)
    user_id = request.GET.get('user_id')
    #return HttpResponse(user_id)
    branchid = request.session.get(CONST_branchid)
    selected_user = User.objects.get(id=user_id)
    branchaccesslevel = UserBranchAccess.objects.filter(user__id = user_id)
    final_branchaccesslevel_table = UserBranchAccessTable(branchaccesslevel)
    
    RequestConfig(request, paginate={'per_page': 25}).configure(final_branchaccesslevel_table)
    context = {
                'userbranchaccess': final_branchaccesslevel_table,
                'user': selected_user,
                CONST_branchid : branchid,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchlist,
                'loggedusers' : loggedusers,
                'title': "User branch access"
                }
    return render(request, 'userbranchaccess.html', context)

@login_required
def edituserbranchaccess(request, userbranch_id):
    #header info
    loggedusers = userselection(request)
    branchlist = branchselection(request)
    menubar = navbar(request)
    # page info
    userbranchanduser_id = request.GET.get('userbranch_id')
    title = "New user access"
    
    userbranchanduserlist = userbranchanduser_id.split('_')
    userbranch_id = userbranchanduserlist[0]
    user_id = userbranchanduserlist[1]
    if userbranch_id.strip() != '0':
        title = "Edit user access"
    # redirect page info
    nextpage = request.POST.get('next', '/')
    try:
        userbainstance =  UserBranchAccess.objects.get(id=userbranch_id)
    except: 
        userbainstance = None
    userselected = User.objects.get(id=user_id)
    loguser = User.objects.get(id=request.session['userid'])
    branchsel_list = Branch.objects.all();
    selectionoption = ["n/a", "view", "edit"]
    if not loguser.is_superuser:
        branchaccesslist = branchlist.values_list('branch__id', flat=True)
        branchsel_list = Branch.objects.filter(id__in=branchaccesslist)
    # processing post
    if request.method == "POST":
        submitted_branchid = request.POST['branchselected'] 
        submitted_masterdata = request.POST['masterdata_auth']
        submitted_branch = request.POST['branch_auth']
        submitted_user = request.POST['user_auth']
        submitted_skupricing = request.POST['skupricing_auth']
        submitted_transaction = request.POST['transaction_auth']
        submitted_custacc = request.POST['custacc_auth']
        submitted_report = request.POST['report_auth']
        
        submitted_branchid = int('0' + submitted_branchid )
        if userbainstance:
            userbainstance.branch_id = submitted_branchid
            userbainstance.masterdata_auth = submitted_masterdata
            userbainstance.branch_auth = submitted_branch
            userbainstance.user_auth = submitted_user
            userbainstance.skupricing_auth = submitted_skupricing
            userbainstance.transaction_auth = submitted_transaction
            userbainstance.custacc_auth = submitted_custacc
            userbainstance.report_auth = submitted_report
            userbainstance.save()
        else:
            userbainstance = UserBranchAccess( user = userselected,
                                               branch_id = submitted_branchid,
                                               masterdata_auth = submitted_masterdata,
                                               branch_auth = submitted_branch,
                                               user_auth = submitted_user,
                                               skupricing_auth = submitted_skupricing,
                                               transaction_auth = submitted_transaction,
                                               custacc_auth = submitted_custacc,
                                               report_auth = submitted_report )
        
            userbainstance.save()
        return HttpResponseRedirect(nextpage)        

    next = '/parcelhubPOS/user/userbranchaccess?user_id='+ user_id
    context = {
                'nav_bar' : sorted(menubar.items()),
                'headerselectiondisabled' : True,
                'branchselection': branchlist,
                'loggedusers' : loggedusers,
                'next' : next,
                'userid' : user_id,
                'user' : userselected,
                'currentuserba' : userbainstance,
                'branchsel_list' : branchsel_list,
                'selectionoption' : selectionoption,
                'title': title
                }
    return render(request, 'edituserbranchaccess.html', context)

@login_required
def deleteuserbranchaccess(request, duserbranch_id ):
    duserbranch_id = request.GET.get('duserbranch_id')
    nextpage = request.POST.get('next', '/')
    ubalist = duserbranch_id.split('_')
    userbranch_id = ubalist[0]
    user_id = ubalist[1]
    uba = UserBranchAccess.objects.filter(id = userbranch_id )
    if uba:
        uba.delete()
    nextpage = "/parcelhubPOS/user/userbranchaccess?user_id="+ user_id
    return HttpResponseRedirect(nextpage)
from django.shortcuts import render
from django_tables2 import RequestConfig
from django.forms import modelformset_factory
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .tables import UserTable, UserBranchAccessTable, UserTable2
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
    branchid = request.session.get(CONST_branchid)
    if branchid == '-1':
        isedit = True
    else:
        branchaccess = UserBranchAccess.objects.get(user__id=request.session.get('userid'), branch__id = request.session.get(CONST_branchid))
        isedit = branchaccess.access_level != 'Cashier'
    currentuser = User.objects.get(id=request.session['userid'])
    if currentuser.is_superuser:
        user_list = User.objects.all();
    else:
        user_list = User.objects.filter(is_superuser = False)
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
            
    
    if branchid == "-1":
        final_user_table = UserTable2(user_list)
    else:
        final_user_table = UserTable(user_list)
    RequestConfig(request, paginate={'per_page': 25}).configure(final_user_table)
    issearchempty = True
    searchmsg = 'There no user matching the search criteria...'
    try:
        if user_list or (not submitted_firstname and not submitted_lastname and not submitted_username and not submitted_email ):
            issearchempty = False
    except:
        issearchempty = False
    context = {
                'userlist': final_user_table,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchlist,
                'loggedusers' : loggedusers,
                'formdata' :formdata,
                'title': "User",
                'isedit' : isedit,
                'issuperuser' : currentuser.is_superuser,
                'isall': branchid != '-1',
                'statusmsg' : request.GET.get('msg'),
                'header': "User",
                'issearchempty': issearchempty,
                'searchmsg': searchmsg
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
            name = request.POST['form-0-username'] 
            msg = 'User "%s" have been updated successfully.' % name
            formset.save()
            return HttpResponseRedirect("/parcelhubPOS/user/?msg=%s" % msg)
    else:
        formset = UserFormSet(queryset=userqueryset)
    context = {
                'formset': formset,
                'headerselectiondisabled' : True,
                'nav_bar' : sorted(menubar.items()),
                'branchselection': branchlist,
                'loggedusers' : loggedusers,
                'user_id': user_id,
                'title' : title,
                'header': title
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
            name = request.POST['username'] 
            msg = 'User "%s" have been created successfully.' % name
            return HttpResponseRedirect("/parcelhubPOS/user/?msg=%s" % msg)
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
                'title': "New user",
                'header': "New user"
                }
    return render(request, 'adduser.html', context)

@login_required
def deleteuser(request, duser_id ):
    duser_id = request.GET.get('duser_id')
    user = User.objects.filter(id = duser_id )
    msg = 'User "%s" have been deleted successfully.' % ( user.first().first_name + ' ' + user.first().last_name )
    if user:
        user.delete()
    return HttpResponseRedirect("/parcelhubPOS/user/?msg=%s" % msg)

@login_required
def userbranchaccess( request, user_id):
    loggedusers = userselection(request)
    branchlist = branchselection(request)
    menubar = navbar(request)
    user_id = request.GET.get('user_id')
    loguser = User.objects.get(id=request.session.get('userid'))
    #return HttpResponse(user_id)
    branchid = request.session.get(CONST_branchid)
    selected_user = User.objects.get(id=user_id)
    if branchid == '-1':
        isedit = True
    else:
        branchaccess = UserBranchAccess.objects.get(user__id=request.session.get('userid'), branch__id = request.session.get(CONST_branchid))
        isedit = branchaccess.access_level != 'Cashier'
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
                'title': "User branch access",
                'isedit' : isedit,
                'issuperuser' : loguser.is_superuser,
                'isall': branchid != '-1',
                'statusmsg' : request.GET.get('msg'),
                'header': "User access"
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
    selectionoption = ["Cashier", "Branch admin"]
    
    if not loguser.is_superuser:
        branchaccesslist = branchlist.values_list('branch__id', flat=True)
        branchsel_list = Branch.objects.filter(id__in=branchaccesslist)
    # processing post
    if request.method == "POST":
        submitted_branchid = request.POST['branchselected'] 
        submitted_access_level = request.POST['access_level']
        
        submitted_branchid = int('0' + submitted_branchid )
        if userbainstance:
            userbainstance.branch_id = submitted_branchid
            userbainstance.access_level = submitted_access_level
            userbainstance.save()
        else:
            userbainstance = UserBranchAccess( user = userselected,
                                               branch_id = submitted_branchid,
                                               access_level = submitted_access_level )
        
            userbainstance.save()
        branch = Branch.objects.get(id= submitted_branchid)
        if title == 'New user access':
            msg = 'User branch access for user "%s" and branch "%s" have been created successfully.' %(userselected.username, branch.name )
        else:
            msg = 'User branch access for user "%s" and branch "%s" have been updated successfully.' %(userselected.username, branch.name )
        nextpage = nextpage + '&msg=' + msg
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
                'title': title,
                'statusmsg' : request.GET.get('msg'),
                'header': title
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
    msg = 'User branch access for user "%s" and branch "%s" have been deleted successfully.' %(uba.first().user.username, uba.first().branch.name )
    if uba:
        uba.delete()
    nextpage = "/parcelhubPOS/user/userbranchaccess?user_id="+ user_id + '&msg=' + msg
    return HttpResponseRedirect(nextpage)
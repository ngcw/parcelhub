from django.shortcuts import render
from .models import *
# Create your views here.

# login POST request
def loginuser(request):
    if request.method != "POST":
        return render(request, CONST_loginhtml)
    if CONST_username in request.POST:
        Submitted_User = request.POST[CONST_username] 
        Submitted_Pas = request.POST['Password']      
        loguser = authenticate(username=Submitted_User, password=Submitted_Pas)
        if loguser is not None:
            login(request, loguser)
            request.session['userid'] = loguser.id 
            name = "%s %s"%(loguser.last_name, loguser.first_name )
            request.session[CONST_username] = name
            return dashboard(request)
        return render(request, CONST_loginhtml, {'match_error': '1'})
    

# admin login method
#@login_required
def dashboard(request):
    loguser = User.objects.get(id=request.session.get('userid'))

    context = {
                'nav_bar' : sorted(menubar.items()),
                'branchselectionaction': '/parcelhubPOS/dashboard/'
                }
    return render(request, 'dashboard.html', context)
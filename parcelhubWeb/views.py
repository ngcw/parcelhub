from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth import authenticate
from .models import *
# Create your views here.

CONST_username = 'Username'
CONST_homehtml = 'home.html'

# login POST request
def loginuser(request):
    if request.method != "POST":
        return render(request, CONST_homehtml)
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
        return render(request, CONST_homehtml, {'match_error': '1'})
    

# admin login method
#@login_required
def dashboard(request):
    loguser = User.objects.get(id=request.session.get('userid'))

    context = {
                }
    return render(request, 'dashboard.html', context)
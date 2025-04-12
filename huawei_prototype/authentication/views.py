from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from dashboard.models import *
# Create your views here.

# login view
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            # Return an 'invalid login' error message.
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

# logout view
@login_required
def custom_logout_view(request):
    logout(request)
    return redirect('login')



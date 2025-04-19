from django.shortcuts import render
from .models import *
# Create your views here.

def dashboard(request):
    return render(request, 'dashboard/dashboard.html')
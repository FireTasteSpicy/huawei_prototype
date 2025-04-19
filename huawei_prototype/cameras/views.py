from django.shortcuts import render
from dashboard.models import *
# Create your views here.

def cameras(request):
    return render(request, 'cameras/cameras.html')  # placeholder
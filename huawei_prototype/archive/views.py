from django.shortcuts import render
from dashboard.models import *
# Create your views here.

def archive(request):
    return render(request, 'archive/archive.html') # placeholder
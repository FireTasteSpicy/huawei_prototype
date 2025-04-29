from django.shortcuts import render
from dashboard.models import *
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def archive(request):
    return render(request, 'archive/archive.html') # placeholder
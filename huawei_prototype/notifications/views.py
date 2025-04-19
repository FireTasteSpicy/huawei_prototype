from django.shortcuts import render
from dashboard.models import *
# Create your views here.

def notifications(request):
    return render(request, 'notifications/notifications.html')  # placeholder
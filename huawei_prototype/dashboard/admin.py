from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Camera)
admin.site.register(Incident)
admin.site.register(ResponseTime)
admin.site.register(Weather)
admin.site.register(KPISnapshot)
admin.site.register(Notification)
admin.site.register(AccidentProbabilityScore)

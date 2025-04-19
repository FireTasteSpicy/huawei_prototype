from django.urls import path
from . import views

urlpatterns = [
    path('', views.archive, name='archive'),  # placeholder
]
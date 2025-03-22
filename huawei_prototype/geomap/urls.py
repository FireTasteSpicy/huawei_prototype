from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('realtime/', views.realtime_incident_map, name='realtime_map'),
    path('heatmap/', views.prediction_heatmap, name='prediction_heatmap'),
]
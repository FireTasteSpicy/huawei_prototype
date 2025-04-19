from django.urls import path
from . import views

urlpatterns = [
    path("", views.map_home, name="geomap"),
    path("camera/", views.camera_map, name="camera_map"),
    path("incident/", views.incident_map, name="incident_map"),
    path("probability/", views.probability_map, name="probability_map"),
    path("weather/", views.weather_map, name="weather_map"),
]

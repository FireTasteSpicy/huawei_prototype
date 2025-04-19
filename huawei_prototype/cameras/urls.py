from django.urls import path
from . import views

urlpatterns = [
    path('', views.cameras, name='cameras'),
    path('view/<int:camera_id>/', views.camera_feed, name='camera_feed'),
]
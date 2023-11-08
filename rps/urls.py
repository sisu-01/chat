# chat/urls.py
from django.urls import path

from . import views

app_name = 'rps'

urlpatterns = [
    path('', views.index, name="index"),
    path('room_list/', views.room_list, name="room_list"),
    path('room_knock/', views.room_knock, name="room_knock"),
    path('room/', views.room, name="room"),
]

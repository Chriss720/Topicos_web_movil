from django.urls import path
from . import views

urlpatterns = [
    path("hola/", views.hola, name="hola"),
    path("estado/", views.estado, name="estado"),
    path("cotizar/", views.cotizar, name="cotizar"),
]

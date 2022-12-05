from django.urls import path
from . import views

urlpatterns = [
    #path("", views.index, name="index"),
    path("", views.get_response, name='get_response'),
    path("add", views.home, name="home"),
]
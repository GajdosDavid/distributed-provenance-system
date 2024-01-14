from django.urls import path

from . import views

urlpatterns = [
    path("graphs/", views.graphs, name="graphs"),
]
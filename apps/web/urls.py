from django.urls import path

from . import views
from .health import healthz


app_name = "web"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("healthz/", healthz, name="healthz"),
]


from django.urls import path

from . import views


app_name = "pilots"

urlpatterns = [
    path("intake/", views.intake, name="intake"),
]


from django.urls import path

from . import views


app_name = "onboarding"

urlpatterns = [
    path("", views.start, name="start"),
    path("chat/", views.go_chat, name="chat"),
]


from django.urls import path

from . import views


app_name = "chat"

urlpatterns = [
    path("", views.chat_home, name="home"),
    path("<uuid:chat_id>/", views.chat_detail, name="detail"),
    path("<uuid:chat_id>/send/", views.send_message, name="send_message"),
]


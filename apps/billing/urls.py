from django.urls import path

from . import views


app_name = "billing"

urlpatterns = [
    path("pay/", views.pay, name="pay"),
    path("checkout/", views.start_checkout, name="checkout"),
    path("success/", views.success, name="success"),
    path("cancel/", views.cancel, name="cancel"),
    path("webhook/", views.webhook, name="webhook"),
]


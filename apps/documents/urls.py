from django.urls import path

from . import views


app_name = "documents"

urlpatterns = [
    path("", views.documents_index, name="index"),
    path("<uuid:document_id>/", views.document_detail, name="detail"),
    path("<uuid:document_id>/download/", views.document_download, name="download"),
    path("<uuid:document_id>/delete/", views.document_delete, name="delete"),
]


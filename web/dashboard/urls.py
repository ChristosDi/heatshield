from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("requests/", views.request_dashboard, name="request_dashboard"),
    path("requests/<int:request_id>/", views.request_detail, name="request_detail"),
    path("requests/create/", views.request_create, name="request_create"),
    path(
        "requests/<int:request_id>/edit/",
        views.request_edit,
        name="request_edit",
    ),
    path(
        "requests/<int:request_id>/delete/",
        views.request_delete,
        name="request_delete",
    ),
]

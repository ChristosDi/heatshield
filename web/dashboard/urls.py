from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("requests/", views.request_dashboard, name="request_dashboard"),
    path("requests/create/", views.request_create, name="request_create"),
    path("requests/<str:reference>/", views.request_detail, name="request_detail"),
    path(
        "requests/<str:reference>/edit/",
        views.request_edit,
        name="request_edit",
    ),
    path(
        "requests/<str:reference>/delete/",
        views.request_delete,
        name="request_delete",
    ),
    path("cooling-centres/", views.cooling_centre_dashboard, name="cooling_centre_dashboard"),
    path("cooling-centres/create/", views.cooling_centre_create, name="cooling_centre_create"),
    path("cooling-centres/<int:centre_id>/", views.cooling_centre_details, name="cooling_centre_details"),
    path("cooling-centres/<int:centre_id>/edit", views.cooling_centre_edit, name="cooling_centre_edit"),
]

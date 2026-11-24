from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "requests/",
        views.request_dashboard,
        name="request_dashboard"
    ),
    path(
        "requests/<int:request_id>/",
        views.request_detail,
        name="request_detail"
    ),
]
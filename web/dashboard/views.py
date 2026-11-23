from django.shortcuts import render

from staff.roles import role_of


def home(request):
    """Placeholder home page. The dashboard pages are built on top of it."""
    return render(request, "dashboard/home.html", {"role": role_of(request.user)})
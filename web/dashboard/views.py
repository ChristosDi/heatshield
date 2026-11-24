import logging

from django.shortcuts import render

from staff.roles import role_of

from . import api_client

logger = logging.getLogger(__name__)


def home(request):
    """Home page: the signed-in staff member's role and the support request counts."""
    try:
        counts = api_client.request_counts()
    except api_client.ApiUnavailable:
        logger.warning("Dashboard counts unavailable", exc_info=True)
        counts = None
    return render(request, "dashboard/home.html", {"role": role_of(request.user), "counts": counts})
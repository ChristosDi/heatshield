import logging
from datetime import datetime

import requests
from django.shortcuts import render
from staff.roles import role_of

from . import api_client
from .api import get

logger = logging.getLogger(__name__)


def home(request):
    """Home page: the signed-in staff member's role and the support request counts."""
    try:
        counts = api_client.request_counts()
    except api_client.ApiUnavailable:
        logger.warning("Dashboard counts unavailable", exc_info=True)
        counts = None
    return render(
        request,
        "dashboard/home.html",
        {"role": role_of(request.user), "counts": counts},
    )


def request_dashboard(request):
    """Display all support requests."""
    try:
        response = get("/api/requests/")
        response.raise_for_status()
        support_requests = response.json()

        error = None

    except requests.RequestException:
        logger.warning("Could not retrieve support requests", exc_info=True)
        support_requests = []
        error = "Support requests are currently unavailable."

    for item in support_requests:
        if item.get("created_at"):
            item["created_at"] = datetime.fromisoformat(item["created_at"])
    return render(
        request,
        "dashboard/requests/dashboard.html",
        {
            "support_requests": support_requests,
            "error": error,
        },
    )


def request_detail(request, request_id):
    """Display details of an individual support request."""
    try:
        response = get(f"/api/requests/{request_id}")
        response.raise_for_status()

        support_request = response.json()
        error = None

        if support_request.get("created_at"):
            support_request["created_at"] = datetime.fromisoformat(
                support_request["created_at"]
            )

    except requests.HTTPError as exc:
        logger.warning(
            "Could not retrieve support request %s: %s",
            request_id,
            exc,
        )

        support_request = None

        if exc.response is not None and exc.response.status_code == 404:
            error = "Support request not found."
        else:
            error = "Could not retrieve this support request."

    except requests.RequestException:
        logger.warning(
            "Flask API unavailable for support request %s",
            request_id,
            exc_info=True,
        )
        support_request = None
        error = "The support request service is currently unavailable."

    return render(
        request,
        "dashboard/requests/detail.html",
        {
            "request_id": request_id,
            "support_request": support_request,
            "error": error,
        },
    )

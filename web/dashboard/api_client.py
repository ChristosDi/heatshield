"""The one place the Django UI calls the Flask API.

Django calls Flask from the server, so the browser never talks to Flask directly.
Every answer is checked before a page uses it.
"""


import requests
from django.conf import settings

# How long to wait for Flask before giving up, so a slow API can't hang a page.
TIMEOUT_SECONDS = 5

COUNT_NAMES = ("outstanding", "completed", "rejected", "total")


class ApiUnavailable(Exception):
    """The Flask API could not be reached, or sent an answer we can't use."""

def get(path, *, timeout=TIMEOUT_SECONDS, **kwargs):
    """Retrieve information from the Flask API."""
    return requests.get(
        f"{settings.FLASK_API_URL.rstrip('/')}{path}",
        timeout=timeout,
        **kwargs,
    )

def post(path, *, timeout=TIMEOUT_SECONDS, **kwargs):
    """Submit information to the Flask API."""
    return requests.post(
        f"{settings.FLASK_API_URL.rstrip('/')}{path}",
        timeout=timeout,
        **kwargs,
    )

def patch(path, *, timeout=TIMEOUT_SECONDS, **kwargs):
    """Update existing information through the Flask API."""
    return requests.patch(
        f"{settings.FLASK_API_URL.rstrip('/')}{path}",
        timeout=timeout,
        **kwargs,
    )

def delete(path, *, timeout=TIMEOUT_SECONDS, **kwargs):
    """Delete information through the Flask API."""
    return requests.delete(
        f"{settings.FLASK_API_URL.rstrip('/')}{path}",
        timeout=timeout,
        **kwargs,
    )

def get_json(path):
    """Ask the Flask API for a path and return its JSON answer."""
    try:
        response = get(path)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        raise ApiUnavailable(
            f"Could not get {path} from the Flask API"
        ) from error

def post_json(path, payload, *, timeout=TIMEOUT_SECONDS):
    """Submit JSON to the Flask API and return its decoded answer."""
    try:
        response = post(path, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError:
        raise
    except (requests.RequestException, ValueError) as error:
        raise ApiUnavailable(
            f"Could not post to {path} on the Flask API"
        ) from error

def request_counts():
    """Return the dashboard counts: outstanding, completed, rejected and total."""
    counts = get_json("/api/reports/request-counts")
    if not isinstance(counts, dict) or not all(type(counts.get(name)) is int for name in COUNT_NAMES):
        raise ApiUnavailable("The Flask API sent the counts in an unexpected shape")
    return {name: counts[name] for name in COUNT_NAMES}
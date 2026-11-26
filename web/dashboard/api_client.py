
"""The one place the Django UI calls the Flask API.

Django calls Flask from the server, so the browser never talks to Flask directly.
Every answer is checked before a page uses it.
"""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import requests
from django.conf import settings


# How long to wait for Flask before giving up.
TIMEOUT_SECONDS = 5

BASE = settings.FLASK_API_URL.rstrip("/")

COUNT_NAMES = ("outstanding", "completed", "rejected", "total")


class ApiUnavailable(Exception):
    """The Flask API could not be reached, or sent an answer we can't use."""


def get_json(path):
    """Ask the Flask API for a path and return its JSON answer."""
    url = f"{BASE}{path}"

    try:
        with urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            return json.load(response)

    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        raise ApiUnavailable(
            f"Could not get {path} from the Flask API"
        ) from error


def get(path, **kwargs):
    """Send a GET request to the Flask API."""
    try:
        return requests.get(
            f"{BASE}{path}",
            timeout=TIMEOUT_SECONDS,
            **kwargs,
        )
    except requests.RequestException as error:
        raise ApiUnavailable(
            f"Could not GET {path} from the Flask API"
        ) from error


def post(path, **kwargs):
    """Send a POST request to the Flask API."""
    try:
        return requests.post(
            f"{BASE}{path}",
            timeout=TIMEOUT_SECONDS,
            **kwargs,
        )
    except requests.RequestException as error:
        raise ApiUnavailable(
            f"Could not POST {path} to the Flask API"
        ) from error


def patch(path, **kwargs):
    """Send a PATCH request to the Flask API."""
    try:
        return requests.patch(
            f"{BASE}{path}",
            timeout=TIMEOUT_SECONDS,
            **kwargs,
        )
    except requests.RequestException as error:
        raise ApiUnavailable(
            f"Could not PATCH {path} on the Flask API"
        ) from error


def delete(path, **kwargs):
    """Send a DELETE request to the Flask API."""
    try:
        return requests.delete(
            f"{BASE}{path}",
            timeout=TIMEOUT_SECONDS,
            **kwargs,
        )
    except requests.RequestException as error:
        raise ApiUnavailable(
            f"Could not DELETE {path} from the Flask API"
        ) from error


def request_counts():
    """Return the dashboard counts: outstanding, completed, rejected and total."""
    counts = get_json("/api/reports/request-counts")

    if not isinstance(counts, dict) or not all(
        type(counts.get(name)) is int for name in COUNT_NAMES
    ):
        raise ApiUnavailable(
            "The Flask API sent the counts in an unexpected shape"
        )

    return {name: counts[name] for name in COUNT_NAMES}

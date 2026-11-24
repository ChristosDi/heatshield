"""The one place the Django UI calls the Flask API.

Django calls Flask from the server, so the browser never talks to Flask directly.
Every answer is checked before a page uses it.
"""
import json
from urllib.error import URLError
from urllib.request import urlopen

from django.conf import settings

# How long to wait for Flask before giving up, so a slow API can't hang a page.
TIMEOUT_SECONDS = 5

COUNT_NAMES = ("outstanding", "completed", "rejected", "total")


class ApiUnavailable(Exception):
    """The Flask API could not be reached, or sent an answer we can't use."""


def get_json(path):
    """Ask the Flask API for a path and return its JSON answer."""
    url = f"{settings.FLASK_API_URL}{path}"
    try:
        with urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            return json.load(response)
    except (URLError, TimeoutError, ValueError) as error:
        raise ApiUnavailable(f"Could not get {path} from the Flask API") from error


def request_counts():
    """Return the dashboard counts: outstanding, completed, rejected and total."""
    counts = get_json("/api/reports/request-counts")
    if not isinstance(counts, dict) or not all(type(counts.get(name)) is int for name in COUNT_NAMES):
        raise ApiUnavailable("The Flask API sent the counts in an unexpected shape")
    return {name: counts[name] for name in COUNT_NAMES}
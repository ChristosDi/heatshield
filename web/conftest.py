"""Shared test set-up for the Django UI.

The tests never call the real Flask API. Every test gets a fake Flask (the `fake_flask`
fixture below) in place of the network call, so the tests run with no Flask server,
no network and no .env.
"""

import json
import pytest
import requests

from dashboard import api_client


class FakeFlask:
    """Stands in for the Flask API during testing."""

    def __init__(self):
        self.body = None
        self.error = None
        self.calls = []
        self.status_code = 200

    def answer(self, data, status_code=200):
        """Answer every call with JSON data."""
        self.body = json.dumps(data).encode()
        self.status_code = status_code

    def answer_raw(self, raw_bytes):
        """Answer with these exact bytes."""
        self.body = raw_bytes

    def fail_with(self, error):
        """Raise the specified error on every call."""
        self.error = error

    def request(self, method, url, **kwargs):
        """Simulate an HTTP request without using the network."""
        self.calls.append({
            "url": url,
            "timeout": kwargs.get("timeout"),
        })

        if self.error is not None:
            raise self.error

        if self.body is None:
            raise requests.ConnectionError(
                "The Flask API is down (fake)"
            )

        response = requests.Response()
        response.status_code = self.status_code
        response._content = self.body
        response.url = url

        return response

@pytest.fixture(autouse=True)
def fake_flask(monkeypatch):
    """Replace HTTP requests so tests cannot reach the real Flask API."""
    fake = FakeFlask()

    monkeypatch.setattr(
        requests.Session,
        "request",
        lambda session, method, url, **kwargs:
            fake.request(method, url, **kwargs),
    )

    return fake
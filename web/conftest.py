"""Shared test set-up for the Django UI.

The tests never call the real Flask API. Every test gets a fake Flask (the `fake_flask`
fixture below) in place of the network call, so the tests run with no Flask server,
no network and no .env.
"""
import io
import json
from urllib.error import URLError

import pytest

from dashboard import api_client


class FakeFlask:
    """Stands in for the Flask API. A test sets the answer it gives, or leaves it down."""

    def __init__(self):
        self.body = None  # None means the API is down.
        self.error = None
        self.calls = []

    def answer(self, data):
        """Answer every call with this data, sent as JSON."""
        self.body = json.dumps(data).encode()

    def answer_raw(self, raw_bytes):
        """Answer with these exact bytes, for example text that isn't JSON."""
        self.body = raw_bytes

    def fail_with(self, error):
        """Raise this error on every call, for example an HTTP 500."""
        self.error = error

    def urlopen(self, url, timeout):
        self.calls.append({"url": url, "timeout": timeout})
        if self.error is not None:
            raise self.error
        if self.body is None:
            raise URLError("The Flask API is down (fake)")
        return io.BytesIO(self.body)


@pytest.fixture(autouse=True)
def fake_flask(monkeypatch):
    """Replace the network call in every test, so no test can reach a real Flask API.

    autouse=True means pytest runs this for every test, even ones that don't name it.
    A test that names `fake_flask` as an argument gets the fake, to set its answer.
    """
    fake = FakeFlask()
    monkeypatch.setattr(api_client, "urlopen", fake.urlopen)
    return fake
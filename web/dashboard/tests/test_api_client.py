"""Tests for the Flask API client: the one place Django calls Flask.

The real network call is replaced by the fake in web/conftest.py, so these tests
need no Flask server. All data is fictional.
"""
import os
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError
from unittest.mock import Mock

import requests

import pytest

from dashboard import api_client

COUNTS = {"outstanding": 3, "completed": 3, "rejected": 1, "total": 7}


def test_request_counts_returns_the_four_numbers(fake_flask):
    """A good answer from Flask comes back as the four counts."""
    fake_flask.answer(COUNTS)

    assert api_client.request_counts() == COUNTS


def test_calls_the_counts_route_on_the_configured_api_with_a_time_limit(fake_flask, settings):
    """Django calls the counts route at the address in FLASK_API_URL, and never waits forever."""
    settings.FLASK_API_URL = "http://127.0.0.1:5001"
    fake_flask.answer(COUNTS)

    api_client.request_counts()

    assert fake_flask.calls == [
        {"url": "http://127.0.0.1:5001/api/reports/request-counts", "timeout": api_client.TIMEOUT_SECONDS}
    ]


def test_api_down_raises_api_unavailable():
    """If Flask can't be reached, the client raises ApiUnavailable, which the page handles."""
    with pytest.raises(api_client.ApiUnavailable):
        api_client.request_counts()


def test_http_error_from_the_api_raises_api_unavailable(fake_flask):
    """An error status from Flask, such as 500, is not treated as counts."""
    fake_flask.fail_with(HTTPError("http://fake", 500, "Server error", {}, None))

    with pytest.raises(api_client.ApiUnavailable):
        api_client.request_counts()


def test_answer_that_is_not_json_raises_api_unavailable(fake_flask):
    """Text that isn't JSON, such as an HTML error page, is refused."""
    fake_flask.answer_raw(b"<html>Not JSON</html>")

    with pytest.raises(api_client.ApiUnavailable):
        api_client.request_counts()


@pytest.mark.parametrize("bad_answer", [
    {"outstanding": 3, "completed": 3, "rejected": 1},              # total missing
    {"outstanding": "3", "completed": 3, "rejected": 1, "total": 7},  # a number sent as text
    {"outstanding": True, "completed": 3, "rejected": 1, "total": 7},  # true/false is not a count
    [3, 3, 1, 7],                                                   # a list, not named counts
])
def test_counts_in_the_wrong_shape_raise_api_unavailable(fake_flask, bad_answer):
    """Counts that are missing or are not whole numbers are refused, so the page never shows them."""
    fake_flask.answer(bad_answer)

    with pytest.raises(api_client.ApiUnavailable):
        api_client.request_counts()


def test_the_site_refuses_to_start_with_a_flask_address_that_is_not_http():
    """FLASK_API_URL must start with http:// or https://, so Django can't be pointed at a local file
    or another kind of address by mistake."""
    env = {
        **os.environ,
        "DJANGO_SETTINGS_MODULE": "config.settings",
        "DJANGO_SECRET_KEY": "tests-only-not-a-real-secret",
        "FLASK_API_URL": "file:///etc/passwd",
    }
    web_folder = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-c", "import django; django.setup()"],
        cwd=web_folder, env=env, capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "FLASK_API_URL must start with http:// or https://" in result.stderr

def test_post_json_returns_decoded_response(monkeypatch, settings):
    """POST sends JSON and returns the decoded API response."""
    settings.FLASK_API_URL = "http://127.0.0.1:5001"

    payload = {"request_id": 45}
    expected = {"id": 12, "status": "pending"}

    response = Mock()
    response.json.return_value = expected

    mock_post = Mock(return_value=response)
    monkeypatch.setattr(api_client.requests, "post", mock_post)

    result = api_client.post_json(
        "/api/test/",
        payload,
        timeout=10,
    )

    assert result == expected

    mock_post.assert_called_once_with(
        "http://127.0.0.1:5001/api/test/",
        json=payload,
        timeout=10,
    )

    response.raise_for_status.assert_called_once()

def test_post_json_timeout_raises_api_unavailable(monkeypatch):
    """A network timeout is reported as an unavailable API."""
    mock_post = Mock(side_effect=requests.Timeout("Timed out"))

    monkeypatch.setattr(api_client.requests, "post", mock_post)

    with pytest.raises(api_client.ApiUnavailable):
        api_client.post_json("/api/test/", {"request_id": 45})

def test_post_json_invalid_response_raises_api_unavailable(monkeypatch):
    """An invalid JSON response is reported as an unavailable API."""
    response = Mock()
    response.json.side_effect = ValueError("Invalid JSON")

    monkeypatch.setattr(
        api_client.requests,
        "post",
        Mock(return_value=response),
    )

    with pytest.raises(api_client.ApiUnavailable):
        api_client.post_json("/api/test/", {"request_id": 45})

def test_post_json_preserves_http_conflict(monkeypatch):
    """An HTTP 409 preserves the API's rejection details."""
    response = requests.Response()
    response.status_code = 409
    response._content = b'{"message": "Cooling centre is full"}'

    monkeypatch.setattr(
        api_client.requests,
        "post",
        Mock(return_value=response),
    )

    with pytest.raises(requests.HTTPError) as error:
        api_client.post_json("/api/test/", {"request_id": 45})

    assert error.value.response.status_code == 409
    assert error.value.response.json()["message"] == (
        "Cooling centre is full"
    )
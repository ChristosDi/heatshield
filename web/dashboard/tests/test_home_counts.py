"""Tests for the support request counts on the dashboard home page.

The Flask API is replaced by the fake in web/conftest.py. All data is fictional.
"""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse

COUNTS = {"outstanding": 3, "completed": 3, "rejected": 1, "total": 7}


@pytest.fixture
def signed_in_client(client, db):
    """A test browser signed in as a fictional staff member."""
    client.force_login(User.objects.create_user("test_worker", password="fictional-pass-123"))
    return client


def test_home_page_shows_the_counts(signed_in_client, fake_flask):
    """The home page shows each count from the API next to its name."""
    fake_flask.answer(COUNTS)

    response = signed_in_client.get(reverse("home"))

    assert response.status_code == 200
    assert response.context["counts"] == COUNTS
    page = response.content.decode()
    for name, number in [("Outstanding", 3), ("Completed", 3), ("Rejected", 1), ("Total", 7)]:
        assert f"<dt>{name}</dt><dd>{number}</dd>" in page


def test_counts_change_when_a_request_status_changes(signed_in_client, fake_flask):
    """When a request is completed in Flask, the next page load shows the new numbers."""
    fake_flask.answer(COUNTS)
    signed_in_client.get(reverse("home"))

    fake_flask.answer({"outstanding": 2, "completed": 4, "rejected": 1, "total": 7})
    response = signed_in_client.get(reverse("home"))

    assert "<dt>Outstanding</dt><dd>2</dd>" in response.content.decode()
    assert "<dt>Completed</dt><dd>4</dd>" in response.content.decode()


def test_zero_counts_are_shown_not_hidden(signed_in_client, fake_flask):
    """With no requests, the page shows 0 for each count rather than the error message."""
    fake_flask.answer({"outstanding": 0, "completed": 0, "rejected": 0, "total": 0})

    response = signed_in_client.get(reverse("home"))

    assert "<dt>Total</dt><dd>0</dd>" in response.content.decode()
    assert b"can't be loaded" not in response.content


def test_home_page_still_loads_when_the_api_is_down(signed_in_client):
    """If Flask is down, staff still get the page, with a message instead of an error page."""
    response = signed_in_client.get(reverse("home"))

    assert response.status_code == 200
    assert response.context["counts"] is None
    assert b"The request counts can't be loaded right now" in response.content


def test_home_page_links_the_counts_stylesheet(signed_in_client, fake_flask):
    """The page loads the stylesheet that lays the counts out on desktops and phones."""
    fake_flask.answer(COUNTS)

    response = signed_in_client.get(reverse("home"))

    assert b'href="/static/dashboard/dashboard.css"' in response.content
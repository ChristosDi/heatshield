"""Wrong and unusual input for sign-in and sign-out, plus app-wide sign-in rules."""
import os
import subprocess
import sys
from pathlib import Path

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import NoReverseMatch, get_resolver, reverse

PASSWORD = "fictional-pass-123"
WRONG_LOGIN_MESSAGE = b"Your username or password is wrong"


@pytest.fixture
def staff_user(db):
    """A fictional staff account that the tests below sign in with."""
    return User.objects.create_user("test_worker", password=PASSWORD)


def test_unknown_username_is_refused_with_the_usual_message(client, db):
    """A username that does not exist is refused, shows the normal error message and signs nobody in."""
    response = client.post(reverse("login"), {"username": "nobody", "password": PASSWORD})
    assert response.status_code == 200
    assert WRONG_LOGIN_MESSAGE in response.content
    assert "_auth_user_id" not in client.session


def test_wrong_password_shows_the_same_message_as_an_unknown_username(client, staff_user):
    """A wrong password shows the same message as an unknown username,
    so nobody can use the sign-in page to find out which usernames exist."""
    response = client.post(reverse("login"), {"username": "test_worker", "password": "wrong"})
    assert WRONG_LOGIN_MESSAGE in response.content


def test_blank_username_and_password_are_refused(client, db):
    """Submitting the form with both boxes empty is refused and signs nobody in."""
    response = client.post(reverse("login"), {"username": "", "password": ""})
    assert response.status_code == 200
    assert "_auth_user_id" not in client.session


def test_disabled_account_cannot_sign_in(client, staff_user):
    """An account switched off in the admin site cannot sign in, even with the right password."""
    staff_user.is_active = False
    staff_user.save()
    client.post(reverse("login"), {"username": "test_worker", "password": PASSWORD})
    assert "_auth_user_id" not in client.session


def test_after_sign_in_you_return_to_the_page_you_asked_for(client, staff_user):
    """If you were sent to sign in from another page, signing in takes you back to that page."""
    response = client.post(reverse("login"), {"username": "test_worker", "password": PASSWORD, "next": "/admin/"})
    assert response.url == "/admin/"


def test_sign_in_never_sends_you_to_another_website(client, staff_user):
    """A link that tries to send you to another website after sign-in is ignored and you go home instead.
    This stops fake links that use our sign-in page to send staff to a phishing site."""
    response = client.post(
        reverse("login"), {"username": "test_worker", "password": PASSWORD, "next": "https://evil.example.com/"}
    )
    assert response.url == reverse("home")


def test_signing_out_with_a_link_is_refused(client, staff_user):
    """Visiting the sign-out address directly (GET) is refused and you stay signed in.
    Only the Sign out button (POST) signs you out, so another website cannot sign our staff out."""
    client.force_login(staff_user)
    response = client.get(reverse("logout"))
    assert response.status_code == 405
    assert "_auth_user_id" in client.session


def test_sign_in_form_without_its_security_token_is_rejected(staff_user):
    """A sign-in form sent without Django's security token (CSRF) is rejected with 403,
    so another website cannot submit our forms on someone's behalf."""
    browser = Client(enforce_csrf_checks=True)
    response = browser.post(reverse("login"), {"username": "test_worker", "password": PASSWORD})
    assert response.status_code == 403


def test_every_page_except_sign_in_needs_sign_in(client, db):
    """Every page except sign-in sends a signed-out visitor to sign in, including the admin site.

    It checks every named page in the app, so new pages are covered automatically and this test
    fails if someone adds a page that is open by mistake. Pages whose address needs a value,
    such as a request ID, are skipped and need their own test.
    """
    public = {"login"}
    names = [name for name in get_resolver().reverse_dict if isinstance(name, str) and name not in public]
    for name in names:
        try:
            url = reverse(name)
        except NoReverseMatch:
            continue
        response = client.get(url)
        assert response.status_code in (302, 405), f"{url} is open to signed-out visitors"
        if response.status_code == 302:
            assert response.url.startswith(reverse("login"))
    admin = client.get(reverse("admin:index"))
    assert admin.status_code == 302 and "/admin/login/" in admin.url


def test_the_site_refuses_to_start_without_a_secret_key():
    """With no secret key set, the site stops at start-up with a clear message,
    instead of running with an unsafe default key."""
    env = {**os.environ, "DJANGO_SETTINGS_MODULE": "config.settings", "DJANGO_SECRET_KEY": ""}
    web_folder = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-c", "import django; django.setup()"],
        cwd=web_folder, env=env, capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "Set DJANGO_SECRET_KEY" in result.stderr
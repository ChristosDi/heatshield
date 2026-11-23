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
    return User.objects.create_user("test_worker", password=PASSWORD)


def test_unknown_username_is_refused_with_the_usual_message(client, db):
    response = client.post(reverse("login"), {"username": "nobody", "password": PASSWORD})
    assert response.status_code == 200
    assert WRONG_LOGIN_MESSAGE in response.content
    assert "_auth_user_id" not in client.session


def test_wrong_password_shows_the_same_message_as_an_unknown_username(client, staff_user):
    response = client.post(reverse("login"), {"username": "test_worker", "password": "wrong"})
    assert WRONG_LOGIN_MESSAGE in response.content


def test_blank_username_and_password_are_refused(client, db):
    response = client.post(reverse("login"), {"username": "", "password": ""})
    assert response.status_code == 200
    assert "_auth_user_id" not in client.session


def test_disabled_account_cannot_sign_in(client, staff_user):
    staff_user.is_active = False
    staff_user.save()
    client.post(reverse("login"), {"username": "test_worker", "password": PASSWORD})
    assert "_auth_user_id" not in client.session


def test_after_sign_in_you_return_to_the_page_you_asked_for(client, staff_user):
    response = client.post(reverse("login"), {"username": "test_worker", "password": PASSWORD, "next": "/admin/"})
    assert response.url == "/admin/"


def test_sign_in_never_sends_you_to_another_website(client, staff_user):
    response = client.post(
        reverse("login"), {"username": "test_worker", "password": PASSWORD, "next": "https://evil.example.com/"}
    )
    assert response.url == reverse("home")


def test_signing_out_with_a_link_is_refused(client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse("logout"))
    assert response.status_code == 405
    assert "_auth_user_id" in client.session


def test_sign_in_form_without_its_security_token_is_rejected(staff_user):
    browser = Client(enforce_csrf_checks=True)
    response = browser.post(reverse("login"), {"username": "test_worker", "password": PASSWORD})
    assert response.status_code == 403


def test_every_page_except_sign_in_needs_sign_in(client, db):
    """Checks every named page, so new pages are covered automatically.

    Pages whose address needs a value, such as a request ID, are skipped and need their own test.
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
    env = {**os.environ, "DJANGO_SETTINGS_MODULE": "config.settings", "DJANGO_SECRET_KEY": ""}
    web_folder = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-c", "import django; django.setup()"],
        cwd=web_folder, env=env, capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "Set DJANGO_SECRET_KEY" in result.stderr
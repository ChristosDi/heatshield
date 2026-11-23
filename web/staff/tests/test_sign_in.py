import pytest
from django.contrib.auth.models import User
from django.urls import reverse

PASSWORD = "fictional-pass-123"


@pytest.fixture
def staff_user(db):
    return User.objects.create_user("test_worker", password=PASSWORD)


def test_sign_in_page_loads(client):
    assert client.get(reverse("login")).status_code == 200


def test_correct_password_signs_in(client, staff_user):
    response = client.post(reverse("login"), {"username": "test_worker", "password": PASSWORD})
    assert response.status_code == 302
    assert response.url == reverse("home")
    assert client.session["_auth_user_id"] == str(staff_user.pk)


def test_wrong_password_is_refused(client, staff_user):
    response = client.post(reverse("login"), {"username": "test_worker", "password": "wrong-password"})
    assert response.status_code == 200
    assert "_auth_user_id" not in client.session


def test_sign_out_ends_the_session(client, staff_user):
    client.force_login(staff_user)
    response = client.post(reverse("logout"))
    assert response.status_code == 302
    assert response.url == reverse("login")
    assert "_auth_user_id" not in client.session
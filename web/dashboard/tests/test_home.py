import pytest
from django.contrib.auth.models import Group, User
from django.urls import reverse

from staff.roles import COORDINATOR


@pytest.mark.django_db
def test_signed_out_visitor_is_sent_to_sign_in(client):
    response = client.get(reverse("home"))
    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={reverse('home')}"


@pytest.mark.django_db
def test_signed_in_user_sees_the_home_page_with_their_role(client):
    user = User.objects.create_user("test_coordinator", password="fictional-pass-123")
    user.groups.add(Group.objects.get(name=COORDINATOR))
    client.force_login(user)

    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert b"Role:" in response.content
    assert b"coordinator" in response.content


@pytest.mark.django_db
def test_user_without_a_role_is_told_to_ask_an_administrator(client):
    user = User.objects.create_user("test_new_starter", password="fictional-pass-123")
    client.force_login(user)

    response = client.get(reverse("home"))

    assert b"no role yet" in response.content
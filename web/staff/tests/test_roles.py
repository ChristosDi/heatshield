import pytest
from django.contrib.auth.models import Group, User

from staff.roles import ALL_ROLES, COORDINATOR, role_of


@pytest.mark.django_db
def test_the_migration_creates_the_three_roles():
    assert set(Group.objects.values_list("name", flat=True)) == set(ALL_ROLES)


@pytest.mark.django_db
def test_role_of_returns_the_users_role():
    user = User.objects.create_user("test_coordinator", password="fictional-pass-123")
    user.groups.add(Group.objects.get(name=COORDINATOR))
    assert role_of(user) == COORDINATOR


@pytest.mark.django_db
def test_role_of_returns_none_when_the_user_has_no_role():
    user = User.objects.create_user("test_new_starter", password="fictional-pass-123")
    assert role_of(user) is None
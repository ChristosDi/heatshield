"""The three staff roles. Each one is a Django group with the same name."""

SUPPORT_WORKER = "support_worker"
COORDINATOR = "coordinator"
ADMIN = "admin"

ALL_ROLES = [SUPPORT_WORKER, COORDINATOR, ADMIN]


def role_of(user):
    """Return the user's role, or None if they have no role yet."""
    group = user.groups.filter(name__in=ALL_ROLES).first()
    return group.name if group else None
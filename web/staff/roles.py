"""The three staff roles. Each one is a Django group with the same name."""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


SUPPORT_WORKER = "support_worker"
COORDINATOR = "coordinator"
ADMIN = "admin"

ALL_ROLES = [SUPPORT_WORKER, COORDINATOR, ADMIN]


def role_of(user):
    """Return the user's role, or None if they have no role yet."""
    group = user.groups.filter(name__in=ALL_ROLES).first()
    return group.name if group else None

def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):

            user_roles = request.user.groups.values_list(
                "name",
                flat=True
            )

            if not any(role in allowed_roles for role in user_roles):
                raise PermissionDenied

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
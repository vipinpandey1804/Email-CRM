from functools import wraps
from ninja.errors import HttpError


def require_role(*roles):
    """Decorator for Django Ninja endpoints requiring specific org roles."""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user = request.auth
            if not user:
                raise HttpError(401, 'Authentication required')
            org_slug = kwargs.get('slug') or getattr(request, '_org_slug', None)
            if org_slug:
                from organizations.models import OrganizationUser
                try:
                    ou = OrganizationUser.objects.get(
                        organization__slug=org_slug, user=user
                    )
                    user_role = getattr(ou, 'profile', None)
                    role = user_role.role if user_role else ('admin' if ou.is_admin else 'viewer')
                    if roles and role not in roles:
                        raise HttpError(403, 'Insufficient permissions')
                except OrganizationUser.DoesNotExist:
                    raise HttpError(403, 'Not a member of this organization')
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

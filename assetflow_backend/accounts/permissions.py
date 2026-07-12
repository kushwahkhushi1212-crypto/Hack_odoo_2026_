from rest_framework import permissions


class IsOrgAdmin(permissions.BasePermission):
    """Full access only for organization admins (Organization Setup screen)."""

    message = 'Only organization admins can perform this action.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_org_admin)


class IsOrgAdminOrReadOnly(permissions.BasePermission):
    """Anyone authenticated can read; only admins can write."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_authenticated and request.user.is_org_admin)


class IsAdminOrOwner(permissions.BasePermission):
    """Admins can touch anything; regular users only their own records."""

    owner_field = 'requested_by'

    def has_object_permission(self, request, view, obj):
        if request.user.is_org_admin:
            return True
        owner = getattr(obj, self.owner_field, None)
        return owner == request.user

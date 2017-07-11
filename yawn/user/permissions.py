from rest_framework.permissions import BasePermission


class ModelPermissions(BasePermission):
    """Allow authenticated users to read, and staff to write"""

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        # authenticated, but not staff: only allow read
        return request.method in ('GET', 'HEAD', 'OPTIONS')

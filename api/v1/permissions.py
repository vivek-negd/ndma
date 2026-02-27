from rest_framework.permissions import BasePermission
from api.v1.rbac import has_role_access, has_geographical_access


class BRDRolePermission(BasePermission):

    def has_object_permission(self, request, view, obj):

        if not request.user.is_authenticated:
            return False

        role_check = has_role_access(request.user, obj)
        geo_check = has_geographical_access(request.user, obj)

        return role_check and geo_check
from rest_framework.permissions import BasePermission


class RoleBasedAccessPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # SUPER ADMIN → Full Access
        if user.user_role == "SUPER_ADMIN":
            return True

        # For other roles, allow but check object level
        return True


    def has_object_permission(self, request, view, obj):
        user = request.user

        # SUPER ADMIN → Full access
        if user.user_role == "SUPER_ADMIN":
            return True

        # STATE LEVEL
        if user.user_role == "STATE_ADMIN":
            return user.state_code == obj.state_code

        # DISTRICT LEVEL
        if user.user_role == "DISTRICT_ADMIN":
            return (
                user.state_code == obj.state_code and
                user.district_code == obj.district_code
            )

        # BLOCK LEVEL
        if user.user_role == "BLOCK_ADMIN":
            return (
                user.state_code == obj.state_code and
                user.district_code == obj.district_code and
                user.block_code == obj.block_code
            )

        return False
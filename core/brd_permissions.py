class HierarchicalAccessPermission(BasePermission):

    def has_object_permission(self, request, view, resource_instance):

        authenticated_user = request.user

        if authenticated_user.user_role == "SUPER_ADMIN":
            return True

        if authenticated_user.user_role == "STATE_ADMIN":
            return (
                authenticated_user.state_code ==
                resource_instance.state_code
            )

        if authenticated_user.user_role == "DISTRICT_ADMIN":
            return (
                authenticated_user.state_code ==
                resource_instance.state_code and
                authenticated_user.district_code ==
                resource_instance.district_code
            )

        if authenticated_user.user_role == "BLOCK_ADMIN":
            return (
                authenticated_user.state_code ==
                resource_instance.state_code and
                authenticated_user.district_code ==
                resource_instance.district_code and
                authenticated_user.block_code ==
                resource_instance.block_code
            )

        return False
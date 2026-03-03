class HierarchicalAccessPermission(BasePermission):

    def has_object_permission(self, request, view, resource_instance):

        authenticated_user = request.user

        if authenticated_user.user_role == "SUPER_ADMIN":
            return True

        if authenticated_user.user_role == "SDMA_ADMIN":
            return (
                authenticated_user.state_id ==
                getattr(resource_instance, 'state_id', None)
            )

        if authenticated_user.user_role == "DDMA_NODAL_OFFICER":
            return (
                authenticated_user.state_id ==
                getattr(resource_instance, 'state_id', None) and
                authenticated_user.district_id ==
                getattr(resource_instance, 'district_id', None)
            )

        return False
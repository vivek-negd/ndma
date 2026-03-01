from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from models.role import Permission, Role, UserRole, RolePermissionAudit, UserPermissionOverride
from api.v1.serializers.rbac_serializers import (
    PermissionSerializer, RoleSerializer, RoleDetailSerializer,
    UserRoleSerializer, RolePermissionAuditSerializer, UserPermissionOverrideSerializer
)
from api.v1.rbac import has_role_access, has_geographical_access

User = get_user_model()


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """View permissions - SUPER_ADMIN only"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['module', 'action', 'code']
    search_fields = ['name', 'code', 'description']
    
    def check_super_admin(self, request):
        if getattr(request.user, "user_role", None) != 'SUPER_ADMIN':
            raise PermissionDenied("Only Super Admin can access permissions")
    
    def list(self, request, *args, **kwargs):
        self.check_super_admin(request)
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        self.check_super_admin(request)
        return super().retrieve(request, *args, **kwargs)


class RoleViewSet(viewsets.ModelViewSet):
    """Manage roles - SUPER_ADMIN only"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['name', 'is_active']
    search_fields = ['name', 'description']
    
    def check_super_admin(self, request):
        if getattr(request.user, "user_role", None) != 'SUPER_ADMIN':
            raise PermissionDenied("Only Super Admin can manage roles")
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RoleDetailSerializer
        return RoleSerializer
    
    def list(self, request, *args, **kwargs):
        self.check_super_admin(request)
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        self.check_super_admin(request)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        self.check_super_admin(request)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        self.check_super_admin(request)
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def assign_permission(self, request, pk=None):
        """Assign permission to role"""
        self.check_super_admin(request)
        role = self.get_object()
        permission_id = request.data.get('permission_id')
        
        if not permission_id:
            return Response({'error': 'permission_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            permission = Permission.objects.get(id=permission_id)
            role.permissions.add(permission)
            
            # Audit log
            RolePermissionAudit.objects.create(
                user=request.user,
                action='ASSIGN',
                role=role,
                permission=permission,
                ip_address=self.get_client_ip(request)
            )
            
            return Response({'message': 'Permission assigned successfully'})
        except Permission.DoesNotExist:
            return Response({'error': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def revoke_permission(self, request, pk=None):
        """Revoke permission from role"""
        self.check_super_admin(request)
        role = self.get_object()
        permission_id = request.data.get('permission_id')
        
        if not permission_id:
            return Response({'error': 'permission_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            permission = Permission.objects.get(id=permission_id)
            role.permissions.remove(permission)
            
            # Audit log
            RolePermissionAudit.objects.create(
                user=request.user,
                action='REVOKE',
                role=role,
                permission=permission,
                ip_address=self.get_client_ip(request)
            )
            
            return Response({'message': 'Permission revoked successfully'})
        except Permission.DoesNotExist:
            return Response({'error': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserRoleViewSet(viewsets.ModelViewSet):
    """Manage user roles"""
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['role__name', 'is_active', 'state', 'district']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'organization']
    
    def check_permissions(self, request):
        user_role = getattr(request.user, "user_role", None)
        if user_role not in ['SUPER_ADMIN', 'TECHNICAL_ADMIN', 'NDMA_ADMIN']:
            raise PermissionDenied("Insufficient permissions to manage user roles")

    def _validate_target_user(self, request, target_user):
        if not has_role_access(request.user, target_user):
            raise PermissionDenied("Cannot manage users with higher or equal role")
        if not has_geographical_access(request.user, target_user):
            raise PermissionDenied("User outside your geographical scope")

    def _resolve_target_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise PermissionDenied("Target user not found")
    
    def list(self, request, *args, **kwargs):
        self.check_permissions(request)
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        self.check_permissions(request)
        user_id = request.data.get('user')
        if user_id:
            target_user = self._resolve_target_user(user_id)
            self._validate_target_user(request, target_user)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        self.check_permissions(request)
        target_user = self.get_object().user
        self._validate_target_user(request, target_user)
        return super().update(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def activate(self, request, pk=None):
        """Activate user role"""
        self.check_permissions(request)
        user_role = self.get_object()
        self._validate_target_user(request, user_role.user)
        user_role.is_active = True
        user_role.save()
        
        RolePermissionAudit.objects.create(
            user=request.user,
            action='ACTIVATE',
            target_user=user_role.user,
            role=user_role.role,
            ip_address=self.get_client_ip(request)
        )
        
        return Response({'message': 'User role activated'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def deactivate(self, request, pk=None):
        """Deactivate user role"""
        self.check_permissions(request)
        user_role = self.get_object()
        self._validate_target_user(request, user_role.user)
        user_role.is_active = False
        user_role.save()
        
        RolePermissionAudit.objects.create(
            user=request.user,
            action='DEACTIVATE',
            target_user=user_role.user,
            role=user_role.role,
            ip_address=self.get_client_ip(request)
        )
        
        return Response({'message': 'User role deactivated'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def grant_permission(self, request, pk=None):
        """Grant a direct permission override to the user linked with this user-role"""
        self.check_permissions(request)
        user_role = self.get_object()
        self._validate_target_user(request, user_role.user)

        permission_id = request.data.get('permission_id')
        permission_code = request.data.get('permission_code')
        reason = request.data.get('reason', '')

        if not permission_id and not permission_code:
            return Response({'error': 'permission_id or permission_code required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if permission_id:
                permission = Permission.objects.get(pk=permission_id)
            else:
                permission = Permission.objects.get(code=permission_code)
        except Permission.DoesNotExist:
            return Response({'error': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)

        override, _ = UserPermissionOverride.objects.update_or_create(
            user=user_role.user,
            permission=permission,
            defaults={'granted_by': request.user, 'reason': reason, 'is_active': True}
        )

        RolePermissionAudit.objects.create(
            user=request.user,
            action='GRANT_USER_PERMISSION',
            role=user_role.role,
            permission=permission,
            target_user=user_role.user,
            ip_address=self.get_client_ip(request)
        )

        serializer = UserPermissionOverrideSerializer(override)
        return Response({
            'message': 'Permission granted to user',
            'override': serializer.data,
            'effective_permissions': user_role.user.get_effective_permissions()
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def revoke_permission(self, request, pk=None):
        """Revoke a direct permission override from the user linked with this user-role"""
        self.check_permissions(request)
        user_role = self.get_object()
        self._validate_target_user(request, user_role.user)

        permission_id = request.data.get('permission_id')
        permission_code = request.data.get('permission_code')

        if not permission_id and not permission_code:
            return Response({'error': 'permission_id or permission_code required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if permission_id:
                permission = Permission.objects.get(pk=permission_id)
            else:
                permission = Permission.objects.get(code=permission_code)
        except Permission.DoesNotExist:
            return Response({'error': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            override = UserPermissionOverride.objects.get(user=user_role.user, permission=permission)
        except UserPermissionOverride.DoesNotExist:
            return Response({'error': 'Override not found'}, status=status.HTTP_404_NOT_FOUND)

        override.is_active = False
        override.save()

        RolePermissionAudit.objects.create(
            user=request.user,
            action='REVOKE_USER_PERMISSION',
            role=user_role.role,
            permission=permission,
            target_user=user_role.user,
            ip_address=self.get_client_ip(request)
        )

        return Response({
            'message': 'Permission revoked from user',
            'effective_permissions': user_role.user.get_effective_permissions()
        })
    
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolePermissionAuditViewSet(viewsets.ReadOnlyModelViewSet):
    """View audit logs - SUPER_ADMIN and TECHNICAL_ADMIN only"""
    queryset = RolePermissionAudit.objects.all()
    serializer_class = RolePermissionAuditSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['action', 'user__email']
    search_fields = ['target_user__email', 'action']
    ordering = ['-created_at']
    
    def check_permissions(self, request):
        user_role = getattr(request.user, "user_role", None)
        if user_role not in ['SUPER_ADMIN', 'TECHNICAL_ADMIN']:
            raise PermissionDenied("Only admins can view audit logs")
    
    def list(self, request, *args, **kwargs):
        self.check_permissions(request)
        return super().list(request, *args, **kwargs)
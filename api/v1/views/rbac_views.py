from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from models.role import Permission, Role, UserRole, RolePermissionAudit
from api.v1.serializers.rbac_serializers import (
    PermissionSerializer, RoleSerializer, RoleDetailSerializer,
    UserRoleSerializer, RolePermissionAuditSerializer
)


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
    
    def list(self, request, *args, **kwargs):
        self.check_permissions(request)
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        self.check_permissions(request)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        self.check_permissions(request)
        return super().update(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def activate(self, request, pk=None):
        """Activate user role"""
        self.check_permissions(request)
        user_role = self.get_object()
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
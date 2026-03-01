from rest_framework import serializers
from django.contrib.auth import get_user_model
from models.role import (
    Permission,
    Role,
    UserRole,
    RolePermissionAudit,
    UserPermissionOverride,
)

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'code', 'description', 'module', 'action', 'created_at']
        read_only_fields = ['id', 'created_at']


class RoleDetailSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_codes = serializers.SerializerMethodField()
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(), many=True, write_only=True, required=False
    )
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'permissions', 'permission_codes', 'permission_ids',
            'is_active', 'hierarchy_level', 'is_system_role', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_permission_codes(self, obj):
        return obj.get_all_permissions()


class RoleSerializer(serializers.ModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(), many=True, write_only=True, required=False
    )
    permission_codes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'is_active', 'hierarchy_level', 'is_system_role', 'permission_ids', 'permission_codes']
        read_only_fields = ['id']

    def get_permission_codes(self, obj):
        return obj.get_all_permissions()

    def _apply_permissions(self, role, permission_ids):
        if permission_ids is not None:
            role.permissions.set(permission_ids)
        return role

    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        role = super().create(validated_data)
        return self._apply_permissions(role, permission_ids)

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        role = super().update(instance, validated_data)
        return self._apply_permissions(role, permission_ids)


class UserRoleSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    permissions = serializers.SerializerMethodField()
    effective_permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'user_email', 'user_name', 'role', 'role_name', 
            'state', 'district', 'organization', 'designation', 
            'is_active', 'is_mfa_enabled', 'last_login', 'permissions', 'effective_permissions', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_login']
    
    def get_permissions(self, obj):
        return obj.get_all_permissions()

    def get_effective_permissions(self, obj):
        return obj.user.get_effective_permissions()


class RolePermissionAuditSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    target_user_email = serializers.CharField(source='target_user.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    permission_code = serializers.CharField(source='permission.code', read_only=True)
    
    class Meta:
        model = RolePermissionAudit
        fields = [
            'id', 'user', 'user_email', 'action', 'role', 'role_name', 
            'permission', 'permission_code', 'target_user', 'target_user_email', 
            'details', 'ip_address', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserPermissionOverrideSerializer(serializers.ModelSerializer):
    permission_code = serializers.CharField(source='permission.code', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = UserPermissionOverride
        fields = [
            'id', 'user', 'user_email', 'permission', 'permission_code', 'is_active',
            'reason', 'granted_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'granted_by']
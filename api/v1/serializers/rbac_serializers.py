from rest_framework import serializers
from models.role import Permission, Role, UserRole, RolePermissionAudit
from django.contrib.auth.models import User


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'code', 'description', 'module', 'action', 'created_at']
        read_only_fields = ['id', 'created_at']


class RoleDetailSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_codes = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions', 'permission_codes', 'is_active', 'hierarchy_level', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_permission_codes(self, obj):
        return obj.get_all_permissions()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'is_active', 'hierarchy_level']
        read_only_fields = ['id']


class UserRoleSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    role_name = serializers.CharField(source='role.get_name_display', read_only=True)
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'user_email', 'user_name', 'role', 'role_name', 
            'state', 'district', 'organization', 'designation', 
            'is_active', 'is_mfa_enabled', 'last_login', 'permissions', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_login']
    
    def get_permissions(self, obj):
        return obj.get_all_permissions()


class RolePermissionAuditSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    target_user_email = serializers.CharField(source='target_user.email', read_only=True)
    role_name = serializers.CharField(source='role.get_name_display', read_only=True)
    permission_code = serializers.CharField(source='permission.code', read_only=True)
    
    class Meta:
        model = RolePermissionAudit
        fields = [
            'id', 'user', 'user_email', 'action', 'role', 'role_name', 
            'permission', 'permission_code', 'target_user', 'target_user_email', 
            'details', 'ip_address', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
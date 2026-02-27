from rest_framework.permissions import BasePermission
from rest_framework import status
from rest_framework.exceptions import PermissionDenied


class HasPermission(BasePermission):
    """Check if user has specific permission"""
    permission_code = None
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            user_role = request.user.user_role
            if not user_role.is_active:
                raise PermissionDenied("User role is inactive")
            
            if not self.permission_code:
                return True
            
            return user_role.has_permission(self.permission_code)
        except Exception:
            return False


class IsVolunteer(BasePermission):
    """Check if user is volunteer"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            return request.user.user_role.role.name == 'VOLUNTEER'
        except:
            return False


class IsDDMAOfficer(BasePermission):
    """Check if user is DDMA Nodal Officer"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            return request.user.user_role.role.name == 'DDMA_NODAL_OFFICER'
        except:
            return False


class IsNDMAAdmin(BasePermission):
    """Check if user is NDMA Admin"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            return request.user.user_role.role.name == 'NDMA_ADMIN'
        except:
            return False


class IsSuperAdmin(BasePermission):
    """Check if user is Super Admin"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            return request.user.user_role.role.name == 'SUPER_ADMIN'
        except:
            return False


class IsStaffLevel(BasePermission):
    """Check if user is staff level (NDMA, SDMA, DDMA)"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            role = request.user.user_role.role.name
            return role in ['NDMA_ADMIN', 'SDMA_ADMIN', 'DDMA_NODAL_OFFICER', 'SUPER_ADMIN']
        except:
            return False
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
import csv
import io
from django.db import transaction

from api.v1.serializers.auth_serializers import (
    UserCreateSerializer,
    UserLoginSerializer,
    UserSerializer,
)
from core.constants import UserRoles, ErrorMessages
from models.state import State
from models.district import District

User = get_user_model()


class LoginView(viewsets.ViewSet):
    """Authentication endpoints"""

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "status_code": 200,
                    "message": "Login successful",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status_code": 400,
                "message": "Login failed",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def create_user(self, request):
        user_role = getattr(request.user, "user_role", None)
        if user_role not in UserRoles.ADMIN_ROLES:
            return Response(
                {
                    "status_code": 403,
                    "error": ErrorMessages.INSUFFICIENT_ROLE_CREATE_USER
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "status_code": 201,
                    "message": "User created successfully",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status_code": 400,
                "message": "User creation failed",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        return Response(
            {
                "status_code": 200,
                "message": "Logout successful"
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def profile(self, request):
        return Response(
            {
                "status_code": 200,
                "data": UserSerializer(request.user).data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def create_user_with_privilege(self, request):
        """
        Create user with privilege (role) in ONE API call - INCLUDES role assignment
        
        Request body for SDMA_ADMIN (state-level, no district needed):
        {
            "email": "state_admin@state.gov.in",
            "password": "SecurePass@2026",
            "first_name": "State",
            "last_name": "Admin",
            "privilege": "SDMA_ADMIN",
            "state_id": 38,
            "is_active": true
        }
        
        Request body for DDMA_NODAL_OFFICER (district-level, district required):
        {
            "email": "officer@district.gov.in",
            "password": "SecurePass@2026",
            "first_name": "District",
            "last_name": "Officer",
            "privilege": "DDMA_NODAL_OFFICER",
            "state_id": 38,
            "district_id": 5,
            "is_active": true
        }
        
        Rules:
        - SDMA_ADMIN: Only needs state_id (has access to all districts in state)
        - DDMA_NODAL_OFFICER: Requires both state_id AND district_id
        - SUPER_ADMIN/NDMA_ADMIN: No geographic restrictions needed
        """
        user_role = getattr(request.user, "user_role", None)
        if user_role not in UserRoles.ADMIN_ROLES:
            return Response(
                {
                    "status_code": 403,
                    "error": ErrorMessages.INSUFFICIENT_ROLE_CREATE_USER
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Extract privilege
        privilege = request.data.get('privilege')
        if not privilege:
            return Response(
                {
                    "status_code": 400,
                    "error": "privilege (role) is required"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate privilege value
        valid_roles = UserRoles.ALL_ROLES
        if privilege not in valid_roles:
            return Response(
                {
                    "status_code": 400,
                    "error": f"Invalid privilege. Must be one of: {', '.join(valid_roles)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Check district requirement based on privilege role
        state_id = request.data.get('state_id')
        district_id = request.data.get('district_id')
        
        # SDMA_ADMIN: Only needs state_id (has access to ALL districts in their state)
        if privilege == UserRoles.SDMA_ADMIN:
            if not state_id:
                return Response(
                    {
                        "status_code": 400,
                        "error": "state_id is required for SDMA_ADMIN"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # district_id NOT required for SDMA_ADMIN - they have access to all districts in state
        
        # DDMA_NODAL_OFFICER: Requires BOTH state_id AND district_id
        elif privilege == UserRoles.DDMA_NODAL_OFFICER:
            if not state_id:
                return Response(
                    {
                        "status_code": 400,
                        "error": "state_id is required for DDMA_NODAL_OFFICER"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not district_id:
                return Response(
                    {
                        "status_code": 400,
                        "error": "district_id is required for DDMA_NODAL_OFFICER"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        # Other roles (SUPER_ADMIN, NDMA_ADMIN, etc.): No geographic restrictions

        # Convert privilege to user_role for serializer
        data = dict(request.data)
        data['user_role'] = privilege  # Map privilege → user_role
        
        # Create user
        serializer = UserCreateSerializer(data=data)
        if not serializer.is_valid():
            return Response(
                {
                    "status_code": 400,
                    "message": "User creation failed",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()
        
        # Now create the role assignment (UserRole)
        from models.role import Role, UserRole
        
        try:
            role = Role.objects.filter(name=privilege).first()
            if not role:
                return Response(
                    {
                        "status_code": 201,
                        "message": "User created but role not found in database",
                        "user": UserSerializer(user).data,
                        "warning": f"Role '{privilege}' not found. Run: python manage.py seed_rbac"
                    },
                    status=status.HTTP_201_CREATED,
                )
            
            # Create UserRole mapping
            user_role_obj, created = UserRole.objects.get_or_create(
                user=user,
                role=role,
                defaults={
                    'state': state_id,
                    'district': district_id,  # Will be None for SDMA_ADMIN (not needed)
                    'designation': request.data.get('designation'),
                    'is_active': True
                }
            )
            
            return Response(
                {
                    "status_code": 201,
                    "message": "User created with privilege successfully",
                    "user": UserSerializer(user).data,
                    "privilege": privilege,
                    "role_assigned": created,
                    "state_id": state_id,
                    "district_id": district_id,
                    "note": "SDMA_ADMIN: Has access to all districts in state" if privilege == UserRoles.SDMA_ADMIN else ""
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "status_code": 201,
                    "message": "User created but role assignment failed",
                    "user": UserSerializer(user).data,
                    "error": str(e)
                },
                status=status.HTTP_201_CREATED,
            )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response(
                {
                    "status_code": 400,
                    "message": "Validation failed",
                    "error": "old_password and new_password are required"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(old_password):
            return Response(
                {
                    "status_code": 400,
                    "message": "Password change failed",
                    "error": "Old password is incorrect"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        return Response(
            {
                "status_code": 200,
                "message": "Password changed successfully"
            },
            status=status.HTTP_200_OK,
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving users.
    Provides list and retrieve operations only (no create/update/delete).
    
    Permissions:
    - SUPER_ADMIN: Can see all users
    - NDMA_ADMIN: Can see users in their geography
    - Others: Can see only themselves
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_role', 'is_active', 'state_id']
    search_fields = ['email_address', 'name', 'mobile']
    ordering_fields = ['created_at', 'name', 'email_address']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter users based on current user's role and permissions
        """
        user = self.request.user
        queryset = User.objects.all()
        
        # SUPER_ADMIN, NDMA_ADMIN, TECHNICAL_ADMIN: see all users
        if user.user_role in UserRoles.ADMIN_ROLES:
            return queryset
        
        # SDMA_ADMIN: see users in their state only
        if user.user_role == UserRoles.SDMA_ADMIN and user.state_id:
            return queryset.filter(state_id=user.state_id)
        
        # DDMA_NODAL_OFFICER: see users in their district only
        if user.user_role == UserRoles.DDMA_NODAL_OFFICER and user.district_id:
            return queryset.filter(district_id=user.district_id)
        
        # All others: see only themselves
        return queryset.filter(id=user.id)
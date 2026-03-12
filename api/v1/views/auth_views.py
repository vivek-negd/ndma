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

        # ✅ Check geographic requirements based on privilege role
        state_id = request.data.get('state_id')
        district_id = request.data.get('district_id')
        
        # SUPER_ADMIN/NDMA_ADMIN: No geographic restrictions needed
        if privilege in [UserRoles.SUPER_ADMIN, UserRoles.NDMA_ADMIN]:
            # Geographic fields not needed - remove them
            pass
        
        # SDMA_ADMIN: Only needs state_id (district_id optional, will be ignored)
        elif privilege == UserRoles.SDMA_ADMIN:
            if not state_id:
                return Response(
                    {
                        "status_code": 400,
                        "error": "state_id is required for SDMA_ADMIN"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # district_id is OPTIONAL for SDMA_ADMIN - they have access to ALL districts in state
            # Even if provided, it will be ignored/set to None
        
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

        # Convert privilege to user_role for serializer
        data = dict(request.data)
        data['user_role'] = privilege  # Map privilege → user_role
        
        # ✅ Handle district_id based on role
        # For SDMA_ADMIN: Always set district_id to None (they manage all districts in state)
        if privilege == UserRoles.SDMA_ADMIN:
            data['district_id'] = None  # Force to None - they don't need it
        
        # For SUPER_ADMIN and NDMA_ADMIN: Remove district_id entirely
        if privilege in [UserRoles.SUPER_ADMIN, UserRoles.NDMA_ADMIN]:
            data.pop('district_id', None)
        
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

        # Wrap entire operation in try-except to catch IntegrityError
        from django.db import IntegrityError
        from models.role import Role, UserRole
        
        try:
            user = serializer.save()
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
            
            # ✅ Optional: Auto-revoke old privileges if admin requested
            auto_revoke_previous = request.data.get('auto_revoke_previous', False)
            revoked_users = []
            
            if auto_revoke_previous:
                # Find and revoke old users with same role in same geography
                old_users_to_revoke = []
                
                if privilege == UserRoles.SDMA_ADMIN:
                    old_users = User.objects.filter(
                        user_role=UserRoles.SDMA_ADMIN,
                        state_id=user.state_id
                    ).exclude(id=user.id)
                    old_users_to_revoke.extend(list(old_users))
                
                elif privilege == UserRoles.DDMA_NODAL_OFFICER:
                    old_users = User.objects.filter(
                        user_role=UserRoles.DDMA_NODAL_OFFICER,
                        state_id=user.state_id,
                        district_id=user.district_id
                    ).exclude(id=user.id)
                    old_users_to_revoke.extend(list(old_users))
                
                elif privilege == UserRoles.YOUTH_ORG_ADMIN:
                    old_users = User.objects.filter(
                        user_role=UserRoles.YOUTH_ORG_ADMIN,
                        state_id=user.state_id,
                        district_id=user.district_id
                    ).exclude(id=user.id)
                    old_users_to_revoke.extend(list(old_users))
                
                elif privilege == UserRoles.TRAINING_INSTITUTE:
                    old_users = User.objects.filter(
                        user_role=UserRoles.TRAINING_INSTITUTE,
                        state_id=user.state_id
                    ).exclude(id=user.id)
                    old_users_to_revoke.extend(list(old_users))
                
                # Revoke old users if found
                if old_users_to_revoke:
                    for old_user in old_users_to_revoke:
                        old_user.is_active = False
                        old_user.save()
                        UserRole.objects.filter(user=old_user).delete()
                        revoked_users.append({
                            "id": old_user.id,
                            "email": old_user.email_address,
                            "previous_role": privilege,
                            "status": "revoked"
                        })
            
            # Build response
            response_data = {
                "status_code": 201,
                "message": "User created with privilege successfully",
                "user": UserSerializer(user).data,
                "privilege": privilege,
                "role_assigned": created,
                "state_id": state_id,
                "district_id": district_id,
                "note": "SDMA_ADMIN: Has access to all districts in state" if privilege == UserRoles.SDMA_ADMIN else ""
            }
            
            # Add revocation info if applicable
            if auto_revoke_previous:
                response_data["auto_revoke_previous"] = True
                response_data["revoked_users"] = revoked_users
                response_data["revoked_count"] = len(revoked_users)
                if revoked_users:
                    response_data["message"] = f"User created AND {len(revoked_users)} old user(s) revoked"
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except IntegrityError as ie:
            # Handle database constraint violations
            error_message = str(ie)
            if "email_address" in error_message or "Duplicate entry" in error_message:
                return Response(
                    {
                        "status_code": 400,
                        "error": "Email address already exists. Please use a different email.",
                        "detail": error_message
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif "state_id" in error_message or "district_id" in error_message:
                return Response(
                    {
                        "status_code": 400,
                        "error": "Invalid foreign key reference for state or district.",
                        "detail": error_message
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                return Response(
                    {
                        "status_code": 400,
                        "error": "Database constraint violation occurred",
                        "detail": error_message
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        except Exception as e:
            return Response(
                {
                    "status_code": 500,
                    "message": "User creation failed with unexpected error",
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def revoke_old_user_privileges(self, request):
        """
        Revoke old user's privileges when new admin takes over
        
        Use Case:
        - New SDMA comes, revoke old SDMA's permissions
        - New DDMA comes, revoke old DDMA's permissions
        - New Youth Org Admin comes, revoke old ones
        
        Request body:
        {
            "new_user_id": 154,  # ID of new admin taking over
            "revoke_previous": true
        }
        
        Or by email:
        {
            "new_user_email": "new.admin@state.gov.in",
            "revoke_previous": true
        }
        """
        # Check permission - only SUPER_ADMIN, NDMA_ADMIN, SDMA_ADMIN can do this
        user_role = getattr(request.user, "user_role", None)
        allowed_roles = [UserRoles.SUPER_ADMIN, UserRoles.NDMA_ADMIN, UserRoles.SDMA_ADMIN]
        
        if user_role not in allowed_roles:
            return Response(
                {
                    "status_code": 403,
                    "error": "Only SUPER_ADMIN, NDMA_ADMIN, or SDMA_ADMIN can revoke privileges"
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get the new admin user
        new_user_id = request.data.get('new_user_id')
        new_user_email = request.data.get('new_user_email')
        revoke_previous = request.data.get('revoke_previous', False)

        if not new_user_id and not new_user_email:
            return Response(
                {
                    "status_code": 400,
                    "error": "Either new_user_id or new_user_email is required"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Find new user
            if new_user_id:
                new_user = User.objects.get(id=new_user_id)
            else:
                new_user = User.objects.get(email_address=new_user_email)
        except User.DoesNotExist:
            return Response(
                {
                    "status_code": 404,
                    "error": "New user not found"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        new_user_role = getattr(new_user, 'user_role', None)

        # Find old users to revoke
        old_users_to_revoke = []

        # 1️⃣ SDMA_ADMIN: Revoke other SDMA_ADMIN in same state
        if new_user_role == UserRoles.SDMA_ADMIN:
            old_users = User.objects.filter(
                user_role=UserRoles.SDMA_ADMIN,
                state_id=new_user.state_id
            ).exclude(id=new_user.id)
            old_users_to_revoke.extend(list(old_users))

        # 2️⃣ DDMA_NODAL_OFFICER: Revoke other DDMA in same district+state
        elif new_user_role == UserRoles.DDMA_NODAL_OFFICER:
            old_users = User.objects.filter(
                user_role=UserRoles.DDMA_NODAL_OFFICER,
                state_id=new_user.state_id,
                district_id=new_user.district_id
            ).exclude(id=new_user.id)
            old_users_to_revoke.extend(list(old_users))

        # 3️⃣ YOUTH_ORG_ADMIN: Revoke other admins for same organization
        elif new_user_role == UserRoles.YOUTH_ORG_ADMIN:
            from models.organization import Organization
            # Find new user's organization (if set)
            try:
                org = Organization.objects.get(
                    state_id=new_user.state_id,
                    district_id=new_user.district_id
                )
                old_admins = User.objects.filter(
                    user_role=UserRoles.YOUTH_ORG_ADMIN,
                    state_id=new_user.state_id,
                    district_id=new_user.district_id
                ).exclude(id=new_user.id)
                old_users_to_revoke.extend(list(old_admins))
            except Organization.DoesNotExist:
                pass

        # 4️⃣ TRAINING_INSTITUTE: Revoke other institute admins in same state
        elif new_user_role == UserRoles.TRAINING_INSTITUTE:
            old_users = User.objects.filter(
                user_role=UserRoles.TRAINING_INSTITUTE,
                state_id=new_user.state_id
            ).exclude(id=new_user.id)
            old_users_to_revoke.extend(list(old_users))

        # If no old users found
        if not revoke_previous or not old_users_to_revoke:
            return Response(
                {
                    "status_code": 200,
                    "message": "No old users found to revoke or revoke_previous not enabled",
                    "old_users_found": len(old_users_to_revoke),
                    "new_user": {
                        "id": new_user.id,
                        "email": new_user.email_address,
                        "role": new_user_role,
                        "state_id": new_user.state_id,
                        "district_id": new_user.district_id
                    }
                },
                status=status.HTTP_200_OK,
            )

        # Revoke old users' privileges
        revoked_count = 0
        revoked_users = []

        try:
            with transaction.atomic():
                from models.role import UserRole
                
                for old_user in old_users_to_revoke:
                    # Deactivate user
                    old_user.is_active = False
                    old_user.save()
                    
                    # Remove role assignments
                    UserRole.objects.filter(user=old_user).delete()
                    
                    revoked_count += 1
                    revoked_users.append({
                        "id": old_user.id,
                        "email": old_user.email_address,
                        "previous_role": old_user_role,
                        "revoked_at": "now"
                    })

                return Response(
                    {
                        "status_code": 200,
                        "message": f"Successfully revoked {revoked_count} old user(s)",
                        "new_admin": {
                            "id": new_user.id,
                            "email": new_user.email_address,
                            "role": new_user_role,
                            "state_id": new_user.state_id,
                            "district_id": new_user.district_id
                        },
                        "revoked_users": revoked_users,
                        "revoked_count": revoked_count,
                        "note": "Old user(s) deactivated and role assignments removed"
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            return Response(
                {
                    "status_code": 500,
                    "error": "Failed to revoke privileges",
                    "detail": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from api.v1.serializers.auth_serializers import (
    UserCreateSerializer,
    UserLoginSerializer,
    UserSerializer,
)

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
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def create_user(self, request):
        user_role = getattr(request.user, "user_role", None)
        if user_role not in ["SUPER_ADMIN", "NDMA_ADMIN", "TECHNICAL_ADMIN"]:
            return Response(
                {"error": "Only SUPER_ADMIN/NDMA_ADMIN/TECHNICAL_ADMIN can create users"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User created successfully",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def profile(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response(
                {"error": "old_password and new_password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(old_password):
            return Response(
                {"error": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        return Response(
            {"message": "Password changed successfully"},
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
    filterset_fields = ['user_role', 'is_active', 'state_code']
    search_fields = ['email', 'name', 'mobile']
    ordering_fields = ['created_at', 'name', 'email']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter users based on current user's role and permissions
        """
        user = self.request.user
        queryset = User.objects.all()
        
        # SUPER_ADMIN, NDMA_ADMIN, TECHNICAL_ADMIN: see all users
        if user.user_role in ['SUPER_ADMIN', 'NDMA_ADMIN', 'TECHNICAL_ADMIN']:
            return queryset
        
        # SDMA_ADMIN: see users in their state only
        if user.user_role == 'SDMA_ADMIN' and user.state_code:
            return queryset.filter(state_code=user.state_code)
        
        # DDMA_NODAL_OFFICER: see users in their district only
        if user.user_role == 'DDMA_NODAL_OFFICER' and user.district_code:
            return queryset.filter(district_code=user.district_code)
        
        # All others: see only themselves
        return queryset.filter(id=user.id)
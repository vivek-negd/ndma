from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from models.training import TrainingSchedule
from api.v1.serializers.training_serializers import TrainingScheduleSerializer
from core.constants import UserRoles, ErrorMessages


class TrainingScheduleViewSet(viewsets.ModelViewSet):
    queryset = TrainingSchedule.objects.all().order_by('-created_at')
    serializer_class = TrainingScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter training schedules based on user role and state/district scope.
        
        - SUPER_ADMIN: All trainings
        - NDMA_ADMIN: All trainings
        - SDMA_ADMIN: Only trainings in their assigned state
        - DDMA_NODAL_OFFICER: Only trainings in their assigned district (AND state validation)
        - Others: Only trainings in their state (if assigned)
        """
        user = self.request.user
        queryset = TrainingSchedule.objects.all().order_by('-created_at')
        
        # SUPER_ADMIN and NDMA_ADMIN can see all trainings
        if getattr(user, 'user_role', None) in UserRoles.ADMIN_ROLES:
            return queryset
        
        # SDMA_ADMIN: Only trainings in their state
        if getattr(user, 'user_role', None) == UserRoles.SDMA_ADMIN:
            if getattr(user, 'state_id', None):
                return queryset.filter(state_id=user.state_id)
            return TrainingSchedule.objects.none()  # No state assigned, return empty
        
        # DDMA_NODAL_OFFICER: Only trainings in their district AND state
        if getattr(user, 'user_role', None) == UserRoles.DDMA_NODAL_OFFICER:
            user_district = getattr(user, 'district_id', None)
            user_state = getattr(user, 'state_id', None)
            
            if user_district and user_state:
                # Filter by BOTH district AND state to avoid data inconsistency issues
                return queryset.filter(district_id=user_district, state_id=user_state)
            return TrainingSchedule.objects.none()  # No district/state assigned, return empty
        
        # Other roles: Trainings in their state (if assigned)
        if getattr(user, 'state_id', None):
            return queryset.filter(state_id=user.state_id)
        
        # Default: No access
        return TrainingSchedule.objects.none()

    def _check_create_permission(self, request):
        """Check if user has role permission to create/modify trainings"""
        allowed_roles = [
            UserRoles.SUPER_ADMIN,
            UserRoles.NDMA_ADMIN,
            UserRoles.SDMA_ADMIN,
            UserRoles.DDMA_NODAL_OFFICER,
            UserRoles.TRAINING_INSTITUTE,
            UserRoles.YOUTH_ORG_ADMIN,
        ]
        if getattr(request.user, 'user_role', None) not in allowed_roles:
            raise PermissionDenied(ErrorMessages.INSUFFICIENT_ROLE_CREATE_TRAINING)

    def _check_geographic_scope(self, request, action='create'):
        """
        Validate that user can only create/update trainings in their geographic scope.
        
        SUPER_ADMIN/NDMA_ADMIN: Can create in any state/district
        SDMA_ADMIN: Can only create in their assigned state
        DDMA_NODAL_OFFICER: Can only create in their assigned district AND state
        """
        user = request.user
        user_role = getattr(user, 'user_role', None)
        
        # SUPER_ADMIN/NDMA_ADMIN: No restriction
        if user_role in UserRoles.ADMIN_ROLES:
            return True
        
        # Get state_id and district_id from request data
        request_state_id = request.data.get('state')
        request_district_id = request.data.get('district')
        
        # Validate required fields
        if not request_state_id:
            raise PermissionDenied(ErrorMessages.STATE_REQUIRED)
        
        try:
            request_state_id = int(request_state_id)
        except (ValueError, TypeError):
            raise PermissionDenied(ErrorMessages.INVALID_STATE)
        
        # SDMA_ADMIN: Must create in their state only
        if user_role == UserRoles.SDMA_ADMIN:
            user_state_id = getattr(user, 'state_id', None)
            if not user_state_id:
                raise PermissionDenied(ErrorMessages.NO_STATE_ASSIGNED)
            
            # Ensure user_state_id is an integer (it could be a State object)
            if hasattr(user_state_id, 'id'):
                user_state_id = user_state_id.id
            else:
                user_state_id = int(user_state_id)
            
            # Check if requested state matches user's state
            if request_state_id != user_state_id:
                raise PermissionDenied(ErrorMessages.STATE_MISMATCH)
            return True
        
        # DDMA_NODAL_OFFICER: Must create in their district AND state
        if user_role == UserRoles.DDMA_NODAL_OFFICER:
            user_state_id = getattr(user, 'state_id', None)
            user_district_id = getattr(user, 'district_id', None)
            
            if not user_state_id or not user_district_id:
                raise PermissionDenied(ErrorMessages.NO_DISTRICT_ASSIGNED)
            
            # Ensure IDs are integers (they could be model objects)
            if hasattr(user_state_id, 'id'):
                user_state_id = user_state_id.id
            else:
                user_state_id = int(user_state_id)
            
            if hasattr(user_district_id, 'id'):
                user_district_id = user_district_id.id
            else:
                user_district_id = int(user_district_id)
            
            # Validate district field
            if not request_district_id:
                raise PermissionDenied(ErrorMessages.DISTRICT_REQUIRED)
            
            try:
                request_district_id = int(request_district_id)
            except (ValueError, TypeError):
                raise PermissionDenied(ErrorMessages.INVALID_DISTRICT)
            
            # Check if requested state AND district match user's scope
            if request_state_id != user_state_id:
                raise PermissionDenied(ErrorMessages.STATE_MISMATCH)
            
            if request_district_id != user_district_id:
                raise PermissionDenied(ErrorMessages.DISTRICT_MISMATCH)
            return True
        
        # Other roles: Check if they have geographic scope restrictions
        return True

    def create(self, request, *args, **kwargs):
        """Create training schedule with geographic scope validation"""
        self._check_create_permission(request)
        self._check_geographic_scope(request, 'create')  # ← NEW: Validate geographic scope
        
        # set created_by automatically
        request.data['created_by'] = getattr(request.user, 'id', None)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update training schedule with geographic scope validation"""
        self._check_create_permission(request)
        self._check_geographic_scope(request, 'update')  # ← NEW: Validate geographic scope
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete training schedule with geographic scope validation"""
        self._check_create_permission(request)
        self._check_geographic_scope(request, 'delete')  # ← NEW: Validate geographic scope
        return super().destroy(request, *args, **kwargs)

from rest_framework import viewsets, status, permissions, views
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from models.organization import Organization
from models.organization_type import OrganizationType
from api.v1.serializers.organization_serializers import (
    OrganizationSerializer, OrganizationListSerializer
)
from api.v1.rbac import has_role_access, has_geographical_access
from core.constants import UserRoles, ErrorMessages


# Public API endpoint - Organization Types (no authentication required)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_organization_types(request):
    """
    Get all active organization types for dropdown.
    PUBLIC ENDPOINT - no authentication required.
    
    GET /api/v1/organizations/org-types/
    
    Response:
    {
        "status_code": 200,
        "message": "Organization types retrieved",
        "organization_types": [
            {"id": 1, "code": "NCC", "name": "National Cadet Corps", "description": "..."},
            {"id": 2, "code": "NSS", "name": "National Service Scheme", "description": "..."},
            {"id": 3, "code": "BSG", "name": "Bharat Scouts & Guides", "description": "..."},
            {"id": 4, "code": "NYKS", "name": "National Youth Korps Society", "description": "..."}
        ]
    }
    """
    org_types = OrganizationType.objects.filter(is_active=True).order_by('code').values(
        'id', 'code', 'name', 'description'
    )
    
    return Response(
        {
            "status_code": 200,
            "message": "Organization types retrieved",
            "organization_types": list(org_types)
        },
        status=status.HTTP_200_OK
    )


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organizations (NCC, NSS, BS&G, NYKS).
    
    Permissions:
    - SUPER_ADMIN, NDMA_ADMIN: Create/Edit/Delete orgs anywhere
    - SDMA_ADMIN: Create/Edit/Delete orgs in their state only
    - YOUTH_ORG_ADMIN: View their organization only
    - VOLUNTEER: View their organization only
    """
    
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['state', 'district', 'org_type', 'is_active']
    search_fields = ['name', 'contact_email']
    ordering_fields = ['name', 'org_type', 'created_at']
    ordering = ['org_type', 'name']
    
    def get_permissions(self):
        """Override permissions for specific actions"""
        if self.action == 'org_types':
            # org_types endpoint is public - no authentication required
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        """Use simplified serializer for list, full for detail/create"""
        if self.action == 'list':
            return OrganizationListSerializer
        return OrganizationSerializer
    
    def get_queryset(self):
        """Filter organizations based on user role and geography"""
        user = self.request.user
        queryset = Organization.objects.all()
        
        # SUPER_ADMIN, NDMA_ADMIN, TECHNICAL_ADMIN: see all
        if user.user_role in UserRoles.ADMIN_ROLES:
            return queryset
        
        # SDMA_ADMIN: see only their state
        if user.user_role == UserRoles.SDMA_ADMIN:
            if user.state_id:
                return queryset.filter(state_id=user.state_id)
            return queryset.none()
        
        # DDMA_NODAL_OFFICER: see only their district
        if user.user_role == UserRoles.DDMA_NODAL_OFFICER:
            if user.district_id:
                return queryset.filter(district_id=user.district_id)
            return queryset.none()
        
        # YOUTH_ORG_ADMIN: see only their organization
        if user.user_role == UserRoles.YOUTH_ORG_ADMIN:
            from models.role import UserRole
            user_role = UserRole.objects.filter(user=user).first()
            if user_role and user_role.organization:
                # UserRole.organization is stored as a free-text field (id or name).
                # Support both numeric id values and organization name lookups.
                try:
                    org_id = int(user_role.organization)
                    return queryset.filter(id=org_id)
                except Exception:
                    return queryset.filter(name__iexact=user_role.organization)
            return queryset.none()
        
        # VOLUNTEER: see their organization only
        if user.user_role == UserRoles.VOLUNTEER:
            # Get volunteer's organization
            from models.volunteer import Volunteer
            volunteer = Volunteer.objects.filter(
                mis_id=user.id  # Assuming user.id links to volunteer
            ).first()
            if volunteer and volunteer.organization:
                return queryset.filter(id=volunteer.organization.id)
            return queryset.none()
        
        # Default: no access
        return queryset.none()
    
    def check_create_permission(self, request):
        """Check if user can create organization"""
        user = request.user
        
        allowed_roles = [
            UserRoles.SUPER_ADMIN,
            UserRoles.NDMA_ADMIN,
            UserRoles.TECHNICAL_ADMIN,
            UserRoles.SDMA_ADMIN
        ]
        if user.user_role not in allowed_roles:
            raise PermissionDenied(ErrorMessages.INSUFFICIENT_ROLE_CREATE_ORG)
        
        # SDMA_ADMIN can only create in their state
        if user.user_role == UserRoles.SDMA_ADMIN:
            state_id = request.data.get('state')
            if not state_id:
                raise PermissionDenied(ErrorMessages.STATE_REQUIRED)
            
            if int(state_id) != user.state_id:
                raise PermissionDenied(ErrorMessages.STATE_MISMATCH)
    
    def create(self, request, *args, **kwargs):
        """Create new organization"""
        self.check_create_permission(request)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Update organization"""
        user = request.user
        instance = self.get_object()
        
        allowed_roles = [
            UserRoles.SUPER_ADMIN,
            UserRoles.NDMA_ADMIN,
            UserRoles.TECHNICAL_ADMIN,
            UserRoles.SDMA_ADMIN
        ]
        if user.user_role not in allowed_roles:
            raise PermissionDenied(ErrorMessages.INSUFFICIENT_ROLE)
        
        # SDMA_ADMIN can only edit orgs in their state
        if user.user_role == UserRoles.SDMA_ADMIN:
            if instance.state_id != user.state_id:
                raise PermissionDenied(ErrorMessages.STATE_MISMATCH)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete organization"""
        user = request.user
        instance = self.get_object()
        
        allowed_roles = [UserRoles.SUPER_ADMIN, UserRoles.NDMA_ADMIN, UserRoles.TECHNICAL_ADMIN]
        if user.user_role not in allowed_roles:
            raise PermissionDenied(ErrorMessages.INSUFFICIENT_ROLE)
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get organizations filtered by type (NCC, NSS, BSG, NYKS)"""
        org_type_code = request.query_params.get('type')
        if not org_type_code:
            return Response(
                {'status_code': 400, 'error': 'type parameter required (NCC, NSS, BSG, NYKS)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(org_type__code=org_type_code)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status_code': 200,
            'message': f'Organizations retrieved for type: {org_type_code}',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about organizations"""
        queryset = self.get_queryset()
        
        stats = {
            'total_organizations': queryset.count(),
            'by_type': {},
            'total_volunteers': 0,
            'by_state': {}
        }
        
        # Count by org type (from OrganizationType table)
        from django.db.models import Count
        org_type_counts = queryset.values('org_type__code', 'org_type__name').annotate(
            count=Count('id')
        )
        for item in org_type_counts:
            stats['by_type'][item['org_type__code']] = {
                'name': item['org_type__name'],
                'count': item['count']
            }
        
        # Count volunteers
        for org in queryset:
            stats['total_volunteers'] += org.volunteer_count
        
        # Count by state
        by_state = queryset.values('state__name').annotate(
            count=Count('id'),
            volunteers=Count('volunteers')
        )
        stats['by_state'] = list(by_state)
        
        return Response(stats)

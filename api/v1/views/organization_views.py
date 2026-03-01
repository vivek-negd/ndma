from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from models.organization import Organization
from api.v1.serializers.organization_serializers import (
    OrganizationSerializer, OrganizationListSerializer
)
from api.v1.rbac import has_role_access, has_geographical_access


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
        if user.user_role in ['SUPER_ADMIN', 'NDMA_ADMIN', 'TECHNICAL_ADMIN']:
            return queryset
        
        # SDMA_ADMIN: see only their state
        if user.user_role == 'SDMA_ADMIN':
            if user.state_code:
                from models.state import State
                state = State.objects.filter(lgd_code=user.state_code).first()
                if state:
                    return queryset.filter(state=state)
            return queryset.none()
        
        # DDMA_NODAL_OFFICER: see only their district
        if user.user_role == 'DDMA_NODAL_OFFICER':
            if user.district_code:
                from models.district import District
                district = District.objects.filter(lgd_code=user.district_code).first()
                if district:
                    return queryset.filter(district=district)
            return queryset.none()
        
        # YOUTH_ORG_ADMIN: see only their organization
        if user.user_role == 'YOUTH_ORG_ADMIN':
            from models.role import UserRole
            user_role = UserRole.objects.filter(user=user).first()
            if user_role and user_role.organization:
                return queryset.filter(id=user_role.organization.id)
            return queryset.none()
        
        # VOLUNTEER: see their organization only
        if user.user_role == 'VOLUNTEER':
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
        
        allowed_roles = ['SUPER_ADMIN', 'NDMA_ADMIN', 'TECHNICAL_ADMIN', 'SDMA_ADMIN']
        if user.user_role not in allowed_roles:
            raise PermissionDenied(
                f"Users with role {user.user_role} cannot create organizations"
            )
        
        # SDMA_ADMIN can only create in their state
        if user.user_role == 'SDMA_ADMIN':
            state_id = request.data.get('state')
            if not state_id:
                raise PermissionDenied("Must specify state")
            
            from models.state import State
            state = State.objects.filter(id=state_id).first()
            if not state or state.lgd_code != user.state_code:
                raise PermissionDenied(
                    f"SDMA_ADMIN can only create organizations in their state"
                )
    
    def create(self, request, *args, **kwargs):
        """Create new organization"""
        self.check_create_permission(request)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Update organization"""
        user = request.user
        instance = self.get_object()
        
        allowed_roles = ['SUPER_ADMIN', 'NDMA_ADMIN', 'TECHNICAL_ADMIN', 'SDMA_ADMIN']
        if user.user_role not in allowed_roles:
            raise PermissionDenied(
                f"Users with role {user.user_role} cannot edit organizations"
            )
        
        # SDMA_ADMIN can only edit orgs in their state
        if user.user_role == 'SDMA_ADMIN':
            if instance.state.lgd_code != user.state_code:
                raise PermissionDenied(
                    "SDMA_ADMIN can only edit organizations in their state"
                )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete organization"""
        user = request.user
        instance = self.get_object()
        
        allowed_roles = ['SUPER_ADMIN', 'NDMA_ADMIN', 'TECHNICAL_ADMIN']
        if user.user_role not in allowed_roles:
            raise PermissionDenied(
                f"Users with role {user.user_role} cannot delete organizations"
            )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get organizations filtered by type (NCC, NSS, BSG, NYKS)"""
        org_type = request.query_params.get('type')
        if not org_type:
            return Response(
                {'error': 'type parameter required (NCC, NSS, BSG, NYKS)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(org_type=org_type)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
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
        
        # Count by org type
        for org_type, _ in Organization.ORG_TYPE_CHOICES:
            count = queryset.filter(org_type=org_type).count()
            stats['by_type'][org_type] = count
        
        # Count volunteers
        for org in queryset:
            stats['total_volunteers'] += org.volunteer_count
        
        # Count by state
        from django.db.models import Count
        by_state = queryset.values('state__name').annotate(
            count=Count('id'),
            volunteers=Count('volunteers')
        )
        stats['by_state'] = list(by_state)
        
        return Response(stats)

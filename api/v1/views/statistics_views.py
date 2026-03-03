"""
API views for State, District, and Volunteer statistics
Provides endpoints for accessing geographical data and volunteer counts
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from models.state import State
from models.district import District
from api.v1.serializers.statistics_serializers import (
    StateSerializer,
    StateDetailSerializer,
    DistrictSerializer,
    VolunteerStatisticsSerializer
)
from services.volunteer_count_service import VolunteerCountService


class StateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for State model.
    
    Endpoints:
    - GET /api/v1/states/ - List all states with volunteer counts
    - GET /api/v1/states/{id}/ - Get state details with districts
    - GET /api/v1/states/statistics/overview/ - Get volunteer statistics
    """
    queryset = State.objects.prefetch_related('districts').all()
    serializer_class = StateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['name', 'volunteer_count', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return StateDetailSerializer
        return StateSerializer
    
    @action(detail=False, methods=['get'], url_path='statistics/overview')
    def statistics_overview(self, request):
        """
        Get comprehensive volunteer statistics across all states.
        
        Returns:
        ```json
        {
            "total_volunteers": 3789,
            "total_states_with_volunteers": 25,
            "total_districts_with_volunteers": 187,
            "top_states": [...],
            "top_districts": [...]
        }
        ```
        """
        stats = VolunteerCountService.get_volunteer_statistics()
        serializer = VolunteerStatisticsSerializer(stats)
        return Response(
            {"status": "success", "data": serializer.data, "message": "Volunteer statistics retrieved successfully"}
        )
    
    @action(detail=True, methods=['get'])
    def districts(self, request, pk=None):
        """
        Get all districts for a specific state with volunteer counts.
        
        Returns:
        ```json
        {
            "state": {...},
            "districts": [...]
        }
        ```
        """
        try:
            state = self.get_object()
            districts = state.districts.all()
            serializer = DistrictSerializer(districts, many=True)
            return Response(
                {
                    'status': 'success',
                    'data': {
                        'state': StateSerializer(state).data,
                        'districts': serializer.data,
                        'total_districts': len(serializer.data),
                        'total_volunteers_in_state': state.volunteer_count
                    },
                    'message': f"Districts for {state.name} retrieved successfully"
                }
            )
        except State.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'State not found', 'code': 'STATE_NOT_FOUND'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'], url_path='update-counts')
    def update_counts(self, request):
        """
        Manually trigger volunteer count update for all states and districts.
        Use this after bulk import operations if needed.
        
        Returns:
        ```json
        {
            "states_updated": 5,
            "districts_updated": 12,
            "total_updates": 17
        }
        ```
        """
        result = VolunteerCountService.bulk_update_volunteer_counts()
        return Response(
            {'status': 'success', 'data': result, 'message': 'Volunteer counts updated successfully'}
        )


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for District model.
    
    Endpoints:
    - GET /api/v1/districts/ - List all districts with volunteer counts
    - GET /api/v1/districts/{id}/ - Get district details
    - GET /api/v1/districts/by_state/{state_id}/ - Get districts by state
    """
    queryset = District.objects.select_related('state').all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'state_id']
    search_fields = ['name', 'state__name']
    ordering_fields = ['name', 'volunteer_count', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'], url_path='by_state/(?P<state_id>[0-9]+)')
    def by_state(self, request, state_id=None):
        """
        Get all districts for a specific state.
        
        Example: GET /api/v1/districts/by_state/4/
        """
        try:
            state = State.objects.get(id=state_id)
            districts = District.objects.filter(state=state).order_by('name')
            serializer = self.get_serializer(districts, many=True)
            return Response(
                {
                    'status': 'success',
                    'data': {
                        'state': StateSerializer(state).data,
                        'districts': serializer.data,
                        'total_districts': len(serializer.data)
                    },
                    'message': f"Districts for {state.name} retrieved successfully"
                }
            )
        except State.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'State not found', 'code': 'STATE_NOT_FOUND'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def top_performers(self, request):
        """
        Get top 5 districts by volunteer count globally.
        """
        top_districts = District.objects.filter(
            volunteer_count__gt=0
        ).order_by('-volunteer_count')[:5]
        
        serializer = self.get_serializer(top_districts, many=True)
        return Response(
            {'status': 'success', 'data': serializer.data, 'message': 'Top performing districts retrieved successfully'}
        )

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from models.training import TrainingSchedule
from api.v1.serializers.training_serializers import TrainingScheduleSerializer


class TrainingScheduleViewSet(viewsets.ModelViewSet):
    queryset = TrainingSchedule.objects.all().order_by('-created_at')
    serializer_class = TrainingScheduleSerializer
    permission_classes = [IsAuthenticated]

    def _check_create_permission(self, request):
        allowed_roles = ['SUPER_ADMIN', 'NDMA_ADMIN', 'SDMA_ADMIN', 'DDMA_NODAL_OFFICER', 'TRAINING_INSTITUTE', 'YOUTH_ORG_ADMIN']
        if getattr(request.user, 'user_role', None) not in allowed_roles:
            raise PermissionDenied('Insufficient role to create or modify training schedules')

    def create(self, request, *args, **kwargs):
        self._check_create_permission(request)
        # set created_by automatically
        request.data['created_by'] = getattr(request.user, 'id', None)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._check_create_permission(request)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self._check_create_permission(request)
        return super().destroy(request, *args, **kwargs)

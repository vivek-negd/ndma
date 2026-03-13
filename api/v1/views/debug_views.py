from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from models.role import UserRole
from models.organization import Organization
from models.volunteer import Volunteer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resolve_user_scope(request):
    """Return how the backend resolves the current user's org/state/district scope.

    Useful for frontend debugging when a YOUTH_ORG_ADMIN cannot see expected volunteers.
    """
    User = get_user_model()
    try:
        db_user = User.objects.select_related('state_id', 'district_id').get(id=request.user.id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    user_role = getattr(db_user, 'user_role', None)
    state_id = db_user.state_id.id if db_user.state_id else None
    state_name = db_user.state_id.name if db_user.state_id else None
    district_id = db_user.district_id.id if db_user.district_id else None
    district_name = db_user.district_id.name if db_user.district_id else None

    user_role_obj = UserRole.objects.filter(user=db_user).first()

    resolved_orgs = []
    volunteers_count = 0
    org_lookup = None

    if user_role_obj and user_role_obj.organization:
        org_lookup = user_role_obj.organization
        # support numeric id or organization name
        try:
            org_id = int(org_lookup)
            org_qs = Organization.objects.filter(id=org_id)
        except Exception:
            org_qs = Organization.objects.filter(name__iexact=str(org_lookup))

        resolved_orgs = list(org_qs.values('id', 'name', 'state_id', 'district_id'))
        volunteers_count = Volunteer.objects.filter(organization__in=org_qs, deleted_at__isnull=True).count()
    else:
        # fallback: use state+distrct if available
        if state_id and district_id:
            org_qs = Organization.objects.filter(state_id=state_id, district_id=district_id)
            resolved_orgs = list(org_qs.values('id', 'name', 'state_id', 'district_id'))
            volunteers_count = Volunteer.objects.filter(state_id=state_id, district_id=district_id, deleted_at__isnull=True).count()

    return Response({
        'user_id': db_user.id,
        'user_role': user_role,
        'state_id': state_id,
        'state_name': state_name,
        'district_id': district_id,
        'district_name': district_name,
        'user_role_object': {
            'organization_field': user_role_obj.organization if user_role_obj else None
        } if user_role_obj else None,
        'resolved_organizations': resolved_orgs,
        'visible_volunteers_count': volunteers_count,
    })

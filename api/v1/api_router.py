from rest_framework.routers import DefaultRouter
from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

 
from api.v1.views.auth_views import LoginView, UserViewSet
 
from api.v1.views.organization_views import OrganizationViewSet, get_organization_types

# ============================================================================
# RBAC VIEWS
# ============================================================================
from api.v1.views.rbac_views import (
    PermissionViewSet,
    RoleViewSet,
    UserRoleViewSet,
    RolePermissionAuditViewSet
)

# ============================================================================
# TRAINING VIEWS
# ============================================================================
from api.v1.views.training_views import TrainingScheduleViewSet
from api.v1.views.training_media_views import TrainingSessionMediaViewSet

# ============================================================================
# HEALTH CHECK & MONITORING VIEWS
# ============================================================================
from api.v1.views.health_views import HealthCheckViewSet, MetricsViewSet

# ============================================================================
# STATISTICS & GEOGRAPHICAL DATA VIEWS
# ============================================================================
from api.v1.views.statistics_views import StateViewSet, DistrictViewSet

# ============================================================================
# MODELS
# ============================================================================
from models.district import District
from models.state import State
from api.v1.serializers.statistics_serializers import DistrictSerializer, StateSerializer

# ============================================================================
# VOLUNTEER VIEWS
# ============================================================================
# Volunteer endpoints are handled via routes.py for backward compatibility
# In future, convert to ViewSet-based endpoints


# ============================================================================
# ROUTER CONFIGURATION
# ============================================================================

router = DefaultRouter()

# ────────────────────────────────────────────────────────────────────────
# AUTH ENDPOINTS
# ────────────────────────────────────────────────────────────────────────
router.register(
    r'auth',
    LoginView,
    basename='auth'
)
router.register(
    r'users',
    UserViewSet,
    basename='user'
)

# ────────────────────────────────────────────────────────────────────────
# ORGANIZATION ENDPOINTS
# ────────────────────────────────────────────────────────────────────────
router.register(
    r'organizations',
    OrganizationViewSet,
    basename='organization'
)

# ────────────────────────────────────────────────────────────────────────
# RBAC ENDPOINTS
# ────────────────────────────────────────────────────────────────────────
router.register(
    r'rbac/permissions',
    PermissionViewSet,
    basename='permission'
)
router.register(
    r'rbac/roles',
    RoleViewSet,
    basename='role'
)
router.register(
    r'rbac/user-roles',
    UserRoleViewSet,
    basename='user-role'
)
router.register(
    r'rbac/audit/role-permissions',
    RolePermissionAuditViewSet,
    basename='role-permission-audit'
)

# ────────────────────────────────────────────────────────────────────────
# TRAINING ENDPOINTS
# ────────────────────────────────────────────────────────────────────────
router.register(
    r'training-schedules',
    TrainingScheduleViewSet,
    basename='training-schedule'
)
router.register(
    r'training-session-media',
    TrainingSessionMediaViewSet,
    basename='training-session-media'
)

# ────────────────────────────────────────────────────────────────────────
# VOLUNTEER ENDPOINTS
# ────────────────────────────────────────────────────────────────────────
# Note: Volunteer endpoints are handled via separate routes.py
# Include in main urls.py: path('volunteer/', include(volunteer_routes))

# ────────────────────────────────────────────────────────────────────────
# HEALTH CHECK & MONITORING ENDPOINTS
# ────────────────────────────────────────────────────────────────────────
router.register(
    r'health',
    HealthCheckViewSet,
    basename='health'
)
router.register(
    r'metrics',
    MetricsViewSet,
    basename='metrics'
)

# ────────────────────────────────────────────────────────────────────────
# STATISTICS & GEOGRAPHICAL DATA ENDPOINTS
# ────────────────────────────────────────────────────────────────────────
router.register(
    r'states',
    StateViewSet,
    basename='state'
)
router.register(
    r'districts',
    DistrictViewSet,
    basename='district'
)

# ============================================================================
# URL PATTERNS
# ============================================================================

# Custom endpoint for getting districts by state_id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_districts_by_state_id(request, state_id):
    """
    Get all districts for a specific state by state ID.
    
    Endpoint: GET /api/v1/districts/{state_id}/
    
    Returns: List of all districts for the state with volunteer counts
    """
    try:
        state = State.objects.get(id=state_id)
        districts = District.objects.filter(state=state).order_by('name')
        serializer = DistrictSerializer(districts, many=True)
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

urlpatterns = [
    # PUBLIC ENDPOINTS (no authentication required) - MUST BE BEFORE router.urls
    # GET /api/v1/organizations/org-types/
    path('organizations/org-types/', get_organization_types, name='organization-types'),
    # CUSTOM DISTRICTS BY STATE ENDPOINT - MUST BE BEFORE router.urls
    # GET /api/v1/districts/{state_id}/
    re_path(r'^districts/(?P<state_id>[0-9]+)/$', get_districts_by_state_id, name='districts-by-state-id'),
] + router.urls + [
    # JWT Token Refresh
    # POST /api/v1/auth/token/refresh/
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


# ============================================================================
# API ENDPOINT REGISTRY (For Documentation)
# ============================================================================

API_REGISTRY = {
    "AUTH": {
        "LOGIN": {
            "endpoint": "POST /auth/login/",
            "description": "Get JWT token",
            "auth_required": False,
            "roles": ["All"]
        },
        "CREATE_USER": {
            "endpoint": "POST /auth/create_user/",
            "description": "Create new user (Admin only)",
            "auth_required": True,
            "roles": ["SUPER_ADMIN", "NDMA_ADMIN", "TECHNICAL_ADMIN"]
        },
        "PROFILE": {
            "endpoint": "GET /auth/profile/",
            "description": "Get current user profile",
            "auth_required": True,
            "roles": ["All authenticated"]
        },
        "LOGOUT": {
            "endpoint": "POST /auth/logout/",
            "description": "Logout user",
            "auth_required": True,
            "roles": ["All authenticated"]
        },
        "CHANGE_PASSWORD": {
            "endpoint": "POST /auth/change_password/",
            "description": "Change password",
            "auth_required": True,
            "roles": ["All authenticated"]
        },
        "TOKEN_REFRESH": {
            "endpoint": "POST /auth/token/refresh/",
            "description": "Refresh access token",
            "auth_required": False,
            "roles": ["All"]
        },
    },
    "USERS": {
        "LIST": {
            "endpoint": "GET /users/",
            "description": "List all users (filtered)",
            "auth_required": True,
            "roles": ["All authenticated"]
        },
        "RETRIEVE": {
            "endpoint": "GET /users/{id}/",
            "description": "Get user details",
            "auth_required": True,
            "roles": ["All authenticated"]
        },
    },
    "ORGANIZATIONS": {
        "LIST": {
            "endpoint": "GET /organizations/",
            "description": "List organizations",
            "auth_required": True,
            "roles": ["All authenticated"]
        },
        "ORG_TYPES": {
            "endpoint": "GET /organizations/org-types/",
            "description": "Get 4 organization types for dropdown (NCC, NSS, BSG, NYKS)",
            "auth_required": False,
            "roles": ["All (public, no auth required)"]
        },
        "CREATE": {
            "endpoint": "POST /organizations/",
            "description": "Create organization",
            "auth_required": True,
            "roles": ["SUPER_ADMIN", "NDMA_ADMIN", "TECHNICAL_ADMIN", "SDMA_ADMIN"]
        },
        "RETRIEVE": {
            "endpoint": "GET /organizations/{id}/",
            "description": "Get organization details",
            "auth_required": True,
            "roles": ["All authenticated"]
        },
        "UPDATE": {
            "endpoint": "PUT /organizations/{id}/",
            "description": "Update organization (full)",
            "auth_required": True,
            "roles": ["SUPER_ADMIN", "NDMA_ADMIN", "TECHNICAL_ADMIN", "SDMA_ADMIN"]
        },
        "PARTIAL_UPDATE": {
            "endpoint": "PATCH /organizations/{id}/",
            "description": "Update organization (partial)",
            "auth_required": True,
            "roles": ["SUPER_ADMIN", "NDMA_ADMIN", "TECHNICAL_ADMIN", "SDMA_ADMIN"]
        },
        "DELETE": {
            "endpoint": "DELETE /organizations/{id}/",
            "description": "Delete organization",
            "auth_required": True,
            "roles": ["SUPER_ADMIN", "NDMA_ADMIN", "TECHNICAL_ADMIN"]
        },
    },
    "RBAC": {
        "PERMISSIONS_LIST": {
            "endpoint": "GET /rbac/permissions/",
            "description": "List all permissions",
            "auth_required": True,
            "roles": ["SUPER_ADMIN"]
        },
        "PERMISSIONS_DETAIL": {
            "endpoint": "GET /rbac/permissions/{id}/",
            "description": "Get permission details",
            "auth_required": True,
            "roles": ["SUPER_ADMIN"]
        },
        "ROLES_LIST": {
            "endpoint": "GET /rbac/roles/",
            "description": "List all roles",
            "auth_required": True,
            "roles": ["SUPER_ADMIN"]
        },
        "ROLES_CREATE": {
            "endpoint": "POST /rbac/roles/",
            "description": "Create role",
            "auth_required": True,
            "roles": ["SUPER_ADMIN"]
        },
        "ROLES_DETAIL": {
            "endpoint": "GET /rbac/roles/{id}/",
            "description": "Get role details",
            "auth_required": True,
            "roles": ["SUPER_ADMIN"]
        },
        "ASSIGN_PERMISSION": {
            "endpoint": "POST /rbac/roles/{id}/assign_permission/",
            "description": "Assign permission to role",
            "auth_required": True,
            "roles": ["SUPER_ADMIN"]
        },
        "REVOKE_PERMISSION": {
            "endpoint": "POST /rbac/roles/{id}/revoke_permission/",
            "description": "Revoke permission from role",
            "auth_required": True,
            "roles": ["SUPER_ADMIN"]
        },
        "USER_ROLES_LIST": {
            "endpoint": "GET /rbac/user-roles/",
            "description": "List user roles",
            "auth_required": True,
            "roles": ["SUPER_ADMIN"]
        },
        "USER_ROLES_CREATE": {
            "endpoint": "POST /rbac/user-roles/",
            "description": "Assign role to user",
            "auth_required": True,
            "roles": ["SUPER_ADMIN"]
        },
        "AUDIT_LOG": {
            "endpoint": "GET /rbac/audit/role-permissions/",
            "description": "Permission audit log",
            "auth_required": True,
            "roles": ["SUPER_ADMIN"]
        },
    },
    "TRAINING": {
        "LIST": {
            "endpoint": "GET /training-schedules/",
            "description": "List training schedules",
            "auth_required": True,
            "roles": ["All authenticated"]
        },
        "CREATE": {
            "endpoint": "POST /training-schedules/",
            "description": "Create training schedule",
            "auth_required": True,
            "roles": ["TRAINER", "SUPER_ADMIN"]
        },
        "RETRIEVE": {
            "endpoint": "GET /training-schedules/{id}/",
            "description": "Get training details",
            "auth_required": True,
            "roles": ["All authenticated"]
        },
        "UPDATE": {
            "endpoint": "PUT /training-schedules/{id}/",
            "description": "Update training (full)",
            "auth_required": True,
            "roles": ["TRAINER", "SUPER_ADMIN"]
        },
        "PARTIAL_UPDATE": {
            "endpoint": "PATCH /training-schedules/{id}/",
            "description": "Update training (partial)",
            "auth_required": True,
            "roles": ["TRAINER", "SUPER_ADMIN"]
        },
        "DELETE": {
            "endpoint": "DELETE /training-schedules/{id}/",
            "description": "Delete training",
            "auth_required": True,
            "roles": ["TRAINER", "SUPER_ADMIN"]
        },
    },
    "VOLUNTEERS": {
        "LIST": {
            "endpoint": "GET /volunteers/",
            "description": "List volunteers",
            "auth_required": True,
            "roles": ["All authenticated"]
        },
        "CREATE": {
            "endpoint": "POST /volunteers/create/",
            "description": "Create single volunteer",
            "auth_required": True,
            "roles": ["SUPER_ADMIN", "NDMA_ADMIN", "SDMA_ADMIN", "DDMA_NODAL_OFFICER", "YOUTH_ORG_ADMIN"]
        },
        "RETRIEVE": {
            "endpoint": "GET /volunteers/{id}/",
            "description": "Get volunteer details",
            "auth_required": True,
            "roles": ["All authenticated"]
        },
        "BULK_UPLOAD": {
            "endpoint": "POST /volunteers/bulk-upload/",
            "description": "Bulk upload volunteers",
            "auth_required": True,
            "roles": ["SUPER_ADMIN", "NDMA_ADMIN", "SDMA_ADMIN", "DDMA_NODAL_OFFICER", "YOUTH_ORG_ADMIN"]
        },
        "COVERAGE": {
            "endpoint": "GET /volunteers/coverage/",
            "description": "Get coverage statistics",
            "auth_required": True,
            "roles": ["All authenticated"]
        },
    },
    "HEALTH_CHECK": {
        "STATUS": {
            "endpoint": "GET /health/status/",
            "description": "Full system health status (DB, cache, app)",
            "auth_required": False,
            "roles": ["All (public)"]
        },
        "DATABASE": {
            "endpoint": "GET /health/database/",
            "description": "Check database connectivity and performance",
            "auth_required": False,
            "roles": ["All (public)"]
        },
        "CACHE": {
            "endpoint": "GET /health/cache/",
            "description": "Check cache system (Redis/Memcached)",
            "auth_required": False,
            "roles": ["All (public)"]
        },
        "ALIVE": {
            "endpoint": "GET /health/alive/",
            "description": "Quick lightweight check - is API running?",
            "auth_required": False,
            "roles": ["All (public)"]
        },
        "READINESS": {
            "endpoint": "GET /health/readiness/",
            "description": "Readiness probe - is API ready for traffic?",
            "auth_required": False,
            "roles": ["All (public)"]
        },
    },
    "METRICS": {
        "SYSTEM_INFO": {
            "endpoint": "GET /metrics/system-info/",
            "description": "System and API information (Python, Platform, Versions)",
            "auth_required": False,
            "roles": ["All (public)"]
        },
        "VERSION": {
            "endpoint": "GET /metrics/version/",
            "description": "Get API version information",
            "auth_required": False,
            "roles": ["All (public)"]
        },
    },
}

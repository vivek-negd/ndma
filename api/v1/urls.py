from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from api.v1.views.rbac_views import (
    PermissionViewSet, RoleViewSet, UserRoleViewSet, RolePermissionAuditViewSet
)
from api.v1.views.auth_views import LoginView, UserViewSet
from api.v1.views.organization_views import OrganizationViewSet
from api.v1.volunteer import routes as volunteer_routes
from api.v1.views.training_views import TrainingScheduleViewSet

router = DefaultRouter()
router.register(r'auth', LoginView, basename='auth')
router.register(r'users', UserViewSet, basename='user')
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'rbac/permissions', PermissionViewSet, basename='permission')
router.register(r'rbac/roles', RoleViewSet, basename='role')
router.register(r'rbac/user-roles', UserRoleViewSet, basename='user-role')
router.register(r'rbac/audit/role-permissions', RolePermissionAuditViewSet, basename='role-permission-audit')
router.register(r'training-schedules', TrainingScheduleViewSet, basename='training-schedule')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('volunteer/', include(volunteer_routes)),
]
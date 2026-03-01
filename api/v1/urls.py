from django.urls import path, include
from api.v1.api_router import router, urlpatterns as router_urls
from api.v1.volunteer import routes as volunteer_routes

# ============================================================================
# API v1 URLS - CENTRALIZED
# ============================================================================
# All main endpoints are registered and configured in api_router.py
# Volunteer endpoints are included from volunteer/routes.py
# This file combines both centralized and volunteer route configurations

app_name = 'api_v1'

urlpatterns = router_urls + [
    path('volunteer/', include(volunteer_routes)),
]
from django.urls import path, include

urlpatterns = [
    # API v1
    path("api/v1/", include("api.v1.urls")),
]
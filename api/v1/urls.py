from django.urls import path, include

urlpatterns = [
    path("auth/", include("api.v1.auth.routes")),
]
from django.urls import path
from api.v1.auth.views import LoginAPIView, TestAPIView

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("test/", TestAPIView.as_view(), name="test"),

]
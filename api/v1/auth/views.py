from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated



class LoginAPIView(APIView):

    permission_classes = [AllowAny]   # 🔥 IMPORTANT

    def post(self, request):

        email = request.data.get("email_address")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            request=request,
            email_address=email,
            password=password
        )

        if user is None:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user_role": user.user_role,
                "email_address": user.email_address,
            },
            status=status.HTTP_200_OK
        )

class TestAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(
            {
                "message": "Test API working",
                "user": request.user.email_address,
                "role": request.user.user_role
            },
            status=status.HTTP_200_OK
        )
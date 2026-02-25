from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


class LoginSerializer(serializers.Serializer):

    email_address = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email_address")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            email_address=email,   # 🔥 THIS IS THE FIX
            password=password,
        )

        if user is None:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User account is inactive")

        refresh = RefreshToken.for_user(user)

        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user_role": user.user_role,
            "email_address": user.email_address,
        }
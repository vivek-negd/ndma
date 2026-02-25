from rest_framework_simplejwt.tokens import RefreshToken


class TokenUtil:

    @staticmethod
    def generate_token(user):

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
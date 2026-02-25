from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from models.permissions import RoleBasedAccessPermission


class TestAPIView(APIView):

    permission_classes = [IsAuthenticated, RoleBasedAccessPermission]

    def get(self, request):
        return Response({
            "message": "RBAC working",
            "user_role": request.user.user_role
        })
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from models.organization import Organization
from .serializers import VolunteerSerializer


class VolunteerCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    ALLOWED_ROLES = [
        "SUPER_ADMIN",
        "NATIONAL_ADMIN",
        "STATE_ADMIN",
        "DISTRICT_ADMIN",
    ]

    def post(self, request):

        if request.user.user_role not in self.ALLOWED_ROLES:
            return Response(
                {"error": "You do not have permission to create volunteer"},
                status=status.HTTP_403_FORBIDDEN
            )

        organization_id = request.data.get("organization_id")

        if not organization_id:
            return Response(
                {"error": "organization_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response(
                {"error": "Invalid organization_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = VolunteerSerializer(data=request.data)

        if serializer.is_valid():
            volunteer = serializer.save()

            return Response(
                {
                    "message": "Volunteer uploaded successfully",
                    "volunteer_id": volunteer.id,
                    "organization": organization.name,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VolunteerBulkUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    ALLOWED_ROLES = [
        "SUPER_ADMIN",
        "NATIONAL_ADMIN",
        "STATE_ADMIN",
        "DISTRICT_ADMIN",
    ]

    def post(self, request):

        if request.user.user_role not in self.ALLOWED_ROLES:
            return Response(
                {"error": "You do not have permission to upload volunteers"},
                status=status.HTTP_403_FORBIDDEN
            )

        volunteers_data = request.data

        if not isinstance(volunteers_data, list):
            return Response(
                {"error": "Expected list of volunteers"},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_records = []
        errors = []

        with transaction.atomic():
            for index, volunteer_data in enumerate(volunteers_data):

                serializer = VolunteerSerializer(data=volunteer_data)

                if serializer.is_valid():
                    volunteer = serializer.save()
                    created_records.append(volunteer.mis_id)
                else:
                    errors.append({
                        "index": index,
                        "errors": serializer.errors
                    })

        return Response({
            "created_count": len(created_records),
            "created_mis_ids": created_records,
            "error_count": len(errors),
            "errors": errors
        }, status=status.HTTP_201_CREATED)
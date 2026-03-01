import csv
import io

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from models.organization import Organization
from .serializers import VolunteerSerializer
from models.volunteer import Volunteer
from django.db.models import Count


class VolunteerCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    ALLOWED_ROLES = [
        "SUPER_ADMIN",
        "NATIONAL_ADMIN",
        "STATE_ADMIN",
        "DISTRICT_ADMIN",
        "YOUTH_ORG_ADMIN",
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
        "YOUTH_ORG_ADMIN",
    ]

    EXPECTED_COLUMNS = {
        "mis_id",
        "name",
        "gender",
        "blood_group",
        "dob",
        "aadhar",
        "mobile",
        "email",
        "mybharat_id",
        "organization_id",
        "organization_name",
        "state",
        "district",
        "state_lgd_code",
        "district_lgd_code",
        "postal_code",
        "town",
        "village",
        "full_address",
    }

    def _parse_csv(self, file_obj):
        decoded = io.TextIOWrapper(file_obj, encoding='utf-8-sig')
        reader = csv.DictReader(decoded)
        rows = []
        for row in reader:
            # Normalize keys to snake_case-like fields
            normalized = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items() if k}
            rows.append(normalized)
        return rows

    def _role_allowed(self, user):
        return getattr(user, "user_role", None) in self.ALLOWED_ROLES

    def post(self, request):

        if not self._role_allowed(request.user):
            return Response(
                {"error": "You do not have permission to upload volunteers"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Optional defaults supplied via form-data fields: state, district, organization_id/name, expected_count
        default_org_id = request.data.get('organization_id')
        default_org_name = request.data.get('organization_name')
        default_state = request.data.get('state')
        default_district = request.data.get('district')
        default_state_lgd_code = request.data.get('state_lgd_code')
        default_district_lgd_code = request.data.get('district_lgd_code')
        expected_count = request.data.get('expected_count')

        is_csv = 'file' in request.FILES
        if is_csv:
            volunteers_data = self._parse_csv(request.FILES['file'])
        else:
            volunteers_data = request.data

        if not isinstance(volunteers_data, list):
            return Response(
                {"error": "Expected list of volunteers or CSV file"},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_records = []
        errors = []
        warnings = []

        # Apply defaults to each row if missing
        def apply_defaults(row):
            if default_org_id and 'organization_id' not in row and 'organization_name' not in row:
                row['organization_id'] = default_org_id
            if default_org_name and 'organization_name' not in row:
                row['organization_name'] = default_org_name

            # Prefer name-based inputs to avoid PK type errors
            if default_state_lgd_code and 'state_lgd_code' not in row:
                row['state_lgd_code'] = default_state_lgd_code
            if default_state and 'state' not in row and 'state_name' not in row:
                row['state_name'] = default_state
            if 'state' in row and isinstance(row['state'], str) and 'state_name' not in row:
                row['state_name'] = row.pop('state')

            if default_district_lgd_code and 'district_lgd_code' not in row:
                row['district_lgd_code'] = default_district_lgd_code
            if default_district and 'district' not in row and 'district_name' not in row:
                row['district_name'] = default_district
            if 'district' in row and isinstance(row['district'], str) and 'district_name' not in row:
                row['district_name'] = row.pop('district')

            return row

        volunteers_data = [apply_defaults(dict(v)) for v in volunteers_data]

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

        if expected_count is not None:
            try:
                expected_int = int(expected_count)
                if expected_int != len(volunteers_data):
                    warnings.append({
                        "expected_count": expected_int,
                        "actual_rows": len(volunteers_data),
                        "message": "Row count does not match expected_count"
                    })
            except (TypeError, ValueError):
                warnings.append({"expected_count": expected_count, "message": "expected_count must be integer"})

        return Response({
            "created_count": len(created_records),
            "created_mis_ids": created_records,
            "error_count": len(errors),
            "errors": errors,
            "warnings": warnings
        }, status=status.HTTP_201_CREATED)


class OrganizationCoverageAPIView(APIView):
    """Return organizations with states and districts coverage and volunteer counts"""
    permission_classes = [IsAuthenticated]

    ALLOWED_ROLES = [
        "SUPER_ADMIN",
        "NATIONAL_ADMIN",
        "STATE_ADMIN",
        "DISTRICT_ADMIN",
        "YOUTH_ORG_ADMIN",
    ]

    def _role_allowed(self, user):
        return getattr(user, "user_role", None) in self.ALLOWED_ROLES

    def get(self, request):
        if not self._role_allowed(request.user):
            return Response({"error": "You do not have permission to view coverage"}, status=status.HTTP_403_FORBIDDEN)

        orgs = Organization.objects.all()
        result = []

        for org in orgs:
            qs = Volunteer.objects.filter(organization=org, deleted_at__isnull=True)
            total_volunteers = qs.count()

            # aggregate by state and district
            state_agg = qs.values('state__id', 'state__name', 'state__lgd_code').annotate(state_count=Count('id'))
            states = []
            for s in state_agg:
                state_id = s['state__id']
                state_name = s.get('state__name')
                state_lgd = s.get('state__lgd_code')

                districts_qs = qs.filter(state_id=state_id).values('district__id', 'district__name', 'district__lgd_code').annotate(district_count=Count('id'))
                districts = []
                for d in districts_qs:
                    districts.append({
                        'district_id': d.get('district__id'),
                        'district_name': d.get('district__name'),
                        'district_lgd_code': d.get('district__lgd_code'),
                        'volunteer_count': d.get('district_count')
                    })

                states.append({
                    'state_id': state_id,
                    'state_name': state_name,
                    'state_lgd_code': state_lgd,
                    'volunteer_count': s.get('state_count'),
                    'districts': districts
                })

            result.append({
                'organization_id': org.id,
                'organization_name': org.name,
                'total_volunteers': total_volunteers,
                'states': states
            })

        return Response({'organizations': result}, status=status.HTTP_200_OK)
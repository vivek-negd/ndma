import csv
import io
import openpyxl

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.db import transaction
from models.organization import Organization
from .serializers import VolunteerSerializer
from models.volunteer import Volunteer
from models.choices import (
    SalutationChoice,
    GenderChoice,
    BloodGroupChoice,
    MaritalStatusChoice,
    EducationChoice,
    SkillChoice,
    AreaTypeChoice,
)
from django.db.models import Count


# ============================================================================
# PUBLIC ENDPOINT - Volunteer Dropdown Choices (NO AUTH REQUIRED)
# ============================================================================

class VolunteerChoicesAPIView(APIView):
    """
    GET /api/v1/volunteer/choices/
    
    Returns all dropdown choices for volunteer form fields from database.
    PUBLIC ENDPOINT - no authentication required.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "status_code": 200,
                "message": "Volunteer dropdown choices retrieved",
                "choices": {
                    "salutation": [
                        {"id": choice.code, "label": choice.label}
                        for choice in SalutationChoice.objects.filter(is_active=True).order_by('code')
                    ],
                    "gender": [
                        {"id": choice.code, "label": choice.label}
                        for choice in GenderChoice.objects.filter(is_active=True).order_by('code')
                    ],
                    "bloodgroup": [
                        {"id": choice.code, "label": choice.label}
                        for choice in BloodGroupChoice.objects.filter(is_active=True).order_by('code')
                    ],
                    "maritalstatus": [
                        {"id": choice.code, "label": choice.label}
                        for choice in MaritalStatusChoice.objects.filter(is_active=True).order_by('code')
                    ],
                    "education": [
                        {"id": choice.code, "label": choice.label}
                        for choice in EducationChoice.objects.filter(is_active=True).order_by('code')
                    ],
                    "skill": [
                        {"id": choice.code, "label": choice.label}
                        for choice in SkillChoice.objects.filter(is_active=True).order_by('code')
                    ],
                    "area_type": [
                        {"id": choice.code, "label": choice.label}
                        for choice in AreaTypeChoice.objects.filter(is_active=True).order_by('code')
                    ],
                }
            },
            status=status.HTTP_200_OK
        )


class VolunteerCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    ALLOWED_ROLES = [
        "SUPER_ADMIN",
        "NDMA_ADMIN",
        "SDMA_ADMIN",
        "DDMA_NODAL_OFFICER",
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
        "NDMA_ADMIN",
        "SDMA_ADMIN",
        "DDMA_NODAL_OFFICER",
        "YOUTH_ORG_ADMIN",
    ]

    EXPECTED_COLUMNS = {
        "mis_id",
        "name",
        "salutation",
        "gender",
        "blood_group",
        "dob",
        "aadhar",
        "mobile",
        "email",
        "mybharat_id",
        "maritalstatus",
        "emergency_contact",
        "education",
        "education_field",
        "skill",
        "organization_id",
        "organization_name",
        "state_name",
        "district_name",
        "area_type",
        "postal_code",
        "town",
        "village",
        "full_address",
        "id_card",
        "certificate",
        "photo",
    }

    def _parse_csv(self, file_obj):
        """Parse CSV file with multiple encoding support"""
        encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                file_obj.seek(0)  # Reset file pointer
                decoded = io.TextIOWrapper(file_obj, encoding=encoding)
                reader = csv.DictReader(decoded)
                rows = []
                for row in reader:
                    # Normalize keys to snake_case-like fields
                    normalized = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items() if k}
                    rows.append(normalized)
                return rows
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                continue
        
        # If all encodings fail
        raise ValueError(f"Unable to parse CSV file. Tried encodings: {', '.join(encodings)}")

    def _parse_excel(self, file_obj):
        """Parse Excel (.xlsx) file"""
        try:
            workbook = openpyxl.load_workbook(file_obj)
            worksheet = workbook.active
            
            # Get headers from first row
            headers = []
            for cell in worksheet[1]:
                if cell.value:
                    headers.append(str(cell.value).strip())
            
            rows = []
            for row_idx, row in enumerate(worksheet.iter_rows(min_row=2, values_only=True), start=2):
                row_dict = {}
                for col_idx, header in enumerate(headers):
                    value = row[col_idx]
                    if value is not None:
                        row_dict[header] = str(value).strip() if isinstance(value, str) else value
                if any(row_dict.values()):  # Only add non-empty rows
                    rows.append(row_dict)
            
            return rows
        except Exception as e:
            raise ValueError(f"Unable to parse Excel file: {str(e)}")

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
        default_state = request.data.get('state_name')
        default_district = request.data.get('district_name')
        expected_count = request.data.get('expected_count')

        volunteers_data = None
        error_msg = None

        # Check for file upload
        if 'file' in request.FILES:
            file_obj = request.FILES['file']
            filename = file_obj.name.lower()
            
            try:
                if filename.endswith('.xlsx') or filename.endswith('.xls'):
                    # Parse Excel file
                    volunteers_data = self._parse_excel(file_obj)
                elif filename.endswith('.csv'):
                    # Parse CSV file
                    volunteers_data = self._parse_csv(file_obj)
                else:
                    error_msg = "Unsupported file format. Use .xlsx, .xls, or .csv"
            except Exception as e:
                error_msg = f"Error parsing file: {str(e)}"
        else:
            # Try to parse as JSON array from request.data
            volunteers_data = request.data

        # Return error if file parsing failed
        if error_msg:
            return Response(
                {"error": error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(volunteers_data, list):
            return Response(
                {"error": "Expected list of volunteers or CSV/Excel file"},
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
            if default_state and 'state_name' not in row:
                row['state_name'] = default_state
            if default_district and 'district_name' not in row:
                row['district_name'] = default_district
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
            state_agg = qs.values('state__id', 'state__name').annotate(state_count=Count('id'))
            states = []
            for s in state_agg:
                state_id = s['state__id']
                state_name = s.get('state__name')

                districts_qs = qs.filter(state_id=state_id).values('district__id', 'district__name').annotate(district_count=Count('id'))
                districts = []
                for d in districts_qs:
                    districts.append({
                        'district_id': d.get('district__id'),
                        'district_name': d.get('district__name'),
                        'volunteer_count': d.get('district_count')
                    })

                states.append({
                    'state_id': state_id,
                    'state_name': state_name,
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
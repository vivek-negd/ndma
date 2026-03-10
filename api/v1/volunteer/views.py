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
from django.db.models import Count, Max


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
        # Allow if user's role is in the whitelist OR they have the 'view_volunteer' permission.
        if getattr(user, "user_role", None) in self.ALLOWED_ROLES:
            return True
        perms = getattr(user, "permissions", None)
        # If permissions aren't attached to the user object (typical with JWT),
        # fetch them from AuthService which reads role permissions from DB.
        if not perms:
            try:
                from services.auth_service import AuthService
                perms = AuthService.get_user_permissions(user)
            except Exception:
                perms = None

        try:
            if perms and "view_volunteer" in perms:
                return True
        except Exception:
            pass
        return False

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

        # Check for file upload (EXCEL ONLY)
        if 'file' in request.FILES:
            file_obj = request.FILES['file']
            filename = file_obj.name.lower()
            
            # Only accept Excel files
            if not (filename.endswith('.xlsx') or filename.endswith('.xls')):
                return Response(
                    {"error": "Only Excel files (.xlsx, .xls) are supported. Please upload an Excel file."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                volunteers_data = self._parse_excel(file_obj)
            except Exception as e:
                return Response(
                    {"error": f"Error parsing Excel file: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "File upload is required. Please provide an Excel file (.xlsx or .xls)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(volunteers_data, list):
            return Response(
                {"error": "Expected valid Excel file with volunteer data"},
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

        # Determine response status code
        if len(errors) > 0:
            # Partial success/failure
            response_status = status.HTTP_207_MULTI_STATUS if len(created_records) > 0 else status.HTTP_400_BAD_REQUEST
        else:
            # All successful
            response_status = status.HTTP_201_CREATED

        return Response({
            "created_count": len(created_records),
            "created_mis_ids": created_records,
            "error_count": len(errors),
            "errors": errors,
            "warnings": warnings
        }, status=response_status)


class OrganizationCoverageAPIView(APIView):
    """Return organizations with states and districts coverage and volunteer counts"""
    permission_classes = [IsAuthenticated]

    ALLOWED_ROLES = [
        "SUPER_ADMIN",
        "NATIONAL_ADMIN",
        "STATE_ADMIN",
        "SDMA_ADMIN",
        "DISTRICT_ADMIN",
        "DDMA_NODAL_OFFICER",
        "YOUTH_ORG_ADMIN",
    ]

    def _role_allowed(self, user):
        # For JWT-authenticated users, user_role is not attached to request.user.
        # Query the database to get the actual user object with role and permissions.
        from django.contrib.auth import get_user_model
        from models.role import UserRole, Permission
        
        User = get_user_model()
        
        try:
            # Try to get user_role from the user object (may work in some cases)
            user_role = getattr(user, "user_role", None)
            
            # If user_role is not on the request.user object, query the database
            if not user_role:
                db_user = User.objects.get(id=user.id)
                user_role = db_user.user_role
            
            # Check if role is in the allowed list
            if user_role in self.ALLOWED_ROLES:
                return True
            
            # If role not in whitelist, check permissions by querying the database
            db_user = User.objects.get(id=user.id)
            user_role_obj = UserRole.objects.filter(user=db_user).first()
            
            if user_role_obj and user_role_obj.role:
                perms = Permission.objects.filter(role=user_role_obj.role).values_list('code', flat=True)
                if "view_volunteer" in perms:
                    return True
            
            return False
        except Exception as e:
            return False

    def get(self, request):
        if not self._role_allowed(request.user):
            return Response({"error": "You do not have permission to view coverage"}, status=status.HTTP_403_FORBIDDEN)

        from django.contrib.auth import get_user_model
        from django.db.models import Q
        from datetime import datetime
        User = get_user_model()
        
        # Get user object from database to ensure we have all attributes
        # Use select_related to load the state relationship (field is named state_id)
        db_user = User.objects.select_related('state_id').get(id=request.user.id)
        user_role = db_user.user_role
        user_state = db_user.state_id
        user_district = db_user.district_id
        
        # Build tabular coverage data
        volunteers = Volunteer.objects.select_related('state', 'district', 'organization').filter(deleted_at__isnull=True)
        
        # Filter by user role
        if user_role in ("SDMA_ADMIN", "STATE_ADMIN") and user_state:
            volunteers = volunteers.filter(state_id=user_state)
        elif user_role == "DISTRICT_ADMIN" and user_state and user_district:
            volunteers = volunteers.filter(state_id=user_state, district_id=user_district)
        
        # Group by state, district, organization (avoiding INNER JOIN with org_type due to NULL values)
        coverage_data = []
        grouped = volunteers.exclude(
            Q(state__isnull=True) | Q(district__isnull=True) | Q(organization__isnull=True)
        ).values(
            'state__id',
            'state__name',
            'district__id',
            'district__name',
            'organization__id',
            'organization__name'
        ).annotate(
            volunteer_count=Count('id'),
            latest_date=Max('created_at')
        ).order_by('state__name', 'district__name', 'organization__name')
        
        # Build coverage data and fetch org_type for each organization
        from models.organization import Organization
        org_type_cache = {}
        
        for record in grouped:
            org_id = record['organization__id']
            if org_id not in org_type_cache:
                try:
                    org = Organization.objects.get(id=org_id)
                    org_type_cache[org_id] = {
                        'org_type_id': org.org_type_id,
                        'org_type_code': org.org_type.code if org.org_type else None,
                        'org_type_name': org.org_type.name if org.org_type else None
                    }
                except:
                    org_type_cache[org_id] = {
                        'org_type_id': None,
                        'org_type_code': None,
                        'org_type_name': None
                    }
            
            org_data = org_type_cache[org_id]
            coverage_data.append({
                'state_id': record['state__id'],
                'state': record['state__name'],
                'district_id': record['district__id'],
                'district': record['district__name'],
                'organization_id': record['organization__id'],
                'organization': record['organization__name'],
                'organization_type_id': org_data['org_type_id'],
                'organization_type_code': org_data['org_type_code'],
                'organization_type': org_data['org_type_name'],
                'no_of_volunteers': record['volunteer_count'],
                'date': record['latest_date'].strftime('%Y-%m-%d %H:%M:%S') if record['latest_date'] else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Summary statistics for tabular format (excluding only null state/district/org)
        valid_volunteers = volunteers.exclude(
            Q(state__isnull=True) | Q(district__isnull=True) | Q(organization__isnull=True)
        )
        
        # For SDMA_ADMIN and STATE_ADMIN, provide district-level view of all volunteers in their state
        if user_role in ("SDMA_ADMIN", "STATE_ADMIN") and user_state:
            volunteers_old = Volunteer.objects.filter(state_id=user_state, deleted_at__isnull=True)
            
            # Aggregate by district
            district_agg = volunteers_old.values('district__id', 'district__name').annotate(volunteer_count=Count('id')).order_by('-volunteer_count')
            
            districts = []
            for d in district_agg:
                districts.append({
                    'district_id': d.get('district__id'),
                    'district_name': d.get('district__name'),
                    'volunteer_count': d.get('volunteer_count')
                })
            
            return Response({
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'state_id': db_user.state_id.id if db_user.state_id else None,
                'state_name': db_user.state_id.name if db_user.state_id else None,
                'total_volunteers': volunteers_old.count(),
                'districts': districts,
                'tabular_format': {
                    'summary': {
                        'total_volunteers': valid_volunteers.count(),
                        'unique_states': valid_volunteers.values('state_id').distinct().count(),
                        'unique_districts': valid_volunteers.values('district_id').distinct().count(),
                        'unique_organizations': valid_volunteers.values('organization_id').distinct().count(),
                    },
                    'coverage': coverage_data
                }
            }, status=status.HTTP_200_OK)
        
        # For other roles, show organization-level coverage
        orgs = Organization.objects.all()

        if user_role == "DISTRICT_ADMIN" and user_state and user_district:
            orgs = orgs.filter(state_id=user_state, district_id=user_district)
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

        return Response({
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'organizations': result,
            'tabular_format': {
                'summary': {
                    'total_volunteers': valid_volunteers.count(),
                    'unique_states': valid_volunteers.values('state_id').distinct().count(),
                    'unique_districts': valid_volunteers.values('district_id').distinct().count(),
                    'unique_organizations': valid_volunteers.values('organization_id').distinct().count(),
                },
                'coverage': coverage_data
            }
        }, status=status.HTTP_200_OK)


# ============================================================================
# VOLUNTEER COVERAGE REPORT - TABULAR FORMAT (STATE/DISTRICT/ORG/COUNT)
# ============================================================================

class VolunteerCoverageReportAPIView(APIView):
    """
    Return volunteer coverage in tabular format: STATE, DISTRICT, ORGANIZATION, NO. OF VOL., DATE
    Designed for easy viewing and CSV export
    """
    permission_classes = [IsAuthenticated]

    ALLOWED_ROLES = [
        "SUPER_ADMIN",
        "NATIONAL_ADMIN",
        "STATE_ADMIN",
        "SDMA_ADMIN",
        "DISTRICT_ADMIN",
        "DDMA_NODAL_OFFICER",
        "YOUTH_ORG_ADMIN",
    ]

    def _role_allowed(self, user):
        from django.contrib.auth import get_user_model
        from models.role import UserRole, Permission
        
        User = get_user_model()
        
        try:
            user_role = getattr(user, "user_role", None)
            
            if not user_role:
                db_user = User.objects.get(id=user.id)
                user_role = db_user.user_role
            
            if user_role in self.ALLOWED_ROLES:
                return True
            
            db_user = User.objects.get(id=user.id)
            user_role_obj = UserRole.objects.filter(user=db_user).first()
            
            if user_role_obj and user_role_obj.role:
                perms = Permission.objects.filter(role=user_role_obj.role).values_list('code', flat=True)
                if "view_volunteer" in perms:
                    return True
            
            return False
        except Exception as e:
            return False

    def get(self, request):
        if not self._role_allowed(request.user):
            return Response({"error": "You do not have permission to view coverage"}, status=status.HTTP_403_FORBIDDEN)

        from django.contrib.auth import get_user_model
        from datetime import datetime
        User = get_user_model()
        
        db_user = User.objects.select_related('state_id').get(id=request.user.id)
        user_role = db_user.user_role
        user_state = db_user.state_id
        user_district = db_user.district_id
        
        # Get all volunteers based on user role
        volunteers = Volunteer.objects.select_related('state', 'district', 'organization').filter(deleted_at__isnull=True)
        
        # Filter by user role
        if user_role in ("SDMA_ADMIN", "STATE_ADMIN") and user_state:
            volunteers = volunteers.filter(state_id=user_state)
        elif user_role == "DISTRICT_ADMIN" and user_state and user_district:
            volunteers = volunteers.filter(state_id=user_state, district_id=user_district)
        
        # Build coverage data: STATE | DISTRICT | ORGANIZATION | NO. OF VOL. | DATE
        coverage_data = []
        
        # Group by state, district, organization (avoiding INNER JOIN with org_type due to NULL values)
        from django.db.models import Q
        grouped = volunteers.exclude(
            Q(state__isnull=True) | Q(district__isnull=True) | Q(organization__isnull=True)
        ).values(
            'state__id',
            'state__name',
            'district__id',
            'district__name',
            'organization__id',
            'organization__name'
        ).annotate(
            volunteer_count=Count('id'),
            latest_date=Max('created_at')
        ).order_by('state__name', 'district__name', 'organization__name')
        
        # Build coverage data and fetch org_type for each organization
        from models.organization import Organization
        org_type_cache = {}
        
        for record in grouped:
            org_id = record['organization__id']
            if org_id not in org_type_cache:
                try:
                    org = Organization.objects.get(id=org_id)
                    org_type_cache[org_id] = {
                        'org_type_id': org.org_type_id,
                        'org_type_code': org.org_type.code if org.org_type else None,
                        'org_type_name': org.org_type.name if org.org_type else None
                    }
                except:
                    org_type_cache[org_id] = {
                        'org_type_id': None,
                        'org_type_code': None,
                        'org_type_name': None
                    }
            
            org_data = org_type_cache[org_id]
            coverage_data.append({
                'state_id': record['state__id'],
                'state': record['state__name'],
                'district_id': record['district__id'],
                'district': record['district__name'],
                'organization_id': record['organization__id'],
                'organization': record['organization__name'],
                'organization_type_id': org_data['org_type_id'],
                'organization_type_code': org_data['org_type_code'],
                'organization_type': org_data['org_type_name'],
                'no_of_volunteers': record['volunteer_count'],
                'date': record['latest_date'].strftime('%Y-%m-%d %H:%M:%S') if record['latest_date'] else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Summary statistics - exclude incomplete records (only null state/district/org will be excluded)
        valid_volunteers = volunteers.exclude(
            Q(state__isnull=True) | Q(district__isnull=True) | Q(organization__isnull=True)
        )
        total_volunteers = valid_volunteers.count()
        unique_states = valid_volunteers.values('state_id').distinct().count()
        unique_districts = valid_volunteers.values('district_id').distinct().count()
        unique_organizations = valid_volunteers.values('organization_id').distinct().count()
        
        return Response({
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_volunteers': total_volunteers,
                'unique_states': unique_states,
                'unique_districts': unique_districts,
                'unique_organizations': unique_organizations,
            },
            'coverage': coverage_data
        }, status=status.HTTP_200_OK)


# ============================================================================
# VOLUNTEER EXPORT TO EXCEL - ROLE-BASED
# ============================================================================

class VolunteerExportAPIView(APIView):
    """
    GET /api/v1/volunteer/export/
    
    Export volunteer data to Excel based on user role:
    - SUPER_ADMIN: All volunteers nationwide
    - NATIONAL_ADMIN: All volunteers nationwide
    - STATE_ADMIN: All volunteers in their state
    - SDMA_ADMIN: All volunteers in their state
    - DISTRICT_ADMIN: All volunteers in their district
    - DDMA_NODAL_OFFICER: All volunteers in their district
    - YOUTH_ORG_ADMIN: All volunteers in their organization
    """
    permission_classes = [IsAuthenticated]

    ALLOWED_ROLES = [
        "SUPER_ADMIN",
        "NATIONAL_ADMIN",
        "STATE_ADMIN",
        "SDMA_ADMIN",
        "DISTRICT_ADMIN",
        "DDMA_NODAL_OFFICER",
        "YOUTH_ORG_ADMIN",
    ]

    def _role_allowed(self, user):
        """Check if user role is allowed to export"""
        user_role = getattr(user, "user_role", None)
        
        if not user_role:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                db_user = User.objects.get(id=user.id)
                user_role = db_user.user_role
            except:
                return False
        
        return user_role in self.ALLOWED_ROLES

    def get(self, request):
        """Export volunteer data to Excel
        
        Query Parameters:
        - district_id: Filter by specific district (for STATE_ADMIN/SDMA_ADMIN)
        - state_id: Filter by specific state (for SUPER_ADMIN/NATIONAL_ADMIN only)
        """
        if not self._role_allowed(request.user):
            return Response(
                {"error": "You do not have permission to export volunteers"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get user details from database
        from django.contrib.auth import get_user_model
        User = get_user_model()
        db_user = User.objects.select_related('state_id').get(id=request.user.id)
        user_role = db_user.user_role
        user_state = db_user.state_id
        user_district = db_user.district_id
        
        # Get query parameters
        district_id = request.query_params.get('district_id')

        # Filter volunteers based on role and geography
        volunteers = Volunteer.objects.filter(deleted_at__isnull=True)

        # Apply role-based filtering
        if user_role in ["STATE_ADMIN", "SDMA_ADMIN"] and user_state:
            volunteers = volunteers.filter(state_id=user_state)
            
            # Allow STATE_ADMIN to filter by specific district within their state
            if district_id:
                try:
                    volunteers = volunteers.filter(district_id=int(district_id))
                    file_name = f"volunteers_{user_state.name}_district_{district_id}_{db_user.id}.xlsx"
                except (ValueError, TypeError):
                    return Response(
                        {"error": "Invalid district_id parameter"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                file_name = f"volunteers_{user_state.name}_{db_user.id}.xlsx"
        elif user_role in ["DISTRICT_ADMIN", "DDMA_NODAL_OFFICER"] and user_state and user_district:
            volunteers = volunteers.filter(state_id=user_state, district_id=user_district)
            file_name = f"volunteers_{user_state.name}_{user_district.name}_{db_user.id}.xlsx"
        elif user_role == "YOUTH_ORG_ADMIN":
            # Get organizations managed by this user
            from models.organization import Organization
            org_ids = Organization.objects.filter(
                # Assuming there's a way to link organization to user
            ).values_list('id', flat=True)
            volunteers = volunteers.filter(organization_id__in=org_ids) if org_ids else volunteers.none()
            file_name = f"volunteers_org_{db_user.id}.xlsx"
        else:  # SUPER_ADMIN, NATIONAL_ADMIN
            file_name = f"volunteers_all_{db_user.id}.xlsx"

        # Create Excel workbook
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Volunteers"

        # Define headers
        headers = [
            "ID", "MIS ID", "Name", "Salutation", "Gender", "Blood Group", "DOB",
            "Aadhar", "Mobile", "Email", "MyBharat ID", "Marital Status",
            "Emergency Contact", "Education", "Education Field", "Skill", "Area Type",
            "State", "District", "Postal Code", "Town", "Village", "Full Address",
            "Organization", "Created At"
        ]

        # Write headers
        for col_idx, header in enumerate(headers, start=1):
            cell = worksheet.cell(row=1, column=col_idx, value=header)
            cell.font = openpyxl.styles.Font(bold=True, color="FFFFFF")
            cell.fill = openpyxl.styles.PatternFill(start_color="667eea", end_color="667eea", fill_type="solid")

        # Write volunteer data
        row_idx = 2
        for vol in volunteers.select_related('state', 'district', 'organization'):
            worksheet.cell(row=row_idx, column=1, value=vol.id)
            worksheet.cell(row=row_idx, column=2, value=vol.mis_id)
            worksheet.cell(row=row_idx, column=3, value=vol.name)
            worksheet.cell(row=row_idx, column=4, value=self._get_choice_label("salutation", vol.salutation_id))
            worksheet.cell(row=row_idx, column=5, value=self._get_choice_label("gender", vol.gender_id))
            worksheet.cell(row=row_idx, column=6, value=self._get_choice_label("bloodgroup", vol.bloodgroup_id))
            worksheet.cell(row=row_idx, column=7, value=vol.dob.strftime('%Y-%m-%d') if vol.dob else "")
            worksheet.cell(row=row_idx, column=8, value=vol.aadhar or "")
            worksheet.cell(row=row_idx, column=9, value=vol.mobile or "")
            worksheet.cell(row=row_idx, column=10, value=vol.email or "")
            worksheet.cell(row=row_idx, column=11, value=vol.mybharat_id or "")
            worksheet.cell(row=row_idx, column=12, value=self._get_choice_label("maritalstatus", vol.maritalstatus_id))
            worksheet.cell(row=row_idx, column=13, value=vol.emergency_contact or "")
            worksheet.cell(row=row_idx, column=14, value=self._get_choice_label("education", vol.education_id))
            worksheet.cell(row=row_idx, column=15, value=vol.education_field or "")
            worksheet.cell(row=row_idx, column=16, value=self._get_choice_label("skill", vol.skill_id))
            worksheet.cell(row=row_idx, column=17, value=self._get_choice_label("area_type", vol.area_type_id))
            worksheet.cell(row=row_idx, column=18, value=vol.state.name if vol.state else "")
            worksheet.cell(row=row_idx, column=19, value=vol.district.name if vol.district else "")
            worksheet.cell(row=row_idx, column=20, value=vol.postal_code or "")
            worksheet.cell(row=row_idx, column=21, value=vol.town or "")
            worksheet.cell(row=row_idx, column=22, value=vol.village or "")
            worksheet.cell(row=row_idx, column=23, value=vol.full_address or "")
            worksheet.cell(row=row_idx, column=24, value=vol.organization.name if vol.organization else "")
            worksheet.cell(row=row_idx, column=25, value=vol.created_at.strftime('%Y-%m-%d %H:%M:%S') if vol.created_at else "")
            row_idx += 1

        # Auto-adjust column widths
        for col_idx, header in enumerate(headers, start=1):
            max_length = len(str(header))
            column_letter = openpyxl.utils.get_column_letter(col_idx)
            worksheet.column_dimensions[column_letter].width = min(max_length + 2, 30)

        # Return Excel file as response
        from django.http import HttpResponse
        from io import BytesIO
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        
        excel_file = BytesIO()
        workbook.save(excel_file)
        excel_file.seek(0)
        response.write(excel_file.read())
        
        return response

    def _get_choice_label(self, choice_type, choice_id):
        """Get label for choice ID"""
        if not choice_id:
            return ""
        
        try:
            if choice_type == "salutation":
                choice = SalutationChoice.objects.get(code=choice_id)
            elif choice_type == "gender":
                choice = GenderChoice.objects.get(code=choice_id)
            elif choice_type == "bloodgroup":
                choice = BloodGroupChoice.objects.get(code=choice_id)
            elif choice_type == "maritalstatus":
                choice = MaritalStatusChoice.objects.get(code=choice_id)
            elif choice_type == "education":
                choice = EducationChoice.objects.get(code=choice_id)
            elif choice_type == "skill":
                choice = SkillChoice.objects.get(code=choice_id)
            elif choice_type == "area_type":
                choice = AreaTypeChoice.objects.get(code=choice_id)
            else:
                return ""
            
            return choice.label if hasattr(choice, 'label') else str(choice)
        except:
            return ""
import openpyxl
import os

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.db import IntegrityError, transaction
from django.http import FileResponse, HttpResponse
from models.organization import Organization
from .serializers import VolunteerSerializer
from models.volunteer import Volunteer
from models.bulk_upload_session import BulkUploadSession
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


def _get_active_user_role_mapping(db_user):
    from models.role import UserRole

    role_name = getattr(db_user, 'user_role', None)
    role_mapping = UserRole.objects.filter(user=db_user, is_active=True)
    if role_name:
        scoped_mapping = role_mapping.filter(role__name=role_name).first()
        if scoped_mapping:
            return scoped_mapping
    return role_mapping.first()


def _resolve_user_organization(db_user):
    user_role_obj = _get_active_user_role_mapping(db_user)
    if not user_role_obj or not user_role_obj.organization:
        return None

    raw_value = str(user_role_obj.organization).strip()
    if not raw_value:
        return None

    organization = None
    try:
        organization = Organization.objects.filter(id=int(raw_value)).first()
    except (TypeError, ValueError):
        organization = None

    if organization:
        return organization

    organization = Organization.objects.filter(name__iexact=raw_value).first()
    if organization:
        return organization

    if getattr(db_user, 'user_role', None) == 'YOUTH_ORG_ADMIN' and db_user.state_id and db_user.district_id:
        scoped_orgs = Organization.objects.filter(state=db_user.state_id, district=db_user.district_id)
        if scoped_orgs.count() == 1:
            return scoped_orgs.first()

    return None


def _ensure_user_organization(db_user):
    user_org = _resolve_user_organization(db_user)
    if user_org:
        return user_org

    if getattr(db_user, 'user_role', None) != 'YOUTH_ORG_ADMIN':
        return None
    if not db_user.state_id or not db_user.district_id:
        return None

    from models.organization_type import OrganizationType

    user_role_obj = _get_active_user_role_mapping(db_user)
    if not user_role_obj:
        return None

    scoped_org = Organization.objects.filter(state=db_user.state_id, district=db_user.district_id).order_by('id').first()
    if not scoped_org:
        org_type = OrganizationType.objects.filter(code='NYKS').first() or OrganizationType.objects.order_by('id').first()
        if not org_type:
            return None

        org_name = f"{db_user.state_id.name} {db_user.district_id.name} Youth Organisation"
        scoped_org, _ = Organization.objects.get_or_create(
            name=org_name,
            state=db_user.state_id,
            district=db_user.district_id,
            defaults={
                'org_type': org_type,
                'contact_person': db_user.name or db_user.email_address or '',
                'contact_email': db_user.email_address or '',
            }
        )

    if user_role_obj.organization != str(scoped_org.id):
        user_role_obj.organization = str(scoped_org.id)
        user_role_obj.state = str(db_user.state_id.id)
        user_role_obj.district = str(db_user.district_id.id)
        user_role_obj.save(update_fields=['organization', 'state', 'district'])

    return scoped_org


def _build_org_export_url(org_id):
    if not org_id:
        return None
    return f"/api/v1/volunteer/export/?organization_id={org_id}"


def _build_session_export_url(session_id):
    if not session_id:
        return None
    return f"/api/v1/volunteer/export/?bulk_upload_session_id={session_id}"


def _safe_filename_part(value):
    if not value:
        return "organization"
    cleaned = "".join(char if char.isalnum() else "_" for char in str(value).strip())
    cleaned = cleaned.strip("_")
    return cleaned or "organization"


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


class BulkUploadSessionListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    ALLOWED_ROLES = [
        "SUPER_ADMIN",
        "NATIONAL_ADMIN",
        "NDMA_ADMIN",
        "STATE_ADMIN",
        "SDMA_ADMIN",
        "DISTRICT_ADMIN",
        "DDMA_NODAL_OFFICER",
        "YOUTH_ORG_ADMIN",
    ]

    def get(self, request):
        from django.contrib.auth import get_user_model
        from datetime import datetime, time

        User = get_user_model()
        db_user = User.objects.select_related('state_id', 'district_id').get(id=request.user.id)
        user_role = db_user.user_role

        if user_role not in self.ALLOWED_ROLES:
            return Response(
                {"error": "You do not have permission to view bulk upload sessions"},
                status=status.HTTP_403_FORBIDDEN
            )

        sessions = BulkUploadSession.objects.select_related(
            'uploaded_by', 'state', 'district', 'organization'
        )

        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        if user_role in ["STATE_ADMIN", "SDMA_ADMIN"] and db_user.state_id:
            sessions = sessions.filter(state=db_user.state_id)
        elif user_role in ["DISTRICT_ADMIN", "DDMA_NODAL_OFFICER"] and db_user.state_id and db_user.district_id:
            sessions = sessions.filter(state=db_user.state_id, district=db_user.district_id)
        elif user_role == "YOUTH_ORG_ADMIN":
            sessions = sessions.filter(uploaded_by=db_user)

        if from_date:
            try:
                from_dt = datetime.combine(datetime.strptime(from_date, '%Y-%m-%d').date(), time.min)
                sessions = sessions.filter(uploaded_at__gte=from_dt)
            except ValueError:
                return Response(
                    {"error": "Invalid from_date. Use YYYY-MM-DD format."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if to_date:
            try:
                to_dt = datetime.combine(datetime.strptime(to_date, '%Y-%m-%d').date(), time.max)
                sessions = sessions.filter(uploaded_at__lte=to_dt)
            except ValueError:
                return Response(
                    {"error": "Invalid to_date. Use YYYY-MM-DD format."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        session_rows = []
        for session in sessions.order_by('-uploaded_at'):
            session_rows.append({
                "id": session.id,
                "uploaded_at": session.uploaded_at.isoformat(),
                "file_name": session.file_name,
                "status": session.status,
                "volunteers_created": session.volunteers_created,
                "total_rows": session.total_rows_in_file,
                "error_count": session.error_count,
                "uploaded_by": session.uploaded_by.name if session.uploaded_by else None,
                "state": session.state.name if session.state else None,
                "district": session.district.name if session.district else None,
                "organization_id": session.organization_id,
                "organization": session.organization.name if session.organization else None,
                "excel_download_url": _build_org_export_url(session.organization_id),
                "session_download_url": _build_session_export_url(session.id),
            })

        return Response(
            {
                "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "count": len(session_rows),
                "sessions": session_rows,
            },
            status=status.HTTP_200_OK
        )


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
            
            # Get headers from first row - CLEAN UP asterisks and special chars
            headers = []
            for cell in worksheet[1]:
                if cell.value:
                    # Remove asterisks and extra whitespace from header names
                    header_name = str(cell.value).strip().replace('*', '').strip()
                    headers.append(header_name)
            
            rows = []
            scope_only_fields = {
                'organization_id',
                'organization_name',
                'state_id',
                'state_name',
                'district_id',
                'district_name',
            }
            for row_idx, row in enumerate(worksheet.iter_rows(min_row=2, values_only=True), start=2):
                row_dict = {}
                for col_idx, header in enumerate(headers):
                    value = row[col_idx]
                    # Skip None and empty strings
                    if value is not None and value != "":
                        if isinstance(value, str):
                            stripped_val = value.strip()
                            # Only add if not empty after stripping
                            if stripped_val:
                                row_dict[header] = stripped_val
                        else:
                            row_dict[header] = value

                # Ignore template rows that only contain auto-filled scope fields.
                has_meaningful_data = any(field not in scope_only_fields for field in row_dict.keys())

                if row_dict and has_meaningful_data:
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
                {
                    "status": "error",
                    "status_code": 403,
                    "message": "You do not have permission to upload volunteers",
                    "data": None
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Get user info for role-based enforcement
        from django.contrib.auth import get_user_model
        User = get_user_model()
        db_user = User.objects.get(id=request.user.id)
        user_role = db_user.user_role
        user_state_id = db_user.state_id
        user_district_id = db_user.district_id
        
        user_org = _resolve_user_organization(db_user)
        if user_role == "YOUTH_ORG_ADMIN":
            user_org = user_org or _ensure_user_organization(db_user)
        user_org_id = user_org.id if user_org else None

        # Optional defaults supplied via form-data fields: state, district, organization_id/name, expected_count
        default_org_id = request.data.get('organization_id')
        default_org_name = request.data.get('organization_name')
        default_state = request.data.get('state_name')
        default_district = request.data.get('district_name')
        expected_count = request.data.get('expected_count')
        
        # IMPORTANT: For YOUTH_ORG_ADMIN, FORCE use their account's state/district/organization
        # This prevents uploading volunteers to unauthorized locations or organizations
        if user_role == "YOUTH_ORG_ADMIN":
            if user_state_id:
                default_state = user_state_id.id if hasattr(user_state_id, 'id') else user_state_id
            if user_district_id:
                default_district = user_district_id.id if hasattr(user_district_id, 'id') else user_district_id
            if user_org_id:
                default_org_id = user_org_id

        # Transform default state_name to state_id if provided as name
        # Skip transformation if it's already a numeric ID (from user account)
        default_state_id = None
        if default_state and isinstance(default_state, int):
            # Already numeric ID, use as-is
            default_state_id = default_state
        elif default_state and isinstance(default_state, str) and not default_state.isdigit():
            # It's a state name, not a numeric ID
            try:
                from models.state import State
                state = State.objects.get(name__iexact=default_state)
                default_state_id = state.id
                default_state = default_state_id
            except:
                pass
        elif default_state and default_state.isdigit():
            default_state_id = int(default_state)
            default_state = default_state_id

        # Transform default district_name to district_id if provided as name
        # Skip transformation if it's already a numeric ID (from user account)
        default_district_id = None
        if default_district and isinstance(default_district, int):
            # Already numeric ID, use as-is
            default_district_id = default_district
        elif default_district and isinstance(default_district, str) and not default_district.isdigit():
            # It's a district name, not a numeric ID
            try:
                from models.district import District
                state_id = default_state_id if default_state_id else (default_state if isinstance(default_state, int) else None)
                if state_id:
                    district = District.objects.get(name__iexact=default_district, state_id=state_id)
                    default_district_id = district.id
                    default_district = default_district_id
            except:
                pass
        elif default_district and isinstance(default_district, str) and default_district.isdigit():
            default_district_id = int(default_district)
            default_district = default_district_id

        # Transform default organization_name to organization_id if provided as name
        default_org_id_final = None
        if default_org_name:
            # If org_name provided, try to lookup its ID
            try:
                from models.organization import Organization
                org = Organization.objects.get(name__iexact=default_org_name)
                default_org_id_final = org.id
                default_org_id = default_org_id_final
            except:
                default_org_id = None
        elif default_org_id:
            # If numeric org_id provided, use it as-is
            try:
                default_org_id = int(default_org_id)
            except:
                default_org_id = None

        volunteers_data = None
        error_msg = None

        # Check for file upload (EXCEL ONLY)
        if 'file' in request.FILES:
            file_obj = request.FILES['file']
            filename = file_obj.name.lower()
            
            # Only accept Excel files
            if not (filename.endswith('.xlsx') or filename.endswith('.xls')):
                return Response(
                    {
                        "status": "error",
                        "status_code": 400,
                        "message": "Only Excel files (.xlsx, .xls) are supported",
                        "data": None
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                volunteers_data = self._parse_excel(file_obj)
            except Exception as e:
                return Response(
                    {
                        "status": "error",
                        "status_code": 400,
                        "message": f"Error parsing Excel file: {str(e)}",
                        "data": None
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {
                    "status": "error",
                    "status_code": 400,
                    "message": "File upload is required. Please provide an Excel file (.xlsx or .xls)",
                    "data": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(volunteers_data, list):
            return Response(
                {
                    "status": "error",
                    "status_code": 400,
                    "message": "Expected valid Excel file with volunteer data",
                    "data": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        created_records = []
        errors = []
        warnings = []
        row_results = []

        def add_row_error(index, volunteer_data, error_message):
            row_number = index + 2
            error_item = {
                "index": index,
                "row_number": row_number,
                "mis_id": volunteer_data.get('mis_id'),
                "error": error_message,
                "data": volunteer_data
            }
            errors.append(error_item)
            row_results.append({
                "index": index,
                "row_number": row_number,
                "mis_id": volunteer_data.get('mis_id'),
                "status": "error",
                "error": error_message
            })

        def add_row_success(index, volunteer, volunteer_data):
            row_results.append({
                "index": index,
                "row_number": index + 2,
                "mis_id": volunteer.mis_id or volunteer_data.get('mis_id'),
                "volunteer_id": volunteer.id,
                "status": "created"
            })

        def add_row_skipped(index, volunteer_data, reason):
            row_results.append({
                "index": index,
                "row_number": index + 2,
                "mis_id": volunteer_data.get('mis_id'),
                "status": "skipped",
                "reason": reason
            })
            warnings.append({
                "row_number": index + 2,
                "message": reason
            })

        # Apply defaults to each row if missing
        # For YOUTH_ORG_ADMIN, force state/district/organization and clear name fields to prevent re-lookup
        def apply_defaults(row):
            # For YOUTH_ORG_ADMIN, FORCE state/district/organization IDs and remove name-based fields
            if user_role == "YOUTH_ORG_ADMIN":
                if default_state:
                    row['state_id'] = default_state
                    # Remove state_name to prevent re-lookup of Excel value
                    row.pop('state_name', None)
                if default_district:
                    row['district_id'] = default_district
                    # Remove district_name to prevent re-lookup of Excel value
                    row.pop('district_name', None)
                if default_org_id:
                    row['organization_id'] = default_org_id
                    # Remove organization names to prevent override of Excel value
                    row.pop('organization_name', None)
            else:
                # For other roles, apply defaults if missing
                # Apply organization_id default
                if default_org_id and 'organization_id' not in row and 'organization_name' not in row:
                    row['organization_id'] = default_org_id
                # Apply state_id default
                if default_state and 'state_name' not in row and 'state_id' not in row:
                    row['state_id'] = default_state
                # Apply district_id default
                if default_district and 'district_name' not in row and 'district_id' not in row:
                    row['district_id'] = default_district
            return row

        volunteers_data = [apply_defaults(dict(v)) for v in volunteers_data]

        # Import models for lookups
        from models.state import State
        from models.district import District
        from models.organization import Organization

        # CREATE BULK UPLOAD SESSION - track this upload event
        session_state = None
        session_district = None
        session_organization = None

        # Determine session scope from defaults
        if default_state_id:
            try:
                session_state = State.objects.get(id=default_state_id)
            except Exception:
                pass

        if default_district_id:
            try:
                session_district = District.objects.get(id=default_district_id)
            except Exception:
                pass

        if default_org_id:
            try:
                session_organization = user_org if user_org and user_org.id == default_org_id else Organization.objects.get(id=default_org_id)
            except Exception:
                pass

        bulk_upload_session = BulkUploadSession.objects.create(
            uploaded_by=db_user,
            state=session_state,
            district=session_district,
            organization=session_organization,
            total_rows_in_file=len(volunteers_data),
            file_name=request.FILES.get('file').name if 'file' in request.FILES else 'Unknown',
            status='pending'  # Will update to success/partial/failed after processing
        )

        # Accept both relation field names (state) and DB attnames (state_id)
        # so direct model creation keeps FK ids coming from the Excel transform step.
        model_fields = set()
        for field in Volunteer._meta.get_fields():
            field_name = getattr(field, 'name', None)
            if field_name:
                model_fields.add(field_name)
            field_attname = getattr(field, 'attname', None)
            if field_attname:
                model_fields.add(field_attname)

        for index, volunteer_data in enumerate(volunteers_data):
            try:
                with transaction.atomic():
                    # Transform state_name and district_name to their IDs
                    transformed_data = dict(volunteer_data)
                    
                    # Transform state_name -> state_id
                    if 'state_name' in transformed_data and 'state_id' not in transformed_data:
                        try:
                            state = State.objects.get(name__iexact=transformed_data['state_name'])
                            transformed_data['state_id'] = state.id
                        except State.DoesNotExist:
                            # Try to create state if it doesn't exist
                            try:
                                state, _ = State.objects.get_or_create(
                                    name=transformed_data['state_name'],
                                    defaults={'status': 'active'}
                                )
                                transformed_data['state_id'] = state.id
                            except Exception:
                                add_row_error(index, volunteer_data, f"State '{transformed_data['state_name']}' not found and could not be created")
                                continue
                        except Exception as e:
                            add_row_error(index, volunteer_data, f"Error looking up state: {str(e)}")
                            continue
                    
                    # Transform district_name -> district_id
                    if 'district_name' in transformed_data and 'district_id' not in transformed_data:
                        state_id = transformed_data.get('state_id')
                        if not state_id:
                            add_row_error(index, volunteer_data, "district_name provided but state_id not found")
                            continue
                        
                        try:
                            district = District.objects.get(
                                name__iexact=transformed_data['district_name'],
                                state_id=state_id
                            )
                            transformed_data['district_id'] = district.id
                        except District.DoesNotExist:
                            # Try to create district if it doesn't exist
                            try:
                                district, _ = District.objects.get_or_create(
                                    name=transformed_data['district_name'],
                                    state_id=state_id,
                                    defaults={'status': 'active'}
                                )
                                transformed_data['district_id'] = district.id
                            except Exception:
                                add_row_error(index, volunteer_data, f"District '{transformed_data['district_name']}' not found in state and could not be created")
                                continue
                        except Exception as e:
                            add_row_error(index, volunteer_data, f"Error looking up district: {str(e)}")
                            continue
                    
                    # Transform organization_name -> organization_id if needed
                    if 'organization_name' in transformed_data and 'organization_id' not in transformed_data:
                        try:
                            org = Organization.objects.get(name__iexact=transformed_data['organization_name'])
                            transformed_data['organization_id'] = org.id
                        except Organization.DoesNotExist:
                            # If organization doesn't exist, we'll just skip it
                            # This allows flexibility for org name variations
                            pass
                        except Exception:
                            pass
                    
                    # Filter data to only include valid model fields
                    clean_data = {}
                    for k, v in transformed_data.items():
                        if k in model_fields and v not in [None, '', 'None']:
                            clean_data[k] = v
                    
                    # Link volunteer to this bulk upload session
                    clean_data['bulk_upload_session_id'] = bulk_upload_session.id

                    # Ignore incomplete rows instead of failing the whole upload.
                    if not clean_data.get('mis_id'):
                        add_row_skipped(index, volunteer_data, "Row skipped because mis_id is missing")
                        continue

                    # Create volunteer directly, bypassing serializer validation
                    if clean_data:
                        volunteer = Volunteer.objects.create(**clean_data)
                        add_row_success(index, volunteer, volunteer_data)
                        if volunteer.mis_id:
                            created_records.append(volunteer.mis_id)
                        else:
                            created_records.append(f"Row {index}")
                    else:
                        # No valid fields found in the row
                        add_row_error(index, volunteer_data, "No valid fields found in row")
            except IntegrityError as db_error:
                add_row_error(index, volunteer_data, str(db_error))
            except Exception as e:
                # Unexpected errors
                add_row_error(index, volunteer_data, str(e))

        # Update bulk_upload_session with final statistics
        bulk_upload_session.volunteers_created = len(created_records)
        bulk_upload_session.error_count = len(errors)

        # Determine session status
        if len(created_records) == 0:
            bulk_upload_session.status = 'failed'
        elif len(created_records) < len(volunteers_data):
            bulk_upload_session.status = 'partial'
        else:
            bulk_upload_session.status = 'success'

        bulk_upload_session.save()

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
                pass

        # Determine response status and message
        if len(created_records) == 0:
            # No records created
            if len(errors) > 0:
                # Failed with errors - show them
                response_status = status.HTTP_400_BAD_REQUEST
                response_message = f"Failed to upload: {len(errors)} error(s) occurred"
                success = False
            else:
                # No records and no errors = empty file or silent failure
                response_status = status.HTTP_400_BAD_REQUEST
                response_message = "No volunteers were created from the uploaded file"
                success = False
        elif len(created_records) < len(volunteers_data):
            # Partial success
            response_status = status.HTTP_207_MULTI_STATUS
            response_message = f"Partial success: {len(created_records)} of {len(volunteers_data)} volunteers created"
            success = True
        else:
            # All successful
            response_status = status.HTTP_201_CREATED
            response_message = f"Successfully created {len(created_records)} volunteers"
            success = True

        # Get organization types for response
        from models.organization_type import OrganizationType
        org_types = list(OrganizationType.objects.values('id', 'code', 'name', 'description').order_by('name'))

        return Response({
            "status": "success" if success else "error",
            "status_code": response_status,
            "message": response_message,
            "data": {
                "created_count": len(created_records),
                "created_mis_ids": created_records,
                "total_rows": len(volunteers_data),
                "error_count": len(errors),
                "row_results": row_results,
                "errors": errors,
                "warnings": warnings + (
                    [
                        f"SECURITY: Youth org admin account - all volunteers assigned to your state/district ({db_user.state_id.name if db_user.state_id else 'N/A'}, {db_user.district_id.name if db_user.district_id else 'N/A'}) and organization {'ID: ' + str(user_org_id) if user_org_id else '(none assigned)'} regardless of Excel/form values"
                    ]
                    if user_role == "YOUTH_ORG_ADMIN" else []
                ),
                "organization_types": org_types,
                "bulk_upload_session": {
                    "id": bulk_upload_session.id,
                    "uploaded_at": bulk_upload_session.uploaded_at.isoformat(),
                    "status": bulk_upload_session.status,
                    "volunteers_created": bulk_upload_session.volunteers_created,
                    "total_rows": bulk_upload_session.total_rows_in_file,
                    "file_name": bulk_upload_session.file_name
                }
            }
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
        # For JWT-authenticated users, check if user_role attribute exists
        try:
            # First try to get user_role from request.user (works for some token types)
            user_role = getattr(user, "user_role", None)
            
            # If user_role is attached to JWT, use it
            if user_role and user_role in self.ALLOWED_ROLES:
                return True
            
            # Otherwise query the database to get the role
            from django.contrib.auth import get_user_model
            from models.role import UserRole, Permission
            
            User = get_user_model()
            db_user = User.objects.get(id=user.id)
            user_role = db_user.user_role
            
            # Check if role is in the allowed list
            if user_role in self.ALLOWED_ROLES:
                return True
            
            # If role not in whitelist, check if they have view_volunteer permission
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

        # If YOUTH_ORG_ADMIN, scope volunteers to their organization (if mapped) or to their state+district
        if user_role == "YOUTH_ORG_ADMIN":
            user_org = _resolve_user_organization(db_user)
            if user_org:
                volunteers = volunteers.filter(organization_id=user_org.id)
            else:
                if user_state and user_district:
                    volunteers = volunteers.filter(state_id=user_state, district_id=user_district)
                else:
                    volunteers = volunteers.none()
        
        # Filter by user role
        if user_role in ("SDMA_ADMIN", "STATE_ADMIN") and user_state:
            volunteers = volunteers.filter(state_id=user_state)
        elif user_role == "DISTRICT_ADMIN" and user_state and user_district:
            volunteers = volunteers.filter(state_id=user_state, district_id=user_district)
        
        # Group by state, district, organization, and bulk upload session so each
        # upload batch appears as a separate row in the coverage table.
        coverage_data = []
        grouped = volunteers.exclude(
            Q(state__isnull=True) | Q(district__isnull=True)
        ).values(
            'state__id',
            'state__name',
            'district__id',
            'district__name',
            'organization__id',
            'organization__name',
            'bulk_upload_session_id',
            'bulk_upload_session__file_name',
            'bulk_upload_session__uploaded_at'
        ).annotate(
            volunteer_count=Count('id'),
            latest_date=Max('created_at')
        ).order_by('-bulk_upload_session__uploaded_at', '-latest_date', 'state__name', 'district__name', 'organization__name')
        
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
                'bulk_upload_session_id': record['bulk_upload_session_id'],
                'upload_file_name': record['bulk_upload_session__file_name'],
                'session_download_url': _build_session_export_url(record['bulk_upload_session_id']),
                'excel_download_url': _build_session_export_url(record['bulk_upload_session_id']) or _build_org_export_url(record['organization__id']),
                'organization_type_id': org_data['org_type_id'],
                'organization_type_code': org_data['org_type_code'],
                'organization_type': org_data['org_type_name'],
                'no_of_volunteers': record['volunteer_count'],
                'date': (
                    record['bulk_upload_session__uploaded_at'].strftime('%Y-%m-%d %H:%M:%S')
                    if record['bulk_upload_session__uploaded_at']
                    else record['latest_date'].strftime('%Y-%m-%d %H:%M:%S') if record['latest_date'] else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            })
        
        # Summary statistics for tabular format (excluding only null state/district, org is optional)
        valid_volunteers = volunteers.exclude(
            Q(state__isnull=True) | Q(district__isnull=True)
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

        # YOUTH_ORG_ADMIN: scope to organization(s) they manage OR to their state/district
        if user_role == "YOUTH_ORG_ADMIN":
            from models.role import UserRole
            user_role_obj = UserRole.objects.filter(user=db_user).first()
            if user_role_obj and user_role_obj.organization:
                try:
                    org_id = int(user_role_obj.organization)
                    orgs = orgs.filter(id=org_id)
                except Exception:
                    orgs = orgs.filter(name__iexact=user_role_obj.organization)
            elif user_state and user_district:
                orgs = orgs.filter(state_id=user_state, district_id=user_district)
            else:
                orgs = orgs.none()

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
        # For JWT-authenticated users, check if user_role attribute exists
        try:
            # First try to get user_role from request.user (works for some token types)
            user_role = getattr(user, "user_role", None)
            
            # If user_role is attached to JWT, use it
            if user_role and user_role in self.ALLOWED_ROLES:
                return True
            
            # Otherwise query the database to get the role
            from django.contrib.auth import get_user_model
            from models.role import UserRole, Permission
            
            User = get_user_model()
            db_user = User.objects.get(id=user.id)
            user_role = db_user.user_role
            
            # Check if role is in the allowed list
            if user_role in self.ALLOWED_ROLES:
                return True
            
            # If role not in whitelist, check if they have view_volunteer permission
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

        # If YOUTH_ORG_ADMIN, scope volunteers to their organization (if mapped) or to their state+district
        if user_role == "YOUTH_ORG_ADMIN":
            user_org = _resolve_user_organization(db_user)
            if user_org:
                volunteers = volunteers.filter(organization_id=user_org.id)
            else:
                if user_state and user_district:
                    volunteers = volunteers.filter(state_id=user_state, district_id=user_district)
                else:
                    volunteers = volunteers.none()
        
        # Filter by user role
        if user_role in ("SDMA_ADMIN", "STATE_ADMIN") and user_state:
            volunteers = volunteers.filter(state_id=user_state)
        elif user_role == "DISTRICT_ADMIN" and user_state and user_district:
            volunteers = volunteers.filter(state_id=user_state, district_id=user_district)
        
        # Build coverage data: STATE | DISTRICT | ORGANIZATION | NO. OF VOL. | UPLOADS | DATE
        coverage_data = []
        
        # Group by state, district, organization (organization is optional)
        from django.db.models import Q, F
        from django.db.models import Count as DjangoCount, Case, When, IntegerField
        
        grouped = volunteers.exclude(
            Q(state__isnull=True) | Q(district__isnull=True)
        ).values(
            'state__id',
            'state__name',
            'district__id',
            'district__name',
            'organization__id',
            'organization__name'
        ).annotate(
            volunteer_count=Count('id'),
            # Count only non-null bulk_upload_session IDs
            upload_count=Count('bulk_upload_session_id', distinct=True, filter=Q(bulk_upload_session_id__isnull=False)),
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
                'excel_download_url': _build_org_export_url(record['organization__id']),
                'organization_type_id': org_data['org_type_id'],
                'organization_type_code': org_data['org_type_code'],
                'organization_type': org_data['org_type_name'],
                'no_of_volunteers': record['volunteer_count'],
                'upload_count': record['upload_count'],  # ✨ NEW: How many bulk uploads for this group
                'date': record['latest_date'].strftime('%Y-%m-%d %H:%M:%S') if record['latest_date'] else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Summary statistics - exclude incomplete records (org is optional)
        valid_volunteers = volunteers.exclude(
            Q(state__isnull=True) | Q(district__isnull=True)
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
        organization_id = request.query_params.get('organization_id')
        bulk_upload_session_id = request.query_params.get('bulk_upload_session_id')

        # Filter volunteers based on role and geography
        volunteers = Volunteer.objects.filter(deleted_at__isnull=True)
        file_name = f"volunteers_{db_user.id}.xlsx"

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
            user_org = _resolve_user_organization(db_user)
            if user_org:
                if organization_id and str(user_org.id) != str(organization_id):
                    return Response(
                        {"error": "You can only export volunteers for your assigned organization"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                volunteers = volunteers.filter(organization_id=user_org.id)
                file_name = f"volunteers_{_safe_filename_part(user_org.name)}_{db_user.id}.xlsx"
            elif user_state and user_district:
                volunteers = volunteers.filter(state_id=user_state, district_id=user_district)
                file_name = f"volunteers_{user_state.name}_{user_district.name}_{db_user.id}.xlsx"
            else:
                volunteers = volunteers.none()
                file_name = f"volunteers_org_{db_user.id}.xlsx"
        else:  # SUPER_ADMIN, NATIONAL_ADMIN
            file_name = f"volunteers_all_{db_user.id}.xlsx"

        if organization_id and user_role not in ["YOUTH_ORG_ADMIN"]:
            try:
                volunteers = volunteers.filter(organization_id=int(organization_id))
            except (TypeError, ValueError):
                return Response(
                    {"error": "Invalid organization_id parameter"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if bulk_upload_session_id:
            try:
                session_id_int = int(bulk_upload_session_id)
            except (TypeError, ValueError):
                return Response(
                    {"error": "Invalid bulk_upload_session_id parameter"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            session = BulkUploadSession.objects.filter(id=session_id_int).first()
            if not session:
                return Response(
                    {"error": "Bulk upload session not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            session_volunteers = volunteers.filter(bulk_upload_session_id=session_id_int)
            if not session_volunteers.exists():
                return Response(
                    {"error": "You do not have permission to export this bulk upload session"},
                    status=status.HTTP_403_FORBIDDEN
                )

            volunteers = session_volunteers
            file_stub = _safe_filename_part(session.file_name or f"bulk_upload_session_{session_id_int}")
            file_name = f"{file_stub}_{session_id_int}.xlsx"

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


# ============================================================================
# DOWNLOAD TEMPLATE ENDPOINT - Bulk Upload Excel Template
# ============================================================================

class DownloadBulkUploadTemplateAPIView(APIView):
    """
    GET /api/v1/volunteer/bulk-upload/template/
    
    Download the Excel template for bulk volunteer upload.
    For use by Youth Organizations and authorized administrators.
    
    Returns: Excel file (.xlsx) with proper headers and formatting
    Permissions: SUPER_ADMIN, NDMA_ADMIN, SDMA_ADMIN, DDMA_NODAL_OFFICER, YOUTH_ORG_ADMIN
    """
    permission_classes = [IsAuthenticated]

    ALLOWED_ROLES = [
        "SUPER_ADMIN",
        "NDMA_ADMIN",
        "SDMA_ADMIN",
        "DDMA_NODAL_OFFICER",
        "YOUTH_ORG_ADMIN",
    ]

    def get(self, request):
        """Download the bulk upload Excel template - Generated Dynamically"""
        
        # Check user permissions
        from django.contrib.auth import get_user_model
        User = get_user_model()
        db_user = User.objects.select_related('state_id', 'district_id').get(id=request.user.id)
        user_role = db_user.user_role
        if user_role not in self.ALLOWED_ROLES:
            return Response(
                {
                    "error": "You do not have permission to download the bulk upload template",
                    "allowed_roles": self.ALLOWED_ROLES
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
            from io import BytesIO
            
            # Get user's state and district names for pre-filling
            user_state_name = ""
            user_district_name = ""
            user_org_id = ""
            user_org_name = ""
            
            if db_user.state_id:
                user_state_name = db_user.state_id.name if hasattr(db_user.state_id, 'name') else str(db_user.state_id)
            if db_user.district_id:
                user_district_name = db_user.district_id.name if hasattr(db_user.district_id, 'name') else str(db_user.district_id)
            
            # For YOUTH_ORG_ADMIN, also get their organization
            if user_role == "YOUTH_ORG_ADMIN":
                user_org = _resolve_user_organization(db_user)
                if user_org:
                    user_org_id = user_org.id
                    user_org_name = user_org.name

            # Create workbook
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Volunteers"

            # Define headers - EXACT field names that match upload API
            headers = [
                "mis_id",
                "name",
                "salutation",
                "gender",
                "dob",
                "blood_group",
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
            ]

            # Write headers
            for col_idx, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_idx, value=header)
                cell.font = Font(bold=True, color="FFFFFF", size=11)
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            # Set column widths
            column_widths = {
                'A': 12, 'B': 20, 'C': 14, 'D': 12, 'E': 12, 'F': 14, 'G': 14, 'H': 12,
                'I': 18, 'J': 14, 'K': 16, 'L': 18, 'M': 14, 'N': 16, 'O': 14, 'P': 14,
                'Q': 18, 'R': 14, 'S': 14, 'T': 13, 'U': 14, 'V': 14, 'W': 20, 'X': 14,
                'Y': 16, 'Z': 12,
            }
            for col, width in column_widths.items():
                ws.column_dimensions[col].width = width

            # Add sample data - pre-filled with user's state/district
            # All rows will have user's assigned state, district, and organization
            sample_data = [
                ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", user_org_id, user_org_name, user_state_name, user_district_name, "", "", "", "", "", "", "", ""],
                ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", user_org_id, user_org_name, user_state_name, user_district_name, "", "", "", "", "", "", "", ""],
                ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", user_org_id, user_org_name, user_state_name, user_district_name, "", "", "", "", "", "", "", ""],
            ]

            for row_idx, row_data in enumerate(sample_data, 2):
                for col_idx, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=value)
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                    if row_idx <= 3:
                        cell.fill = PatternFill(start_color="E8F4F8", end_color="E8F4F8", fill_type="solid")
            
            # DO NOT auto-fill empty rows - only 3 sample rows should have state/district
            # Users will fill rows 4 onwards manually

            # ADD DATA VALIDATION FOR STATE AND DISTRICT DROPDOWNS - RELIABLE METHOD
            try:
                from openpyxl.worksheet.datavalidation import DataValidation
                from models.state import State
                from models.district import District
                
                # GET DATA FROM DATABASE (no status filter - all states/districts available)
                states = list(State.objects.all().order_by('name').values_list('name', flat=True))
                districts = list(District.objects.all().order_by('name').values_list('name', flat=True))
                
                # FALLBACK IF DATABASE IS EMPTY
                if not states:
                    states = ["Maharashtra", "Gujarat", "Goa", "Karnataka", "Tamil Nadu"]
                if not districts:
                    districts = ["Mumbai", "Pune", "Ahmedabad", "Surat", "Goa", "Bangalore"]
                
                # CREATE REFERENCE SHEET FOR DROPDOWNS (hidden from user)
                ref_ws = wb.create_sheet("_DataValidation")
                ref_ws.sheet_state = 'hidden'  # Hide this sheet
                
                # Write states to reference sheet column A
                for idx, state in enumerate(states, 1):
                    ref_ws.cell(row=idx, column=1, value=state)
                
                # Write districts to reference sheet column B
                for idx, district in enumerate(districts, 1):
                    ref_ws.cell(row=idx, column=2, value=district)
                
                # STATE DROPDOWN - References the hidden sheet
                # Soft validation - allows custom entries not in dropdown
                state_validation = DataValidation(
                    type="list",
                    formula1=f"=_DataValidation!$A$1:$A${len(states)}",
                    allow_blank=True,
                    showDropDown=True
                )
                state_validation.error = 'Please select a valid state from the list'
                state_validation.errorTitle = 'Invalid State'
                state_validation.prompt = 'Type or select state from dropdown'
                state_validation.promptTitle = 'State Selection'
                state_validation.showInputMessage = True
                state_validation.showErrorMessage = False  # Don't block custom entries (soft validation)
                ws.add_data_validation(state_validation)
                state_validation.add(f'R2:R1000')  # Apply to state_name column
                
                # DISTRICT DROPDOWN - References the hidden sheet
                # Soft validation - allows custom entries not in dropdown
                district_validation = DataValidation(
                    type="list",
                    formula1=f"=_DataValidation!$B$1:$B${len(districts)}",
                    allow_blank=True,
                    showDropDown=True
                )
                district_validation.error = 'Please select a valid district from the list'
                district_validation.errorTitle = 'Invalid District'
                district_validation.prompt = 'Type or select district from dropdown'
                district_validation.promptTitle = 'District Selection'
                district_validation.showInputMessage = True
                district_validation.showErrorMessage = False  # Don't block custom entries (soft validation)
                ws.add_data_validation(district_validation)
                district_validation.add(f'S2:S1000')  # Apply to district_name column
                
            except Exception as e:
                # If data validation fails, continue without dropdowns
                import traceback
                traceback.print_exc()

            # Add Instructions sheet
            instructions_ws = wb.create_sheet("Instructions")
            instructions_ws.column_dimensions['A'].width = 80

            instructions = [
                ("VOLUNTEER BULK UPLOAD - FIELD GUIDE", 14, True),
                ("", 11, False),
                ("REQUIRED FIELDS (must fill):", 12, True),
                ("  • mis_id - Unique ID for volunteer (integer, must be unique)", 11, False),
                ("  • name - Full name of volunteer (text, max 100 characters)", 11, False),
                ("  • mobile - 10 digit phone number", 11, False),
                ("  • state_name - State name (e.g. Maharashtra, Gujarat, Delhi)", 11, False),
                ("  • district_name - District name (e.g. Mumbai, Ahmedabad, New Delhi)", 11, False),
                ("", 11, False),
                ("FIELD VALUE EXAMPLES:", 12, True),
                ("  • salutation - Mr., Mrs., Ms., Dr., Prof.", 11, False),
                ("  • gender - Male, Female, Other", 11, False),
                ("  • dob - Date format: 1990-05-15 (YYYY-MM-DD)", 11, False),
                ("  • blood_group - A+, A-, B+, B-, O+, O-, AB+, AB-", 11, False),
                ("  • aadhar - 12 digit number (unique)", 11, False),
                ("  • email - valid email (unique)", 11, False),
                ("  • maritalstatus - Single, Married, Divorced, Widowed, Separated", 11, False),
                ("  • education - Below 10th, 10th Pass, 12th Pass, Diploma, Bachelor, Master, PhD, Other", 11, False),
                ("  • skill - First Aid, Disaster Management, Rescue Operations, Community Care, Training, Other", 11, False),
                ("  • area_type - Urban, Rural, Semi-Urban", 11, False),
                ("  • organization_id - Numeric ID of organization OR organization_name (text)", 11, False),
                ("", 11, False),
                ("TIPS:", 12, True),
                ("  • Fill mis_id and name for basic data entry", 11, False),
                ("  • All other fields are optional", 11, False),
                ("  • Use exact values shown in examples above (case-insensitive for most fields)", 11, False),
                ("  • Leave optional fields empty if not available", 11, False),
                ("  • Maximum file size: 10 MB", 11, False),
            ]

            for row_idx, (text, size, bold) in enumerate(instructions, 1):
                cell = instructions_ws.cell(row=row_idx, column=1, value=text)
                cell.font = Font(size=size, bold=bold)
                cell.alignment = Alignment(wrap_text=True, vertical="top")
                instructions_ws.row_dimensions[row_idx].height = 20 if size == 14 else 18

            # Save to BytesIO instead of disk
            output = BytesIO()
            wb.save(output)
            output.seek(0)

            # Return as FileResponse
            response = FileResponse(
                output,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            file_name = 'VolunteerBulkUploadTemplate.xlsx'
            if user_role == "YOUTH_ORG_ADMIN" and user_org_name:
                file_name = f'VolunteerBulkUploadTemplate_{_safe_filename_part(user_org_name)}.xlsx'
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            response['X-User-Role'] = user_role
            response['X-Downloaded-At'] = __import__('datetime').datetime.now().isoformat()
            
            return response

        except Exception as e:
            return Response(
                {
                    "error": "Error downloading template file",
                    "detail": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
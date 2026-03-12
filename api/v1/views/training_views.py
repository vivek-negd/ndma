from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from django.db.models import Q, Count
from django.db import IntegrityError
from datetime import datetime

from models.training import TrainingSchedule, TrainingSession
from models.training_media import TrainingSessionMedia
from api.v1.serializers.training_serializers import TrainingScheduleSerializer
from core.constants import UserRoles, ErrorMessages


class TrainingScheduleViewSet(viewsets.ModelViewSet):
    queryset = TrainingSchedule.objects.all().order_by('-created_at')
    serializer_class = TrainingScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter training schedules based on user role and state/district scope.
        
        - SUPER_ADMIN: All trainings
        - NDMA_ADMIN: All trainings
        - SDMA_ADMIN: Only trainings in their assigned state
        - DDMA_NODAL_OFFICER: Only trainings in their assigned district (AND state validation)
        - Others: Only trainings in their state (if assigned)
        """
        user = self.request.user
        queryset = TrainingSchedule.objects.all().order_by('-created_at')
        
        # SUPER_ADMIN and NDMA_ADMIN can see all trainings
        if getattr(user, 'user_role', None) in UserRoles.ADMIN_ROLES:
            return queryset
        
        # SDMA_ADMIN: Only trainings in their state
        if getattr(user, 'user_role', None) == UserRoles.SDMA_ADMIN:
            if getattr(user, 'state_id', None):
                return queryset.filter(state_id=user.state_id)
            return TrainingSchedule.objects.none()  # No state assigned, return empty
        
        # DDMA_NODAL_OFFICER: Only trainings in their district AND state
        if getattr(user, 'user_role', None) == UserRoles.DDMA_NODAL_OFFICER:
            user_district = getattr(user, 'district_id', None)
            user_state = getattr(user, 'state_id', None)
            
            if user_district and user_state:
                # Filter by BOTH district AND state to avoid data inconsistency issues
                return queryset.filter(district_id=user_district, state_id=user_state)
            return TrainingSchedule.objects.none()  # No district/state assigned, return empty
        
        # Other roles: Trainings in their state (if assigned)
        if getattr(user, 'state_id', None):
            return queryset.filter(state_id=user.state_id)
        
        # Default: No access
        return TrainingSchedule.objects.none()

    def _check_create_permission(self, request):
        """Check if user has role permission to create/modify trainings"""
        allowed_roles = [
            UserRoles.SUPER_ADMIN,
            UserRoles.NDMA_ADMIN,
            UserRoles.SDMA_ADMIN,
            UserRoles.DDMA_NODAL_OFFICER,
            UserRoles.TRAINING_INSTITUTE,
            UserRoles.YOUTH_ORG_ADMIN,
        ]
        if getattr(request.user, 'user_role', None) not in allowed_roles:
            raise PermissionDenied(ErrorMessages.INSUFFICIENT_ROLE_CREATE_TRAINING)

    def _check_geographic_scope(self, request, action='create'):
        """
        Validate that user can only create/update trainings in their geographic scope.
        
        SUPER_ADMIN/NDMA_ADMIN: Can create in any state/district
        SDMA_ADMIN: Can only create in their assigned state
        DDMA_NODAL_OFFICER: Can only create in their assigned district AND state
        """
        user = request.user
        user_role = getattr(user, 'user_role', None)
        
        # SUPER_ADMIN/NDMA_ADMIN: No restriction
        if user_role in UserRoles.ADMIN_ROLES:
            return True
        
        # Get state_id and district_id from request data
        request_state_id = request.data.get('state')
        request_district_id = request.data.get('district')
        
        # Validate required fields
        if not request_state_id:
            raise PermissionDenied(ErrorMessages.STATE_REQUIRED)
        
        try:
            request_state_id = int(request_state_id)
        except (ValueError, TypeError):
            raise PermissionDenied(ErrorMessages.INVALID_STATE)
        
        # SDMA_ADMIN: Must create in their state only
        if user_role == UserRoles.SDMA_ADMIN:
            user_state_id = getattr(user, 'state_id', None)
            if not user_state_id:
                raise PermissionDenied(ErrorMessages.NO_STATE_ASSIGNED)
            
            # Ensure user_state_id is an integer (it could be a State object)
            if hasattr(user_state_id, 'id'):
                user_state_id = user_state_id.id
            else:
                user_state_id = int(user_state_id)
            
            # Check if requested state matches user's state
            if request_state_id != user_state_id:
                raise PermissionDenied(ErrorMessages.STATE_MISMATCH)
            return True
        
        # DDMA_NODAL_OFFICER: Must create in their district AND state
        if user_role == UserRoles.DDMA_NODAL_OFFICER:
            user_state_id = getattr(user, 'state_id', None)
            user_district_id = getattr(user, 'district_id', None)
            
            if not user_state_id or not user_district_id:
                raise PermissionDenied(ErrorMessages.NO_DISTRICT_ASSIGNED)
            
            # Ensure IDs are integers (they could be model objects)
            if hasattr(user_state_id, 'id'):
                user_state_id = user_state_id.id
            else:
                user_state_id = int(user_state_id)
            
            if hasattr(user_district_id, 'id'):
                user_district_id = user_district_id.id
            else:
                user_district_id = int(user_district_id)
            
            # Validate district field
            if not request_district_id:
                raise PermissionDenied(ErrorMessages.DISTRICT_REQUIRED)
            
            try:
                request_district_id = int(request_district_id)
            except (ValueError, TypeError):
                raise PermissionDenied(ErrorMessages.INVALID_DISTRICT)
            
            # Check if requested state AND district match user's scope
            if request_state_id != user_state_id:
                raise PermissionDenied(ErrorMessages.STATE_MISMATCH)
            
            if request_district_id != user_district_id:
                raise PermissionDenied(ErrorMessages.DISTRICT_MISMATCH)
            return True
        
        # Other roles: Check if they have geographic scope restrictions
        return True

    def create(self, request, *args, **kwargs):
        """Create training schedule with geographic scope validation"""
        self._check_create_permission(request)
        self._check_geographic_scope(request, 'create')  # ← NEW: Validate geographic scope
        
        # set created_by automatically
        request.data['created_by'] = getattr(request.user, 'id', None)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update training schedule with geographic scope validation"""
        self._check_create_permission(request)
        self._check_geographic_scope(request, 'update')  # ← NEW: Validate geographic scope
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete training schedule with geographic scope validation"""
        self._check_create_permission(request)
        self._check_geographic_scope(request, 'delete')  # ← NEW: Validate geographic scope
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_daywise(self, request):
        """
        Create training day-by-day (progressive day-wise approach).
        
        ✅ VALIDATION:
        - Day must be valid (1, 4, or 7 ONLY)
        - Batch number MUST exist OR must be for Day 1 with state
        - If batch_no doesn't exist and day is 4 or 7 → ERROR
        
        First day (creates new training with all fields):
        {
            "state": 1,
            "district": 5,
            "batch_no": "FEB2026-MH-MUM-001",
            "organization_name": "NCC Unit A",
            "organization_type": "NCC",
            "number_of_volunteers": 100,
            "day": 1,
            "day_date": "2026-03-15",
            "day_notes": "Opening ceremony"
        }
        
        Subsequent days (adds to existing batch):
        {
            "batch_no": "FEB2026-MH-MUM-001",
            "day": 4,
            "day_date": "2026-03-18",
            "day_notes": "Practical training"
        }
        """
        self._check_create_permission(request)
        
        batch_no = request.data.get('batch_no')
        day = request.data.get('day')
        day_date = request.data.get('day_date')
        day_notes = request.data.get('day_notes', '')
        
        # Validate required fields
        if not batch_no or not day or not day_date:
            return Response(
                {
                    'status_code': 400,
                    'errors': {
                        'batch_no': 'Required' if not batch_no else None,
                        'day': 'Required (1, 4, or 7)' if not day else None,
                        'day_date': 'Required (YYYY-MM-DD)' if not day_date else None,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ✅ FIXED: Validate day is ONLY 1, 4, or 7
        try:
            day = int(day)
            valid_days = [1, 4, 7]
            if day not in valid_days:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {
                    'status_code': 400,
                    'error': 'Day must be one of: 1, 4, or 7',
                    'valid_days': [1, 4, 7],
                    'provided_value': day
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ✅ FIXED: Check if batch already exists
        training = TrainingSchedule.objects.filter(batch_no=batch_no).first()
        
        if training:
            # ✅ Batch exists - just add this day
            self._check_geographic_scope(request, 'update')
        else:
            # ✅ FIXED: Batch DOES NOT exist
            
            # ✅ NEW CHECK: Only allow NEW batch creation for Day 1
            if day != 1:
                return Response(
                    {
                        'status_code': 404,
                        'error': f'Training batch "{batch_no}" not found in system',
                        'hint': f'Batch must exist to add Day {day}. Create Day 1 first or use existing batch_no',
                        'provided_batch_no': batch_no,
                        'attempted_day': day
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # ✅ For Day 1, state is required to create NEW batch
            self._check_geographic_scope(request, 'create')
            
            state = request.data.get('state')
            if not state:
                return Response(
                    {
                        'status_code': 400,
                        'error': 'state is required to create new batch',
                        'hint': 'Provide state ID to create new training batch',
                        'creating_for': 'New batch (first time)',
                        'batch_no': batch_no
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # ✅ Validate all required fields for NEW batch on Day 1
            required_fields = {
                'organization_name': 'Organization name',
                'organization_type': 'Organization type',
                'number_of_volunteers': 'Number of volunteers',
                'institute_details': 'Institute details',
                'trainers_details': 'Trainers details',
            }
            
            missing_fields = {}
            for field, label in required_fields.items():
                if not request.data.get(field):
                    missing_fields[field] = f'{label} is required'
            
            if missing_fields:
                return Response(
                    {
                        'status_code': 400,
                        'error': 'Missing required fields for new batch',
                        'missing_fields': missing_fields,
                        'hint': 'All fields required for Day 1 batch creation'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # ✅ Create NEW training schedule (only reachable for Day 1 with state)
            training_data = {
                'state_id': state,
                'district_id': request.data.get('district'),
                'organization_name': request.data.get('organization_name'),
                'organization_type': request.data.get('organization_type', 'OTHER'),
                'number_of_volunteers': request.data.get('number_of_volunteers', 0),
                'batch_no': batch_no,
                'institute_details': request.data.get('institute_details'),
                'trainers_details': request.data.get('trainers_details'),
                'created_by_id': getattr(request.user, 'id', None),
                'status': 'DRAFT',
            }
            
            try:
                training = TrainingSchedule.objects.create(**training_data)
            except IntegrityError as e:
                # ✅ Catch duplicate batch_no (shouldn't happen after above checks)
                if 'batch_no' in str(e).lower():
                    return Response(
                        {
                            'status_code': 400,
                            'error': f'Batch "{batch_no}" already exists (concurrent creation detected)',
                            'hint': 'Try again or use different batch number'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                raise
            except Exception as e:
                return Response(
                    {
                        'status_code': 400,
                        'error': f'Failed to create training: {str(e)}'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create or get session for this day
        day_label = f"Day {day}"
        session, created = TrainingSession.objects.get_or_create(
            schedule=training,
            day_label=day_label,
            defaults={
                'date': day_date,
                'notes': day_notes,
            }
        )
        
        if not created:
            # Update existing session
            session.date = day_date
            session.notes = day_notes
            session.save()
        
        return Response(
            {
                'status_code': 201 if created else 200,
                'message': f'Training {day_label} {"created" if created else "updated"}',
                'data': {
                    'id': training.id,
                    'batch_no': training.batch_no,
                    'organization_name': training.organization_name,
                    'state_id': training.state_id,
                    'district_id': training.district_id,
                    'day_created': day,
                    'total_days': training.sessions.count(),
                    'session': {
                        'id': session.id,
                        'schedule_id': training.id,
                        'day_label': session.day_label,
                        'date': str(session.date),
                        'session_number': day,
                    }
                }
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def training_report(self, request):
        """
        Generate training report with day-wise breakdown.
        
        Query Parameters:
        - day: "day_1" or "day_4" or "day_7" (required)
        - batch_no: "FEB2026-MH-MUM-001" (optional - filter by batch)
        - from_date: "YYYY-MM-DD" (optional)
        - to_date: "YYYY-MM-DD" (optional)
        - state_id: State ID (optional, auto-filled for non-admin users)
        - district_id: District ID (optional, for DDMA officers)
        - status: "DRAFT" | "APPROVED" | "PUBLISHED" (optional)
        
        Returns:
        {
            "status_code": 200,
            "message": "Day 1 Training Report",
            "filters": {
                "day": "day_1",
                "from_date": "2026-03-01",
                "to_date": "2026-03-31",
                "state_id": null,
                "district_id": null
            },
            "summary": {
                "total_trainings": 5,
                "total_states": 3,
                "total_districts": 5,
                "total_volunteers": 450,
                "total_media": 18
            },
            "data": [
                {
                    "id": 1,
                    "state": "Maharashtra",
                    "district": "Mumbai",
                    "organization": "NCC Unit-A",
                    "org_type": "NCC",
                    "no_of_volunteers": 100,
                    "batch_no": "FEB2026",
                    "institute_details": "XYZ Institute",
                    "trainers": "Dr. ABC, Prof XYZ",
                    "session_date": "2026-03-20",
                    "day_label": "Day 1",
                    "total_media": 4,
                    "status": "PUBLISHED"
                },
                ...
            ]
        }
        """
        day_label = request.query_params.get('day', '').lower()
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        state_id = request.query_params.get('state_id')
        district_id = request.query_params.get('district_id')
        sched_status = request.query_params.get('status')
        batch_no = request.query_params.get('batch_no')
        
        # Validate day parameter
        day_map = {
            'day_1': 'Day 1',
            'day_4': 'Day 4',
            'day_7': 'Day 7',
            'day1': 'Day 1',
            'day4': 'Day 4',
            'day7': 'Day 7',
        }
        
        if day_label not in day_map:
            return Response(
                {
                    'status_code': 400,
                    'error': 'Invalid day parameter. Use: day_1, day_4, or day_7'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        day_label_mapped = day_map[day_label]
        
        # Get user's queryset based on role and scope
        queryset = self.get_queryset()
        
        # Filter by status
        if sched_status:
            queryset = queryset.filter(status=sched_status)
        
        # Filter by state_id from query parameter or user context
        if state_id:
            queryset = queryset.filter(state_id=state_id)
        
        # Filter by district_id
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        
        # Filter by batch_no
        if batch_no:
            queryset = queryset.filter(batch_no=batch_no)
        
        # Build training report with day-wise sessions
        report_data = []
        
        for schedule in queryset:
            # Get sessions for this day
            sessions = schedule.sessions.filter(day_label=day_label_mapped)
            
            for session in sessions:
                # Count media for this session
                media_count = session.media_files.count()
                
                # Check if session date falls within the date range
                session_date = session.date
                
                if from_date:
                    try:
                        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
                        if session_date < from_date_obj:
                            continue
                    except ValueError:
                        pass
                
                if to_date:
                    try:
                        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
                        if session_date > to_date_obj:
                            continue
                    except ValueError:
                        pass
                
                # Build record
                record = {
                    'id': schedule.id,
                    'state': schedule.state.name if schedule.state else 'N/A',
                    'state_id': schedule.state_id,
                    'district': schedule.district.name if schedule.district else 'N/A',
                    'district_id': schedule.district_id,
                    'organization': schedule.organization_name or (schedule.organization.name if schedule.organization else 'N/A'),
                    'org_type': schedule.organization_type or 'N/A',
                    'no_of_volunteers': schedule.number_of_volunteers,
                    'batch_no': schedule.batch_no or 'N/A',
                    'institute_details': schedule.institute_details or 'N/A',
                    'trainers': schedule.trainers_details or 'N/A',
                    'session_date': str(session.date) if session.date else 'N/A',
                    'day_label': session.day_label,
                    'total_media': media_count,
                    'status': schedule.status,
                }
                report_data.append(record)
        
        # Calculate summary statistics
        total_trainings = len(set([r['id'] for r in report_data]))
        total_states = len(set([r['state_id'] for r in report_data if r['state_id'] is not None]))
        total_districts = len(set([r['district_id'] for r in report_data if r['district_id'] is not None]))
        total_volunteers = sum([r['no_of_volunteers'] for r in report_data])
        total_media = sum([r['total_media'] for r in report_data])
        
        return Response(
            {
                'status_code': 200,
                'message': f'{day_label_mapped} Training Report',
                'filters': {
                    'day': day_label,
                    'batch_no': batch_no,
                    'from_date': from_date,
                    'to_date': to_date,
                    'state_id': state_id,
                    'district_id': district_id,
                    'status': sched_status,
                },
                'summary': {
                    'total_trainings': total_trainings,
                    'total_states': total_states,
                    'total_districts': total_districts,
                    'total_volunteers': total_volunteers,
                    'total_media': total_media,
                },
                'data': report_data,
                'count': len(report_data)
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def list_batch_numbers(self, request):
        """
        Get list of existing batch numbers from created training schedules.
        
        Query Parameters:
        - state_id: Filter by state (optional, auto-filled for SDMA_ADMIN)
        - district_id: Filter by district (optional, auto-filled for DDMA officers)
        - status: Filter by status "DRAFT" | "APPROVED" | "PUBLISHED" (optional)
        - search: Search batch number by keyword (optional)
        - limit: Max results (default: 100, max: 500)
        
        Returns:
        {
            "status_code": 200,
            "message": "Batch numbers retrieved successfully",
            "count": 5,
            "data": ["BATCH-2026-001", "BATCH-2026-002", "BATCH-2026-003", ...]
        }
        """
        state_id = request.query_params.get('state_id')
        district_id = request.query_params.get('district_id')
        status_filter = request.query_params.get('status')
        search = request.query_params.get('search', '').strip()
        
        try:
            limit = int(request.query_params.get('limit', 100))
            limit = min(limit, 500)  # Max 500
        except (ValueError, TypeError):
            limit = 100
        
        # Get user's queryset based on role and scope
        queryset = self.get_queryset()
        
        # Apply filters
        if state_id:
            try:
                queryset = queryset.filter(state_id=int(state_id))
            except (ValueError, TypeError):
                pass
        
        if district_id:
            try:
                queryset = queryset.filter(district_id=int(district_id))
            except (ValueError, TypeError):
                pass
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Search by batch number
        if search:
            queryset = queryset.filter(batch_no__icontains=search)
        
        # Get distinct batch numbers
        trainings = queryset.order_by('-created_at').values_list('batch_no', flat=True).distinct()[:limit]
        batch_list = list(trainings)
        
        return Response(
            {
                'status_code': 200,
                'message': 'Batch numbers retrieved successfully',
                'count': len(batch_list),
                'data': batch_list
            },
            status=status.HTTP_200_OK
        )


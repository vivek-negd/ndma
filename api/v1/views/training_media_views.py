from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied

from models.training_media import TrainingSessionMedia
from models.training import TrainingSession
from api.v1.serializers.training_serializers import TrainingSessionMediaSerializer


class TrainingSessionMediaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing training session media files (images).
    
    Endpoints:
    - GET /api/v1/training-session-media/ - List all media files
    - POST /api/v1/training-session-media/ - Upload single image
    - GET /api/v1/training-session-media/{id}/ - Get specific media
    - DELETE /api/v1/training-session-media/{id}/ - Delete media
    - POST /api/v1/training-session-media/upload_for_session/ - Upload multiple images
    """

    queryset = TrainingSessionMedia.objects.all().order_by('-uploaded_at')
    serializer_class = TrainingSessionMediaSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        """Filter by session if provided in query parameters"""
        queryset = TrainingSessionMedia.objects.all().order_by('-uploaded_at')
        session_id = self.request.query_params.get('session_id')

        if session_id:
            queryset = queryset.filter(session_id=session_id)

        return queryset

    def perform_create(self, serializer):
        """
        Override to automatically set uploaded_by to current user
        and validate max 4 images per session
        """
        session_id = self.request.data.get('session')

        if not session_id:
            raise PermissionDenied('session is required')

        try:
            session = TrainingSession.objects.get(id=session_id)
        except TrainingSession.DoesNotExist:
            raise PermissionDenied('Session not found')

        # Check existing media count (max 4)
        existing_count = TrainingSessionMedia.objects.filter(session=session).count()

        if existing_count >= 4:
            raise PermissionDenied(
                f'Max 4 images allowed per session. Current: {existing_count}'
            )

        serializer.save(uploaded_by=self.request.user, session=session)

    def destroy(self, request, *args, **kwargs):
        """Delete media file"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
                'status_code': 204,
                'message': 'Media file deleted successfully'
            },
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['post'])
    def upload_for_session(self, request):
        """
        Upload multiple images for a specific training session.

        Request:
        - session_id: Required (integer) - Training session ID
        - images: File(s) - Multiple image files (1-4 files)

        Example:
        curl -X POST ".../training-session-media/upload_for_session/" \\
          -H "Authorization: Bearer TOKEN" \\
          -F "session_id=100" \\
          -F "images=@image1.jpg" \\
          -F "images=@image2.jpg"
        """
        session_id = request.data.get('session_id')

        if not session_id:
            return Response(
                {
                    'status_code': 400,
                    'error': 'session_id is required in request data'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if session exists
        try:
            session = TrainingSession.objects.get(id=session_id)
        except TrainingSession.DoesNotExist:
            return Response(
                {
                    'status_code': 404,
                    'error': f'Session with id {session_id} not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Get uploaded files
        image_files = request.FILES.getlist('images')

        if not image_files:
            return Response(
                {
                    'status_code': 400,
                    'error': 'No image files provided. Use "images" field'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check number of files
        if len(image_files) < 1 or len(image_files) > 4:
            return Response(
                {
                    'status_code': 400,
                    'error': f'Upload 1 to 4 images. You provided: {len(image_files)}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check existing media count (max 4 total)
        existing_count = TrainingSessionMedia.objects.filter(session=session).count()

        if existing_count + len(image_files) > 4:
            return Response(
                {
                    'status_code': 400,
                    'error': f'Max 4 images per session. Current: {existing_count}, '
                             f'Trying to add: {len(image_files)}. '
                             f'Can add: {4 - existing_count} more'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Upload all images
        uploads = []
        errors = []

        for idx, image_file in enumerate(image_files):
            try:
                # Validate using serializer
                serializer_data = {
                    'session': session_id,
                    'image': image_file
                }
                serializer = TrainingSessionMediaSerializer(data=serializer_data)

                if not serializer.is_valid():
                    errors.append({
                        'file': image_file.name,
                        'error': serializer.errors
                    })
                    continue

                # Save media file
                media = serializer.save(
                    uploaded_by=request.user,
                    session=session
                )
                uploads.append(TrainingSessionMediaSerializer(media).data)

            except Exception as e:
                errors.append({
                    'file': image_file.name,
                    'error': str(e)
                })

        if not uploads:
            return Response(
                {
                    'status_code': 400,
                    'message': 'All uploads failed',
                    'errors': errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        response_data = {
            'status_code': 201,
            'message': f'{len(uploads)} image(s) uploaded successfully',
            'uploaded': uploads,
            'session_id': session_id,
            'total_media_in_session': existing_count + len(uploads)
        }

        if errors:
            response_data['partial_errors'] = errors

        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def session_media_count(self, request):
        """
        Get count of media files for a specific session.

        Query Parameters:
        - session_id: Training session ID

        Response:
        {
            'session_id': 100,
            'total_media': 3,
            'max_allowed': 4,
            'can_upload_more': 1
        }
        """
        session_id = request.query_params.get('session_id')

        if not session_id:
            return Response(
                {
                    'status_code': 400,
                    'error': 'session_id is required as query parameter'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = TrainingSession.objects.get(id=session_id)
        except TrainingSession.DoesNotExist:
            return Response(
                {
                    'status_code': 404,
                    'error': f'Session {session_id} not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        media_count = TrainingSessionMedia.objects.filter(session=session).count()

        return Response(
            {
                'status_code': 200,
                'session_id': session_id,
                'total_media': media_count,
                'max_allowed': 4,
                'can_upload_more': 4 - media_count
            },
            status=status.HTTP_200_OK
        )


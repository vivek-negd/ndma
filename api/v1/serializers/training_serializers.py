from rest_framework import serializers
from models.training import TrainingSchedule, TrainingSession
from models.training_media import TrainingSessionMedia


class TrainingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingSession
        fields = ['id', 'day_label', 'date', 'upload_option', 'notes']


class TrainingScheduleSerializer(serializers.ModelSerializer):
    sessions = TrainingSessionSerializer(many=True, required=False)
    state_name = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()

    class Meta:
        model = TrainingSchedule
        fields = [
            'id', 'state', 'state_name', 'district', 'district_name', 'organization', 'organization_name', 'organization_type',
            'number_of_volunteers', 'batch_no', 'institute_details', 'trainers_details',
            'start_date', 'end_date', 'status', 'upload_option', 'sessions'
        ]
    
    def get_state_name(self, obj):
        """Get state name from related State object"""
        if obj.state:
            return obj.state.name
        return None
    
    def get_district_name(self, obj):
        """Get district name from related District object"""
        if obj.district:
            return obj.district.name
        return None

    def get_fields(self):
        fields = super().get_fields()
        # lazy import to avoid circular imports at module import time
        from models.state import State
        from models.district import District
        fields['state'] = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())
        fields['district'] = serializers.PrimaryKeyRelatedField(queryset=District.objects.all(), allow_null=True, required=False)
        return fields

    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and start > end:
            raise serializers.ValidationError('start_date must be before end_date')
        return data

    def create(self, validated_data):
        sessions_data = validated_data.pop('sessions', [])
        schedule = TrainingSchedule.objects.create(**validated_data)
        for s in sessions_data:
            # ensure session date within schedule bounds if provided
            date = s.get('date')
            if date and schedule.start_date and schedule.end_date:
                if date < schedule.start_date or date > schedule.end_date:
                    raise serializers.ValidationError('Session date must be within schedule start and end dates')
            TrainingSession.objects.create(schedule=schedule, **s)
        return schedule

    def update(self, instance, validated_data):
        sessions_data = validated_data.pop('sessions', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if sessions_data is not None:
            # simple replace semantics: delete existing and recreate
            instance.sessions.all().delete()
            for s in sessions_data:
                TrainingSession.objects.create(schedule=instance, **s)

        return instance

class TrainingSessionMediaSerializer(serializers.ModelSerializer):
    session_day = serializers.CharField(source='session.day_label', read_only=True)
    batch_no = serializers.CharField(source='session.schedule.batch_no', read_only=True)
    
    class Meta:
        model = TrainingSessionMedia
        fields = ['id', 'session', 'session_day', 'batch_no', 'image', 'file_size', 'file_name', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['id', 'file_size', 'file_name', 'uploaded_at', 'session_day', 'batch_no']

    def validate_image(self, value):
        """
        Validate image file:
        - Max size: 3 MB (3145728 bytes)
        - Format: JPG, JPEG, PNG
        """
        max_size = 3145728  # 3 MB in bytes

        if value.size > max_size:
            size_mb = value.size / 1048576
            raise serializers.ValidationError(
                f'Image size must be max 3 MB. Your file: {size_mb:.2f} MB'
            )

        # Check format
        if not value.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise serializers.ValidationError(
                'Only JPG, JPEG, and PNG formats are allowed'
            )

        return value
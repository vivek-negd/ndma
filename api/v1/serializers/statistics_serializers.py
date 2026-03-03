"""
Serializers for State and District models with volunteer count statistics
"""
from rest_framework import serializers
from models.state import State
from models.district import District


class StateSerializer(serializers.ModelSerializer):
    """Serializer for State model including volunteer statistics"""
    
    class Meta:
        model = State
        fields = [
            'id', 
            'name', 
            'lgd_code', 
            'volunteer_count',
            'created_at',
            'updated_at',
            'deleted_at'
        ]
        read_only_fields = ['id', 'volunteer_count', 'created_at', 'updated_at', 'deleted_at']


class DistrictSerializer(serializers.ModelSerializer):
    """Serializer for District model including volunteer statistics"""
    state_name = serializers.CharField(source='state.name', read_only=True)
    
    class Meta:
        model = District
        fields = [
            'id',
            'name',
            'lgd_code',
            'state_id',
            'state_name',
            'volunteer_count',
            'created_at',
            'updated_at',
            'deleted_at'
        ]
        read_only_fields = [
            'id', 
            'volunteer_count', 
            'created_at', 
            'updated_at', 
            'deleted_at',
            'state_name'
        ]


class StateDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for State including districts"""
    districts = DistrictSerializer(many=True, read_only=True)
    
    class Meta:
        model = State
        fields = [
            'id',
            'name',
            'lgd_code',
            'volunteer_count',
            'created_at',
            'updated_at',
            'deleted_at',
            'districts'
        ]
        read_only_fields = ['id', 'volunteer_count', 'created_at', 'updated_at', 'deleted_at', 'districts']


class VolunteerStatisticsSerializer(serializers.Serializer):
    """Serializer for volunteer statistics"""
    total_volunteers = serializers.IntegerField()
    total_states_with_volunteers = serializers.IntegerField()
    total_districts_with_volunteers = serializers.IntegerField()
    top_states = serializers.ListField()
    top_districts = serializers.ListField()

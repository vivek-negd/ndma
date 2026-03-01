from rest_framework import serializers
from models.organization import Organization
from models.state import State
from models.district import District


class OrganizationSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    volunteer_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'org_type', 'state', 'state_name', 
            'district', 'district_name', 'contact_person', 'contact_email',
            'contact_phone', 'address', 'website', 'is_active', 
            'volunteer_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'volunteer_count']
    
    def get_volunteer_count(self, obj):
        return obj.volunteer_count
    
    def get_fields(self):
        """Build FK fields at runtime to avoid circular imports"""
        fields = super().get_fields()
        fields['state'] = serializers.PrimaryKeyRelatedField(
            queryset=State.objects.all()
        )
        fields['district'] = serializers.PrimaryKeyRelatedField(
            queryset=District.objects.all()
        )
        return fields
    
    def validate(self, data):
        """Ensure district belongs to selected state"""
        state = data.get('state')
        district = data.get('district')
        
        if state and district:
            if district.state_id != state.id:
                raise serializers.ValidationError(
                    "Selected district must belong to selected state"
                )
        
        return data


class OrganizationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list view"""
    state_name = serializers.CharField(source='state.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    volunteer_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'org_type', 'state_name', 'district_name',
            'contact_email', 'volunteer_count'
        ]
    
    def get_volunteer_count(self, obj):
        return obj.volunteer_count

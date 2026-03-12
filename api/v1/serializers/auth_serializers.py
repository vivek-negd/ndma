from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from models.user import ROLE_CHOICES

User = get_user_model()


class UserLoginSerializer(serializers.Serializer):
    """Login serializer"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Try a case-insensitive lookup first (handles UI-created users)
        try:
            user = User.objects.filter(email_address__iexact=email).first()
        except Exception:
            user = None

        # If user found, check password directly
        if user:
            if not user.check_password(password):
                raise serializers.ValidationError("Invalid email or password")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            data['user'] = user
            return data

        # Fallback to Django authenticate (handles configured backends)
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")
        data['user'] = user
        return data


class UserCreateSerializer(serializers.ModelSerializer):
    """Create user - SUPER_ADMIN/NDMA_ADMIN only. ALL fields required."""
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(source='email_address')
    state_id = serializers.IntegerField(required=False, allow_null=True)
    district_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ['email', 'name', 'mobile', 'designation', 'aadhar', 'user_role', 'password', 'state_id', 'district_id', 'is_active']
        extra_kwargs = {
            'name': {'required': True},
            'mobile': {'required': True},
            'designation': {'required': False},
            'aadhar': {'required': False},
            'user_role': {'required': True},
        }
    
    def validate_user_role(self, value):
        """Validate role exists in ROLE_CHOICES"""
        from models.user import ROLE_CHOICES
        valid_roles = [choice[0] for choice in ROLE_CHOICES]
        if value not in valid_roles:
            raise serializers.ValidationError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        return value

    def validate_mobile(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError('Mobile must be a 10 digit number')
        return value

    def validate_aadhar(self, value):
        if not value.isdigit() or len(value) != 12:
            raise serializers.ValidationError('Aadhar must be a 12 digit number')
        return value
    
    def validate_state_id(self, value):
        from models.state import State
        if not State.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"State with ID {value} does not exist")
        return value
    
    def validate_district_id(self, value):
        # Handle empty string or None
        if value is None or value == '' or value == 0:
            return None
        
        from models.district import District
        # Validate that district exists
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise serializers.ValidationError("district_id must be a valid integer")
        
        if not District.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"District with ID {value} does not exist")
        return value
    
    def create(self, validated_data):
        from models.state import State
        from models.district import District
        
        email = validated_data.pop('email_address')
        password = validated_data.pop('password')
        state_id = validated_data.pop('state_id', None)
        district_id = validated_data.pop('district_id', None)
        
        # Convert IDs to instances
        if state_id:
            state = State.objects.get(id=state_id)
            validated_data['state_id'] = state
        
        # Only convert district if provided
        if district_id:
            district = District.objects.get(id=district_id)
            validated_data['district_id'] = district
        else:
            # Explicitly set to None if not provided
            validated_data['district_id'] = None
        
        user = User.objects.create_user(
            email_address=email,
            password=password,
            **validated_data
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """User details serializer"""
    email = serializers.CharField(source='email_address', read_only=True)
    role_display = serializers.SerializerMethodField(read_only=True)
    permissions = serializers.SerializerMethodField(read_only=True)
    state_name = serializers.CharField(source='state_id.name', read_only=True, allow_null=True)
    district_name = serializers.CharField(source='district_id.name', read_only=True, allow_null=True)
    
    def get_role_display(self, obj):
        """Get human-readable role name"""
        if obj.user_role:
            role_dict = dict(ROLE_CHOICES)
            return role_dict.get(obj.user_role, obj.user_role)
        return ""
    
    def get_permissions(self, obj):
        """Get all effective permissions for the user"""
        try:
            return obj.get_effective_permissions()
        except Exception:
            return []
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'mobile', 'designation', 'aadhar', 'user_role', 'role_display', 'state_id', 'state_name', 'district_id', 'district_name', 'is_active', 'permissions']
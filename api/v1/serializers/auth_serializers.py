from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()


class UserLoginSerializer(serializers.Serializer):
    """Login serializer"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
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
    name = serializers.CharField(required=True, allow_blank=False)
    mobile = serializers.CharField(required=True, allow_blank=False)
    designation = serializers.CharField(required=True, allow_blank=False)
    aadhar = serializers.CharField(required=True, allow_blank=False)
    user_role = serializers.CharField(required=True, allow_blank=False)
    state_code = serializers.CharField(required=True, allow_blank=False)
    
    class Meta:
        model = User
        fields = ['email', 'name', 'mobile', 'designation', 'aadhar', 'user_role', 'password', 'state_code', 'district_code', 'block_code', 'is_active']
        extra_kwargs = {
            'name': {'required': True},
            'mobile': {'required': True},
            'designation': {'required': True},
            'aadhar': {'required': True},
            'user_role': {'required': True},
            'state_code': {'required': True},
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
    
    def create(self, validated_data):
        email = validated_data.pop('email_address')
        password = validated_data.pop('password')
        user = User.objects.create_user(
            email_address=email,
            password=password,
            **validated_data
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """User details serializer"""
    email = serializers.CharField(source='email_address', read_only=True)
    role_display = serializers.CharField(source='get_user_role_display', read_only=True)
    permissions = serializers.SerializerMethodField(read_only=True)
    
    def get_permissions(self, obj):
        """Get all effective permissions for the user"""
        try:
            return obj.get_effective_permissions()
        except Exception:
            return []
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'mobile', 'designation', 'aadhar', 'user_role', 'role_display', 'state_code', 'district_code', 'block_code', 'is_active', 'permissions']
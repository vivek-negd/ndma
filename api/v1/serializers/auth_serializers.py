from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from models.roles import UserRole

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
    """Create user - SUPER_ADMIN only"""
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(source='email_address')
    
    class Meta:
        model = User
        fields = ['email', 'user_role', 'password', 'state_code', 'district_code', 'block_code', 'is_active']
    
    def validate_user_role(self, value):
        """Validate role exists"""
        if value not in dict(UserRole.choices):
            raise serializers.ValidationError(f"Invalid role: {value}")
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
    
    class Meta:
        model = User
        fields = ['id', 'email', 'user_role', 'role_display', 'state_code', 'district_code', 'block_code', 'is_active']
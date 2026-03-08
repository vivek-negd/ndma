 

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import status
import logging

from models.role import UserRole, Permission
from core.logger import logger

User = get_user_model()


class AuthService:
    """
    Authentication service for handling login, token generation, and user validation
    """

    @staticmethod
    def authenticate_user(email_address, password):
        """
        Authenticate user with email and password
        
        Args:
            email_address (str): User's email address
            password (str): User's password (plain text)
            
        Returns:
            dict: {
                'success': bool,
                'status_code': int,
                'message': str,
                'data': {
                    'access': JWT access token,
                    'refresh': JWT refresh token,
                    'user': User object with permissions
                } or None if failed
            }
        """
        try:
            # Step 1: Validate input
            if not email_address or not password:
                return {
                    'success': False,
                    'status_code': 400,
                    'message': 'Email and password are required',
                    'data': None
                }

            # Step 2: Query user from database
            try:
                user = User.objects.get(email_address=email_address)
            except User.DoesNotExist:
                logger.warning(f"Login attempt with non-existent email: {email_address}")
                return {
                    'success': False,
                    'status_code': 401,
                    'message': 'Invalid email or password',
                    'data': None
                }

            # Step 3: Check if user is active
            if not user.is_active:
                logger.warning(f"Login attempt with inactive user: {email_address}")
                return {
                    'success': False,
                    'status_code': 401,
                    'message': 'User account is inactive',
                    'data': None
                }

            # Step 4: Verify password
            if not check_password(password, user.password):
                logger.warning(f"Invalid password for user: {email_address}")
                return {
                    'success': False,
                    'status_code': 401,
                    'message': 'Invalid email or password',
                    'data': None
                }

            # Step 5: Generate JWT tokens
            tokens = AuthService.generate_tokens(user)
            if not tokens['success']:
                return {
                    'success': False,
                    'status_code': 500,
                    'message': 'Error generating tokens',
                    'data': None
                }

            # Step 6: Get user permissions
            permissions = AuthService.get_user_permissions(user)

            # Step 7: Prepare user data
            user_data = {
                'id': user.id,
                'email_address': user.email_address,
                'name': user.name,
                'user_role': user.user_role,
                'state_id': user.state_id,
                'state_name': user.state.name if user.state else None,
                'district_id': user.district_id,
                'district_name': user.district.name if user.district else None,
                'is_active': user.is_active,
                'permissions': permissions
            }

            logger.info(f"User logged in successfully: {email_address} (Role: {user.user_role})")

            return {
                'success': True,
                'status_code': 200,
                'message': 'Login successful',
                'data': {
                    'access': tokens['access'],
                    'refresh': tokens['refresh'],
                    'user': user_data
                }
            }

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {
                'success': False,
                'status_code': 500,
                'message': 'Authentication error occurred',
                'data': None
            }

    @staticmethod
    def generate_tokens(user):
        """
        Generate JWT access and refresh tokens for user
        
        Args:
            user (User): User object
            
        Returns:
            dict: {
                'success': bool,
                'access': access token string,
                'refresh': refresh token string,
                'message': error message if failed
            }
        """
        try:
            refresh = RefreshToken.for_user(user)
            
            # Add custom claims to refresh token
            refresh['user_id'] = user.id
            refresh['email'] = user.email_address
            refresh['role'] = user.user_role
            refresh['state_id'] = user.state_id
            refresh['district_id'] = user.district_id
            
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            logger.info(f"Tokens generated for user: {user.email_address}")
            
            return {
                'success': True,
                'access': access_token,
                'refresh': refresh_token,
                'message': None
            }
        except Exception as e:
            logger.error(f"Token generation error: {str(e)}")
            return {
                'success': False,
                'access': None,
                'refresh': None,
                'message': f"Token generation failed: {str(e)}"
            }

    @staticmethod
    def verify_token(token):
        """
        Verify JWT token and extract user information
        
        Args:
            token (str): JWT token string
            
        Returns:
            dict: {
                'success': bool,
                'user_id': extracted user ID or None,
                'payload': token payload dict or None,
                'message': error message if failed
            }
        """
        try:
            decoded_token = RefreshToken(token)
            user_id = decoded_token.get('user_id')
            
            return {
                'success': True,
                'user_id': user_id,
                'payload': dict(decoded_token),
                'message': None
            }
        except TokenError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return {
                'success': False,
                'user_id': None,
                'payload': None,
                'message': f"Token verification failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return {
                'success': False,
                'user_id': None,
                'payload': None,
                'message': f"Token verification error: {str(e)}"
            }

    @staticmethod
    def refresh_access_token(refresh_token):
        """
        Generate new access token from refresh token
        
        Args:
            refresh_token (str): Refresh token string
            
        Returns:
            dict: {
                'success': bool,
                'access': new access token or None,
                'message': error message if failed
            }
        """
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            
            logger.info(f"Access token refreshed")
            
            return {
                'success': True,
                'access': access_token,
                'message': None
            }
        except TokenError as e:
            logger.warning(f"Token refresh failed: {str(e)}")
            return {
                'success': False,
                'access': None,
                'message': f"Token refresh failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return {
                'success': False,
                'access': None,
                'message': f"Token refresh error: {str(e)}"
            }

    @staticmethod
    def get_user_permissions(user):
        """
        Get list of permissions for a user based on their role
        
        Args:
            user (User): User object
            
        Returns:
            list: List of permission code strings
        """
        try:
            # Query user role
            user_role = UserRole.objects.filter(user=user).first()
            
            if not user_role or not user_role.role:
                logger.warning(f"No role assigned to user: {user.email_address}")
                return []
            
            # Get permissions assigned to this role
            permissions = Permission.objects.filter(
                role=user_role.role
            ).values_list('code', flat=True)
            
            return list(permissions)
        
        except Exception as e:
            logger.error(f"Error fetching user permissions: {str(e)}")
            return []

    @staticmethod
    def validate_user_access(user, required_roles=None, required_permissions=None):
        """
        Validate if user has required role or permissions
        
        Args:
            user (User): User object
            required_roles (list): List of required role strings
            required_permissions (list): List of required permission codes
            
        Returns:
            dict: {
                'has_access': bool,
                'reason': str (if no access)
            }
        """
        try:
            # Check if user is active
            if not user.is_active:
                return {
                    'has_access': False,
                    'reason': 'User account is inactive'
                }
            
            # Check role requirement
            if required_roles:
                if not isinstance(required_roles, list):
                    required_roles = [required_roles]
                
                if user.user_role not in required_roles:
                    return {
                        'has_access': False,
                        'reason': f'User role {user.user_role} not in required roles: {required_roles}'
                    }
            
            # Check permission requirement
            if required_permissions:
                if not isinstance(required_permissions, list):
                    required_permissions = [required_permissions]
                
                user_permissions = AuthService.get_user_permissions(user)
                
                for permission in required_permissions:
                    if permission not in user_permissions:
                        return {
                            'has_access': False,
                            'reason': f'User missing required permission: {permission}'
                        }
            
            return {
                'has_access': True,
                'reason': None
            }
        
        except Exception as e:
            logger.error(f"Access validation error: {str(e)}")
            return {
                'has_access': False,
                'reason': 'Access validation error occurred'
            }

    @staticmethod
    def get_user_by_email(email_address):
        """
        Get user object by email address
        
        Args:
            email_address (str): User's email address
            
        Returns:
            User object or None
        """
        try:
            return User.objects.get(email_address=email_address)
        except User.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error fetching user: {str(e)}")
            return None

    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user object by user ID
        
        Args:
            user_id (int): User's ID
            
        Returns:
            User object or None
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error fetching user: {str(e)}")
            return None

    @staticmethod
    def check_user_state_access(user, state_id):
        """
        Check if user has access to a specific state
        Used for RBAC enforcement
        
        Args:
            user (User): User object
            state_id (int): State ID to check access
            
        Returns:
            bool: True if user has access, False otherwise
        """
        try:
            # SUPER_ADMIN/NDMA_ADMIN can access all states
            if user.user_role in ['SUPER_ADMIN', 'NDMA_ADMIN', 'TECHNICAL_ADMIN']:
                return True
            
            # SDMA_ADMIN can only access their assigned state
            if user.user_role == 'SDMA_ADMIN':
                return user.state_id == state_id
            
            # DDMA_NODAL_OFFICER can access their state
            if user.user_role == 'DDMA_NODAL_OFFICER':
                return user.state_id == state_id
            
            return False
        
        except Exception as e:
            logger.error(f"State access check error: {str(e)}")
            return False

    @staticmethod
    def check_user_district_access(user, district_id, state_id):
        """
        Check if user has access to a specific district
        Used for RBAC enforcement
        
        Args:
            user (User): User object
            district_id (int): District ID to check access
            state_id (int): State ID to check access
            
        Returns:
            bool: True if user has access, False otherwise
        """
        try:
            # SUPER_ADMIN/NDMA_ADMIN can access all districts
            if user.user_role in ['SUPER_ADMIN', 'NDMA_ADMIN', 'TECHNICAL_ADMIN']:
                return True
            
            # SDMA_ADMIN can access any district in their state
            if user.user_role == 'SDMA_ADMIN':
                return user.state_id == state_id
            
            # DDMA_NODAL_OFFICER can only access their assigned district
            if user.user_role == 'DDMA_NODAL_OFFICER':
                return user.state_id == state_id and user.district_id == district_id
            
            return False
        
        except Exception as e:
            logger.error(f"District access check error: {str(e)}")
            return False

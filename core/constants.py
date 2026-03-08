"""
CONSTANTS & CONFIGURATION
=========================
Centralized constants to avoid hardcoding in API
All role names, permissions, and status codes defined here
"""

# ============================================================================
# USER ROLES
# ============================================================================

class UserRoles:
    """All available user roles in the system"""
    SUPER_ADMIN = 'SUPER_ADMIN'
    NDMA_ADMIN = 'NDMA_ADMIN'
    TECHNICAL_ADMIN = 'TECHNICAL_ADMIN'
    SDMA_ADMIN = 'SDMA_ADMIN'
    DDMA_NODAL_OFFICER = 'DDMA_NODAL_OFFICER'
    TRAINING_INSTITUTE = 'TRAINING_INSTITUTE'
    YOUTH_ORG_ADMIN = 'YOUTH_ORG_ADMIN'
    VOLUNTEER = 'VOLUNTEER'
    
    # Role hierarchy
    ADMIN_ROLES = [SUPER_ADMIN, NDMA_ADMIN, TECHNICAL_ADMIN]
    STATE_LEVEL_ROLES = [SDMA_ADMIN]
    DISTRICT_LEVEL_ROLES = [DDMA_NODAL_OFFICER]
    CREATION_ALLOWED_ROLES = [SUPER_ADMIN, NDMA_ADMIN, SDMA_ADMIN, DDMA_NODAL_OFFICER, TRAINING_INSTITUTE, YOUTH_ORG_ADMIN]
    
    # All roles
    ALL_ROLES = [
        SUPER_ADMIN,
        NDMA_ADMIN,
        TECHNICAL_ADMIN,
        SDMA_ADMIN,
        DDMA_NODAL_OFFICER,
        TRAINING_INSTITUTE,
        YOUTH_ORG_ADMIN,
        VOLUNTEER
    ]


# ============================================================================
# PERMISSIONS
# ============================================================================

class Permissions:
    """All available permissions in the system"""
    VIEW_TRAINING = 'view_training'
    CREATE_TRAINING = 'create_training'
    EDIT_TRAINING = 'edit_training'
    DELETE_TRAINING = 'delete_training'
    
    VIEW_VOLUNTEER = 'view_volunteer'
    CREATE_VOLUNTEER = 'create_volunteer'
    EDIT_VOLUNTEER = 'edit_volunteer'
    DELETE_VOLUNTEER = 'delete_volunteer'
    
    VIEW_ORGANIZATION = 'view_organization'
    CREATE_ORGANIZATION = 'create_organization'
    EDIT_ORGANIZATION = 'edit_organization'
    DELETE_ORGANIZATION = 'delete_organization'
    
    VIEW_REPORTS = 'view_reports'
    VIEW_DEPLOYMENT = 'view_deployment'
    
    MANAGE_USERS = 'manage_users'
    MANAGE_RBAC = 'manage_rbac'
    MANAGE_ROLES = 'manage_roles'
    
    # All permissions
    ALL_PERMISSIONS = [
        VIEW_TRAINING,
        CREATE_TRAINING,
        EDIT_TRAINING,
        DELETE_TRAINING,
        VIEW_VOLUNTEER,
        CREATE_VOLUNTEER,
        EDIT_VOLUNTEER,
        DELETE_VOLUNTEER,
        VIEW_ORGANIZATION,
        CREATE_ORGANIZATION,
        EDIT_ORGANIZATION,
        DELETE_ORGANIZATION,
        VIEW_REPORTS,
        VIEW_DEPLOYMENT,
        MANAGE_USERS,
        MANAGE_RBAC,
        MANAGE_ROLES,
    ]


# ============================================================================
# TRAINING STATUS
# ============================================================================

class TrainingStatus:
    """Training schedule status options"""
    DRAFT = 'DRAFT'
    APPROVED = 'APPROVED'
    PUBLISHED = 'PUBLISHED'
    ONGOING = 'ONGOING'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    
    CHOICES = [
        (DRAFT, 'Draft'),
        (APPROVED, 'Approved'),
        (PUBLISHED, 'Published'),
        (ONGOING, 'Ongoing'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]


# ============================================================================
# ORGANIZATION TYPES
# ============================================================================

class OrganizationTypes:
    """Organization type options"""
    NCC = 'NCC'
    NSS = 'NSS'
    YOUTH_ORG = 'YOUTH_ORG'
    INSTITUTE = 'INSTITUTE'
    OTHER = 'OTHER'
    
    CHOICES = [
        (NCC, 'NCC'),
        (NSS, 'NSS'),
        (YOUTH_ORG, 'Youth Organisation'),
        (INSTITUTE, 'Institute'),
        (OTHER, 'Other'),
    ]


# ============================================================================
# VOLUNTEER STATUS
# ============================================================================

class VolunteerStatus:
    """Volunteer status options"""
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    SUSPENDED = 'SUSPENDED'
    GRADUATED = 'GRADUATED'
    
    CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
        (SUSPENDED, 'Suspended'),
        (GRADUATED, 'Graduated'),
    ]


# ============================================================================
# ERROR MESSAGES
# ============================================================================

class ErrorMessages:
    """Standardized error messages"""
    # Authentication
    INVALID_CREDENTIALS = 'Invalid email or password'
    INACTIVE_ACCOUNT = 'User account is inactive'
    MISSING_CREDENTIALS = 'Email and password are required'
    
    # Permissions
    INSUFFICIENT_ROLE = 'Insufficient role to perform this action'
    INSUFFICIENT_ROLE_CREATE_USER = 'Only SUPER_ADMIN/NDMA_ADMIN/TECHNICAL_ADMIN can create users'
    INSUFFICIENT_ROLE_CREATE_TRAINING = 'Insufficient role to create or modify training schedules'
    INSUFFICIENT_ROLE_CREATE_ORG = 'Insufficient role to create organizations'
    
    # Geographic scope
    NO_STATE_ASSIGNED = 'Your account has no state assigned'
    NO_DISTRICT_ASSIGNED = 'Your account has no district assigned'
    STATE_MISMATCH = 'SDMA_ADMIN can only create trainings in their assigned state'
    DISTRICT_MISMATCH = 'DDMA_NODAL_OFFICER can only create trainings in their assigned district'
    
    # Validation
    STATE_REQUIRED = 'state field is required'
    DISTRICT_REQUIRED = 'district field is required'
    INVALID_STATE = 'state must be a valid integer'
    INVALID_DISTRICT = 'district must be a valid integer'
    
    # Data
    INVALID_PASSWORD_OLD = 'Old password is incorrect'
    ROLE_NOT_FOUND = 'Role not found in database'
    USER_NOT_FOUND = 'User not found'


# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

class SuccessMessages:
    """Standardized success messages"""
    LOGIN_SUCCESS = 'Login successful'
    LOGOUT_SUCCESS = 'Logout successful'
    PASSWORD_CHANGED = 'Password changed successfully'
    USER_CREATED = 'User created successfully'
    USER_CREATED_WITH_ROLE = 'User created with privilege successfully'
    TRAINING_CREATED = 'Training schedule created successfully'
    PROFILE_RETRIEVED = 'Profile retrieved successfully'


# ============================================================================
# API RESPONSE CODES
# ============================================================================

class ResponseCodes:
    """HTTP-like response codes used in API"""
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_ERROR = 500


# ============================================================================
# TOKEN CONFIGURATION
# ============================================================================

class TokenConfig:
    """JWT token configuration"""
    ACCESS_TOKEN_LIFETIME_MINUTES = 15
    REFRESH_TOKEN_LIFETIME_DAYS = 7
    ALGORITHM = 'HS256'


# ============================================================================
# RBAC HELPER FUNCTIONS
# ============================================================================

def is_admin_role(role):
    """Check if role is admin-level (full access)"""
    return role in UserRoles.ADMIN_ROLES


def is_state_level_role(role):
    """Check if role is state-level scoped"""
    return role in UserRoles.STATE_LEVEL_ROLES


def is_district_level_role(role):
    """Check if role is district-level scoped"""
    return role in UserRoles.DISTRICT_LEVEL_ROLES


def can_create_training(role):
    """Check if role can create training schedules"""
    return role in [
        UserRoles.SUPER_ADMIN,
        UserRoles.NDMA_ADMIN,
        UserRoles.SDMA_ADMIN,
        UserRoles.DDMA_NODAL_OFFICER,
        UserRoles.TRAINING_INSTITUTE,
    ]


def can_create_user(role):
    """Check if role can create users"""
    return role in [
        UserRoles.SUPER_ADMIN,
        UserRoles.NDMA_ADMIN,
        UserRoles.TECHNICAL_ADMIN,
    ]


def can_create_organization(role):
    """Check if role can create organizations"""
    return role in [
        UserRoles.SUPER_ADMIN,
        UserRoles.NDMA_ADMIN,
        UserRoles.TECHNICAL_ADMIN,
        UserRoles.SDMA_ADMIN,
    ]


# ============================================================================
# EXPORT CONVENIENCE
# ============================================================================

# Make constants easily importable
ROLES = UserRoles
PERMISSIONS = Permissions
TRAINING_STATUS = TrainingStatus
ORG_TYPES = OrganizationTypes
VOLUNTEER_STATUS = VolunteerStatus
ERRORS = ErrorMessages
SUCCESS = SuccessMessages
CODES = ResponseCodes

from models.role import UserRole


# Role hierarchy - lower number = higher authority
ROLE_HIERARCHY = {
    'SUPER_ADMIN': 1,
    'NDMA_ADMIN': 2,
    'TECHNICAL_ADMIN': 2,
    'SDMA_ADMIN': 3,
    'DDMA_NODAL_OFFICER': 4,
    'TRAINING_INSTITUTE': 5,
    'YOUTH_ORG_ADMIN': 5,
    'VOLUNTEER': 6,
    'PUBLIC_USER': 7,
}


def has_role_access(requesting_user, target_user):
    """
    Enforces hierarchical role access.
    Higher authority (lower level number) can access lower.
    Lower cannot access higher.
    """
    
    # Get role levels, default to highest (no access)
    requester_level = ROLE_HIERARCHY.get(requesting_user.user_role, 999)
    target_level = ROLE_HIERARCHY.get(target_user.user_role, 999)
    
    # If either is None or missing, deny access
    if requester_level is None or target_level is None:
        return False
    
    # Requester must have equal or higher authority (lower or equal level number)
    return requester_level <= target_level


def has_geographical_access(requesting_user, target_user):
    """
    Enforces geographical boundary restrictions.
    SUPER_ADMIN can access anywhere.
    NDMA_ADMIN can access anywhere.
    SDMA_ADMIN can only access their state.
    DDMA_NODAL_OFFICER can only access their district.
    """
    
    # Safety check: ensure user has role
    if not requesting_user.user_role:
        return False
    
    # Top-level admins have access everywhere
    if requesting_user.user_role in ['SUPER_ADMIN', 'NDMA_ADMIN', 'TECHNICAL_ADMIN']:
        return True
    
    # State admin can access their state
    if requesting_user.user_role == 'SDMA_ADMIN':
        if requesting_user.state_code and target_user.state_code:
            return requesting_user.state_code == target_user.state_code
        return False
    
    # District admin can access their district
    if requesting_user.user_role == 'DDMA_NODAL_OFFICER':
        if requesting_user.district_code and target_user.district_code:
            return requesting_user.district_code == target_user.district_code
        return False
    
    # Organization admin can access their organization only
    if requesting_user.user_role == 'YOUTH_ORG_ADMIN':
        return requesting_user.id == target_user.id
    
    # Volunteers access only themselves
    if requesting_user.user_role == 'VOLUNTEER':
        return requesting_user.id == target_user.id
    
    return False
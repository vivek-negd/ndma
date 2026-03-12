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
    
    # Extract role names safely (user_role is a string on User model)
    requester_role = getattr(requesting_user, 'user_role', None)
    target_role = getattr(target_user, 'user_role', None)

    # If the target has no role (e.g. Organization, TrainingSchedule),
    # role-hierarchy based restriction does not apply here.
    if target_role is None:
        return True

    # Get role levels, default to lowest authority (large number)
    requester_level = ROLE_HIERARCHY.get(requester_role, 999)
    target_level = ROLE_HIERARCHY.get(target_role, 999)

    # If either role mapping is missing, deny access
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
    
    # Extract role safely
    requester_role = getattr(requesting_user, 'user_role', None)
    if not requester_role:
        return False

    # Top-level admins have access everywhere
    if requester_role in ['SUPER_ADMIN', 'NDMA_ADMIN', 'TECHNICAL_ADMIN']:
        return True

    # Helper to extract id from a field that might be a model instance or raw id
    def _extract_id(field):
        if field is None:
            return None
        try:
            if hasattr(field, 'id'):
                return int(field.id)
            return int(field)
        except Exception:
            return None

    # State admin can access their state
    if requester_role == 'SDMA_ADMIN':
        req_state = _extract_id(getattr(requesting_user, 'state_id', None))
        tgt_state = _extract_id(getattr(target_user, 'state_id', None))
        if req_state is not None and tgt_state is not None:
            return req_state == tgt_state
        return False

    # District admin can access their district
    if requester_role == 'DDMA_NODAL_OFFICER':
        req_district = _extract_id(getattr(requesting_user, 'district_id', None))
        tgt_district = _extract_id(getattr(target_user, 'district_id', None))
        if req_district is not None and tgt_district is not None:
            return req_district == tgt_district
        return False

    # Organization admin can access their organization only (compare organization id if present)
    if requester_role == 'YOUTH_ORG_ADMIN':
        req_org = _extract_id(getattr(requesting_user, 'organization', None))
        tgt_org = _extract_id(getattr(target_user, 'organization', None))
        if req_org is not None and tgt_org is not None:
            return req_org == tgt_org
        # fallback to comparing user identity
        return getattr(requesting_user, 'id', None) == getattr(target_user, 'id', None)

    # Volunteers access only themselves
    if requester_role == 'VOLUNTEER':
        return getattr(requesting_user, 'id', None) == getattr(target_user, 'id', None)

    return False
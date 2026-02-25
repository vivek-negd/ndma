from models.roles import UserRole


ROLE_HIERARCHY = {
    UserRole.SUPER_ADMIN: 1,
    UserRole.NATIONAL_ADMIN: 2,
    UserRole.STATE_ADMIN: 3,
    UserRole.DISTRICT_ADMIN: 4,
    UserRole.BLOCK_ADMIN: 5,
    UserRole.VOLUNTEER: 6,
}


def has_role_access(requesting_user, target_user):
    """
    Enforces BRD hierarchical role access.
    Higher authority can access lower.
    Lower cannot access higher.
    """

    requester_level = ROLE_HIERARCHY.get(requesting_user.user_role)
    target_level = ROLE_HIERARCHY.get(target_user.user_role)

    return requester_level <= target_level


def has_geographical_access(requesting_user, target_user):
    """
    Enforces geographical boundary restrictions.
    """

    if requesting_user.user_role == UserRole.SUPER_ADMIN:
        return True

    if requesting_user.user_role == UserRole.NATIONAL_ADMIN:
        return True

    if requesting_user.user_role == UserRole.STATE_ADMIN:
        return requesting_user.state_code == target_user.state_code

    if requesting_user.user_role == UserRole.DISTRICT_ADMIN:
        return requesting_user.district_code == target_user.district_code

    if requesting_user.user_role == UserRole.BLOCK_ADMIN:
        return requesting_user.block_code == target_user.block_code

    if requesting_user.user_role == UserRole.VOLUNTEER:
        return requesting_user.id == target_user.id

    return False
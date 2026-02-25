ROLE_ACTION_PERMISSION_MATRIX = {

    "SUPER_ADMIN": {
        "User": ["create", "read", "update", "delete"],
        "Resource": ["create", "read", "update", "delete"]
    },

    "STATE_ADMIN": {
        "User": ["create", "read", "update"],
        "Resource": ["create", "read", "update"]
    },

    "DISTRICT_ADMIN": {
        "Resource": ["create", "read"]
    },

    "BLOCK_ADMIN": {
        "Resource": ["read"]
    }
}
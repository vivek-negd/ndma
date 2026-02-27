# API Overview (current endpoints)

Base path: `/api/v1/`

## Auth (JWT)
- `POST /auth/login/` — email/password -> access & refresh tokens. (AllowAny)
- `POST /auth/create_user/` — SUPER_ADMIN creates a user. (Auth: JWT, SUPER_ADMIN)
- `POST /auth/logout/` — placeholder logout response. (Auth: JWT)
- `GET /auth/profile/` — current user profile. (Auth: JWT)
- `POST /auth/change_password/` — change own password. (Auth: JWT)
- `POST /auth/token/refresh/` — refresh JWT (SimpleJWT built-in).

## RBAC
- `GET /rbac/permissions/` — list permissions. (Auth: JWT, SUPER_ADMIN)
- `GET /rbac/permissions/{id}/` — permission detail. (Auth: JWT, SUPER_ADMIN)

- `GET /rbac/roles/` — list roles. (Auth: JWT, SUPER_ADMIN)
- `POST /rbac/roles/` — create role. (Auth: JWT, SUPER_ADMIN)
- `PUT/PATCH /rbac/roles/{id}/` — update role. (Auth: JWT, SUPER_ADMIN)
- `DELETE /rbac/roles/{id}/` — delete role. (Auth: JWT, SUPER_ADMIN)
- `POST /rbac/roles/{id}/assign_permission/` — attach permission. (Auth: JWT, SUPER_ADMIN)
- `POST /rbac/roles/{id}/revoke_permission/` — detach permission. (Auth: JWT, SUPER_ADMIN)

- `GET /rbac/user-roles/` — list user-role mappings. (Auth: JWT; roles: SUPER_ADMIN, TECHNICAL_ADMIN, NDMA_ADMIN)
- `POST /rbac/user-roles/` — create mapping. (same roles)
- `PUT/PATCH /rbac/user-roles/{id}/` — update mapping. (same roles)
- `POST /rbac/user-roles/{id}/activate/` — activate mapping. (same roles)
- `POST /rbac/user-roles/{id}/deactivate/` — deactivate mapping. (same roles)

- `GET /rbac/audit/role-permissions/` — audit log list. (Auth: JWT; roles: SUPER_ADMIN, TECHNICAL_ADMIN)

## Volunteer
- `POST /volunteer/create/` — create single volunteer record. (Auth: JWT; roles: SUPER_ADMIN, NATIONAL_ADMIN, STATE_ADMIN, DISTRICT_ADMIN)
- `POST /volunteer/bulk-upload/` — create many volunteer records. (Auth: JWT; roles: SUPER_ADMIN, NATIONAL_ADMIN, STATE_ADMIN, DISTRICT_ADMIN)

## Notes
- Default DRF permissions in settings require authentication unless overridden (login is AllowAny).
- Legacy routes in `api/v1/auth/routes.py` (LoginAPIView, TestAPIView) are currently **not** included under `/api/v1/` and are unused.

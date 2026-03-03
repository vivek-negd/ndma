# API Documentation - Complete Reference

## Base URL

```
http://localhost:8000/api/v1/
```

---

## Quick Navigation

- **[Authentication](#authentication)** - Login, JWT tokens, user management
- **[Organizations](#organizations)** - Organization management
- **[Volunteers](#volunteers)** - Volunteer upload and management
- **[RBAC](#rbac)** - Role-based access control
- **[Training](#training)** - Training schedules
- **[Statistics](#statistics)** - States and districts data
- **[Health Check](#health-check)** - API monitoring
- **[Error Codes](#error-codes)** - Error handling
- **[Examples](#examples)** - Code examples

---

## Authentication

### POST /auth/login/
**Public endpoint (no auth required)**

Login and get JWT tokens.

```json
Request:
{
    "email": "user@example.com",
    "password": "password123"
}

Response (200 OK):
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "user_role": "SUPER_ADMIN"
    }
}
```

---

### POST /auth/token/refresh/
**Public endpoint**

Refresh expired access token.

```json
Request:
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response (200 OK):
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### POST /auth/create_user/
**Auth Required | Roles: SUPER_ADMIN, NDMA_ADMIN, TECHNICAL_ADMIN**

Create a new user.

```json
Request:
{
    "email": "newuser@example.com",
    "password": "SecurePassword123",
    "first_name": "John",
    "last_name": "Doe",
    "user_role": "STATE_ADMIN"
}

Response (201 Created):
{
    "message": "User created successfully",
    "user": {
        "id": 2,
        "email": "newuser@example.com",
        "user_role": "STATE_ADMIN"
    }
}
```

---

### GET /auth/profile/
**Auth Required | All Users**

Get current user's profile information.

```
Request:
GET /auth/profile/
Authorization: Bearer <access_token>

Response (200 OK):
{
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_role": "SUPER_ADMIN",
    "is_active": true,
    "created_at": "2026-01-15T10:30:00Z"
}
```

---

### POST /auth/change_password/
**Auth Required | All Users**

Change user's password.

```json
Request:
{
    "old_password": "CurrentPassword123",
    "new_password": "NewPassword456"
}

Response (200 OK):
{
    "message": "Password changed successfully"
}
```

---

### POST /auth/logout/
**Auth Required | All Users**

Logout user (optional, mainly for client-side cleanup).

```
Response (200 OK):
{
    "message": "Logout successful"
}
```

---

## Organizations

### GET /organizations/
**Auth Required | All Users**

List all organizations (filtered by role).

```
Query Parameters:
- state: ID - Filter by state
- district: ID - Filter by district
- org_type: STRING - Filter by organization type (NCC, NSS, BSG, NYKS)
- is_active: BOOLEAN - Filter by active status
- search: STRING - Search by name or email
- ordering: STRING - Sort by field (name, org_type, created_at)
- limit: NUMBER - Results per page (default 20)
- offset: NUMBER - Pagination offset

Response (200 OK):
{
    "count": 45,
    "next": "http://localhost:8000/api/v1/organizations/?offset=20",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Red Cross - Maharashtra State",
            "org_type": "NSS",
            "state": 1,
            "district": 5,
            "is_active": true,
            "volunteer_count": 250
        }
    ]
}
```

---

### POST /organizations/
**Auth Required | Roles: SUPER_ADMIN, NDMA_ADMIN, SDMA_ADMIN**

Create a new organization.

```json
Request:
{
    "name": "New Youth Organization",
    "org_type": "NCC",
    "state": 1,
    "district": 5,
    "contact_person": "John Smith",
    "contact_email": "contact@org.com",
    "contact_phone": "9876543210",
    "address": "123 Main Street, City",
    "website": "https://example.com",
    "is_active": true
}

Response (201 Created):
{
    "id": 46,
    "name": "New Youth Organization",
    "org_type": "NCC",
    "state": 1,
    "district": 5,
    "is_active": true,
    "created_at": "2026-03-02T10:00:00Z",
    "volunteer_count": 0
}
```

---

### GET /organizations/{id}/
**Auth Required | All Users**

Get detailed information about an organization.

```
Response (200 OK):
{
    "id": 1,
    "name": "Red Cross - Maharashtra State",
    "org_type": "NSS",
    "state": {
        "id": 1,
        "name": "Maharashtra"
    },
    "district": {
        "id": 5,
        "name": "Mumbai",
        "state": 1
    },
    "contact_person": "Rajesh Kumar",
    "contact_email": "contact@redcross.com",
    "contact_phone": "9876543210",
    "address": "Mumbai Head Office",
    "website": "https://redcross.org",
    "is_active": true,
    "volunteer_count": 250,
    "created_at": "2025-06-15T08:30:00Z",
    "updated_at": "2026-02-20T14:20:00Z"
}
```

---

### PUT /organizations/{id}/
**Auth Required | Roles: SUPER_ADMIN, NDMA_ADMIN, SDMA_ADMIN**

Update an organization (full update - all fields required).

```json
Request:
{
    "name": "Updated Organization Name",
    "org_type": "NSS",
    "state": 1,
    "district": 5,
    "contact_person": "Updated Person",
    "contact_email": "updated@org.com",
    "contact_phone": "9876543211",
    "address": "Updated Address",
    "website": "https://updated.com",
    "is_active": true
}

Response (200 OK):
{
    "id": 1,
    "name": "Updated Organization Name",
    "org_type": "NSS",
    ...
}
```

---

### PATCH /organizations/{id}/
**Auth Required | Roles: SUPER_ADMIN, NDMA_ADMIN, SDMA_ADMIN**

Update an organization (partial update - only provided fields updated).

```json
Request:
{
    "contact_person": "New Contact Person",
    "is_active": false
}

Response (200 OK):
{
    "id": 1,
    "name": "Red Cross - Maharashtra State",
    "contact_person": "New Contact Person",
    "is_active": false,
    ...
}
```

---

### DELETE /organizations/{id}/
**Auth Required | Roles: SUPER_ADMIN, NDMA_ADMIN, TECHNICAL_ADMIN**

Delete an organization.

```
Response (204 No Content):
(Empty body)
```

---

## Volunteers

### POST /volunteer/create/
**Auth Required | Roles: SUPER_ADMIN, NATIONAL_ADMIN, STATE_ADMIN, DISTRICT_ADMIN, YOUTH_ORG_ADMIN**

Create a single volunteer.

```json
Request:
{
    "organization_id": 1,
    "mis_id": 10001,
    "name": "John Smith",
    "salutation": "Mr.",
    "gender": "Male",
    "blood_group": "O+",
    "dob": "1995-05-15",
    "aadhar": "123456789012",
    "mobile": "9876543210",
    "email": "john@example.com",
    "mybharat_id": "MB123456",
    "maritalstatus": "Single",
    "emergency_contact": "9876543211",
    "education": "Bachelor",
    "education_field": "Computer Science",
    "skill": "First Aid",
    "state_name": "Maharashtra",
    "district_name": "Mumbai",
    "area_type": "Urban",
    "postal_code": "400001",
    "town": "Mumbai",
    "village": "Malad",
    "full_address": "123 Main St, Mumbai 400001"
}

Response (201 Created):
{
    "message": "Volunteer uploaded successfully",
    "volunteer_id": 1,
    "organization": "Red Cross India"
}
```

---

### POST /volunteer/bulk-upload/
**Auth Required | Roles: SUPER_ADMIN, NATIONAL_ADMIN, STATE_ADMIN, DISTRICT_ADMIN, YOUTH_ORG_ADMIN**

Bulk upload volunteers via CSV file.

```
Request:
POST /volunteer/bulk-upload/
Content-Type: multipart/form-data

Parameters:
- file: FILE (CSV file with volunteer data)
- organization_id: NUMBER (optional default)
- state_name: STRING (optional default)
- district_name: STRING (optional default)
- expected_count: NUMBER (optional for validation)

CSV Format (27 columns):
mis_id, name, salutation, gender, blood_group, dob, aadhar, mobile, email,
mybharat_id, maritalstatus, emergency_contact, education, education_field,
skill, organization_id, organization_name, state_name, district_name, area_type,
postal_code, town, village, full_address, id_card, certificate, photo

Response (201 Created):
{
    "created_count": 10,
    "created_mis_ids": [10001, 10002, ...],
    "error_count": 0,
    "errors": [],
    "warnings": []
}
```

---

### GET /volunteer/coverage/
**Auth Required | Roles: SUPER_ADMIN, NATIONAL_ADMIN, STATE_ADMIN, DISTRICT_ADMIN, YOUTH_ORG_ADMIN**

Get volunteer coverage statistics by organization.

```
Response (200 OK):
{
    "organizations": [
        {
            "organization_id": 1,
            "organization_name": "Red Cross India",
            "total_volunteers": 250,
            "states": [
                {
                    "state_id": 1,
                    "state_name": "Maharashtra",
                    "volunteer_count": 150,
                    "districts": [
                        {
                            "district_id": 5,
                            "district_name": "Mumbai",
                            "volunteer_count": 100
                        }
                    ]
                }
            ]
        }
    ]
}
```

---

## RBAC (Role-Based Access Control)

### GET /rbac/permissions/
**Auth Required | Roles: SUPER_ADMIN**

List all permissions in the system.

```
Query Parameters:
- search: STRING - Search permissions
- ordering: STRING - Sort by field

Response (200 OK):
{
    "count": 45,
    "results": [
        {
            "id": 1,
            "name": "CREATE_VOLUNTEER",
            "description": "Can create volunteers",
            "category": "VOLUNTEER_MANAGEMENT"
        },
        {
            "id": 2,
            "name": "EDIT_VOLUNTEER",
            "description": "Can edit volunteer records",
            "category": "VOLUNTEER_MANAGEMENT"
        }
    ]
}
```

---

### GET /rbac/roles/
**Auth Required | Roles: SUPER_ADMIN**

List all roles defined in the system.

```
Response (200 OK):
{
    "count": 12,
    "results": [
        {
            "id": 1,
            "name": "SUPER_ADMIN",
            "description": "Super administrator with full access",
            "permissions": [1, 2, 3, ...],
            "created_at": "2025-01-01T00:00:00Z"
        }
    ]
}
```

---

### POST /rbac/roles/
**Auth Required | Roles: SUPER_ADMIN**

Create a new role.

```json
Request:
{
    "name": "CUSTOM_ADMIN",
    "description": "Custom admin role",
    "permissions": [1, 2, 3]
}

Response (201 Created):
{
    "id": 13,
    "name": "CUSTOM_ADMIN",
    "description": "Custom admin role",
    "permissions": [1, 2, 3]
}
```

---

### POST /rbac/roles/{id}/assign_permission/
**Auth Required | Roles: SUPER_ADMIN**

Assign a permission to a role.

```json
Request:
{
    "permission_id": 5
}

Response (200 OK):
{
    "message": "Permission assigned successfully"
}
```

---

### POST /rbac/roles/{id}/revoke_permission/
**Auth Required | Roles: SUPER_ADMIN**

Revoke a permission from a role.

```json
Request:
{
    "permission_id": 5
}

Response (200 OK):
{
    "message": "Permission revoked successfully"
}
```

---

### POST /rbac/user-roles/
**Auth Required | Roles: SUPER_ADMIN**

Assign a role to a user.

```json
Request:
{
    "user_id": 2,
    "role_id": 3
}

Response (201 Created):
{
    "id": 1,
    "user": 2,
    "role": 3,
    "assigned_at": "2026-03-02T10:00:00Z"
}
```

---

### GET /rbac/audit/role-permissions/
**Auth Required | Roles: SUPER_ADMIN**

Get audit log of role and permission changes.

```
Query Parameters:
- user: NUMBER - Filter by user
- action: STRING - Filter by action (ASSIGN, REVOKE)
- limit: NUMBER - Results per page

Response (200 OK):
{
    "count": 120,
    "results": [
        {
            "id": 1,
            "user": 1,
            "role": 3,
            "permission": 5,
            "action": "ASSIGN",
            "timestamp": "2026-03-02T10:00:00Z"
        }
    ]
}
```

---

## Training

### GET /training-schedules/
**Auth Required | All Users**

List all training schedules.

```
Query Parameters:
- state: NUMBER - Filter by state
- training_type: STRING - Filter by type
- status: STRING - Filter by status (SCHEDULED, ONGOING, COMPLETED, CANCELLED)
- search: STRING - Search by title
- ordering: STRING - Sort by field

Response (200 OK):
{
    "count": 15,
    "results": [
        {
            "id": 1,
            "title": "Basic First Aid Training",
            "training_type": "FIRST_AID",
            "description": "Learn basic first aid skills",
            "start_date": "2026-03-15",
            "end_date": "2026-03-20",
            "location": "Mumbai Training Center",
            "max_capacity": 50,
            "current_enrollment": 45,
            "status": "SCHEDULED"
        }
    ]
}
```

---

### POST /training-schedules/
**Auth Required | Roles: TRAINER, SUPER_ADMIN**

Create a new training schedule.

```json
Request:
{
    "title": "Advanced Disaster Management",
    "training_type": "DISASTER_MANAGEMENT",
    "description": "Advanced level disaster management training",
    "start_date": "2026-04-01",
    "end_date": "2026-04-05",
    "location": "New Delhi Training Center",
    "trainer": 2,
    "max_capacity": 30,
    "state": 1
}

Response (201 Created):
{
    "id": 16,
    "title": "Advanced Disaster Management",
    "training_type": "DISASTER_MANAGEMENT",
    "start_date": "2026-04-01",
    "end_date": "2026-04-05",
    "status": "SCHEDULED",
    "created_at": "2026-03-02T10:00:00Z"
}
```

---

### GET /training-schedules/{id}/
**Auth Required | All Users**

Get detailed training schedule information.

```
Response (200 OK):
{
    "id": 1,
    "title": "Basic First Aid Training",
    "training_type": "FIRST_AID",
    "description": "Learn basic first aid skills",
    "start_date": "2026-03-15",
    "end_date": "2026-03-20",
    "location": "Mumbai Training Center",
    "trainer": {
        "id": 2,
        "name": "Dr. Rajesh"
    },
    "max_capacity": 50,
    "current_enrollment": 45,
    "status": "SCHEDULED",
    "created_at": "2026-02-01T08:00:00Z",
    "updated_at": "2026-03-02T10:00:00Z"
}
```

---

### PUT /training-schedules/{id}/
**Auth Required | Roles: TRAINER, SUPER_ADMIN**

Update training schedule (full update).

```json
Request:
{
    "title": "Updated Training Title",
    "status": "ONGOING",
    "max_capacity": 60
}

Response (200 OK):
{
    "id": 1,
    "title": "Updated Training Title",
    "status": "ONGOING",
    "max_capacity": 60,
    ...
}
```

---

### PATCH /training-schedules/{id}/
**Auth Required | Roles: TRAINER, SUPER_ADMIN**

Update training schedule (partial update).

```json
Request:
{
    "status": "COMPLETED"
}

Response (200 OK):
{
    "id": 1,
    "status": "COMPLETED",
    ...
}
```

---

### DELETE /training-schedules/{id}/
**Auth Required | Roles: TRAINER, SUPER_ADMIN**

Delete a training schedule.

```
Response (204 No Content):
(Empty body)
```

---

## Statistics

### GET /states/
**Auth Required | All Users**

List all states with volunteer counts.

```
Query Parameters:
- search: STRING - Search by name
- ordering: STRING - Sort by field (name, volunteer_count)

Response (200 OK):
{
    "count": 28,
    "results": [
        {
            "id": 1,
            "name": "Maharashtra",
            "volunteer_count": 2500,
            "districts_count": 36
        }
    ]
}
```

---

### GET /states/{id}/
**Auth Required | All Users**

Get detailed state information with districts.

```
Response (200 OK):
{
    "id": 1,
    "name": "Maharashtra",
    "volunteer_count": 2500,
    "districts": [
        {
            "id": 5,
            "name": "Mumbai",
            "volunteer_count": 500
        },
        {
            "id": 6,
            "name": "Pune",
            "volunteer_count": 450
        }
    ]
}
```

---

### GET /states/statistics/overview/
**Auth Required | All Users**

Get comprehensive volunteer statistics across all states.

```
Response (200 OK):
{
    "total_volunteers": 50000,
    "total_states": 28,
    "total_districts": 410,
    "top_states": [
        {
            "state_name": "Maharashtra",
            "volunteer_count": 2500
        },
        {
            "state_name": "Gujarat",
            "volunteer_count": 2100
        }
    ]
}
```

---

### GET /districts/
**Auth Required | All Users**

List all districts with volunteer counts.

```
Query Parameters:
- state: NUMBER - Filter by state ID
- search: STRING - Search by name
- ordering: STRING - Sort by field

Response (200 OK):
{
    "count": 410,
    "results": [
        {
            "id": 5,
            "name": "Mumbai",
            "state": 1,
            "state_name": "Maharashtra",
            "volunteer_count": 500
        }
    ]
}
```

---

### GET /districts/{id}/
**Auth Required | All Users**

Get detailed district information.

```
Response (200 OK):
{
    "id": 5,
    "name": "Mumbai",
    "state": {
        "id": 1,
        "name": "Maharashtra"
    },
    "volunteer_count": 500,
    "area_sq_km": 603,
    "population": 20400000,
    "created_at": "2025-12-01T00:00:00Z"
}
```

---

### GET /districts/by_state/{state_id}/
**Auth Required | All Users**

Get all districts for a specific state.

```
Response (200 OK):
{
    "status": "success",
    "data": {
        "state": {
            "id": 1,
            "name": "Maharashtra"
        },
        "districts": [
            {
                "id": 5,
                "name": "Mumbai",
                "volunteer_count": 500
            },
            {
                "id": 6,
                "name": "Pune",
                "volunteer_count": 450
            }
        ],
        "total_districts": 36
    }
}
```

---

## Health Check

### GET /health/status/
**Public endpoint (no auth required)**

Get full system health status.

```
Response (200 OK):
{
    "success": true,
    "code": 200,
    "message": "API healthy",
    "data": {
        "overall_status": "healthy",
        "timestamp": "2026-03-02T10:00:00Z",
        "response_time_ms": 45.2,
        "checks": {
            "database": {
                "status": "healthy",
                "response_time_ms": 5.2
            },
            "cache": {
                "status": "healthy",
                "response_time_ms": 2.1
            },
            "application": {
                "status": "running",
                "uptime_seconds": 3600
            }
        }
    }
}
```

---

### GET /health/alive/
**Public endpoint**

Quick lightweight check - is API running?

```
Response (200 OK):
{
    "success": true,
    "code": 200,
    "message": "API is running",
    "data": {
        "status": "alive",
        "timestamp": "2026-03-02T10:00:00Z"
    }
}
```

---

### GET /health/database/
**Public endpoint**

Check database connectivity.

```
Response (200 OK):
{
    "success": true,
    "data": {
        "status": "healthy",
        "response_time_ms": 5.2,
        "database": "MySQL",
        "pool_size": 10,
        "active_connections": 3
    }
}
```

---

### GET /health/cache/
**Public endpoint**

Check cache system (Redis/Memcached).

```
Response (200 OK):
{
    "success": true,
    "data": {
        "status": "healthy",
        "response_time_ms": 2.1,
        "cache_backend": "Redis",
        "memory_usage_mb": 456,
        "total_keys": 1234
    }
}
```

---

### GET /health/readiness/
**Public endpoint**

Readiness probe - is API ready for traffic?

```
Response (200 OK):
{
    "success": true,
    "data": {
        "ready": true,
        "checks_passed": 4,
        "checks_total": 4
    }
}
```

---

## Metrics

### GET /metrics/system-info/
**Public endpoint**

Get system and API information.

```
Response (200 OK):
{
    "success": true,
    "data": {
        "python_version": "3.10.8",
        "platform": "Linux",
        "django_version": "4.2.5",
        "drf_version": "3.14.0",
        "api_name": "NDMA Volunteer API",
        "environment": "development"
    }
}
```

---

### GET /metrics/version/
**Public endpoint**

Get API version information.

```
Response (200 OK):
{
    "success": true,
    "data": {
        "version": "1.0.0",
        "release_date": "2026-02-01",
        "commit_sha": "abc123def456",
        "build_number": "1234"
    }
}
```

---

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content returned |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflicts (e.g., duplicate mis_id) |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## Examples

See [API_EXAMPLES.md](./API_EXAMPLES.md) for complete code examples.

---

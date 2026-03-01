# NDMA API - Complete User Profile Setup Guide

All user creation and management is **ADMIN-ONLY**. There is NO public signup endpoint.

## Key Principles

1. **NO SIGNUP** - Only SUPER_ADMIN/NDMA_ADMIN/TECHNICAL_ADMIN can create users
2. **NO HARDCODING** - All fields must be provided (name, mobile, designation, aadhar, state_code)
3. **GOVERNMENT FORM COMPLIANT** - Matches official employee onboarding requirements
4. **ROLE-BASED ACCESS** - What you create/see depends on your role and geography

---

## 1. Initial Setup: Create SUPER_ADMIN

**Purpose**: Bootstrap the system with the first administrator.

```bash
python setup_admin.py
```

This interactive script will:
- Prompt for email, name, mobile (10 digits), designation, aadhar (12 digits), state_code, password
- Create SUPER_ADMIN with all required fields
- Show API usage examples

**Example Interactive Input**:
```
NDMA API - Initial Setup
==================================================
Enter SUPER_ADMIN email: admin@ndma.gov.in
Enter full name: Rajesh Kumar
Enter mobile (10 digits): 9876543210
Enter designation: National Director
Enter Aadhar (12 digits): 123456789012
Enter state code: NL
Enter password: SecurePass@123456
```

---

## 2. Login as SUPER_ADMIN

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@ndma.gov.in",
    "password": "SecurePass@123456"
  }'
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "admin@ndma.gov.in",
    "name": "Rajesh Kumar",
    "mobile": "9876543210",
    "designation": "National Director",
    "aadhar": "123456789012",
    "user_role": "SUPER_ADMIN",
    "state_code": "NL",
    "permissions": ["user.create", "org.create", "org.edit", ...],
    "is_active": true
  }
}
```

**Save the `access` token for subsequent API calls**.

---

## 3. Create a New User (SUPER_ADMIN Only)

**Endpoint**: `POST /api/v1/auth/create_user/`

**Required Fields**:
- `email` - unique email address
- `password` - minimum 8 characters, should be strong
- `name` - full name of the person
- `mobile` - exactly 10 digits
- `designation` - job title/position
- `aadhar` - exactly 12 digits (can be masked for privacy, e.g., 123456XXXXXX)
- `user_role` - one of: SUPER_ADMIN, NDMA_ADMIN, SDMA_ADMIN, DDMA_NODAL_OFFICER, YOUTH_ORG_ADMIN, VOLUNTEER, etc.
- `state_code` - state identifier (e.g., "PY" for Puducherry, "NL" for New Delhi)

**Optional Fields**:
- `district_code` - district identifier (if applicable)
- `block_code` - block identifier (if applicable)
- `is_active` - default: true

### Example: Create State Admin (SDMA_ADMIN)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/create_user/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -d '{
    "email": "state_admin@puducherry.gov.in",
    "password": "StateAdmin@2026",
    "name": "Priya Sharma",
    "mobile": "9123456789",
    "designation": "State Disaster Management Authority",
    "aadhar": "987654321012",
    "user_role": "SDMA_ADMIN",
    "state_code": "PY",
    "district_code": null,
    "block_code": null,
    "is_active": true
  }'
```

**Response** (201 Created):
```json
{
  "message": "User created successfully",
  "user": {
    "id": 2,
    "email": "state_admin@puducherry.gov.in",
    "name": "Priya Sharma",
    "mobile": "9123456789",
    "designation": "State Disaster Management Authority",
    "aadhar": "987654321012",
    "user_role": "SDMA_ADMIN",
    "role_display": "SDMA Admin",
    "state_code": "PY",
    "district_code": null,
    "block_code": null,
    "is_active": true,
    "permissions": ["org.view", "org.create", "user.view", ...]
  }
}
```

### Example: Create District Admin (DDMA_NODAL_OFFICER)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/create_user/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "email": "ddma_puducherry@example.com",
    "password": "DistrictAdmin@2026",
    "name": "Anand Verma",
    "mobile": "9111111111",
    "designation": "District Disaster Management",
    "aadhar": "456789123456",
    "user_role": "DDMA_NODAL_OFFICER",
    "state_code": "PY",
    "district_code": "1",
    "block_code": null,
    "is_active": true
  }'
```

### Example: Create Organization Admin (YOUTH_ORG_ADMIN)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/create_user/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "email": "ncc_officer@example.com",
    "password": "OrgAdmin@2026",
    "name": "Captain Vikram Singh",
    "mobile": "9222222222",
    "designation": "NCC Commanding Officer",
    "aadhar": "567890123456",
    "user_role": "YOUTH_ORG_ADMIN",
    "state_code": "PY",
    "district_code": "1",
    "block_code": null,
    "is_active": true
  }'
```

### Example: Create Volunteer

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/create_user/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "email": "volunteer@example.com",
    "password": "VolPass@2026",
    "name": "Sanjana Gupta",
    "mobile": "9333333333",
    "designation": "NCC Cadet",
    "aadhar": "678901234567",
    "user_role": "VOLUNTEER",
    "state_code": "PY",
    "district_code": "1",
    "block_code": null,
    "is_active": true
  }'
```

---

## 4. Available User Roles (Hierarchy)

| Role | Level | Can Create | Scope | Description |
|------|-------|-----------|-------|-------------|
| SUPER_ADMIN | 1 | All | National | Has all permissions, can create any entity anywhere |
| TECHNICAL_ADMIN | 2 | Orgs, Users | National | Technical support and maintenance |
| NDMA_ADMIN | 2 | Orgs, Users | National | National Disaster Management Authority |
| SDMA_ADMIN | 3 | Orgs, Users | State | State Disaster Management Authority (only for their state) |
| DDMA_NODAL_OFFICER | 4 | Volunteers | District | District-level officer (only for their district) |
| TRAINING_INSTITUTE | 5 | Trainings | Organization | Can manage training programs |
| YOUTH_ORG_ADMIN | 5 | Volunteers | Organization | Organization administrator (NCC/NSS/BSG/NYKS) |
| VOLUNTEER | 6 | None | Self | Regular volunteer with limited viewing rights |
| PUBLIC_USER | 7 | None | Self | Public user with minimal access |

---

## 5. Permission-Based Access Control

Each user automatically gets permissions based on their role:

**SUPER_ADMIN Example Permissions**:
```json
{
  "permissions": [
    "user.create",
    "user.edit",
    "user.delete",
    "org.create",
    "org.edit",
    "org.delete",
    "volunteer.create",
    "volunteer.edit",
    "volunteer.bulk_upload",
    "training.create",
    "training.edit",
    "rbac.manage",
    ...
  ]
}
```

**SDMA_ADMIN Typical Permissions**:
```json
{
  "permissions": [
    "user.create",          // Only in their state
    "org.view",
    "org.create",           // Only in their state
    "volunteer.view",       // Only in their state
    "training.view"
  ]
}
```

---

## 6. Create Organizations (State/District/Org Admin)

**Endpoint**: `POST /api/v1/organizations/`

**Required Fields**:
- `name` - Organization name
- `org_type` - One of: NCC, NSS, BSG, NYKS
- `state` - State ID (Foreign Key)
- `district` - District ID (Foreign Key)
- `contact_person` - Contact person name
- `contact_email` - Contact email
- `contact_phone` - Contact phone (10 digits)
- `address` - Full address
- `website` - Website URL (optional)
- `is_active` - Active status (default: true)

### First, get State and District IDs:

```bash
# Get all states
curl http://127.0.0.1:8000/api/v1/states/ \
  -H "Authorization: Bearer <TOKEN>"

# Get districts for a state
curl "http://127.0.0.1:8000/api/v1/districts/?state=1" \
  -H "Authorization: Bearer <TOKEN>"
```

### Create Organization:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/organizations/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "name": "NCC Unit - Puducherry",
    "org_type": "NCC",
    "state": 1,
    "district": 1,
    "contact_person": "Captain Vikram Singh",
    "contact_email": "ncc@puducherry.gov.in",
    "contact_phone": "9876543210",
    "address": "Government College, Puducherry 605001",
    "website": "https://ncc-puducherry.gov.in",
    "is_active": true
  }'
```

---

## 7. Role Assignment (Optional - for Multiple Roles per User)

Some users may need multiple roles. Assign via:

**Endpoint**: `POST /api/v1/rbac/user-roles/`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/rbac/user-roles/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "user": 2,                    # User ID
    "role": 3,                    # Role ID
    "state": "PY",
    "district": null,
    "organization": null,
    "designation": "Officer",
    "is_active": true
  }'
```

---

## 8. Government Data Mapping Example

**From the spreadsheet you provided**:
| Field | Type | Required | Example |
|-------|------|----------|---------|
| Name | String | YES | S. Jeyachandran |
| Mobile | String(10) | YES | 9994264111 |
| Email | String | YES | s.jeyachandiran80@py.gov.in |
| Designation | String | YES | Tahsildar |
| Aadhar | String(12) | YES | 465807E+11 (→ 465807000000) |
| State | String | YES | Puducherry |
| Privilege | String | YES | State Level |
| Password | String(8+) | YES | J!@21e<Y>(a)7Ch86Rin$miS% |

**API Mapping**:
```json
{
  "name": "S. Jeyachandran",         // FROM: Name
  "mobile": "9994264111",            // FROM: Mobile
  "email": "s.jeyachandiran80@py.gov.in",  // FROM: Email
  "designation": "Tahsildar",        // FROM: Designation
  "aadhar": "465807000000",          // FROM: Aadhar (handle scientific notation)
  "state_code": "PY",                // FROM: State
  "user_role": "SDMA_ADMIN",         // FROM: Privilege
  "password": "J!@21e<Y>(a)7Ch86Rin$miS%"  // FROM: Password
}
```

---

## 9. Error Handling

### Missing Required Field
```json
{
  "name": ["This field is required."],
  "email": ["This field is required."]
}
```
**Response Code**: 400 Bad Request

### Permission Denied
```json
{
  "error": "Only SUPER_ADMIN/NDMA_ADMIN/TECHNICAL_ADMIN can create users"
}
```
**Response Code**: 403 Forbidden

### Invalid Mobile/Aadhar Format
```json
{
  "mobile": ["Mobile must be a 10 digit number"],
  "aadhar": ["Aadhar must be a 12 digit number"]
}
```
**Response Code**: 400 Bad Request

### Duplicate Email
```json
{
  "email": ["User with this email already exists"]
}
```
**Response Code**: 409 Conflict

---

## 10. Postman Collection

See `docs/COMPLETE_API_DOCUMENTATION.md` for full Postman examples with all 28 endpoints.

---

## Summary

- ✅ NO SIGNUP: Only admins create users
- ✅ NO HARDCODING: All fields must be provided for each user
- ✅ GOVERNMENT COMPLIANT: Includes name, mobile, designation, aadhar, state (required fields)
- ✅ ROLE-BASED: Users see/create only what their role allows
- ✅ PERMISSIONS: Automatically assigned based on role
- ✅ AUDITED: All creation/modification events logged

**Ready to go!** Run `python setup_admin.py` to begin.

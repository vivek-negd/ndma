# Youth Organization Setup Guide

## Overview
Four types of youth organizations available in **ALL states and ALL districts**:
1. **NCC** - National Cadet Corps
2. **NSS** - National Service Scheme
3. **BSG** - Bharat Scouts & Guides
4. **NYKS** - National Youth Korps

---

## 4 Organization Types

| Type | Code | Full Name | Typical Role | Service Areas |
|------|------|-----------|--------------|---|
| **NCC** | NCC | National Cadet Corps | Military training, discipline | All States, All Districts |
| **NSS** | NSS | National Service Scheme | Community service, social work | All States, All Districts |
| **BSG** | BSG | Bharat Scouts & Guides | Scouting, outdoor skills, character building | All States, All Districts |
| **NYKS** | NYKS | National Youth Korps | Youth development, skill training, community engagement | All States, All Districts |

---

## Step 1: Create Youth Organization (Any Type, Any State)

**Example 1: Create NCC in Delhi**
```
POST http://127.0.0.1:8000/api/v1/organizations/
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "name": "NCC Delhi Chapter",
  "org_type": "NCC",
  "state": 7,
  "district": 27,
  "contact_person": "Col. Rajesh Kumar",
  "contact_email": "ncc.delhi@example.com",
  "contact_phone": "9876543210",
  "address": "New Delhi, Delhi",
  "website": "https://ncc-delhi.org",
  "is_active": true
}
```

**Example 2: Create NSS in Maharashtra**
```
POST http://127.0.0.1:8000/api/v1/organizations/
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "name": "NSS Maharashtra Unit",
  "org_type": "NSS",
  "state": 1,
  "district": 5,
  "contact_person": "Dr. Priya Sharma",
  "contact_email": "nss.maharashtra@example.com",
  "contact_phone": "9876543210",
  "address": "Mumbai, Maharashtra",
  "website": "https://nss-maharashtra.org",
  "is_active": true
}
```

**Example 3: Create BSG in Gujarat**
```
POST http://127.0.0.1:8000/api/v1/organizations/
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "name": "BSG Gujarat Scouts",
  "org_type": "BSG",
  "state": 2,
  "district": 10,
  "contact_person": "Mr. Vikram Patel",
  "contact_email": "bsg.gujarat@example.com",
  "contact_phone": "9876543210",
  "address": "Ahmedabad, Gujarat",
  "website": "https://bsg-gujarat.org",
  "is_active": true
}
```

**Example 4: Create NYKS in Karnataka**
```
POST http://127.0.0.1:8000/api/v1/organizations/
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "name": "NYKS Karnataka Youth Corps",
  "org_type": "NYKS",
  "state": 3,
  "district": 15,
  "contact_person": "Ms. Anjali Desai",
  "contact_email": "nyks.karnataka@example.com",
  "contact_phone": "9876543210",
  "address": "Bangalore, Karnataka",
  "website": "https://nyks-karnataka.org",
  "is_active": true
}
```

---

## Step 2: Create User for Organization (YOUTH_ORG_ADMIN Role)

After creating an organization, assign a user as **YOUTH_ORG_ADMIN** for that organization.

**Create Organization Admin User**
```
POST http://127.0.0.1:8000/api/v1/auth/create_user/
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "email_address": "ncc.admin@example.com",
  "password": "SecurePass123!",
  "name": "NCC Delhi Admin",
  "mobile": "9876543210",
  "designation": "Organization Administrator",
  "aadhar": "123456789012",
  "user_role": "YOUTH_ORG_ADMIN",
  "state_code": "DL"
}
```

**Response:** Contains user `id` (e.g., `10`)

---

## Step 3: Assign Organization Role to User

Link the created user to the organization with a specific role.

**Create UserRole**
```
POST http://127.0.0.1:8000/api/v1/rbac/user-roles/
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "user": 10,
  "role": 5,
  "organization": 1,
  "designation": "NCC Delhi Administrator",
  "state": 7,
  "district": 27,
  "is_active": true
}
```

**Fields:**
- `user` — user id (from Step 2)
- `role` — role id (5 = YOUTH_ORG_ADMIN, or get from GET /rbac/roles/)
- `organization` — organization id (from Step 1)
- `designation` — job title in the organization
- `state` — state id (optional, for geographic scope)
- `district` — district id (optional, for geographic scope)
- `is_active` — activate immediately

---

## Complete Example Workflow

### 1. Login
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin_password"
  }'
# Response: {"access": "<TOKEN>", ...}
```

### 2. Create NCC Organization in Delhi
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/organizations/" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "NCC Delhi Chapter",
    "org_type": "NCC",
    "state": 7,
    "district": 27,
    "contact_person": "Col. Rajesh Kumar",
    "contact_email": "ncc.delhi@example.com",
    "contact_phone": "9876543210",
    "address": "New Delhi",
    "website": "https://ncc-delhi.org",
    "is_active": true
  }'
# Response: {"id": 1, "name": "NCC Delhi Chapter", ...}
```

### 3. Create User (Org Admin)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/create_user/" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "ncc.admin@example.com",
    "password": "SecurePass123!",
    "name": "NCC Delhi Admin",
    "mobile": "9876543210",
    "designation": "Organization Administrator",
    "aadhar": "123456789012",
    "user_role": "YOUTH_ORG_ADMIN",
    "state_code": "DL"
  }'
# Response: {"user": {"id": 10, ...}}
```

### 4. Assign Role to User
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/rbac/user-roles/" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "user": 10,
    "role": 5,
    "organization": 1,
    "designation": "NCC Delhi Administrator",
    "state": 7,
    "district": 27,
    "is_active": true
  }'
# Response: {"id": 1, "user": 10, "role": 5, "organization": 1, ...}
```

---

## Organization Setup in Different States

Create any organization type in any state. Examples:

### NCC in Multiple States
```
Delhi (state_id=7) → NCC Delhi Chapter
Maharashtra (state_id=1) → NCC Maharashtra
Tamil Nadu (state_id=33) → NCC Tamil Nadu
```

### NSS in Multiple States
```
Delhi (state_id=7) → NSS Delhi
Karnataka (state_id=3) → NSS Karnataka
Rajasthan (state_id=8) → NSS Rajasthan
```

### BSG in Multiple States
```
Gujarat (state_id=2) → BSG Gujarat
West Bengal (state_id=19) → BSG West Bengal
Punjab (state_id=26) → BSG Punjab
```

### NYKS in Multiple States
```
Haryana (state_id=6) → NYKS Haryana
Uttar Pradesh (state_id=9) → NYKS Uttar Pradesh
Kerala (state_id=32) → NYKS Kerala
```

---

## Youth Organization Admin Permissions

**YOUTH_ORG_ADMIN can:**
- ✅ View organization details
- ✅ Upload volunteers (single/bulk)
- ✅ Manage volunteers in their organization
- ✅ View volunteer statistics
- ✅ Access training schedules

**YOUTH_ORG_ADMIN cannot:**
- ❌ Create new organizations
- ❌ Delete organizations
- ❌ Manage other organizations
- ❌ Create/manage system users
- ❌ Access state/district level data

---

## Postman Collection Flow

For organizations in all 4 types and all states:

1. **Login** → POST `/auth/login/`
2. **Get States** → GET `/states/`
3. **Get Districts** → GET `/districts/?state_id=<id>`
4. **Create Organization** → POST `/organizations/`
   - Change `org_type` to: NCC, NSS, BSG, or NYKS
   - Change `state` and `district` to any state/district
5. **Create User** → POST `/auth/create_user/`
6. **Assign Role** → POST `/rbac/user-roles/`
7. **Activate Role** → POST `/rbac/user-roles/{id}/activate/`

---

## Quick Reference: All States

Get available states:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/states/" \
  -H "Authorization: Bearer <TOKEN>"
```

Get districts for a state:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/districts/?state_id=<state_id>" \
  -H "Authorization: Bearer <TOKEN>"
```

---

## Notes

- All 4 organization types (NCC, NSS, BSG, NYKS) are available in **every state and district**
- You can create multiple organizations of the **same type** in different locations
- You can create multiple organizations of **different types** in the same location
- Each organization must have at least one admin (YOUTH_ORG_ADMIN role)
- Organization creation requires: `SUPER_ADMIN`, `NDMA_ADMIN`, `TECHNICAL_ADMIN`, or `SDMA_ADMIN` role


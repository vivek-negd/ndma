# NDMA Volunteer Management System - Developer Guide

**Version:** 1.0  
**Date:** March 3, 2026  
**Status:** Production Ready ✅

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Authentication & JWT](#authentication--jwt)
4. [User Roles & Permissions](#user-roles--permissions)
5. [API Endpoints](#api-endpoints)
6. [State & District Management](#state--district-management)
7. [Organization Management](#organization-management)
8. [User Management](#user-management)
9. [Volunteer Management](#volunteer-management)
10. [Frontend Integration Guide](#frontend-integration-guide)
11. [Error Handling](#error-handling)
12. [Common Workflows](#common-workflows)
13. [Database Schema](#database-schema)

---

## System Overview

The NDMA Volunteer Management System is a Django REST Framework backend for managing:
- **Users** with role-based access control (9 roles)
- **Organizations** (NCC, NSS, BSG, NYKS)
- **Volunteers** with bulk upload capability
- **State & District** geographic hierarchy
- **Training & Events** management
- **Audit Logs** for compliance

### Tech Stack
- **Backend:** Django 4.x + Django REST Framework
- **Database:** MariaDB
- **Authentication:** JWT (JSON Web Tokens)
- **File Upload:** CSV, Excel (.xlsx)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React/Vue)                      │
├─────────────────────────────────────────────────────────────┤
│                     API Layer (DRF)                           │
├─────────────────────────────────────────────────────────────┤
│  Views → Serializers → Models → Database (MariaDB)          │
├─────────────────────────────────────────────────────────────┤
│  RBAC → Permissions → Signals → Services                     │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Purpose |
|-----------|---------|
| **Views** | Handle HTTP requests, validate permissions |
| **Serializers** | Convert data between JSON and model objects |
| **Models** | Database schema definitions |
| **RBAC** | Role-based access control checks |
| **Services** | Business logic (e.g., volunteer count updates) |
| **Signals** | Auto-trigger on model events |
| **Middlewares** | Request logging, audit tracking |

---

## Authentication & JWT

### How JWT Works

```
1. User Login
   POST /api/v1/auth/login/
   {"email": "user@example.com", "password": "pass123"}
   
2. Server returns tokens
   {
     "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
     "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
   }
   
3. Frontend stores access token (in memory or localStorage)

4. For every API call, include in header:
   Authorization: Bearer <ACCESS_TOKEN>
```

### Getting a Token

**Request:**
```bash
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "admin@ndma.gov.in",
  "password": "SecurePass@2026"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE4MzQ4OTczNjV9.xxx",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE4MzQ5NzM3NjV9.yyy",
  "user": {
    "id": 1,
    "email": "admin@ndma.gov.in",
    "name": "NDMA Admin",
    "user_role": "NDMA_ADMIN"
  }
}
```

### Frontend: Store & Use Token

```javascript
// 1. Store token after login
localStorage.setItem('access_token', response.data.access);
localStorage.setItem('refresh_token', response.data.refresh);

// 2. Add to all API requests
const token = localStorage.getItem('access_token');
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};

// 3. GET request example
fetch('http://localhost:8000/api/v1/states/', {
  method: 'GET',
  headers: headers
})
.then(r => r.json())
.then(data => console.log(data));
```

### Token Refresh

When access token expires:
```bash
POST /api/v1/auth/refresh/

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Returns new access token.

---

## User Roles & Permissions

### 9 User Roles (Hierarchy)

```
1. SUPER_ADMIN          (System admin - all access)
   ↓
2. NDMA_ADMIN           (National admin - all operations)
   ↓
3. TECHNICAL_ADMIN      (Technical support - read/debug)
   ↓
4. SDMA_ADMIN           (State admin - state-level operations)
   ↓
5. DDMA_NODAL_OFFICER   (District admin - district-level)
   ↓
6. YOUTH_ORG_ADMIN      (Organization manager - org-level)
   ↓
7. TRAINING_INSTITUTE   (Training coordinator)
   ↓
8. VOLUNTEER            (Volunteer user)
   ↓
9. PUBLIC_USER          (Limited public access)
```

### Permission Matrix

| Role | Create User | Create Org | Upload Volunteer | View Organization | Delete Org |
|------|-----------|---------|--------|---------|---------|
| SUPER_ADMIN | ✅ All | ✅ All | ✅ All | ✅ All | ✅ All |
| NDMA_ADMIN | ✅ All | ✅ All | ✅ All | ✅ All | ✅ All |
| SDMA_ADMIN | ✅ Own State | ✅ Own State | ✅ Own State | ✅ Own State | ❌ |
| DDMA_NODAL_OFFICER | ❌ | ❌ | ✅ Own District | ✅ Own District | ❌ |
| YOUTH_ORG_ADMIN | ❌ | ❌ | ✅ Own Org | ✅ Own Org | ❌ |
| VOLUNTEER | ❌ | ❌ | ❌ | ✅ Own Org | ❌ |

### Geographic Scoping

- **SDMA_ADMIN**: Limited to `state_id` (State model FK)
- **DDMA_NODAL_OFFICER**: Limited to `district_id` (District model FK)
- **YOUTH_ORG_ADMIN**: Limited to linked organization

---

## HTTP Status Codes Reference

### Success Codes (2xx)

| Code | Meaning | Used For |
|------|---------|----------|
| **200** | OK | GET requests, successfully retrieved data |
| **201** | Created | POST requests, resource successfully created |
| **204** | No Content | DELETE requests, successfully deleted (no response body) |

### Client Error Codes (4xx)

| Code | Meaning | Solution |
|------|---------|----------|
| **400** | Bad Request | Fix your request data/payload |
| **401** | Unauthorized | Token missing/expired - login again |
| **403** | Forbidden | User doesn't have permission for this action |
| **404** | Not Found | Resource doesn't exist - check ID |
| **409** | Conflict | Duplicate entry (e.g., mis_id already exists) |

### Server Error Codes (5xx)

| Code | Meaning | Action |
|------|---------|--------|
| **500** | Internal Server Error | Contact support - backend issue |

---

## API Endpoints

### BASE URL
```
http://localhost:8000/api/v1/
```

### Authentication Endpoints

#### 1. User Login
```
POST /auth/login/
No auth required

Body:
{
  "email": "user@example.com",
  "password": "password123"
}

✅ Response Status: 200 OK
{
  "message": "Login successful",
  "access": "<JWT_TOKEN>",
  "refresh": "<REFRESH_TOKEN>",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "user_role": "SUPER_ADMIN"
  }
}

❌ Response Status: 400 Bad Request (Invalid credentials)
{
  "error": "Invalid email or password"
}

❌ Response Status: 401 Unauthorized (Account inactive)
{
  "error": "This account is not active"
}
```

#### 2. Create User with Privilege (One-Step User+Role)
```
POST /auth/create_user_with_privilege/
Auth: Required (SUPER_ADMIN, NDMA_ADMIN)

Body:
{
  "email": "officer@state.gov.in",
  "password": "SecurePass@2026",
  "name": "Officer Name",
  "mobile": "9876543210",
  "privilege": "SDMA_ADMIN",
  "state_id": 38,
  "district_id": null
}

✅ Response Status: 201 Created
{
  "message": "User created successfully",
  "privilege": "SDMA_ADMIN",
  "role_assigned": true,
  "user": {
    "id": 50,
    "email": "officer@state.gov.in",
    "name": "Officer Name",
    "mobile": "9876543210",
    "user_role": "SDMA_ADMIN",
    "state_id": 38,
    "state_name": "Puducherry"
  }
}

❌ Response Status: 400 Bad Request (Invalid data)
{
  "email": ["This field may not be blank."],
  "password": ["Password too short"]
}

❌ Response Status: 403 Forbidden (Not authorized)
{
  "error": "Only SUPER_ADMIN can create users"
}
```

#### 3. Change Password
```
POST /auth/change_password/
Auth: Required

Body:
{
  "old_password": "current123",
  "new_password": "NewPass@2026"
}

✅ Response Status: 200 OK
{
  "message": "Password changed successfully"
}

❌ Response Status: 400 Bad Request (Wrong old password)
{
  "error": "Old password is incorrect"
}

❌ Response Status: 401 Unauthorized (Not logged in)
{
  "error": "Authentication credentials were not provided"
}
```

---

### State & District Endpoints

#### Get All States
```
GET /states/
Auth: Optional

✅ Response Status: 200 OK
[
  {
    "id": 38,
    "name": "Puducherry",
    "lgd_code": "PUDUCHERRY",
    "volunteer_count": 150,
    "created_at": "2026-03-01T10:00:00Z"
  },
  {
    "id": 33,
    "name": "Tamil Nadu",
    "volunteer_count": 320
  }
]
```

#### Get Districts by State
```
GET /districts/?state_id=38
Auth: Optional

✅ Response Status: 200 OK
[
  {
    "id": 145,
    "name": "Puducherry",
    "state_id": 38,
    "state_name": "Puducherry",
    "volunteer_count": 75
  }
]

❌ Response Status: 400 Bad Request (Missing state_id)
{
  "error": "state_id parameter is required"
}
```

---

### Organization Endpoints

#### Create Organization
```
POST /organizations/
Auth: Required (SUPER_ADMIN, NDMA_ADMIN, SDMA_ADMIN)

Body:
{
  "name": "NCC Unit Puducherry",
  "org_type": "NCC",
  "state": 38,
  "district": 145,
  "contact_person": "Major John",
  "contact_email": "ncc.puducherry@gov.in",
  "contact_phone": "9876543210",
  "address": "Military Campus"
}

✅ Response Status: 201 Created
{
  "id": 42,
  "name": "NCC Unit Puducherry",
  "org_type": "NCC",
  "state": 38,
  "state_name": "Puducherry",
  "district": 145,
  "district_name": "Puducherry",
  "contact_person": "Major John",
  "contact_email": "ncc.puducherry@gov.in",
  "volunteer_count": 0
}

❌ Response Status: 400 Bad Request (Invalid state)
{
  "state": ["Invalid pk 999 - object does not exist."]
}

❌ Response Status: 403 Forbidden (Permission denied)
{
  "error": "SDMA_ADMIN can only create organizations in their assigned state"
}

❌ Response Status: 409 Conflict (Duplicate name)
{
  "error": "Organization with this name already exists in this state"
}
```

#### List Organizations
```
GET /organizations/
Auth: Required

Query Params:
  ?state=38
  ?district=145
  ?org_type=NCC
  ?is_active=true

✅ Response Status: 200 OK
{
  "count": 15,
  "next": "http://.../organizations/?page=2",
  "results": [
    {
      "id": 42,
      "name": "NCC Unit Puducherry",
      "org_type": "NCC",
      "state": 38,
      "state_name": "Puducherry",
      "volunteer_count": 150
    }
  ]
}

❌ Response Status: 401 Unauthorized (Not logged in)
{
  "error": "Authentication credentials were not provided"
}
```

#### Get Organization Details
```
GET /organizations/{id}/
Auth: Required

✅ Response Status: 200 OK
{
  "id": 42,
  "name": "NCC Unit Puducherry",
  "org_type": "NCC",
  "state": 38,
  "state_name": "Puducherry",
  "volunteer_count": 150,
  "contact_email": "ncc@puducherry.gov.in"
}

❌ Response Status: 404 Not Found (Organization doesn't exist)
{
  "detail": "Not found."
}

❌ Response Status: 403 Forbidden (User can't see this org)
{
  "error": "You do not have permission to view this organization"
}
```

#### Update Organization
```
PUT /organizations/{id}/
PATCH /organizations/{id}/
Auth: Required (same role as create)

Body: (any fields to update)
{
  "contact_email": "new@email.com",
  "contact_phone": "1234567890"
}

✅ Response Status: 200 OK
{
  "id": 42,
  "name": "NCC Unit Puducherry",
  "contact_email": "new@email.com",
  "contact_phone": "1234567890",
  ...
}

❌ Response Status: 400 Bad Request (Invalid data)
{
  "contact_email": ["Enter a valid email address."]
}

❌ Response Status: 403 Forbidden (Can't edit)
{
  "error": "SDMA_ADMIN can only edit organizations in their assigned state"
}
```

#### Delete Organization
```
DELETE /organizations/{id}/
Auth: Required (SUPER_ADMIN, NDMA_ADMIN only)

✅ Response Status: 204 No Content
(No response body)

❌ Response Status: 403 Forbidden (Can't delete)
{
  "error": "Users with role SDMA_ADMIN cannot delete organizations"
}

❌ Response Status: 404 Not Found
{
  "detail": "Not found."
}
```

---

### Volunteer Endpoints

#### Create Single Volunteer
```
POST /volunteer/create/
Auth: Required (SUPER_ADMIN, NDMA_ADMIN, SDMA_ADMIN, DDMA_NODAL_OFFICER, YOUTH_ORG_ADMIN)

Body:
{
  "mis_id": 1001,
  "name": "Rajesh Kumar",
  "mobile": "9876543210",
  "email": "rajesh@example.com",
  "organization_id": 42,
  "state_name": "Puducherry",
  "district_name": "Puducherry",
  "gender": "Male",
  "blood_group": "O+",
  "dob": "1990-05-15",
  "education": "Bachelor",
  "skill": "First Aid"
}

Response (201):
{
  "message": "Volunteer uploaded successfully",
  "volunteer_id": 1,
  "organization": "NCC Unit Puducherry"
}
```

#### Bulk Upload Volunteers (Excel/CSV)
```
POST /volunteer/bulk-upload/
Auth: Required (same roles as create)
Content-Type: multipart/form-data

Form Data:
  file              = volunteer_data.xlsx (or .csv)
  organization_id   = 42
  state_name        = Puducherry
  district_name     = Puducherry
  expected_count    = 20 (optional)

Response (201):
{
  "created_count": 20,
  "created_mis_ids": [1001, 1002, ...],
  "error_count": 0,
  "errors": [],
  "warnings": []
}
```

#### List Volunteers
```
GET /volunteer/
Auth: Required

Query Params:
  ?state_id=38
  ?district_id=145
  ?organization_id=42
  ?search=John

Response (200):
{
  "count": 100,
  "results": [...]
}
```

#### Get Volunteer Details
```
GET /volunteer/{id}/
Auth: Required

Response (200):
{
  "id": 1,
  "mis_id": 1001,
  "name": "Rajesh Kumar",
  ...
}
```

#### Get Organization Coverage
```
GET /volunteer/coverage/
Auth: Required

Response (200):
{
  "organizations": [
    {
      "id": 42,
      "name": "NCC Unit Puducherry",
      "total_volunteers": 150,
      "by_state": [
        {
          "state_id": 38,
          "state_name": "Puducherry",
          "count": 150
        }
      ],
      "by_district": [...]
    }
  ]
}
```

---

### User Management Endpoints

#### Create User (Standard)
```
POST /users/
Auth: Required (SUPER_ADMIN, NDMA_ADMIN)

Body:
{
  "email": "user@example.com",
  "password": "SecurePass@2026",
  "name": "User Name",
  "mobile": "9876543210",
  "state_id": 38,
  "district_id": 145
}

Response (201): User object
```

#### List Users
```
GET /users/
Auth: Required (SUPER_ADMIN, NDMA_ADMIN)

Query Params:
  ?state_id=38
  ?user_role=SDMA_ADMIN
  ?search=john

Response (200):
{
  "count": 50,
  "results": [...]
}
```

#### Get User Details
```
GET /users/{id}/
Auth: Required

Response (200):
{
  "id": 1,
  "email": "user@example.com",
  "name": "User Name",
  "user_role": "SDMA_ADMIN",
  "state_id": 38,
  "state_name": "Puducherry",
  ...
}
```

#### Update User
```
PUT /users/{id}/
PATCH /users/{id}/
Auth: Required (own user or admin)

Body: (any fields except role)
{
  "name": "Updated Name",
  "mobile": "1234567890"
}

Response (200): Updated user
```

---

## State & District Management

### State Model
```python
class State:
    id: Integer (PK)
    name: String (unique)
    lgd_code: String (for reference)
    volunteer_count: Integer (auto-updated)
    created_at: DateTime
    updated_at: DateTime
```

### District Model
```python
class District:
    id: Integer (PK)
    name: String
    state_id: ForeignKey(State)
    volunteer_count: Integer (auto-updated)
    created_at: DateTime
```

### Frontend Usage
```javascript
// 1. Get all states
const states = await fetch('/api/v1/states/').then(r => r.json());

// 2. Get districts for selected state
const state_id = 38;
const districts = await fetch(`/api/v1/districts/?state_id=${state_id}`)
  .then(r => r.json());

// 3. Display in dropdowns
function fillStateDropdown(states) {
  const select = document.getElementById('state');
  states.forEach(state => {
    const option = document.createElement('option');
    option.value = state.id;
    option.text = state.name;
    select.appendChild(option);
  });
}
```

---

## Organization Management

### Organization Model
```python
class Organization:
    id: Integer (PK)
    name: String
    org_type: Choice (NCC, NSS, BSG, NYKS)
    state_id: ForeignKey(State)
    district_id: ForeignKey(District)
    contact_person: String
    contact_email: Email
    contact_phone: String
    address: Text
    website: URL
    is_active: Boolean
    volunteer_count: Integer (property)
    created_at: DateTime
```

### Create Organization Workflow

**Frontend:**
```javascript
async function createOrganization(formData) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('/api/v1/organizations/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: formData.name,
      org_type: formData.type,  // NCC, NSS, BSG, NYKS
      state: formData.state_id,
      district: formData.district_id,
      contact_person: formData.contact,
      contact_email: formData.email,
      contact_phone: formData.phone,
      address: formData.address
    })
  });
  
  return await response.json();
}
```

---

## User Management

### Create User with Role (Complete Workflow)

**Step 1: Create User & Assign Privilege**
```javascript
await fetch('/api/v1/auth/create_user_with_privilege/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'officer@state.gov.in',
    password: 'SecurePass@2026',
    name: 'Officer Name',
    mobile: '9876543210',
    privilege: 'SDMA_ADMIN',  // Role assigned
    state_id: 38,
    district_id: null
  })
})
```

**Step 2: Officer Logs In**
```javascript
const loginResponse = await fetch('/api/v1/auth/login/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'officer@state.gov.in',
    password: 'SecurePass@2026'
  })
});

const {access, refresh} = await loginResponse.json();
localStorage.setItem('access_token', access);
localStorage.setItem('refresh_token', refresh);
```

**Step 3: Use Dashboard (Based on Role)**
- SDMA_ADMIN sees: Only their state's organizations & volunteers
- YOUTH_ORG_ADMIN sees: Only their organization

---

## Volunteer Management

### Volunteer Model
```python
class Volunteer:
    id: Integer (PK)
    mis_id: Integer (unique)
    name: String
    gender_id: Integer (choice: 1-3)
    blood_group_id: Integer (choice: 1-8)
    dob: Date
    aadhar: String (unique)
    mobile: String
    email: Email (unique)
    mybharat_id: String
    maritalstatus_id: Integer (choice: 1-5)
    emergency_contact: String
    education_id: Integer (choice: 1-8)
    education_field: String
    skill_id: Integer (choice: 1-6)
    organization_id: ForeignKey(Organization)
    state_id: ForeignKey(State)
    district_id: ForeignKey(District)
    area_type_id: Integer (choice: 1-3)
    postal_code: String
    town: String
    village: String
    full_address: Text
    id_card: String
    certificate: String
    photo: URL
    created_at: DateTime
    deleted_at: DateTime (soft delete)
```

### Dropdown Values (Choice Mappings)

**Gender:**
```
1: Male, 2: Female, 3: Other
→ Display: "Male", "Female", "Other"
```

**Blood Group:**
```
1: A+, 2: A-, 3: B+, 4: B-, 5: O+, 6: O-, 7: AB+, 8: AB-
```

**Education:**
```
1: Below 10th, 2: 10th Pass, 3: 12th Pass, 4: Diploma, 
5: Bachelor, 6: Master, 7: PhD, 8: Other
```

**Skill:**
```
1: First Aid, 2: Disaster Management, 3: Rescue Operations,
4: Community Care, 5: Training, 6: Other
```

**Area Type:**
```
1: Urban, 2: Rural, 3: Semi-Urban
```

**Marital Status:**
```
1: Single, 2: Married, 3: Divorced, 4: Widowed, 5: Separated
```

**Salutation:**
```
1: Mr., 2: Mrs., 3: Ms., 4: Dr., 5: Prof.
```

### Bulk Upload Workflow

**1. Download Template**
- File: `volunteer_bulk_upload_template.xlsx`
- Contains: 5 sample rows + dropdowns + instructions

**2. Prepare Data**
```
mis_id | name | gender | skill | organization_id | state_name | district_name
1001   | John | Male   | First Aid | 42 | Puducherry | Puducherry
1002   | Jane | Female | Training | 42 | Puducherry | Puducherry
```

**3. Upload via API**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('organization_id', 42);
formData.append('state_name', 'Puducherry');
formData.append('district_name', 'Puducherry');
formData.append('expected_count', 20);

const response = await fetch('/api/v1/volunteer/bulk-upload/', {
  method: 'POST',
  headers: {'Authorization': `Bearer ${token}`},
  body: formData
});

const result = await response.json();
// result.created_count, result.errors, result.warnings
```

**4. Handle Response**
```javascript
if (result.error_count > 0) {
  // Show errors to user
  result.errors.forEach(err => {
    console.log(`Row ${err.index}: ${JSON.stringify(err.errors)}`);
  });
}

if (result.created_count > 0) {
  // Show success
  alert(`${result.created_count} volunteers created`);
  // Update UI: refresh volunteer list
}
```

---

## Frontend Integration Guide

### 1. Login Flow

```javascript
// frontend/src/services/auth.js

export async function login(email, password) {
  const response = await fetch('http://localhost:8000/api/v1/auth/login/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email, password})
  });
  
  if (!response.ok) throw new Error('Login failed');
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  localStorage.setItem('user_role', data.user.user_role);
  
  return data.user;
}

export function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user_role');
}

export function getAuthHeaders() {
  const token = localStorage.getItem('access_token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
}
```

### 2. API Service Layer

```javascript
// frontend/src/services/api.js

const BASE_URL = 'http://localhost:8000/api/v1';

async function apiRequest(endpoint, options = {}) {
  const headers = getAuthHeaders();
  
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {...headers, ...options.headers}
  });
  
  if (response.status === 401) {
    // Token expired, try refresh
    await refreshToken();
    return apiRequest(endpoint, options);
  }
  
  if (!response.ok) {
    const error = await response.json();
    throw error;
  }
  
  return await response.json();
}

// Specific endpoints
export const api = {
  states: {
    list: () => apiRequest('/states/'),
  },
  
  districts: {
    byState: (stateId) => apiRequest(`/districts/?state_id=${stateId}`),
  },
  
  organizations: {
    list: (filters) => {
      const params = new URLSearchParams(filters);
      return apiRequest(`/organizations/?${params}`);
    },
    create: (data) => apiRequest('/organizations/', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
    get: (id) => apiRequest(`/organizations/${id}/`),
    update: (id, data) => apiRequest(`/organizations/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    }),
  },
  
  volunteers: {
    list: (filters) => {
      const params = new URLSearchParams(filters);
      return apiRequest(`/volunteer/?${params}`);
    },
    create: (data) => apiRequest('/volunteer/create/', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
    bulkUpload: (file, metadata) => {
      const formData = new FormData();
      formData.append('file', file);
      Object.entries(metadata).forEach(([key, value]) => {
        formData.append(key, value);
      });
      
      const token = localStorage.getItem('access_token');
      return fetch(`${BASE_URL}/volunteer/bulk-upload/`, {
        method: 'POST',
        headers: {'Authorization': `Bearer ${token}`},
        body: formData
      }).then(r => r.json());
    },
  },
  
  users: {
    createWithPrivilege: (data) => apiRequest('/auth/create_user_with_privilege/', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  }
};
```

### 3. React Component Example

```jsx
// frontend/src/components/VolunteerUpload.jsx

import {useState} from 'react';
import {api} from '../services/api';

export default function VolunteerUpload() {
  const [file, setFile] = useState(null);
  const [orgId, setOrgId] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  
  async function handleUpload(e) {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await api.volunteers.bulkUpload(file, {
        organization_id: orgId,
        expected_count: 20
      });
      
      setResult(response);
      
      if (response.error_count > 0) {
        alert(`${response.error_count} errors found`);
      }
      if (response.created_count > 0) {
        alert(`${response.created_count} volunteers created!`);
      }
    } catch (error) {
      alert('Upload failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  }
  
  return (
    <form onSubmit={handleUpload}>
      <input
        type="file"
        accept=".xlsx,.xls,.csv"
        onChange={(e) => setFile(e.target.files[0])}
        required
      />
      <input
        type="number"
        value={orgId}
        onChange={(e) => setOrgId(e.target.value)}
        placeholder="Organization ID"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Uploading...' : 'Upload'}
      </button>
      
      {result && (
        <div>
          <p>Created: {result.created_count}</p>
          <p>Errors: {result.error_count}</p>
          {result.errors.length > 0 && (
            <details>
              <summary>Errors</summary>
              <pre>{JSON.stringify(result.errors, null, 2)}</pre>
            </details>
          )}
        </div>
      )}
    </form>
  );
}
```

### 4. Form Dropdown Component

```jsx
// frontend/src/components/StateDistrictSelect.jsx

import {useEffect, useState} from 'react';
import {api} from '../services/api';

export default function StateDistrictSelect({onSelect}) {
  const [states, setStates] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [selectedState, setSelectedState] = useState('');
  
  useEffect(() => {
    // Load states on mount
    api.states.list()
      .then(s => setStates(s))
      .catch(e => console.error('Failed to load states:', e));
  }, []);
  
  async function handleStateChange(stateId) {
    setSelectedState(stateId);
    
    // Load districts for selected state
    const districts = await api.districts.byState(stateId);
    setDistricts(districts);
    
    onSelect({state_id: stateId, districts});
  }
  
  return (
    <div>
      <select onChange={(e) => handleStateChange(e.target.value)} required>
        <option value="">Select State</option>
        {states.map(s => (
          <option key={s.id} value={s.id}>
            {s.name} ({s.volunteer_count} volunteers)
          </option>
        ))}
      </select>
      
      <select required disabled={!selectedState}>
        <option value="">Select District</option>
        {districts.map(d => (
          <option key={d.id} value={d.id}>
            {d.name} ({d.volunteer_count})
          </option>
        ))}
      </select>
    </div>
  );
}
```

---

## Error Handling

### Common HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | OK | Success |
| 201 | Created | Resource created |
| 204 | No Content | Success (no response body) |
| 400 | Bad Request | Fix request data |
| 401 | Unauthorized | Login required or token expired |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate entry (e.g., mis_id exists) |
| 500 | Server Error | Backend issue |

### Error Response Format

```json
{
  "error": "Error message",
  "details": {
    "field_name": ["Error for this field"]
  }
}
```

### Frontend Error Handling

```javascript
async function apiCall(endpoint) {
  try {
    const response = await fetch(endpoint, {
      headers: getAuthHeaders()
    });
    
    if (response.status === 401) {
      // Token expired - redirect to login
      window.location.href = '/login';
      return;
    }
    
    if (!response.ok) {
      const error = await response.json();
      
      if (response.status === 400) {
        // Validation error
        console.error('Validation errors:', error.details);
      } else if (response.status === 403) {
        // Permission denied
        alert('You do not have permission for this action');
      } else {
        console.error('Error:', error);
      }
      
      throw error;
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}
```

---

## Common Workflows

### Workflow 1: Create NCC Organization & Upload Volunteers

```javascript
// Step 1: Admin creates organization
const org = await api.organizations.create({
  name: 'NCC Unit Puducherry',
  org_type: 'NCC',
  state: 38,
  district: 145,
  contact_email: 'ncc@puducherry.gov.in'
});
// org.id = 42

// Step 2: Create YOUTH_ORG_ADMIN user
const user = await api.users.createWithPrivilege({
  email: 'ncc.admin@puducherry.gov.in',
  password: 'SecurePass@2026',
  name: 'NCC Admin',
  privilege: 'YOUTH_ORG_ADMIN',
  state_id: 38,
  district_id: 145
});
// user.id = 125

// Step 3: NCC Admin logs in
const {access} = await login('ncc.admin@puducherry.gov.in', 'SecurePass@2026');
localStorage.setItem('access_token', access);

// Step 4: NCC Admin uploads volunteers
const result = await api.volunteers.bulkUpload(excelFile, {
  organization_id: 42,
  expected_count: 50
});

// Result: 50 volunteers created
```

### Workflow 2: Check Volunteer Count by State

```javascript
// Get all states with volunteer counts
const states = await api.states.list();

states.forEach(state => {
  console.log(`${state.name}: ${state.volunteer_count} volunteers`);
});

// Output:
// Puducherry: 150 volunteers
// Tamil Nadu: 320 volunteers
```

### Workflow 3: SDMA Admin Views Only Their State

```javascript
// Login as SDMA_ADMIN (Puducherry)
const {access} = await login('puducherry.admin@state.gov.in', 'password');

// List organizations - auto-filtered to Puducherry only
const orgs = await api.organizations.list();
// Returns only organizations in Puducherry state

// Upload volunteers - auto-scoped to Puducherry
const result = await api.volunteers.bulkUpload(file, {
  organization_id: 42  // NCC in Puducherry
});
```

---

## Database Schema

### States Table
```sql
CREATE TABLE models_state (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) UNIQUE,
  lgd_code VARCHAR(20),
  volunteer_count INT DEFAULT 0,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  deleted_at TIMESTAMP NULL
);
```

### Districts Table
```sql
CREATE TABLE models_district (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  state_id INT,
  volunteer_count INT DEFAULT 0,
  created_at TIMESTAMP,
  FOREIGN KEY (state_id) REFERENCES models_state(id)
);
```

### Organizations Table
```sql
CREATE TABLE models_organization (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  org_type VARCHAR(50),  -- NCC, NSS, BSG, NYKS
  state_id INT,
  district_id INT,
  contact_person VARCHAR(100),
  contact_email VARCHAR(100),
  contact_phone VARCHAR(15),
  address TEXT,
  website VARCHAR(200),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (state_id) REFERENCES models_state(id),
  FOREIGN KEY (district_id) REFERENCES models_district(id),
  UNIQUE(name, state_id, district_id)
);
```

### Volunteers Table
```sql
CREATE TABLE models_volunteer (
  id INT PRIMARY KEY AUTO_INCREMENT,
  mis_id INT UNIQUE,
  name VARCHAR(100),
  gender_id INT,
  blood_group_id INT,
  dob DATE,
  aadhar VARCHAR(12) UNIQUE,
  mobile VARCHAR(10),
  email VARCHAR(100) UNIQUE,
  mybharat_id VARCHAR(50),
  maritalstatus_id INT,
  emergency_contact VARCHAR(15),
  education_id INT,
  education_field VARCHAR(100),
  skill_id INT,
  organization_id INT,
  state_id INT,
  district_id INT,
  area_type_id INT,
  postal_code VARCHAR(10),
  town VARCHAR(100),
  village VARCHAR(100),
  full_address TEXT,
  id_card VARCHAR(50),
  certificate VARCHAR(200),
  photo VARCHAR(200),
  created_at TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  FOREIGN KEY (organization_id) REFERENCES models_organization(id),
  FOREIGN KEY (state_id) REFERENCES models_state(id),
  FOREIGN KEY (district_id) REFERENCES models_district(id)
);
```

### Users Table
```sql
CREATE TABLE models_user (
  id INT PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(100) UNIQUE,
  password VARCHAR(255),
  name VARCHAR(100),
  mobile VARCHAR(10),
  user_role VARCHAR(50),  -- SUPER_ADMIN, NDMA_ADMIN, etc.
  state_id INT,
  district_id INT,
  is_active BOOLEAN,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (state_id) REFERENCES models_state(id),
  FOREIGN KEY (district_id) REFERENCES models_district(id)
);
```

---

## Deployment & Configuration

### Environment Variables (.env)

```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_ENGINE=django.db.backends.mysql
DB_NAME=ndma_db
DB_USER=root
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=3306

# JWT
JWT_SECRET=jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Docker Compose (Production)

```yaml
version: '3'

services:
  db:
    image: mariadb:latest
    environment:
      MYSQL_DATABASE: ndma_db
      MYSQL_ROOT_PASSWORD: secure_password
    volumes:
      - db_data:/var/lib/mysql

  backend:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
    environment:
      DEBUG: "False"
    depends_on:
      - db
    volumes:
      - .:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  db_data:
```

---

## Support & Resources

### Useful Links
- API Documentation: `/api/v1/`
- Admin Panel: `/admin/`
- API Docs (Swagger): `/api/schema/swagger/`

### Common Issues

**Issue: 401 Unauthorized**
- Solution: Check if token is in localStorage
- Try: `localStorage.getItem('access_token')`

**Issue: 403 Forbidden**
- Solution: User role doesn't have permission
- Check: User's `user_role` and organization's `state_id`

**Issue: Volunteers not grouped by state**
- Solution: Ensure `state_id` is set on volunteer records
- Check: Signal handlers are registered in `apps.py`

**Issue: Bulk upload slow**
- Solution: Use `transaction.atomic()` (already implemented)
- Max 1000 volunteers per upload recommended

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-03 | Initial release - Complete RBAC, Orgs, Volunteers, Bulk Upload |

---

**Document Version:** 1.0  
**Last Updated:** March 3, 2026  
**Status:** ✅ Production Ready

For questions or issues, contact: development@ndma.gov.in

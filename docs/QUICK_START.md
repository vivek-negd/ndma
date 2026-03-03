# API Quick Start Guide

## 5-Minute Setup

### Step 1: Get Access Token (1 min)

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@ndma.gov.in",
    "password": "password123"
  }'
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLA...",
    "refresh": "eyJ0eXAiOiJKV1QiLA..."
}
```

**Save the `access` token** (valid for 15 minutes)

---

### Step 2: Test Access (1 min)

```bash
curl -X GET http://localhost:8000/api/v1/organizations/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLA..."
```

**If you get data, you're authenticated!**

---

### Step 3: Create First Volunteer (1 min)

```bash
curl -X POST http://localhost:8000/api/v1/volunteer/create/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLA..." \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": 1,
    "mis_id": 10001,
    "name": "John Smith",
    "gender": "Male",
    "state_name": "Maharashtra",
    "district_name": "Mumbai"
  }'
```

**Response (201):**
```json
{
    "message": "Volunteer uploaded successfully",
    "volunteer_id": 42,
    "organization": "Red Cross India"
}
```

**Success! Volunteer created!**

---

### Step 4: Upload Multiple Volunteers (2 min)

**1. Create file `volunteers.csv`:**
```csv
mis_id,name,gender,state_name,district_name
10002,Jane Doe,Female,Maharashtra,Pune
10003,Bob Johnson,Male,Gujarat,Ahmedabad
10004,Alice Brown,Female,Maharashtra,Mumbai
```

**2. Upload file:**
```bash
curl -X POST http://localhost:8000/api/v1/volunteer/bulk-upload/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLA..." \
  -F "file=@volunteers.csv" \
  -F "organization_id=1"
```

**Response:**
```json
{
    "created_count": 3,
    "created_mis_ids": [10002, 10003, 10004],
    "error_count": 0,
    "errors": []
}
```

**Done! 3 volunteers created!**

---

## API Endpoints at a Glance

### Authentication
```
POST   /api/v1/auth/login/                    - Get access token
POST   /api/v1/auth/token/refresh/            - Refresh token
POST   /api/v1/auth/logout/                   - Logout
GET    /api/v1/auth/profile/                  - Get user profile
POST   /api/v1/auth/change-password/          - Change password
```

### Volunteers
```
POST   /api/v1/volunteer/create/              - Create single volunteer
POST   /api/v1/volunteer/bulk-upload/         - Upload CSV file
GET    /api/v1/volunteer/coverage/            - Get coverage stats
```

### Organizations
```
GET    /api/v1/organizations/                 - List organizations
POST   /api/v1/organizations/                 - Create organization
GET    /api/v1/organizations/{id}/            - Get organization
PUT    /api/v1/organizations/{id}/            - Update organization
DELETE /api/v1/organizations/{id}/            - Delete organization
```

### Users
```
GET    /api/v1/users/                         - List users
POST   /api/v1/users/                         - Create user
GET    /api/v1/users/{id}/                    - Get user
PUT    /api/v1/users/{id}/                    - Update user
DELETE /api/v1/users/{id}/                    - Delete user
```

### Roles & Permissions
```
GET    /api/v1/roles/                         - List roles
POST   /api/v1/roles/                         - Create role
GET    /api/v1/permissions/                   - List permissions
POST   /api/v1/role-assignments/              - Assign role to user
```

### Training
```
GET    /api/v1/training/schedules/            - List schedules
POST   /api/v1/training/schedules/            - Create schedule
GET    /api/v1/training/attendance/           - Get attendance
POST   /api/v1/training/attendance/           - Mark attendance
```

### Statistics
```
GET    /api/v1/stats/states/                  - State statistics
GET    /api/v1/stats/districts/               - District statistics
GET    /api/v1/stats/organizations/           - Org statistics
```

### System
```
GET    /api/v1/health/status/                 - Health check
GET    /api/v1/health/alive/                  - Server alive
GET    /api/v1/health/readiness/              - Ready for requests
```

---

## Common Tasks

### Task 1: List All Volunteers

```bash
curl -X GET http://localhost:8000/api/v1/volunteer/ \
  -H "Authorization: Bearer TOKEN"
```

---

### Task 2: Get Specific Volunteer

```bash
curl -X GET http://localhost:8000/api/v1/volunteer/42/ \
  -H "Authorization: Bearer TOKEN"
```

---

### Task 3: Update Volunteer

```bash
curl -X PUT http://localhost:8000/api/v1/volunteer/42/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith Jr.",
    "mobile": "9876543211"
  }'
```

---

### Task 4: Create Organization

```bash
curl -X POST http://localhost:8000/api/v1/organizations/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Red Crescent",
    "description": "Relief organization"
  }'
```

---

### Task 5: Create User

```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

---

### Task 6: Assign Role to User

```bash
curl -X POST http://localhost:8000/api/v1/role-assignments/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 5,
    "role_id": 2,
    "state_id": 1,
    "district_id": 5
  }'
```

---

### Task 7: Get Organization Coverage

```bash
curl -X GET http://localhost:8000/api/v1/volunteer/coverage/ \
  -H "Authorization: Bearer TOKEN"
```

**Response shows:**
- Organizations
- Volunteers per organization
- States per organization
- Districts per state
- Volunteers per district

---

## Field Reference

### Required Fields
- `organization_id` - Organization ID (1-based)
- `mis_id` - Unique volunteer ID
- `name` - Volunteer name

### Important Fields
- `gender` - Male, Female, Other (or 1, 2, 3)
- `state_name` - Maharashtra, Gujarat, etc.
- `district_name` - Mumbai, Pune, etc.
- `mobile` - 10 digits
- `email` - Valid email

### Optional Fields
- `salutation` - Mr., Mrs., Ms., Dr., Prof.
- `dob` - YYYY-MM-DD
- `blood_group` - A+, B-, etc.
- `maritalstatus` - Single, Married, etc.
- `education` - Bachelor, Master, etc.
- `skill` - First Aid, Training, etc.
- `area_type` - Urban, Rural, Semi-Urban
- `aadhar` - 12 digits
- `emergency_contact` - 10 digits

---

## Role-Based Access

| Role | Can Do |
|------|--------|
| SUPER_ADMIN | Everything - full system control |
| NATIONAL_ADMIN | Create users, organizations, manage national level |
| STATE_ADMIN | Manage state-level data, volunteer upload |
| DISTRICT_ADMIN | Manage district-level data |
| YOUTH_ORG_ADMIN | Manage organization volunteers |
| VOLUNTEER | View own profile, basic access |
| TRAINER | Create training schedules |
| TECHNICAL_ADMIN | System maintenance, database access |

---

## Authentication Flow

```
1. Login with email/password
   ↓
2. Receive access token (15 min) + refresh token (7 days)
   ↓
3. Use access token in Authorization header
   ↓
4. When access expires, use refresh token to get new access
   ↓
5. Token expires after 7 days - login again
```

---

## Error Handling

| Status | Meaning | Solution |
|--------|---------|----------|
| 401 | Not authenticated | Get new token via /auth/login/ |
| 403 | Not authorized | Request required role |
| 404 | Not found | Verify ID/path exists |
| 422 | Validation error | Fix data according to error message |
| 500 | Server error | Check logs, retry later |

---

## Testing Your Setup

### 1. Is server running?
```bash
curl http://localhost:8000/api/v1/health/status/
```

### 2. Can you login?
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@ndma.gov.in", "password": "password123"}'
```

### 3. Is token valid?
```bash
curl http://localhost:8000/api/v1/organizations/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Can you create volunteer?
```bash
curl -X POST http://localhost:8000/api/v1/volunteer/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"organization_id": 1, "mis_id": 99999, "name": "Test"}'
```

---

## Next Steps

1. **Read Full Documentation**
   - [Volunteer API Guide](VOLUNTEERS.md) - All volunteer endpoints
   - [Authentication Guide](AUTHENTICATION.md) - JWT & RBAC details
   - [Error Codes](ERROR_CODES.md) - All error scenarios
   - [API Examples](API_EXAMPLES.md) - Code samples
   - [All Endpoints](API_ENDPOINTS.md) - Complete reference

2. **Integrate into Your Application**
   - Install HTTP client library (requests, axios, etc.)
   - Implement token refresh mechanism
   - Add error handling
   - Cache tokens in localStorage

3. **Get Support**
   - Check error documentation
   - Review code examples
   - Contact admin for role/permission issues

---

## Quick Reference

### Get Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -d '{"email": "admin@ndma.gov.in", "password": "password123"}'
```

### Create Volunteer
```bash
curl -X POST http://localhost:8000/api/v1/volunteer/create/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"organization_id": 1, "mis_id": 10001, "name": "John"}'
```

### Upload Volunteers
```bash
curl -X POST http://localhost:8000/api/v1/volunteer/bulk-upload/ \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@volunteers.csv"
```

### Get Statistics
```bash
curl http://localhost:8000/api/v1/volunteer/coverage/ \
  -H "Authorization: Bearer TOKEN"
```

---

## Environment Configuration

### Base URL
```
Development: http://localhost:8000/api/v1
Staging: https://staging.ndma.gov.in/api/v1
Production: https://api.ndma.gov.in/api/v1
```

### Required Headers
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

### Optional Headers
```
X-Request-ID: unique-request-id
Accept-Language: en-IN
```

---


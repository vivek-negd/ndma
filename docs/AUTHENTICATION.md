# Authentication & Authorization Guide

## Overview

The API uses JWT (JSON Web Tokens) for authentication and role-based access control (RBAC) for authorization.

---

## JWT Authentication

### How It Works

1. **Login** - Send credentials to `/auth/login/` endpoint
2. **Receive Tokens**:
   - `access` token - Use this for API requests (short-lived, ~15 minutes)
   - `refresh` token - Use to get new access token (long-lived, ~7 days)
3. **Make Requests** - Include `Authorization: Bearer <access_token>` header
4. **Token Expires** - When access token expires, use refresh token to get new one

---

## Getting Access Token

### Login Endpoint

**POST /auth/login/**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "user_role": "SUPER_ADMIN",
        "is_active": true
    }
}
```

---

## Refreshing Access Token

When your access token expires, use the refresh token to get a new one.

**POST /auth/token/refresh/**

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Using Access Token in Requests

Include the `Authorization` header in all authenticated requests:

```bash
curl -X GET http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer <access_token>"
```

**Header Format:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## Token Storage

### Browser (JavaScript)

```javascript
// Store after login
localStorage.setItem('accessToken', response.data.access);
localStorage.setItem('refreshToken', response.data.refresh);

// Retrieve for API calls
const token = localStorage.getItem('accessToken');
const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
};
```

### Python

```python
# Store in variable or config file
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Use in request
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}
response = requests.get(url, headers=headers)
```

### Postman

1. Login to get tokens
2. Go to collection settings
3. Set `{{access_token}}` in Authorization tab
4. Use in all requests as Bearer token

---

## User Roles

The API has the following pre-defined roles:

| Role | Description | Permissions |
|------|-------------|-------------|
| **SUPER_ADMIN** | Full system access | All |
| **NDMA_ADMIN** | National admin | National operations |
| **SDMA_ADMIN** | State admin | State operations |
| **DDMA_NODAL_OFFICER** | District admin | District operations |
| **YOUTH_ORG_ADMIN** | Organization admin | Organization operations |
| **VOLUNTEER** | Volunteer user | View own data |
| **TRAINER** | Training instructor | Create/manage trainings |
| **TECHNICAL_ADMIN** | Technical support | System maintenance |

---

## Role-Based Access Control (RBAC)

### Permission System

Permissions are granular and assigned to roles:

```
VOLUNTEER_MANAGEMENT
├── CREATE_VOLUNTEER
├── EDIT_VOLUNTEER
├── DELETE_VOLUNTEER
├── VIEW_VOLUNTEER

ORGANIZATION_MANAGEMENT
├── CREATE_ORGANIZATION
├── EDIT_ORGANIZATION
├── DELETE_ORGANIZATION
├── VIEW_ORGANIZATION

RBAC_MANAGEMENT
├── MANAGE_ROLES
├── MANAGE_PERMISSIONS
```

### How RBAC Works

1. **User has Role** - Each user is assigned one or more roles
2. **Role has Permissions** - Each role contains specific permissions
3. **API checks Permission** - When request is made, API verifies user has permission

### Example: Check if user can create volunteer

```
User "john@example.com" 
  ↓ has role ↓
"YOUTH_ORG_ADMIN" 
  ↓ has permission ↓
"CREATE_VOLUNTEER"
  ↓
✓ User can create volunteer
```

---

## Geographic-Based Access Control

Some roles have geographic restrictions:

**SDMA_ADMIN (State Admin)**
- Can only see/manage organizations in their state
- Identified by `user.state_code`

**DDMA_NODAL_OFFICER (District Admin)**
- Can only see/manage organizations in their district
- Identified by `user.district_code`

**YOUTH_ORG_ADMIN (Organization Admin)**
- Can only see/manage their organization
- Identified by `user.organization_id`

---

## Error Responses

### 401 Unauthorized - No/Invalid Token

```json
{
    "detail": "Authentication credentials were not provided."
}
```

**Fix:** Include valid Authorization header
```bash
curl -H "Authorization: Bearer <valid_token>"
```

---

### 401 Unauthorized - Token Expired

```json
{
    "detail": "Token is invalid or expired"
}
```

**Fix:** Use refresh token to get new access token
```bash
curl -X POST /auth/token/refresh/ \
  -d "{\"refresh\": \"<refresh_token>\"}"
```

---

### 403 Forbidden - Insufficient Permissions

```json
{
    "detail": "You do not have permission to perform this action."
}
```

**Fix:** Contact administrator to grant required role/permission

---

## Best Practices

### Security

1. ✓ **Never commit tokens** to version control
2. ✓ **Use HTTPS only** in production (not HTTP)
3. ✓ **Store tokens securely** (secure cookies, encrypted storage)
4. ✓ **Rotate tokens** regularly
5. ✓ **Short expiry** for access tokens (15 minutes)
6. ✓ **Longer expiry** for refresh tokens (7 days)

### Token Management

```python
# Python - Handle token refresh automatically
class APIClient:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.login()
    
    def login(self):
        response = requests.post(
            'http://localhost:8000/api/v1/auth/login/',
            json={'email': self.email, 'password': self.password}
        )
        data = response.json()
        self.access_token = data['access']
        self.refresh_token = data['refresh']
    
    def refresh_token_if_needed(self):
        # Decode token expiry and refresh if needed
        import jwt
        try:
            jwt.decode(self.access_token, options={"verify_signature": False})
        except jwt.ExpiredSignatureError:
            self._refresh_access_token()
    
    def _refresh_access_token(self):
        response = requests.post(
            'http://localhost:8000/api/v1/auth/token/refresh/',
            json={'refresh': self.refresh_token}
        )
        self.access_token = response.json()['access']
    
    def request(self, method, endpoint, **kwargs):
        self.refresh_token_if_needed()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        return requests.request(
            method,
            f'http://localhost:8000/api/v1{endpoint}',
            headers=headers,
            **kwargs
        )
```

---

## Changing Password

**POST /auth/change_password/**

```bash
curl -X POST http://localhost:8000/api/v1/auth/change_password/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "CurrentPassword123",
    "new_password": "NewSecurePassword456"
  }'
```

**Response:**
```json
{
    "message": "Password changed successfully"
}
```

---

## User Management (Admin Only)

### Create New User

**POST /auth/create_user/**

Roles allowed: SUPER_ADMIN, NDMA_ADMIN, TECHNICAL_ADMIN

```bash
curl -X POST http://localhost:8000/api/v1/auth/create_user/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePassword123",
    "first_name": "John",
    "last_name": "Doe",
    "user_role": "STATE_ADMIN"
  }'
```

**Response:**
```json
{
    "message": "User created successfully",
    "user": {
        "id": 5,
        "email": "newuser@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "user_role": "STATE_ADMIN",
        "is_active": true
    }
}
```

---

## Common Issues

### Issue: "Token is invalid or expired"

**Solution:**
1. Check token hasn't expired (they expire by default after 15 minutes)
2. Use refresh token to get new access token
3. Ensure you're using Bearer token format correctly

---

### Issue: "You do not have permission..."

**Solution:**
1. Check user's role
2. Verify role has required permission
3. Contact admin if permission needed
4. Check geographic restrictions (state/district code)

---

### Issue: "Authentication credentials were not provided"

**Solution:**
1. Include Authorization header in request
2. Use correct format: `Authorization: Bearer <token>`
3. Don't include "Bearer" twice

---


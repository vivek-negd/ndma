# NDMA API - Quick Reference Card

## 🚀 Start Server
```bash
python manage.py runserver 8000
```
Visit: http://127.0.0.1:8000/api/v1/

---

## 🔐 Login (Get Token)

**Endpoint**: `POST /api/v1/auth/login/`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@ndma.gov.in",
    "password": "Admin@2025"
  }'
```

**Response** (save the `access` token):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "email": "admin@ndma.gov.in",
    "user_role": "SUPER_ADMIN"
  }
}
```

---

## 👤 Create New User (SUPER_ADMIN Only)

**Endpoint**: `POST /api/v1/auth/create_user/`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/create_user/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass@2026",
    "name": "User Full Name",
    "mobile": "9876543210",
    "designation": "Officer",
    "aadhar": "123456789012",
    "user_role": "SDMA_ADMIN",
    "state_code": "PY"
  }'
```

### Password Rules
- ✅ Minimum 8 characters
- ✅ Mix of uppercase, lowercase, numbers, special chars
- ✅ Each user gets unique password

### User Roles Available
```
SUPER_ADMIN              ← Can create users
NDMA_ADMIN              ← Can create users
TECHNICAL_ADMIN         ← Can create users
SDMA_ADMIN              ← State admin (cannot create users)
DDMA_NODAL_OFFICER      ← District officer
TRAINING_INSTITUTE      ← Training center
YOUTH_ORG_ADMIN         ← Organization admin
VOLUNTEER               ← Volunteer
PUBLIC_USER             ← General public
```

---

## 🔄 Change Password

**Endpoint**: `POST /api/v1/auth/change_password/`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/change_password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "old_password": "Admin@2025",
    "new_password": "NewSecure@2026"
  }'
```

---

## 🏥 Health Check

```bash
# Simple alive check
curl http://127.0.0.1:8000/api/v1/health/alive/

# Detailed status
curl http://127.0.0.1:8000/api/v1/health/status/

# System info
curl http://127.0.0.1:8000/api/v1/health/system-info/
```

---

## 🗂️ Get User Profile

```bash
curl -X GET http://127.0.0.1:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 👥 List All Users

```bash
curl -X GET http://127.0.0.1:8000/api/v1/users/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔑 Refresh Token

If your token expires:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

---

## 📱 Example: Create Volunteer

```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

curl -X POST http://127.0.0.1:8000/api/v1/auth/create_user/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "email": "volunteer@example.com",
    "password": "VolPass@2026",
    "name": "Raj Kumar",
    "mobile": "9111111111",
    "designation": "NCC Cadet",
    "aadhar": "987654321098",
    "user_role": "VOLUNTEER",
    "state_code": "PY",
    "district_code": "1"
  }'
```

---

## 🗄️ Database Commands

### Check Tables
```bash
mysql -h127.0.0.1 -uroot -p251024 -e "USE ndma_dev_db; SHOW TABLES;"
```

### Check User Count
```bash
mysql -h127.0.0.1 -uroot -p251024 -e "USE ndma_dev_db; SELECT COUNT(*) FROM models_user;"
```

### Check RBAC
```bash
mysql -h127.0.0.1 -uroot -p251024 -e "USE ndma_dev_db; SELECT 'Roles' as Type, COUNT(*) FROM roles UNION SELECT 'Permissions', COUNT(*) FROM permissions UNION SELECT 'Mappings', COUNT(*) FROM roles_permissions;"
```

### Backup Database
```bash
mysqldump -h127.0.0.1 -uroot -p251024 ndma_dev_db > backup.sql
```

### Restore Database
```bash
mysql -h127.0.0.1 -uroot -p251024 ndma_dev_db < backup.sql
```

---

## 🐛 Error Responses

### 401 Unauthorized
```json
{"detail": "Invalid token or token expired"}
```
**Solution**: Get new token via login

### 403 Forbidden
```json
{"error": "Only SUPER_ADMIN/NDMA_ADMIN/TECHNICAL_ADMIN can create users"}
```
**Solution**: Use SUPER_ADMIN account to create users

### 400 Bad Request
```json
{"mobile": ["Mobile must be a 10 digit number"]}
```
**Solution**: Provide valid 10-digit mobile number

### 409 Conflict
```json
{"email": ["User with this email already exists"]}
```
**Solution**: Use different email address

---

## 📊 Current Status

| Component | Status |
|-----------|--------|
| Database | ✅ MariaDB ndma_dev_db |
| Tables | ✅ 23 created |
| Migrations | ✅ 19 applied |
| RBAC Roles | ✅ 9 seeded |
| Permissions | ✅ 50+ seeded |
| Superuser | ✅ admin@ndma.gov.in |
| API | ✅ Ready for use |
| Health Check | ✅ Working |

---

## 📞 Quick Links

- **Admin Panel**: http://127.0.0.1:8000/admin/ (use superuser creds)
- **API Root**: http://127.0.0.1:8000/api/v1/
- **Full Docs**: See README.md

---

**Version**: 1.0.0 | **Date**: March 2026 | **Status**: Production Ready

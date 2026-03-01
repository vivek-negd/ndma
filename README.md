# NDMA API - National Disaster Management Authority
**REST API for Disaster Management, Training & Volunteer Coordination**

**Version**: 1.0.0 (Fresh Setup - March 2026)  
**Status**: ✅ Production Ready  
**Database**: MariaDB (ndma_dev_db)  
**Python**: 3.11+ | Django: 5.0.3 | DRF: 3.15.1

---

## 📋 Quick Start

### Prerequisites
- Python 3.11+
- MariaDB 10.5+
- Git

### Installation
```bash
# Clone repo
git clone <repo-url>
cd ndma_api

# Create virtual environment
python -m venv ndma-venv
source ndma-venv/Scripts/activate  # Windows
# or: source ndma-venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set environment variables (.env)
cp .env.example .env
# Edit .env with your MariaDB credentials

# Run migrations
python manage.py migrate

# Seed RBAC
python manage.py seed_rbac

# Create superuser (if not already created)
python manage.py createsuperuser

# Start server
python manage.py runserver 8000
```

**API URL**: `http://127.0.0.1:8000/api/v1/`  
**Admin Panel**: `http://127.0.0.1:8000/admin/`  
**Health Check**: `http://127.0.0.1:8000/api/v1/health/status/`

---

## 🔐 Authentication

### JWT Token Flow
1. **Login**: `POST /api/v1/auth/login/`
   ```json
   {
     "email": "admin@ndma.gov.in",
     "password": "Admin@2025"
   }
   ```
   Response:
   ```json
   {
     "access": "eyJ0eXAiOiJKV1QiL...",
     "refresh": "eyJ0eXAiOiJKV1QiL...",
     "user": { "email": "admin@ndma.gov.in", "user_role": "SUPER_ADMIN" }
   }
   ```

2. **Use Token**: Add to headers for authenticated requests
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiL...
   ```

3. **Refresh Token**: `POST /api/v1/auth/token/refresh/`
   ```json
   {"refresh": "<REFRESH_TOKEN>"}
   ```

### Superuser Credentials (Fresh Setup)
- **Email**: `admin@ndma.gov.in`
- **Password**: `Admin@2025`

---

## 👥 User Roles (9 Total)

| Role | Description | Can Create Users |
|------|-------------|------------------|
| **SUPER_ADMIN** | System administrator | ✅ Yes |
| **NDMA_ADMIN** | National admin | ✅ Yes |
| **TECHNICAL_ADMIN** | Technical support | ✅ Yes |
| **SDMA_ADMIN** | State DMA admin | ❌ No |
| **DDMA_NODAL_OFFICER** | District nodal officer | ❌ No |
| **TRAINING_INSTITUTE** | Training center | ❌ No |
| **YOUTH_ORG_ADMIN** | Youth organization admin | ❌ No |
| **VOLUNTEER** | Volunteer | ❌ No |
| **PUBLIC_USER** | General public | ❌ No |

---

## 📊 Database Schema (23 Tables)

### Core Models
- **models_user** - User accounts & profiles (1 superuser created)
- **models_district** - Districts (empty, seeded via LGD)
- **models_state** - States (empty, seeded via LGD)
- **models_organization** - Organizations (NCC, NSS, etc.)
- **models_volunteer** - Volunteer records
- **models_auditlog** - Action audit logs
- **models_training_schedule** - Training schedules
- **models_training_session** - Training sessions

### RBAC Models
- **roles** - 9 roles seeded
- **permissions** - 50+ permissions seeded
- **roles_permissions** - Role-permission mappings (56 records)
- **user_roles** - User role assignments
- **user_permission_overrides** - User-specific permission overrides
- **role_permission_audits** - Audit trail of RBAC changes

### Django Built-in Tables
- **auth_user, auth_group, auth_permission** - Django auth
- **django_migrations** - Migration history (19 applied)
- **django_content_type, django_admin_log, django_session** - DRF/Admin

---

## 🔌 API Endpoints

### Health & Monitoring
```
GET  /api/v1/health/alive/          # Simple health check
GET  /api/v1/health/status/         # Detailed status
GET  /api/v1/health/system-info/    # System metrics
```

### Authentication
```
POST /api/v1/auth/login/            # Login with email/password
POST /api/v1/auth/create_user/      # Create new user (SUPER_ADMIN only)
POST /api/v1/auth/logout/           # Logout (invalidate session)
GET  /api/v1/auth/profile/          # Get current user profile
POST /api/v1/auth/change_password/  # Change own password
POST /api/v1/auth/token/refresh/    # Refresh JWT token
```

### RBAC Management
```
GET    /api/v1/rbac/permissions/                      # List all permissions
GET    /api/v1/rbac/permissions/<id>/                 # Permission detail
GET    /api/v1/rbac/roles/                            # List all roles
POST   /api/v1/rbac/roles/                            # Create role (SUPER_ADMIN)
PUT/PATCH /api/v1/rbac/roles/<id>/                    # Update role
DELETE /api/v1/rbac/roles/<id>/                       # Delete role
POST   /api/v1/rbac/roles/<id>/assign_permission/     # Add permission to role
POST   /api/v1/rbac/roles/<id>/revoke_permission/     # Remove permission from role
GET    /api/v1/rbac/user-roles/                       # List user role mappings
POST   /api/v1/rbac/user-roles/                       # Assign role to user
PUT/PATCH /api/v1/rbac/user-roles/<id>/               # Update user role
POST   /api/v1/rbac/user-roles/<id>/activate/         # Activate mapping
POST   /api/v1/rbac/user-roles/<id>/deactivate/       # Deactivate mapping
GET    /api/v1/rbac/audit/                            # Audit log
```

### User Management
```
GET  /api/v1/users/                 # List users (filtered by role)
GET  /api/v1/users/<id>/            # User detail
PUT  /api/v1/users/<id>/            # Update user profile
```

### Master Data
```
GET  /api/v1/states/                # List states
GET  /api/v1/districts/             # List districts (filter by state)
GET  /api/v1/organizations/         # List organizations
POST /api/v1/organizations/         # Create organization (NDMA_ADMIN)
```

### Volunteers
```
POST /api/v1/volunteer/create/              # Create single volunteer
POST /api/v1/volunteer/bulk-upload/         # Bulk upload (CSV)
GET  /api/v1/volunteer/                     # List volunteers
GET  /api/v1/volunteer/<id>/                # Volunteer detail
```

---

## 📝 Example: Create New User

**Only SUPER_ADMIN/NDMA_ADMIN/TECHNICAL_ADMIN** can create users.

### Step 1: Get Access Token
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@ndma.gov.in",
    "password": "Admin@2025"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {"email": "admin@ndma.gov.in", "user_role": "SUPER_ADMIN"}
}
```

### Step 2: Create User
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/create_user/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass@2026",
    "name": "Amit Kumar",
    "mobile": "9876543210",
    "designation": "State Officer",
    "aadhar": "123456789012",
    "user_role": "SDMA_ADMIN",
    "state_code": "PY",
    "district_code": null,
    "is_active": true
  }'
```

**Password Policy**:
- Minimum 8 characters
- Recommended: Mix of uppercase, lowercase, numbers, special chars
- Each user gets unique password set by admin
- Users can change password via `/api/v1/auth/change_password/`

---

## ⚙️ Configuration

### Environment Variables (.env)
```ini
# Database
DB_NAME_DEV=ndma_dev_db
DB_USER_DEV=root
DB_PASSWORD_DEV=251024
DB_HOST_DEV=127.0.0.1
DB_PORT_DEV=3306

# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=127.0.0.1,localhost

# JWT
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Settings Hierarchy
- `config/settings/base.py` - Shared settings
- `config/settings/dev.py` - Development (default)
- `config/settings/prod.py` - Production
- `config/settings/uat.example.py` - UAT template

---

## 🗄️ Database Management

### Fresh Setup (from scratch)
```bash
# Drop existing database and recreate
mysql -h127.0.0.1 -uroot -p251024 -e "DROP DATABASE IF EXISTS ndma_dev_db; CREATE DATABASE ndma_dev_db CHARACTER SET utf8mb4"

# Create fresh migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Seed RBAC
python manage.py seed_rbac
```

### Backup & Restore
```bash
# Backup
mysqldump -h127.0.0.1 -uroot -p251024 ndma_dev_db > backup.sql

# Restore
mysql -h127.0.0.1 -uroot -p251024 ndma_dev_db < backup.sql
```

### Check Database Status
```bash
# List all tables
mysql -h127.0.0.1 -uroot -p251024 -e "USE ndma_dev_db; SHOW TABLES;"

# Table structure
mysql -h127.0.0.1 -uroot -p251024 -e "USE ndma_dev_db; DESC models_user;"

# Row counts
mysql -h127.0.0.1 -uroot -p251024 -e "USE ndma_dev_db; SELECT TABLE_NAME, TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='ndma_dev_db' ORDER BY TABLE_NAME;"
```

---

## 🚀 Deployment

### Development
```bash
python manage.py runserver 8000
```

### Production (using Gunicorn)
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Docker (optional)
See `Dockerfile` and `docker-compose.yml` for containerized deployment.

---

## 🧪 Testing

### Run Tests
```bash
python manage.py test api.v1.test
```

### Test Coverage
```bash
coverage run --source='.' manage.py test
coverage report
```

---

## 📋 Project Structure

```
ndma_api/
├── config/                 # Django settings
│   ├── settings/
│   │   ├── base.py        # Shared settings
│   │   ├── dev.py         # Development
│   │   ├── prod.py        # Production
│   │   └── uat.example.py # UAT template
│   ├── urls.py            # ROOT URL routing
│   ├── wsgi.py            # WSGI server
│   └── asgi.py            # ASGI server
├── api/                    # Main app
│   └── v1/                # API v1
│       ├── views/         # ViewSets for endpoints
│       ├── serializers/   # DRF serializers
│       ├── permissions.py # Custom permissions
│       ├── urls.py        # API routing
│       └── views/         # Views
├── models/                # Database models
│   ├── user.py           # User model
│   ├── organization.py   # Organization
│   ├── volunteer.py      # Volunteer
│   ├── role.py           # Role model
│   ├── district.py       # District
│   ├── state.py          # State
│   ├── managers.py       # Custom managers
│   └── migrations/       # Database migrations (19 applied)
├── core/                  # Core utilities
│   ├── authentication.py # Auth logic
│   ├── rbac_permissions.py # RBAC checks
│   ├── exceptions.py     # Custom exceptions
│   └── utils/            # Helpers & utilities
├── middlewares/           # Custom middlewares
├── services/              # Business logic
├── manage.py             # Django CLI
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
└── README.md             # This file
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: `No such table: models_user`
- **Solution**: Run `python manage.py migrate`

**Issue**: `ModuleNotFoundError: No module named 'xyz'`
- **Solution**: Run `pip install -r requirements.txt`

**Issue**: `Connection refused` (MariaDB)
- **Solution**: Verify MariaDB is running and credentials in .env are correct

**Issue**: `CORS error` in frontend
- **Solution**: Update `CORS_ALLOWED_ORIGINS` in settings

**Issue**: `Invalid token` or `TokenError`
- **Solution**: Token may be expired, refresh using `/api/v1/auth/token/refresh/`

---

## 📞 Support & Documentation

- **API Reference**: See endpoint examples above
- **RBAC Guide**: [RBAC Design Document](./docs/RBAC_DESIGN.md)
- **Database Schema**: [Schema Details](./docs/DATABASE_SCHEMA.md)
- **Troubleshooting**: [FAQ & Issues](./docs/TROUBLESHOOTING.md)
- **Contributing**: [Contribution Guidelines](./CONTRIBUTING.md)

---

## 📄 License

Government of India - NDMA  
All rights reserved

---

## ✅ Setup Verification Checklist

- ✅ Database: MariaDB ndma_dev_db (23 tables created)
- ✅ Schema: All migrations applied (19 migrations)
- ✅ RBAC: 9 roles + 50+ permissions seeded
- ✅ Superuser: Created (admin@ndma.gov.in / Admin@2025)
- ✅ Dependencies: All installed from requirements.txt
- ✅ Health Endpoints: Ready for monitoring
- ✅ System Check: No issues found ✓

**Last Updated**: March 2, 2026  
**Status**: 🟢 Production Ready

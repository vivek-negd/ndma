# NDMA Volunteer API - Complete Documentation

Welcome to the NDMA Volunteer Management API comprehensive documentation.

---

## Quick Navigation

### 📚 Getting Started
- **[QUICK_START.md](QUICK_START.md)** - 5-minute setup guide (START HERE)
- **[AUTHENTICATION.md](AUTHENTICATION.md)** - JWT authentication & RBAC

### 🚀 API Reference
- **[API_ENDPOINTS.md](API_ENDPOINTS.md)** - All 40+ endpoints with examples (2000+ lines)
- **[API_EXAMPLES.md](API_EXAMPLES.md)** - Code samples in Python, cURL, JavaScript
- **[VOLUNTEERS.md](VOLUNTEERS.md)** - Volunteer API complete guide
- **[ERROR_CODES.md](ERROR_CODES.md)** - All error scenarios & solutions

### 🗄️ Technical
- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Database tables, fields, relationships
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Setup in Dev, Staging, Production

---

## Documentation Overview

### 1. QUICK_START.md (5 minutes)
**Best for:** First-time users, quick testing

- Get authentication token
- Create single volunteer
- Bulk upload volunteers
- Common tasks
- Quick endpoints reference
- Field reference

### 2. API_ENDPOINTS.md (2000+ lines)
**Best for:** Complete API reference

- All 40+ endpoints documented
- Authentication endpoints (5)
- User management endpoints (2)
- Organization endpoints (7)
- RBAC endpoints (8)
- Training endpoints (6)
- Volunteer endpoints (4)
- Health check endpoints (5)
- Statistics endpoints (2)
- Each endpoint includes:
  - HTTP method
  - Path with parameters
  - Request example
  - Response example (multiple status codes)
  - Query parameters
  - Permission requirements

### 3. API_EXAMPLES.md (900+ lines)
**Best for:** Code samples

- Python examples (requests library)
- JavaScript examples (axios, fetch)
- cURL command examples
- Complete working code
- Authentication flow
- Volunteer operations
- Bulk examples

### 4. AUTHENTICATION.md (400+ lines)
**Best for:** Security & permissions

- JWT authentication flow
- Token management (access/refresh)
- User roles (8 types)
- RBAC (Role-Based Access Control)
- Permission system
- Geographic access control
- Security best practices
- Troubleshooting auth issues

### 5. VOLUNTEERS.md (800+ lines)
**Best for:** Volunteer operations

- Single volunteer creation
- Bulk volunteer CSV upload
- Volunteer coverage statistics
- Field-by-field documentation
- CSV format guide
- Choice field values
- Validation rules
- Common errors
- Best practices
- Workflow diagrams

### 6. ERROR_CODES.md (700+ lines)
**Best for:** Troubleshooting

- Standard HTTP status codes (200, 201, 400, 401, 403, 404, 409, 422, 429, 500)
- Error response format
- Authentication errors (401)
- Permission errors (403)
- Validation errors (422)
- Resource not found errors (404)
- Bulk upload errors
- Rate limiting (429)
- Server errors (500)
- Error handling best practices
- Troubleshooting guide

### 7. DATABASE_SCHEMA.md (600+ lines)
**Best for:** Data structure

- Complete SQL schema
- 12 core tables:
  - Volunteer (27 fields)
  - Organization
  - State
  - District
  - User
  - Role
  - Permission
  - RolePermission
  - RoleAssignment
  - Training
  - TrainingAttendance
  - AuditLog
- Choice field values
- Relationships & ER diagram
- Indexes & optimization
- Backup & recovery

### 8. DEPLOYMENT.md (800+ lines)
**Best for:** DevOps & deployment

- Development setup (local)
- Staging deployment
- Production setup
- Security hardening
- Database optimization
- Scaling (horizontal/vertical/auto)
- Monitoring & alerts
- Troubleshooting
- Disaster recovery
- Rollback procedures

---

## File Structure

```
docs/
├── README.md                    ← You are here
├── QUICK_START.md              ← Start here (5 min)
├── API_ENDPOINTS.md            ← Complete endpoint reference
├── API_EXAMPLES.md             ← Code samples
├── AUTHENTICATION.md           ← JWT & RBAC
├── VOLUNTEERS.md               ← Volunteer operations
├── ERROR_CODES.md              ← Error troubleshooting
├── DATABASE_SCHEMA.md          ← Database structure
└── DEPLOYMENT.md               ← DevOps guide
```

---

## Which Document to Read?

### "I just want to try the API"
→ Read [QUICK_START.md](QUICK_START.md) (5 min)

### "I need all endpoint details"
→ Read [API_ENDPOINTS.md](API_ENDPOINTS.md) (30 min)

### "I want code examples"
→ Read [API_EXAMPLES.md](API_EXAMPLES.md) (15 min)

### "How do I authenticate?"
→ Read [AUTHENTICATION.md](AUTHENTICATION.md) (10 min)

### "How do I upload volunteers?"
→ Read [VOLUNTEERS.md](VOLUNTEERS.md) (15 min)

### "I'm getting errors"
→ Read [ERROR_CODES.md](ERROR_CODES.md) (20 min)

### "I need to deploy"
→ Read [DEPLOYMENT.md](DEPLOYMENT.md) (45 min)

### "What's the database schema?"
→ Read [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) (25 min)

---

## Common Scenarios

### Scenario 1: First-Time Setup
1. Read [QUICK_START.md](QUICK_START.md) - sections 1-3
2. Test with curl command
3. Read [AUTHENTICATION.md](AUTHENTICATION.md) - JWT section
4. Try creating volunteers from [QUICK_START.md](QUICK_START.md) - section Task 1

### Scenario 2: Bulk Upload
1. Read [VOLUNTEERS.md](VOLUNTEERS.md) - Endpoints section
2. Use CSV template from [VOLUNTEERS.md](VOLUNTEERS.md)
3. Upload with examples from [API_EXAMPLES.md](API_EXAMPLES.md)
4. If errors, check [ERROR_CODES.md](ERROR_CODES.md)

### Scenario 3: Production Deployment
1. Read [DEPLOYMENT.md](DEPLOYMENT.md) - Production Setup
2. Read [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Optimization section
3. Configure based on checklist in [DEPLOYMENT.md](DEPLOYMENT.md)
4. Monitor using guidelines in [DEPLOYMENT.md](DEPLOYMENT.md)

### Scenario 4: Developer Integration
1. Read [QUICK_START.md](QUICK_START.md) - full
2. Read [API_EXAMPLES.md](API_EXAMPLES.md) - select language
3. Read [AUTHENTICATION.md](AUTHENTICATION.md) - RBAC section
4. Reference [API_ENDPOINTS.md](API_ENDPOINTS.md) - needed endpoints
5. Implement error handling from [ERROR_CODES.md](ERROR_CODES.md)

---

## API Overview

### Authentication
```
POST   /api/v1/auth/login/              - Get access token
POST   /api/v1/auth/token/refresh/      - Refresh token
POST   /api/v1/auth/logout/             - Logout
```

### Volunteers (Most Used)
```
POST   /api/v1/volunteer/create/        - Create single volunteer
POST   /api/v1/volunteer/bulk-upload/   - Bulk CSV upload
GET    /api/v1/volunteer/coverage/      - Get statistics
```

### Management
```
GET/POST/PUT/DELETE /api/v1/organizations/    - Organization CRUD
GET/POST/PUT/DELETE /api/v1/users/            - User management
GET/POST/PUT/DELETE /api/v1/roles/            - Role management
POST /api/v1/role-assignments/                - Assign roles
```

### Training
```
GET/POST /api/v1/training/schedules/   - Training CRUD
POST /api/v1/training/attendance/      - Mark attendance
```

### System
```
GET /api/v1/health/status/             - Health check
GET /api/v1/health/alive/              - Server alive
GET /api/v1/health/readiness/          - Ready for requests
```

---

## Choice Field Reference

| Type | Values | Example |
|------|--------|---------|
| Gender | Male(1), Female(2), Other(3) | Can use "Male" or 1 |
| Blood | A+(1)...AB-(8) | Can use "O+" or 5 |
| Salutation | Mr(1), Mrs(2), Ms(3), Dr(4), Prof(5) | Can use "Dr." or 4 |
| Education | Below10th(1)...PhD(7) | Can use "Bachelor" or 5 |
| Skill | FirstAid(1)...Other(6) | Can use "Training" or 5 |
| Area | Urban(1), Rural(2), SemiUrban(3) | Can use "Urban" or 1 |
| Marital | Single(1)...Separated(5) | Can use "Married" or 2 |

---

## Key Concepts

### Volunteer
A registered disaster management volunteer with personal & professional details.

### Organization
NGO/disaster management organization managing volunteers.

### Role
User role defining permissions (SUPER_ADMIN, NATIONAL_ADMIN, STATE_ADMIN, etc.)

### State/District
Geographic divisions for volunteer management.

### Token
JWT authentication token (15 min access, 7 day refresh).

### RBAC
Role-Based Access Control - permissions based on user role & geographic scope.

---

## Response Format

### Success Response (200/201)
```json
{
    "data": {...},
    "message": "Success"
}
```

### Error Response (400/422)
```json
{
    "field_name": ["Error message"],
    "another_field": ["Error 1", "Error 2"]
}
```

### Bulk Upload Response
```json
{
    "created_count": 5,
    "created_mis_ids": [10001, 10002, ...],
    "error_count": 1,
    "errors": [
        {
            "index": 3,
            "errors": {"email": ["Duplicate"]}
        }
    ]
}
```

---

## Performance Guidelines

### Single Upload
- Use when: < 10 volunteers
- Latency: 50-100ms
- Endpoint: POST /volunteer/create/

### Bulk Upload
- Use when: 10-1000 volunteers
- Latency: 5-10ms per volunteer
- Endpoint: POST /volunteer/bulk-upload/
- Format: CSV file

### Queries
- List volunteers: Max 1000 per page (use pagination)
- Filter by state: Fast (indexed)
- Filter by organization: Fast (indexed)

---

## Troubleshooting Paths

| Problem | Solution | Docs |
|---------|----------|------|
| Can't get token | Check credentials, server running | [AUTHENTICATION.md](AUTHENTICATION.md) |
| Volunteer won't upload | Check field validation, unique constraints | [VOLUNTEERS.md](VOLUNTEERS.md), [ERROR_CODES.md](ERROR_CODES.md) |
| Permission denied | Check user role & geographic scope | [AUTHENTICATION.md](AUTHENTICATION.md) |
| High response time | Check database indexes | [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) |
| Server won't start | Check database connection | [DEPLOYMENT.md](DEPLOYMENT.md) |

---

## Useful Links

### API Features
- **Volunteer Management**: Upload single/bulk, track coverage
- **RBAC**: 8 roles, geographic scoping, permission matrix
- **Training**: Schedule, attendance tracking
- **Audit**: Complete activity log for compliance
- **Health**: System monitoring endpoints
- **Statistics**: Coverage by organization/state/district

### Tech Stack
- **Framework**: Django 4.2.5 + Django REST Framework 3.14.0
- **Database**: MySQL 5.7+
- **Cache**: Redis
- **Auth**: JWT (SimpleJWT)
- **Python**: 3.8+

### Environment
- **Dev**: http://localhost:8000
- **Staging**: https://staging.ndma.gov.in
- **Production**: https://api.ndma.gov.in

---

## Getting Help

### Documentation Issues
- Check the troubleshooting section in relevant doc
- Search [ERROR_CODES.md](ERROR_CODES.md) for your error
- Review code examples in [API_EXAMPLES.md](API_EXAMPLES.md)

### API Issues
- Check server health: GET /api/v1/health/status/
- Review recent errors: GET /api/v1/health/logs/
- Check database: GET /api/v1/health/database/

### Deployment Issues
- Follow [DEPLOYMENT.md](DEPLOYMENT.md) setup steps
- Check logs on server
- Review troubleshooting section

---

## Version Info

- **API Version**: v1
- **Documentation Version**: 1.0
- **Last Updated**: 2026-03-02
- **Maintained By**: NDMA Dev Team

---

## Document Index

| Document | Lines | Focus | Read Time |
|----------|-------|-------|-----------|
| QUICK_START.md | 300 | Getting started | 5 min |
| API_ENDPOINTS.md | 2000+ | Complete reference | 30 min |
| API_EXAMPLES.md | 900+ | Code samples | 15 min |
| AUTHENTICATION.md | 400+ | JWT & RBAC | 10 min |
| VOLUNTEERS.md | 800+ | Volunteer ops | 15 min |
| ERROR_CODES.md | 700+ | Troubleshooting | 20 min |
| DATABASE_SCHEMA.md | 600+ | Data structure | 25 min |
| DEPLOYMENT.md | 800+ | DevOps | 45 min |
| **TOTAL** | **6500+** | Complete API docs | **2+ hours** |

---

## Start Reading

**First time here?** → Go to [QUICK_START.md](QUICK_START.md)

**Want specifics?** → Use navigation at top or table of contents

**Looking for code?** → Check [API_EXAMPLES.md](API_EXAMPLES.md)

**Getting errors?** → See [ERROR_CODES.md](ERROR_CODES.md)

---


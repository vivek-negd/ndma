# Testing Quick Reference & Execution Guide

**Project:** NDMA Training Management API  
**Testing Phase:** End-to-End Validation  
**Credentials:** Super Admin (superadmin@ndma.gov.in / !YLRdJQc6u8njs^0)  
**Database:** MySQL (Non-destructive testing required)

---

## **Quick Start Checklist**

### **Step 1: Pre-Testing Setup** (30 minutes)
- [ ] Start Django dev server: `python manage.py runserver`
- [ ] Start frontend: `npm start` (port 5173)
- [ ] Verify database connectivity
- [ ] Create testing users (SDMA_ADMIN, DDMA_OFFICER, INSTITUTE)
- [ ] Note down user credentials

### **Step 2: API Authentication** (5 minutes)
- [ ] Login with Super Admin credentials
- [ ] Save JWT access token in `$TOKEN` environment variable
- [ ] Verify token is valid (test a GET request)

### **Step 3: Run API Test Cases** (45 minutes)
- [ ] Execute all 14 test cases from `API_TEST_CASES.md`
- [ ] Log results (pass/fail) for each test
- [ ] Note any error messages or unexpected responses
- [ ] Screenshot failures if encountered

### **Step 4: Database Validation** (30 minutes)
- [ ] Run all 16 integrity checks from `DATABASE_VALIDATION.md`
- [ ] Verify no orphaned records
- [ ] Check foreign key integrity
- [ ] Validate timestamps
- [ ] Record results

### **Step 5: RBAC Security Testing** (60 minutes)
- [ ] Create test users for each role
- [ ] Execute all 20+ RBAC test cases from `RBAC_TESTING.md`
- [ ] Verify no data leakage between users
- [ ] Check permission enforcement
- [ ] Document security findings

### **Step 6: Cleanup & Report** (15 minutes)
- [ ] Delete all test data (batch numbers starting with "TEST-" or "RBAC-")
- [ ] Verify database is clean
- [ ] Generate test report
- [ ] Sign off on validation

**Total Testing Time:** ~3 hours

---

## **Key Test Files & Their Purpose**

| File | Purpose | Time |
|------|---------|------|
| **E2E_TEST_PLAN.md** | High-level workflow + DB checks | 45m |
| **API_TEST_CASES.md** | 14 API endpoint tests with curl examples | 45m |
| **DATABASE_VALIDATION.md** | 16 SQL integrity queries | 30m |
| **RBAC_TESTING.md** | Security tests for all 6 user roles | 60m |
| **QUICK_REFERENCE.md** (this file) | Fast lookup & execution guide | - |

---

## **Database Tables Affected During Testing**

| Table | Read | Create | Update | Delete |
|-------|------|--------|--------|--------|
| models_training_schedule | ✅ | ✅ | ✅ | ✅ |
| models_training_session | ✅ | ✅ | ✅ (via parent) | ✅ (cascade) |
| models_training_session_media | ✅ | ✅ | ✅ | ✅ (cascade) |
| auth_user | ✅ | (create test users) | ❌ | ❌ |

**⚠️ IMPORTANT:** All test data must match pattern `TEST-*` or `RBAC-*` for safe cleanup.

---

## **Environment Setup Commands**

### **Start Django Server**
```bash
# Activate virtual environment
.\ndma-venv\Scripts\activate

# Run migrations (if needed)
python manage.py migrate

# Start development server
python manage.py runserver
```

### **Start Frontend**
```bash
# In frontend directory
npm start
# Should open at http://localhost:5173
```

### **Access Django Shell (For Manual Queries)**
```bash
python manage.py shell

# Then:
from models.training import TrainingSchedule
from django.contrib.auth.models import User
# ... run queries
```

### **Access MySQL Directly (If Needed)**
```bash
mysql -u root -p ndma_api
# Enter password when prompted
```

---

## **Authentication - Getting JWT Token**

### **Method 1: Via API (cURL)**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@ndma.gov.in",
    "password": "!YLRdJQc6u8njs^0"
  }' | jq '.access_token' -r
```

### **Method 2: Via Django Shell**
```python
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

user = User.objects.get(email='superadmin@ndma.gov.in')
token = Token.objects.get(user=user)
print(token.key)
```

### **Save Token to Environment Variable (Windows PowerShell)**
```powershell
$TOKEN = (curl -s -X POST http://localhost:8000/api/v1/auth/login/ `
  -H "Content-Type: application/json" `
  -d '@{"email":"superadmin@ndma.gov.in","password":"!YLRdJQc6u8njs^0"}' | ConvertFrom-Json).access_token

$env:TOKEN = $TOKEN
echo $env:TOKEN  # Verify
```

### **Save Token to Environment Variable (Bash/Linux)**
```bash
export TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@ndma.gov.in","password":"!YLRdJQc6u8njs^0"}' | jq -r '.access_token')

echo $TOKEN
```

---

## **API Endpoints Quick Reference**

| Endpoint | Method | Purpose | Status Code |
|----------|--------|---------|------------|
| `/training-schedules/` | GET | List all | 200 |
| `/training-schedules/` | POST | Create new | 201 |
| `/training-schedules/{id}/` | GET | Retrieve one | 200 |
| `/training-schedules/{id}/` | PATCH | Update | 200 |
| `/training-schedules/{id}/` | DELETE | Delete | 204 |
| `/training-schedules/create_daywise/` | POST | Create with Day1 auto-extract | 201 |
| `/training-schedules/create_daywise_with_media/` | POST | Create + upload media | 201 |
| `/training-schedules/session_history/` | GET | List with pagination | 200 |
| `/training-schedules/training_report/` | GET | Analytics by day | 200 |
| `/training-schedules/list_batch_numbers/` | GET | Batch dropdown | 200 |

---

## **Test Data Naming Convention**

**All test data MUST follow this pattern for safe cleanup:**

```
TEST-E2E-*      # End-to-end workflow tests
RBAC-*          # RBAC security tests
TEST-BATCH-*    # Generic batch tests
TEST-CASCADE-*  # Cascade delete tests
```

**Example Valid Names:**
- ✅ TEST-E2E-BATCH-01
- ✅ RBAC-STATE6-DT69-001
- ✅ TEST-CASCADE-DELETE-01

**Never Use:**
- ❌ PROD-BATCH (looks like production)
- ❌ My-Test (ambiguous)
- ❌ BATCH-123 (no TEST prefix)

---

## **Common Curl Command Templates**

### **List with Authorization**
```bash
curl -X GET http://localhost:8000/api/v1/training-schedules/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### **Create with Data**
```bash
curl -X POST http://localhost:8000/api/v1/training-schedules/create_daywise/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @request.json
```

### **Update/Patch**
```bash
curl -X PATCH http://localhost:8000/api/v1/training-schedules/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "APPROVED"}'
```

### **Delete**
```bash
curl -X DELETE http://localhost:8000/api/v1/training-schedules/1/ \
  -H "Authorization: Bearer $TOKEN"
```

### **Upload Media**
```bash
curl -X POST http://localhost:8000/api/v1/training-schedules/create_daywise_with_media/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "batch_no=TEST-BATCH-001" \
  -F "day=1" \
  -F "day_date=2026-03-13" \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg"
```

---

## **Error Code Reference**

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 204 | No Content | Delete successful (no response body) |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Invalid/missing token |
| 403 | Forbidden | User lacks permission |
| 404 | Not Found | Resource doesn't exist |
| 405 | Method Not Allowed | Wrong HTTP method |
| 409 | Conflict | Duplicate batch number |
| 500 | Server Error | Server-side bug |

---

## **Database Cleanup Commands**

### **Safe Cleanup - Only Test Data**

**Django Shell (Safest):**
```python
from models.training import TrainingSchedule

# Delete test batches only
test_batches = TrainingSchedule.objects.filter(
    batch_no__contains__in=['TEST-E2E-', 'RBAC-', 'TEST-BATCH-', 'TEST-CASCADE-']
)
count = test_batches.count()
for batch in test_batches:
    batch.delete()  # Cascade delete sessions & media
print(f"Deleted {count} test batches")
```

**SQL (Direct - Use with caution):**
```sql
DELETE FROM models_training_schedule 
WHERE batch_no LIKE 'TEST-%' 
   OR batch_no LIKE 'RBAC-%'
   OR batch_no LIKE 'TEST-CASCADE-%';

-- Verify
SELECT COUNT(*) FROM models_training_schedule 
WHERE batch_no LIKE 'TEST-%' OR batch_no LIKE 'RBAC-%';
```

### **Verify Cleanup**
```python
from models.training import TrainingSchedule

remaining = TrainingSchedule.objects.filter(
    batch_no__startswith__in=['TEST-', 'RBAC-']
).count()

print(f"Test batches remaining: {remaining}")
print("✅ CLEANUP COMPLETE" if remaining == 0 else f"⚠️  {remaining} test batches still present")
```

---

## **Troubleshooting Guide**

### **Issue: 401 Unauthorized**
**Solution:** Token expired or invalid
```bash
# Get new token
export TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@ndma.gov.in","password":"!YLRdJQc6u8njs^0"}' \
  | jq -r '.access_token')
```

### **Issue: 500 Server Error**
**Solution:** Check Django logs
```bash
# Django logs appear in server terminal
# Check last 20 lines for error traceback
# Common causes: DB connection, missing migrations
```

### **Issue: Database Connection Failed**
**Solution:** Verify MySQL is running
```bash
# Windows
net start MySQL80  # or your MySQL service name

# Check connection
python manage.py dbshell
```

### **Issue: CORS/Cross-Origin Error**
**Solution:** Make sure you're using correct API base URL
- ✅ `http://localhost:8000/api/v1/...`
- ❌ `http://127.0.0.1:8000/...` (use localhost)
- ❌ `https://...` (use http for dev)

### **Issue: 404 Not Found**
**Solution:** Check endpoint URL spelling
- ✅ `/training-schedules/` (trailing slash required)
- ❌ `/training-schedule/` (missing 's')
- ❌ `/api/v1/trainings/` (wrong endpoint name)

---

## **Expected Response Structures**

### **Successful Create**
```json
{
  "status_code": 201,
  "message": "Training schedule created",
  "data": {
    "id": 1,
    "batch_no": "TEST-BATCH-001",
    "state_id": 6,
    "status": "DRAFT"
  }
}
```

### **Successful List**
```json
{
  "status_code": 200,
  "count": 5,
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_pages": 1
  },
  "data": [...]
}
```

### **Error Response**
```json
{
  "status_code": 400,
  "message": "Validation error",
  "errors": {
    "field_name": ["Error message"]
  }
}
```

---

## **Test Result Template**

Copy this for each major test phase:

```markdown
## Test Phase: [NAME]
**Date:** [DATE]
**Tester:** [NAME]
**Duration:** [TIME]

### Results
- Total Tests: [X]
- Passed: [X] ✅
- Failed: [X] ❌
- Skipped: [X] ⏭️

### Issues Found
1. [Issue 1] - Impact: HIGH/MEDIUM/LOW
   - Steps to reproduce: ...
   - Expected: ...
   - Actual: ...
   
### Database State After Testing
- TrainingSchedule records: [X]
- TrainingSession records: [X]
- TrainingSessionMedia records: [X]
- Test data cleaned up: YES/NO

### Recommendations
- [ ] Ready for production
- [ ] Needs fixes (list issues)
- [ ] Blocked on (list dependencies)

### Sign-off
Tested by: ________________
Date: ________________
Status: APPROVED / REJECTED
```

---

## **Contact Information**

For issues during testing:
- **API Questions:** Check `API_DOCUMENTATION.md` in docs/
- **RBAC Questions:** Check `ADMIN_PRIVILEGES_SYSTEM_SUMMARY.md`
- **Database Issues:** Check `DATABASE_SCHEMA.md`
- **Frontend Integration:** Check `FRONTEND_API_INTEGRATION_GUIDE.md`

---

## **Quick Links**

- [E2E Test Plan](./E2E_TEST_PLAN.md)
- [API Test Cases](./API_TEST_CASES.md)
- [Database Validation](./DATABASE_VALIDATION.md)
- [RBAC Testing](./RBAC_TESTING.md)
- [API Documentation](../docs/API_DOCUMENTATION.html)
- [Database Schema](../docs/DATABASE_SCHEMA.md)

---

**Testing Status:** ⏳ **READY TO EXECUTE**

**Next Steps:**
1. Set up environment (Django + Frontend running)
2. Start with E2E_TEST_PLAN.md
3. Log all results in provided templates
4. Complete database cleanup
5. Generate final test report


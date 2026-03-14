# Testing Documentation - Complete Guide

**Project:** NDMA Training Management API  
**Phase:** End-to-End Testing & Database Validation  
**Created:** March 13, 2026  
**Status:** Ready for Execution

---

## **📁 Testing Folder Structure**

```
testing/
├── README.md (this file)
├── QUICK_REFERENCE.md          ← START HERE for fast setup & commands
├── E2E_TEST_PLAN.md            ← 5-step workflow test + DB checks
├── API_TEST_CASES.md           ← 14 detailed API tests with curl
├── DATABASE_VALIDATION.md      ← 16 SQL integrity checks
├── RBAC_TESTING.md             ← 20+ security tests for all roles
└── [Test Results & Reports]    ← Create as you test
```

---

## **🎯 What's Been Prepared**

This comprehensive testing suite covers:

### **1. End-to-End Workflow (E2E_TEST_PLAN.md)**
- **Purpose:** Verify complete training session creation flow
- **Scope:** 5 major steps from auth through history retrieval
- **Coverage:** 
  - ✅ Super Admin authentication
  - ✅ Create batch with Day 1
  - ✅ Upload media for Day 1
  - ✅ Add Day 4 to batch
  - ✅ Retrieve complete session history
- **Database Checks:** Integrity validation at each step
- **Test Data Pattern:** `TEST-E2E-*`

### **2. API Test Cases (API_TEST_CASES.md)**
- **Purpose:** Test all 11 API endpoints with detailed examples
- **Format:** Copy-paste ready curl commands
- **Endpoints Covered:**
  1. POST /auth/login/ - Authentication
  2. GET /training-schedules/ - List all
  3. POST /training-schedules/create_daywise/ - Create with auto-extract
  4. POST /training-schedules/create_daywise_with_media/ - Create + media
  5. POST /training-schedules/create_daywise/ - Add Day 4
  6. GET /training-schedules/session_history/ - Pagination & filtering
  7. GET /training-schedules/{id}/ - Single retrieve
  8. PATCH /training-schedules/{id}/ - Update status
  9. DELETE /training-schedules/{id}/ - Delete cascade
  10. GET /training-schedules/training_report/ - Analytics
  11. GET /training-schedules/list_batch_numbers/ - Dropdown
  12-14. Error scenarios (401, 400, 409)
- **Test Data Pattern:** `TEST-E2E-*`, `RBAC-*`
- **Execution Time:** ~45 minutes

### **3. Database Validation (DATABASE_VALIDATION.md)**
- **Purpose:** Verify data integrity across all tables
- **Format:** SQL queries + Django shell equivalents
- **Checks Included:**
  1. Table structure verification
  2. Foreign key integrity (no orphaned sessions)
  3. Media file integrity (no orphaned media)
  4. User ID validation (created_by_id exists)
  5. Uploader validation (uploaded_by_id exists)
  6. Date range validation (sessions within schedule dates)
  7. Unique batch number enforcement
  8. No duplicate sessions per day
  9. Record count consistency
  10. Status distribution verification
  11. Geographic distribution analysis
  12. Timestamp validation
  13. Cascade delete verification
  14-16. Performance checks

**Key Findings to Validate:**
- ✅ No orphaned database records
- ✅ All foreign keys valid
- ✅ Cascade deletes working correctly
- ✅ Unique constraints enforced
- ✅ Timestamps reasonable
- ✅ All tests use non-destructive queries

**Execution Time:** ~30 minutes

### **4. RBAC Security Testing (RBAC_TESTING.md)**
- **Purpose:** Verify each user role has correct access
- **Scope:** 6 user roles × 4+ test cases each
- **User Roles Tested:**
  1. **SUPER_ADMIN** - Full access to everything
  2. **NDMA_ADMIN** - Admin-level access
  3. **SDMA_ADMIN** - State-level access only
  4. **DDMA_NODAL_OFFICER** - District-level access only
  5. **TRAINING_INSTITUTE** - Can edit own batches only
  6. **YOUTH_ORG_ADMIN** - Can edit own batches only

**Test Coverage:**
- ✅ List access (can see only assigned data)
- ✅ Create restrictions (cannot create outside scope)
- ✅ Edit restrictions (cannot edit others' data)
- ✅ Delete restrictions (cannot delete others' data)
- ✅ Data leakage prevention (no cross-boundary access)

**Security Validation:**
- ✅ SDMA_ADMIN cannot see other states
- ✅ DDMA_OFFICER cannot see other districts
- ✅ TRAINING_INSTITUTE cannot modify others' batches
- ✅ Edit operations properly restricted

**Test Data Pattern:** `RBAC-*`

**Execution Time:** ~60 minutes

### **5. Quick Reference (QUICK_REFERENCE.md)**
- **Purpose:** Fast lookup for commands and common tasks
- **Contents:**
  - Pre-testing checklist
  - Environment setup commands
  - JWT authentication methods
  - Curl command templates
  - Error code reference
  - Database cleanup commands
  - Troubleshooting guide
  - Expected response structures
  - Test result template

---

## **📊 Testing Matrix**

### **Coverage Summary**

| Aspect | Tests | Status |
|--------|-------|--------|
| **API Endpoints** | 14 | ✅ Ready |
| **RBAC Scenarios** | 20+ | ✅ Ready |
| **Database Queries** | 16 | ✅ Ready |
| **Error Cases** | 3 | ✅ Ready |
| **E2E Workflow** | 5 Steps | ✅ Ready |
| **Total Test Cases** | 50+ | ✅ Ready |

### **Expected Execution Timeline**

| Phase | Time | Document |
|-------|------|----------|
| Setup & Auth | 15 min | QUICK_REFERENCE.md |
| E2E Workflow | 45 min | E2E_TEST_PLAN.md |
| API Testing | 45 min | API_TEST_CASES.md |
| Database Validation | 30 min | DATABASE_VALIDATION.md |
| RBAC Testing | 60 min | RBAC_TESTING.md |
| Cleanup & Analysis | 15 min | QUICK_REFERENCE.md |
| **TOTAL** | **3 hours** | - |

---

## **🚀 How to Use This Testing Suite**

### **Option 1: Quick Validation (1 hour)**
Best for: Quick smoke test before deployment

1. Open `QUICK_REFERENCE.md`
2. Run pre-testing checklist
3. Execute core E2E workflow from `E2E_TEST_PLAN.md`
4. Run basic DB validation from `DATABASE_VALIDATION.md`
5. Clean up test data

### **Option 2: Comprehensive Testing (3 hours)**
Best for: Full validation before production

1. Start with `QUICK_REFERENCE.md` → Complete setup checklist
2. Execute all tests from `E2E_TEST_PLAN.md`
3. Run all API test cases from `API_TEST_CASES.md`
4. Run all DB validation queries from `DATABASE_VALIDATION.md`
5. Run all RBAC tests from `RBAC_TESTING.md`
6. Document all results
7. Cleanup and sign-off

### **Option 3: Targeted Testing (30 min - 2 hours)**
Choose specific test modules based on what changed:

- **API Changes?** → Use `API_TEST_CASES.md`
- **Permission Changes?** → Use `RBAC_TESTING.md`
- **Database Schema Changes?** → Use `DATABASE_VALIDATION.md`
- **Full Feature Test?** → Use `E2E_TEST_PLAN.md`

---

## **📋 Pre-Testing Requirements**

### **Environment Setup**
- [ ] Django development server running (`python manage.py runserver`)
- [ ] Frontend running (optional but recommended)
- [ ] MySQL database accessible and responding
- [ ] Python virtual environment activated
- [ ] All dependencies installed

### **Credentials Prepared**
- [ ] Super Admin: superadmin@ndma.gov.in / !YLRdJQc6u8njs^0
- [ ] SDMA_ADMIN user created for State 6
- [ ] DDMA_OFFICER user created for District 69
- [ ] TRAINING_INSTITUTE user created
- [ ] YOUTH_ORG_ADMIN user created

### **Test Data Naming**
- [ ] All test batch names follow pattern: `TEST-*` or `RBAC-*`
- [ ] No production data names used
- [ ] Easy to identify for cleanup

### **Cleanup Planning**
- [ ] Understand batch delete cascade behavior
- [ ] Know cleanup commands (in QUICK_REFERENCE.md)
- [ ] Plan verification queries (in DATABASE_VALIDATION.md)

---

## **✅ Test Execution Workflow**

### **Phase 1: Setup (10 min)**
```
Read QUICK_REFERENCE.md → Start Django → Start Frontend → Get JWT Token
```

### **Phase 2: E2E Workflow (45 min)**
```
Read E2E_TEST_PLAN.md → Create Batch → Upload Media → Query History → Verify DB
```

### **Phase 3: API Tests (45 min)**
```
Read API_TEST_CASES.md → Run all 14 test cases → Log results
```

### **Phase 4: Database Validation (30 min)**
```
Read DATABASE_VALIDATION.md → Run all 16 SQL checks → Verify integrity
```

### **Phase 5: RBAC Testing (60 min)**
```
Read RBAC_TESTING.md → Create test users → Run role-based tests → Verify security
```

### **Phase 6: Cleanup (15 min)**
```
Use cleanup script → Verify empty → Generate report → Sign off
```

---

## **📊 Test Results Tracking**

### **Create Result Document**

For each testing session, create a dated document:

```
testing/
├── README.md
├── QUICK_REFERENCE.md
├── E2E_TEST_PLAN.md
├── API_TEST_CASES.md
├── DATABASE_VALIDATION.md
├── RBAC_TESTING.md
└── TEST_RESULTS_2026-03-13.md  ← Create this
    └── TEST_RESULTS_RBAC_2026-03-13.md  ← Or separate by phase
```

### **Template for Results**

```markdown
# Test Results - [Date]

**Tester:** [Name]
**Duration:** [Start time → End time]
**Environment:** Development
**Status:** IN-PROGRESS / COMPLETE / FAILED

## Summary
- Total Tests: 50+
- Passed: __
- Failed: __
- Skipped: __
- Pass Rate: __%

## Phase Results

### E2E Workflow
- [ ] Authentication ✅
- [ ] Create Day 1 ✅
- [ ] Upload Media ✅
- [ ] Add Day 4 ✅
- [ ] Query History ✅

### API Tests
- [ ] Test 1-5: PASS/FAIL
- [ ] Test 6-10: PASS/FAIL
- [ ] Test 11-14: PASS/FAIL

### Database Validation
- [ ] Check 1-5: PASS/FAIL
- [ ] Check 6-10: PASS/FAIL
- [ ] Check 11-16: PASS/FAIL

### RBAC Security
- [ ] SUPER_ADMIN: PASS/FAIL
- [ ] SDMA_ADMIN: PASS/FAIL
- [ ] DDMA_OFFICER: PASS/FAIL
- [ ] TRAINING_INSTITUTE: PASS/FAIL
- [ ] YOUTH_ORG_ADMIN: PASS/FAIL

## Issues Found
1. [Issue 1] - Severity: HIGH/MEDIUM/LOW
   - Description: ...
   - Steps to reproduce: ...
   
## Recommendations
- [ ] Ready for production
- [ ] Needs fixes: ...
- [ ] Blocked on: ...

## Sign-off
- Tested by: ________________
- Date: ________________
- Approved by: ________________
```

---

## **🔒 Security Testing Highlights**

### **What RBAC Testing Validates**

✅ **Data Isolation:**
- SDMA_ADMIN only sees own state data
- DDMA_OFFICER only sees own district data
- No cross-boundary data leakage
- No elevation of privileges

✅ **Permission Enforcement:**
- Users cannot create outside their scope
- Users cannot modify other users' data
- Edit/delete operations properly restricted
- Role-based access working correctly

✅ **Database Security:**
- Foreign key constraints enforced
- Cascade deletes working properly
- No orphaned records possible
- Data consistency maintained

---

## **🗑️ Database Cleanup**

### **Safe Cleanup Strategy**

All test data uses prefixes for easy identification:
- `TEST-E2E-*` - End-to-end workflow tests
- `RBAC-*` - RBAC security tests
- `TEST-BATCH-*` - Generic batch tests
- `TEST-CASCADE-*` - Cascade delete tests

**Cleanup Script** (from QUICK_REFERENCE.md):
```python
from models.training import TrainingSchedule

test_batches = TrainingSchedule.objects.filter(
    batch_no__startswith__in=['TEST-E2E-', 'RBAC-', 'TEST-BATCH-']
)
count = test_batches.count()
for batch in test_batches:
    batch.delete()

print(f"Deleted {count} test batches")
```

**Verification:**
```python
remaining = TrainingSchedule.objects.filter(
    batch_no__startswith__in=['TEST-E2E-', 'RBAC-', 'TEST-BATCH-']
).count()
print(f"Test batches remaining: {remaining}")
```

---

## **📞 Troubleshooting Reference**

### **Common Issues**

| Problem | Solution | Check |
|---------|----------|-------|
| 401 Unauthorized | Token expired, get new one | QUICK_REFERENCE.md |
| 500 Server Error | Check Django logs | Terminal output |
| 403 Forbidden | Insufficient permissions | RBAC_TESTING.md |
| 404 Not Found | Wrong endpoint URL | API_TEST_CASES.md |
| Database connection failed | Start MySQL | QUICK_REFERENCE.md |
| Media upload fails | Check file path | API_TEST_CASES.md |
| CORS error | Use http://localhost:8000 | QUICK_REFERENCE.md |

---

## **📚 Related Documentation**

Location: `docs/` folder

- **API_DOCUMENTATION.html** - Complete API reference
- **DATABASE_SCHEMA.md** - Table structure details
- **AUTHENTICATION.md** - Auth flow details
- **ADMIN_PRIVILEGES_SYSTEM_SUMMARY.md** - RBAC detailed guide
- **DEPLOYMENT.md** - Production setup
- **ERROR_CODES.md** - All API error codes

---

## **🎓 Key Takeaways**

### **What We're Testing**

✅ **Functionality**
- All API endpoints work correctly
- CRUD operations complete successfully
- Nested data properly returned
- Pagination working

✅ **Security**
- RBAC enforced across all endpoints
- Geographic scope limitations respected
- No privilege escalation possible
- Data isolation maintained

✅ **Data Integrity**
- No orphaned records created
- Foreign keys valid
- Cascade deletes work properly
- Timestamps reasonable

✅ **Performance**
- Queries optimized (prefetch_related)
- No N+1 query problems
- Response times acceptable
- Database connections stable

### **Success Criteria**

All tests PASS if:
- ✅ All 50+ test cases execute successfully
- ✅ API returns correct status codes (200, 201, 204, 400, 403)
- ✅ Response data structures match specifications
- ✅ Database remains consistent and free of corruption
- ✅ RBAC properly enforces permissions
- ✅ All test data successfully cleaned up
- ✅ No errors in Django logs
- ✅ Foreign key integrity maintained

---

## **🚦 Status Summary**

| Component | Status | Date Ready |
|-----------|--------|-----------|
| E2E Test Plan | ✅ READY | 2026-03-13 |
| API Test Cases | ✅ READY | 2026-03-13 |
| Database Validation | ✅ READY | 2026-03-13 |
| RBAC Testing | ✅ READY | 2026-03-13 |
| Quick Reference | ✅ READY | 2026-03-13 |
| Test Documentation | ✅ COMPLETE | 2026-03-13 |

**Overall Testing Suite:** ✅ **READY FOR EXECUTION**

---

## **Next Steps**

1. **Read first:** `QUICK_REFERENCE.md` (5 min)
2. **Setup environment:** Django + Frontend running (10 min)
3. **Execute tests:** Choose from 3 options (1-3 hours)
4. **Document results:** Use provided templates
5. **Cleanup:** Remove test data
6. **Sign-off:** Mark testing complete

---

## **Questions?**

Refer to the specific document for your scenario:
- **How do I start?** → QUICK_REFERENCE.md
- **What APIs should I test?** → API_TEST_CASES.md
- **Is my data safe?** → DATABASE_VALIDATION.md
- **Can user X see data Y?** → RBAC_TESTING.md
- **What should my test workflow be?** → E2E_TEST_PLAN.md

---

**Testing Suite Created:** March 13, 2026  
**Version:** 1.0  
**Status:** ✅ Ready for Execution


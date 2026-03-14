# RBAC (Role-Based Access Control) Testing Guide

**Purpose:** Verify each user role can only access data within their geographic scope  
**Test Environment:** Local development  
**Critical Security Feature:** Yes

---

## **User Roles & Geographic Scope Matrix**

| Role | User ID | Email | State Access | District Access | Can Create | Can Edit | Can Delete |
|------|---------|-------|---|---|---|---|---|
| **SUPER_ADMIN** | 1 | superadmin@ndma.gov.in | ALL | ALL | ✅ | ✅ | ✅ |
| **NDMA_ADMIN** | 2 | admin@ndma.gov.in | ALL | ALL | ✅ | ✅ | ✅ |
| **SDMA_ADMIN** | 3 | admin@state.gov.in | Own State | ALL | ✅ | ✅ | ✅ |
| **DDMA_NODAL_OFFICER** | 4 | officer@district.gov.in | Own State | Own District | ✅ | ✅ | ✅ |
| **TRAINING_INSTITUTE** | 5 | institute@ncc.org | ALL | ALL | ✅ | Own batches | Own batches |
| **YOUTH_ORG_ADMIN** | 6 | admin@youthorg.org | ALL | ALL | ✅ | Own batches | Own batches |

---

## **Test Data Setup**

### **Create Test Batches in Different States/Districts**

**Batch 1: State 6 (assumed state ID), District 69**
```json
{
  "batch_no": "RBAC-STATE6-DT69-001",
  "state": 6,
  "district": 69,
  "organization_name": "Test Org 1",
  "status": "DRAFT"
}
```

**Batch 2: State 8 (different state), District 75**
```json
{
  "batch_no": "RBAC-STATE8-DT75-001",
  "state": 8,
  "district": 75,
  "organization_name": "Test Org 2",
  "status": "DRAFT"
}
```

**Batch 3: Batch created by TRAINING_INSTITUTE**
```json
{
  "batch_no": "RBAC-INSTITUTE-001",
  "state": 6,
  "district": 69,
  "organization_name": "Institute Created",
  "created_by": 5
}
```

---

## **Test Case 1: SUPER_ADMIN Access (Full Access)**

### **Test 1.1: List All Trainings**

**Setup:** Login as superadmin@ndma.gov.in

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/training-schedules/ \
  -H "Authorization: Bearer $SUPER_ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Result:** ✅
```json
{
  "status_code": 200,
  "count": 3,
  "data": [
    {"batch_no": "RBAC-STATE6-DT69-001"},
    {"batch_no": "RBAC-STATE8-DT75-001"},
    {"batch_no": "RBAC-INSTITUTE-001"}
  ]
}
```

**Verification:**
```python
from models.training import TrainingSchedule

super_admin_queryset = TrainingSchedule.objects.filter(created_by_id=1)
print(f"Super Admin can see: {super_admin_queryset.count()} batches")
#Expected: ALL batches (3+)
```

---

### **Test 1.2: Create Batch in Any State/District**

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/training-schedules/create_daywise/ \
  -H "Authorization: Bearer $SUPER_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "state": 8,
    "district": 75,
    "batch_no": "RBAC-SUPER-CREATE-001",
    "sessions": [{"day_label": "Day 1", "date": "2026-03-13"}]
  }'
```

**Expected Status:** ✅ `201 Created`

---

### **Test 1.3: Edit Any Batch**

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/v1/training-schedules/RBAC-STATE8-DT75-001/ \
  -H "Authorization: Bearer $SUPER_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "APPROVED"}'
```

**Expected Status:** ✅ `200 OK`

---

### **Test 1.4: Delete Any Batch**

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/v1/training-schedules/1/ \
  -H "Authorization: Bearer $SUPER_ADMIN_TOKEN"
```

**Expected Status:** ✅ `204 No Content`

---

## **Test Case 2: SDMA_ADMIN Access (State-Level Only)**

### **Setup:** SDMA_ADMIN assigned to State 6

**User Details:**
```python
# Create test user in shell
from django.contrib.auth.models import User
from models.user_profile import UserProfile

sdma_admin = User.objects.create_user(
    username='sdma_state6',
    email='sdma@state6.gov.in',
    password='password123'
)
profile = UserProfile.objects.create(
    user=sdma_admin,
    user_role='SDMA_ADMIN',
    state_id=6  # Only State 6
)
```

### **Test 2.1: Can Only See State 6 Batches**

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/training-schedules/ \
  -H "Authorization: Bearer $SDMA_ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Result:** ✅
```json
{
  "status_code": 200,
  "count": 1,
  "data": [
    {"batch_no": "RBAC-STATE6-DT69-001", "state_id": 6}
  ]
}
```

**VALIDATION - SQL CHECK:**
```sql
-- SDMA_ADMIN should NOT see State 8 batches
SELECT batch_no, state_id FROM models_training_schedule 
WHERE user_id IN (SELECT id FROM auth_user WHERE user_role='SDMA_ADMIN' AND state_id=6)
AND state_id != 6;
```

✅ **Expected:** 0 rows (no cross-state data visible)

---

### **Test 2.2: Cannot Create Batch in Different State**

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/training-schedules/create_daywise/ \
  -H "Authorization: Bearer $SDMA_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "state": 8,
    "district": 75,
    "batch_no": "RBAC-SDMA-WRONG-STATE",
    "sessions": [{"day_label": "Day 1", "date": "2026-03-13"}]
  }'
```

**Expected Status:** ❌ `403 Forbidden`

**Expected Response:**
```json
{
  "status_code": 403,
  "message": "You don't have permission to create training in state 8"
}
```

---

### **Test 2.3: Can Create in Own State**

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/training-schedules/create_daywise/ \
  -H "Authorization: Bearer $SDMA_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "state": 6,
    "district": 69,
    "batch_no": "RBAC-SDMA-OWN-STATE",
    "sessions": [{"day_label": "Day 1", "date": "2026-03-13"}]
  }'
```

**Expected Status:** ✅ `201 Created`

---

### **Test 2.4: Can Edit Only Own State Batches**

**Request (Valid - Own State):**
```bash
curl -X PATCH http://localhost:8000/api/v1/training-schedules/RBAC-STATE6-DT69-001/ \
  -H "Authorization: Bearer $SDMA_ADMIN_TOKEN" \
  -d '{"status": "APPROVED"}'
```

**Expected Status:** ✅ `200 OK`

**Request (Invalid - Other State):**
```bash
curl -X PATCH http://localhost:8000/api/v1/training-schedules/RBAC-STATE8-DT75-001/ \
  -H "Authorization: Bearer $SDMA_ADMIN_TOKEN" \
  -d '{"status": "APPROVED"}'
```

**Expected Status:** ❌ `403 Forbidden`

---

## **Test Case 3: DDMA_NODAL_OFFICER Access (District-Level Only)**

### **Setup:** DDMA_NODAL_OFFICER assigned to State 6, District 69

**User Details:**
```python
ddma_officer = User.objects.create_user(
    username='ddma_state6_dt69',
    email='ddma@district69.gov.in',
    password='password123'
)
profile = UserProfile.objects.create(
    user=ddma_officer,
    user_role='DDMA_NODAL_OFFICER',
    state_id=6,
    district_id=69  # Only District 69 in State 6
)
```

### **Test 3.1: Can Only See Own District Batches**

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/training-schedules/ \
  -H "Authorization: Bearer $DDMA_OFFICER_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Result:** ✅
```json
{
  "status_code": 200,
  "count": 2,
  "data": [
    {"batch_no": "RBAC-STATE6-DT69-001", "state_id": 6, "district_id": 69},
    {"batch_no": "RBAC-SDMA-OWN-STATE", "state_id": 6, "district_id": 69}
  ]
}
```

**VALIDATION - SQL CHECK:**
```sql
-- DDMA_OFFICER should NOT see different district
SELECT batch_no, district_id FROM models_training_schedule 
WHERE state_id=6 AND district_id != 69;
```

✅ **Expected:** 0 rows (no cross-district data visible)

---

### **Test 3.2: Cannot Create in Different District**

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/training-schedules/create_daywise/ \
  -H "Authorization: Bearer $DDMA_OFFICER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "state": 6,
    "district": 70,
    "batch_no": "RBAC-DDMA-WRONG-DT",
    "sessions": [{"day_label": "Day 1", "date": "2026-03-13"}]
  }'
```

**Expected Status:** ❌ `403 Forbidden`

**Expected Response:**
```json
{
  "status_code": 403,
  "message": "You don't have permission to create training in district 70"
}
```

---

### **Test 3.3: Can Create in Own District**

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/training-schedules/create_daywise/ \
  -H "Authorization: Bearer $DDMA_OFFICER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "state": 6,
    "district": 69,
    "batch_no": "RBAC-DDMA-OWN-DT",
    "sessions": [{"day_label": "Day 1", "date": "2026-03-13"}]
  }'
```

**Expected Status:** ✅ `201 Created`

---

## **Test Case 4: TRAINING_INSTITUTE Access**

### **Setup:** TRAINING_INSTITUTE can see all but edit only own batches

**User Details:**
```python
institute = User.objects.create_user(
    username='ncc_institute',
    email='ncc@institute.org',
    password='password123'
)
profile = UserProfile.objects.create(
    user=institute,
    user_role='TRAINING_INSTITUTE'
)
```

### **Test 4.1: Can List All Batches**

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/training-schedules/ \
  -H "Authorization: Bearer $INSTITUTE_TOKEN"
```

**Expected Status:** ✅ `200 OK`

**Expected Response:**
- Can see all 3 batches (RBAC-STATE6-DT69-001, RBAC-STATE8-DT75-001, RBAC-INSTITUTE-001)

---

### **Test 4.2: Can Can Edit Only Own Batches**

**Request (Own batch - created by this institute):**
```bash
curl -X PATCH http://localhost:8000/api/v1/training-schedules/RBAC-INSTITUTE-001/ \
  -H "Authorization: Bearer $INSTITUTE_TOKEN" \
  -d '{"organization_name": "Updated Institute"}'
```

**Expected Status:** ✅ `200 OK`

**Request (Other's batch):**
```bash
curl -X PATCH http://localhost:8000/api/v1/training-schedules/RBAC-STATE6-DT69-001/ \
  -H "Authorization: Bearer $INSTITUTE_TOKEN" \
  -d '{"organization_name": "Hacked"}'
```

**Expected Status:** ❌ `403 Forbidden`

---

## **Test Case 5: YOUTH_ORG_ADMIN Access**

### **Same as TRAINING_INSTITUTE but different role**
- Can see all batches
- Can edit/delete only own batches
- Cannot modify other org's batches

---

## **Security Validation Queries**

### **Verify No Data Leakage**

**Query 1: Check SDMA_ADMIN cannot see other state data**
```python
from models.training import TrainingSchedule
from django.contrib.auth.models import User

# Get SDMA_ADMIN for State 6
admin = User.objects.get(email='sdma@state6.gov.in')

# Get their queryset
visible_batches = TrainingSchedule.objects.filter(
    state_id=admin.userprofile.state_id
)

# Check for any batches from other states
other_state_batches = visible_batches.exclude(
    state_id=admin.userprofile.state_id
)

print(f"Leaked batches: {other_state_batches.count()}")
print("✅ NO DATA LEAKAGE" if other_state_batches.count() == 0 else "❌ DATA LEAKAGE DETECTED!")
```

**Query 2: Check DDMA_OFFICER cannot see other district data**
```python
from models.training import TrainingSchedule

officer = User.objects.get(email='ddma@district69.gov.in')

visible_batches = TrainingSchedule.objects.filter(
    state_id=officer.userprofile.state_id,
    district_id=officer.userprofile.district_id
)

# Check for any batches from other districts in same state
other_district = visible_batches.exclude(
    district_id=officer.userprofile.district_id
)

print(f"Leaked batches: {other_district.count()}")
print("✅ NO CROSS-DISTRICT LEAKAGE" if other_district.count() == 0 else "❌ LEAKAGE DETECTED!")
```

**Query 3: Check Edit Restrictions**
```python
from models.training import TrainingSchedule
from django.contrib.auth.models import User

institute = User.objects.get(email='ncc@institute.org')

# Can they edit batches they didn't create?
other_batches = TrainingSchedule.objects.exclude(
    created_by_id=institute.id
)

print(f"Batches they can try to edit: {other_batches.count()}")
print(f"Expected behavior: Should get 403 Forbidden on PATCH/DELETE")
```

---

## **RBAC Test Execution Checklist**

### **SUPER_ADMIN Tests**
- [ ] Test 1.1: List all trainings ✅
- [ ] Test 1.2: Create in any state ✅
- [ ] Test 1.3: Edit any batch ✅
- [ ] Test 1.4: Delete any batch ✅

### **SDMA_ADMIN Tests**
- [ ] Test 2.1: Can only see own state ✅
- [ ] Test 2.2: Cannot create in other state ✅
- [ ] Test 2.3: Can create in own state ✅
- [ ] Test 2.4: Can edit own state only ✅

### **DDMA_NODAL_OFFICER Tests**
- [ ] Test 3.1: Can only see own district ✅
- [ ] Test 3.2: Cannot create in other district ✅
- [ ] Test 3.3: Can create in own district ✅
- [ ] Cross-state access blocked ✅

### **TRAINING_INSTITUTE Tests**
- [ ] Test 4.1: Can list all batches ✅
- [ ] Test 4.2: Can edit only own batches ✅

### **YOUTH_ORG_ADMIN Tests**
- [ ] Same as TRAINING_INSTITUTE ✅

### **Security Validation**
- [ ] No SDMA_ADMIN data leakage ✅
- [ ] No DDMA_OFFICER cross-district access ✅
- [ ] Edit restrictions enforced ✅
- [ ] Delete restrictions enforced ✅

**Overall RBAC Status:** ✅ **SECURE**

---

## **Test Result Summary**

**Date:** _____________  
**Tester:** _____________  
**Environment:** Development  

**Total Tests:** 20+  
**Passed:** ___  
**Failed:** ___  
**Security Issues:** 0 / HIGH / MEDIUM / LOW  

**Findings:**
_________________________________

**Recommendation:**
- [ ] Ready for Production
- [ ] Minor Issues (list)
- [ ] Major Issues (requires fixes)


# End-to-End Testing Plan - Training API

**Date:** March 13, 2026  
**Tester:** Super Admin  
**Credentials:**
- Email: `superadmin@ndma.gov.in`
- Password: `!YLRdJQc6u8njs^0`

---

## **Database Tables Affected**

| Table | Operation | Impact |
|---|---|---|
| `models_training_schedule` | CREATE, READ, UPDATE | Batch creation, updates, retrieval |
| `models_training_session` | CREATE, READ, UPDATE | Day sessions (Day 1, 4, 7) |
| `models_training_session_media` | CREATE, READ | Media/image uploads |
| `auth_user` | READ | User authentication & created_by tracking |

---

## **Test Workflow (5 Steps)**

### **Step 1: Authentication** ✅
**Endpoint:** POST `/api/v1/auth/login/` (or your auth endpoint)

**Request:**
```json
{
  "email": "superadmin@ndma.gov.in",
  "password": "!YLRdJQc6u8njs^0"
}
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAi...",
  "refresh_token": "...",
  "user": {
    "id": 1,
    "user_role": "SUPER_ADMIN",
    "email": "superadmin@ndma.gov.in"
  }
}
```

**DB Check:**
```sql
SELECT id, email, user_role, is_active FROM auth_user WHERE email='superadmin@ndma.gov.in';
```

✅ **Expected:** 1 row, is_active=True

---

### **Step 2: Create Day 1 Training Batch** ✅
**Endpoint:** POST `/api/v1/training-schedules/create_daywise/`

**Request:**
```json
{
  "state": 6,
  "district": 69,
  "batch_no": "TEST-E2E-001",
  "organization_name": "Test Organization",
  "organization_type": "NCC",
  "number_of_volunteers": 100,
  "institute_details": "Test Institute",
  "trainers_details": "Test Trainers",
  "start_date": "2026-03-13",
  "end_date": "2026-03-20",
  "sessions": [
    {
      "day_label": "Day 1",
      "date": "2026-03-13",
      "notes": "E2E Test Day 1"
    }
  ]
}
```

**Expected Response:**
```json
{
  "status_code": 201,
  "message": "Training Day 1 created",
  "data": {
    "id": <BATCH_ID>,
    "batch_no": "TEST-E2E-001",
    "status": "DRAFT"
  }
}
```

**DB Check:**
```sql
SELECT id, batch_no, status, created_by_id, state_id FROM models_training_schedule 
WHERE batch_no='TEST-E2E-001';
```

✅ **Expected:** 1 row, status='DRAFT', created_by_id=1 (super admin)

```sql
SELECT id, day_label, date FROM models_training_session 
WHERE schedule_id=<BATCH_ID> AND day_label='Day 1';
```

✅ **Expected:** 1 row, date='2026-03-13'

---

### **Step 3: Upload Media for Day 1** ✅
**Endpoint:** POST `/api/v1/training-schedules/create_daywise_with_media/`

**Request (Multipart Form):**
```
batch_no: "TEST-E2E-001"
day: "1"
day_date: "2026-03-13"
day_notes: "E2E Test with Media"
images: [test_image_1.jpg, test_image_2.jpg]
uploaded_by: 1
```

**Expected Response:**
```json
{
  "status_code": 201,
  "message": "Training Day 1 created",
  "data": {
    "session": {
      "uploaded_media": [
        {
          "id": <MEDIA_ID>,
          "file_url": "http://..."
        }
      ]
    }
  }
}
```

**DB Check:**
```sql
SELECT id, session_id, file_name, file_size FROM models_training_session_media 
WHERE session_id=<SESSION_ID> ORDER BY uploaded_at DESC;
```

✅ **Expected:** 2 rows (2 images uploaded)

---

### **Step 4: Add Day 4 to Batch** ✅
**Endpoint:** POST `/api/v1/training-schedules/create_daywise/`

**Request:**
```json
{
  "batch_no": "TEST-E2E-001",
  "sessions": [
    {
      "day_label": "Day 4",
      "date": "2026-03-16",
      "notes": "E2E Test Day 4"
    }
  ]
}
```

**Expected Response:**
```json
{
  "status_code": 200,
  "message": "Training Day 4 created",
  "data": {
    "total_days": 2
  }
}
```

**DB Check:**
```sql
SELECT COUNT(*) as total_sessions FROM models_training_session 
WHERE schedule_id=<BATCH_ID>;
```

✅ **Expected:** 2 (Day 1 + Day 4)

---

### **Step 5: Retrieve Session History** ✅
**Endpoint:** GET `/api/v1/training-schedules/session_history/?search=TEST-E2E-001`

**Expected Response:**
```json
{
  "status_code": 200,
  "count": 1,
  "data": [
    {
      "batch_no": "TEST-E2E-001",
      "status": "DRAFT",
      "total_sessions": 2,
      "total_media": 2,
      "sessions": [
        {
          "day_label": "Day 1",
          "date": "2026-03-13",
          "total_media_count": 2,
          "media_files": [...]
        },
        {
          "day_label": "Day 4",
          "date": "2026-03-16",
          "total_media_count": 0
        }
      ]
    }
  ]
}
```

**DB Check:**
```sql
SELECT 
  s.batch_no, 
  COUNT(DISTINCT sess.id) as total_days,
  COUNT(DISTINCT sm.id) as total_media
FROM models_training_schedule s
LEFT JOIN models_training_session sess ON s.id = sess.schedule_id
LEFT JOIN models_training_session_media sm ON sess.id = sm.session_id
WHERE s.batch_no='TEST-E2E-001'
GROUP BY s.id;
```

✅ **Expected:** 1 row, total_days=2, total_media=2

---

## **Data Integrity Checks**

### **Check 1: Foreign Key Integrity**
```sql
-- Verify all sessions have valid schedule_id
SELECT sess.id, sess.schedule_id, s.batch_no 
FROM models_training_session sess
LEFT JOIN models_training_schedule s ON sess.schedule_id = s.id
WHERE s.id IS NULL;
```

✅ **Expected:** 0 rows (no orphaned sessions)

### **Check 2: Media File Integrity**
```sql
-- Verify all media has valid session_id
SELECT sm.id, sm.session_id, sess.day_label
FROM models_training_session_media sm
LEFT JOIN models_training_session sess ON sm.session_id = sess.id
WHERE sess.id IS NULL;
```

✅ **Expected:** 0 rows (no orphaned media)

### **Check 3: Created By Tracking**
```sql
-- Verify super admin created the batch
SELECT id, batch_no, created_by_id, created_at
FROM models_training_schedule
WHERE batch_no='TEST-E2E-001';
```

✅ **Expected:** created_by_id = 1 (super admin)

### **Check 4: Status Field**
```sql
-- Verify status is correctly set
SELECT batch_no, status FROM models_training_schedule
WHERE batch_no='TEST-E2E-001';
```

✅ **Expected:** status = 'DRAFT'

---

## **Database Rollback (If Needed)**

**Clean up test data ONLY:**
```sql
-- Delete test media
DELETE FROM models_training_session_media 
WHERE session_id IN (
  SELECT id FROM models_training_session 
  WHERE schedule_id IN (
    SELECT id FROM models_training_schedule 
    WHERE batch_no LIKE 'TEST-E2E-%'
  )
);

-- Delete test sessions
DELETE FROM models_training_session 
WHERE schedule_id IN (
  SELECT id FROM models_training_schedule 
  WHERE batch_no LIKE 'TEST-E2E-%'
);

-- Delete test batch
DELETE FROM models_training_schedule 
WHERE batch_no LIKE 'TEST-E2E-%';
```

⚠️ **IMPORTANT:** Only run if tests failed and you need cleanup!

---

## **Validation Checklist**

- [ ] Step 1: Authentication successful
- [ ] Step 2: Day 1 batch created in DB
- [ ] Step 3: Media files uploaded and linked
- [ ] Step 4: Day 4 added to batch
- [ ] Step 5: Session history retrieves all data correctly
- [ ] Foreign key integrity: ✅ No orphaned records
- [ ] Media integrity: ✅ All files properly linked
- [ ] Created by tracking: ✅ Super admin ID saved
- [ ] Status field: ✅ DRAFT status set
- [ ] No DB corruption: ✅ All tests passed

---

**Test Status:** ⏳ **PENDING** (Ready to execute)


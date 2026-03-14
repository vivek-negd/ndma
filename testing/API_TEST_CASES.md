# API Test Cases - Training Management System

**Environment:** Local Development (Port 8000/5173)  
**Auth Token:** Replace `<YOUR_ACCESS_TOKEN>` with actual JWT token  
**Base URL:** `http://localhost:8000/api/v1`

---

## **Test Case 1: Authentication**

### **Endpoint:** `POST /api/v1/auth/login/`

**Test:** Login with Super Admin credentials

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@ndma.gov.in",
    "password": "!YLRdJQc6u8njs^0"
  }'
```

**Expected Status:** `200 OK`

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAi...",
  "user": {
    "id": 1,
    "user_role": "SUPER_ADMIN",
    "email": "superadmin@ndma.gov.in"
  }
}
```

**Save Token:**
```bash
export TOKEN="<access_token_from_response>"
echo $TOKEN  # Verify token is saved
```

---

## **Test Case 2: List Training Schedules (RBAC Test)**

### **Endpoint:** `GET /api/v1/training-schedules/`

**Test:** Super Admin can see all trainings

```bash
curl -X GET http://localhost:8000/api/v1/training-schedules/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Status:** `200 OK`

**Expected Response:**
```json
{
  "status_code": 200,
  "count": <number_of_training_schedules>,
  "data": [
    {
      "id": 1,
      "batch_no": "BATCH-001",
      "state_id": 6,
      "state_name": "State Name",
      "district_id": 69,
      "district_name": "District Name",
      "status": "DRAFT",
      "created_at": "2026-01-15T10:00:00Z"
    },
    ...
  ]
}
```

**Validation:**
- ✅ Status 200
- ✅ Can see all batches (Super Admin privilege)
- ✅ state_name and district_name are populated

---

## **Test Case 3: Create Training Batch (Day 1 Auto-Extract)**

### **Endpoint:** `POST /api/v1/training-schedules/create_daywise/`

**Test:** Create batch with auto-extraction from sessions array

```bash
curl -X POST http://localhost:8000/api/v1/training-schedules/create_daywise/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "state": 6,
    "district": 69,
    "batch_no": "TEST-E2E-BATCH-01",
    "organization_name": "Test Organization",
    "organization_type": "NCC",
    "number_of_volunteers": 100,
    "institute_details": "Test Institute Details",
    "trainers_details": "Test Trainers",
    "start_date": "2026-03-13",
    "end_date": "2026-03-20",
    "sessions": [
      {
        "day_label": "Day 1",
        "date": "2026-03-13",
        "notes": "Opening session"
      }
    ]
  }'
```

**Expected Status:** `201 Created`

**Expected Response:**
```json
{
  "status_code": 201,
  "message": "Training Day 1 created",
  "data": {
    "id": <BATCH_ID>,
    "batch_no": "TEST-E2E-BATCH-01",
    "state": 6,
    "district": 69,
    "status": "DRAFT",
    "sessions": [
      {
        "id": <SESSION_ID>,
        "day_label": "Day 1",
        "date": "2026-03-13"
      }
    ]
  }
}
```

**Save IDs for Next Tests:**
```bash
export BATCH_ID="<id_from_response>"
export SESSION_ID="<session_id_from_response>"
echo "Batch ID: $BATCH_ID"
echo "Session ID: $SESSION_ID"
```

**Validation:**
- ✅ Status 201
- ✅ Batch created in DRAFT status
- ✅ Session created for Day 1
- ✅ Auto-extracted day=1 from "Day 1" label

---

## **Test Case 4: Upload Media for Session**

### **Endpoint:** `POST /api/v1/training-schedules/create_daywise_with_media/`

**Test:** Upload images for Day 1 session

**Step A: Prepare test images**
```bash
# Create dummy test images (1x1 pixel PNGs)
convert -size 1x1 xc:red test_image_1.png
convert -size 1x1 xc:blue test_image_2.png
```

**Step B: Upload media**
```bash
curl -X POST http://localhost:8000/api/v1/training-schedules/create_daywise_with_media/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "batch_no=TEST-E2E-BATCH-01" \
  -F "day=1" \
  -F "day_date=2026-03-13" \
  -F "day_notes=E2E Test Media Upload" \
  -F "uploaded_by=1" \
  -F "images=@test_image_1.png" \
  -F "images=@test_image_2.png"
```

**Expected Status:** `201 Created`

**Expected Response:**
```json
{
  "status_code": 201,
  "message": "Training Day 1 created",
  "data": {
    "session": {
      "id": <SESSION_ID>,
      "uploaded_media": [
        {
          "id": <MEDIA_ID_1>,
          "file_name": "test_image_1.png",
          "file_url": "http://localhost:8000/media/training/...",
          "file_size": 1024
        },
        {
          "id": <MEDIA_ID_2>,
          "file_name": "test_image_2.png",
          "file_url": "http://localhost:8000/media/training/...",
          "file_size": 1024
        }
      ]
    }
  }
}
```

**Validation:**
- ✅ Status 201
- ✅ 2 media files uploaded
- ✅ File URLs are accessible
- ✅ File sizes recorded correctly

---

## **Test Case 5: Add Day 4 to Batch**

### **Endpoint:** `POST /api/v1/training-schedules/create_daywise/`

**Test:** Add Day 4 to existing batch

```bash
curl -X POST http://localhost:8000/api/v1/training-schedules/create_daywise/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_no": "TEST-E2E-BATCH-01",
    "sessions": [
      {
        "day_label": "Day 4",
        "date": "2026-03-16",
        "notes": "Fourth day session"
      }
    ]
  }'
```

**Expected Status:** `200 OK`

**Expected Response:**
```json
{
  "status_code": 200,
  "message": "Training Day 4 created",
  "data": {
    "id": <BATCH_ID>,
    "batch_no": "TEST-E2E-BATCH-01",
    "total_sessions": 2,
    "sessions": [
      {
        "day_label": "Day 1",
        "date": "2026-03-13"
      },
      {
        "day_label": "Day 4",
        "date": "2026-03-16"
      }
    ]
  }
}
```

**Validation:**
- ✅ Status 200 (update, not create)
- ✅ total_sessions increased to 2
- ✅ Both days listed in sessions array
- ✅ No duplicate Day 1 created

---

## **Test Case 6: Retrieve Session History with Pagination**

### **Endpoint:** `GET /api/v1/training-schedules/session_history/?search=TEST-E2E-BATCH-01&page=1`

**Test:** Get complete history for batch with nested media

```bash
curl -X GET "http://localhost:8000/api/v1/training-schedules/session_history/?search=TEST-E2E-BATCH-01&page=1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Status:** `200 OK`

**Expected Response:**
```json
{
  "status_code": 200,
  "count": 1,
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  },
  "data": [
    {
      "id": <BATCH_ID>,
      "batch_no": "TEST-E2E-BATCH-01",
      "state_id": 6,
      "state_name": "State Name",
      "district_id": 69,
      "district_name": "District Name",
      "status": "DRAFT",
      "organization_name": "Test Organization",
      "organization_type": "NCC",
      "total_sessions": 2,
      "total_media": 2,
      "created_at": "2026-03-13T...",
      "sessions": [
        {
          "id": <SESSION_ID_1>,
          "day_label": "Day 1",
          "date": "2026-03-13",
          "notes": "Opening session",
          "total_media_count": 2,
          "media_files": [
            {
              "id": <MEDIA_ID_1>,
              "file_name": "test_image_1.png",
              "file_url": "http://...",
              "uploaded_at": "2026-03-13T..."
            },
            {
              "id": <MEDIA_ID_2>,
              "file_name": "test_image_2.png",
              "file_url": "http://...",
              "uploaded_at": "2026-03-13T..."
            }
          ]
        },
        {
          "id": <SESSION_ID_2>,
          "day_label": "Day 4",
          "date": "2026-03-16",
          "notes": "Fourth day session",
          "total_media_count": 0,
          "media_files": []
        }
      ]
    }
  ]
}
```

**Validation:**
- ✅ Status 200
- ✅ Pagination info present
- ✅ Can filter by batch_no via search
- ✅ Sessions array contains both Day 1 and Day 4
- ✅ Media properly nested under Day 1
- ✅ Day 4 has empty media_files array
- ✅ total_sessions = 2, total_media = 2

---

## **Test Case 7: Retrieve Single Batch Details**

### **Endpoint:** `GET /api/v1/training-schedules/{id}/`

**Test:** Get full details of a single batch

```bash
curl -X GET "http://localhost:8000/api/v1/training-schedules/$BATCH_ID/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Status:** `200 OK`

**Expected Response:**
```json
{
  "status_code": 200,
  "data": {
    "id": <BATCH_ID>,
    "batch_no": "TEST-E2E-BATCH-01",
    "state": 6,
    "district": 69,
    "status": "DRAFT",
    "organization_name": "Test Organization",
    "sessions": [...]
  }
}
```

**Validation:**
- ✅ Status 200
- ✅ All batch details returned
- ✅ Sessions nested in response

---

## **Test Case 8: Update Batch Status**

### **Endpoint:** `PATCH /api/v1/training-schedules/{id}/`

**Test:** Change batch status from DRAFT to APPROVED

```bash
curl -X PATCH "http://localhost:8000/api/v1/training-schedules/$BATCH_ID/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "APPROVED"
  }'
```

**Expected Status:** `200 OK`

**Expected Response:**
```json
{
  "status_code": 200,
  "message": "Training schedule updated",
  "data": {
    "id": <BATCH_ID>,
    "batch_no": "TEST-E2E-BATCH-01",
    "status": "APPROVED"
  }
}
```

**Validation:**
- ✅ Status 200
- ✅ Status changed from DRAFT to APPROVED
- ✅ Other fields unchanged

---

## **Test Case 9: Delete Batch**

### **Endpoint:** `DELETE /api/v1/training-schedules/{id}/`

**Test:** Delete batch (with all dependent sessions & media)

```bash
curl -X DELETE "http://localhost:8000/api/v1/training-schedules/$BATCH_ID/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Status:** `204 No Content` or `200 OK`

**Expected Response:**
```json
{
  "status_code": 204,
  "message": "Training schedule deleted successfully"
}
```

**Validation:**
- ✅ Status 204 or 200
- ✅ Batch deleted
- ✅ All dependent sessions deleted (cascade)
- ✅ All dependent media deleted (cascade)

---

## **Test Case 10: Training Report (Analytics)**

### **Endpoint:** `GET /api/v1/training-schedules/training_report/?search=day&order=day_label`

**Test:** Get analytics report grouped by training day

```bash
curl -X GET "http://localhost:8000/api/v1/training-schedules/training_report/?search=Day" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Status:** `200 OK`

**Expected Response:**
```json
{
  "status_code": 200,
  "count": 7,
  "pagination": {
    "page": 1,
    "page_size": 10,
    "has_next": false
  },
  "data": [
    {
      "day_label": "Day 1",
      "total_batches": 5,
      "total_sessions": 5,
      "total_media_uploaded": 12,
      "last_session_date": "2026-03-13"
    },
    {
      "day_label": "Day 4",
      "total_batches": 3,
      "total_sessions": 3,
      "total_media_uploaded": 8,
      "last_session_date": "2026-03-16"
    },
    ...
  ]
}
```

**Validation:**
- ✅ Status 200
- ✅ Groups by day_label
- ✅ Aggregated counts correct
- ✅ Can search by day label
- ✅ Pagination working

---

## **Test Case 11: List Batch Numbers (Dropdown)**

### **Endpoint:** `GET /api/v1/training-schedules/list_batch_numbers/?status=DRAFT`

**Test:** Get batch numbers for dropdown filter

```bash
curl -X GET "http://localhost:8000/api/v1/training-schedules/list_batch_numbers/?status=DRAFT" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Status:** `200 OK`

**Expected Response:**
```json
{
  "status_code": 200,
  "count": 15,
  "data": [
    {
      "id": 1,
      "batch_no": "BATCH-001",
      "status": "DRAFT"
    },
    {
      "id": 2,
      "batch_no": "BATCH-002",
      "status": "DRAFT"
    },
    ...
  ]
}
```

**Validation:**
- ✅ Status 200
- ✅ Only DRAFT batches returned
- ✅ Format suitable for dropdown/select
- ✅ Can filter by status parameter

---

## **Error Scenario Tests**

### **Test Case 12: Invalid Token**

```bash
curl -X GET http://localhost:8000/api/v1/training-schedules/ \
  -H "Authorization: Bearer invalid_token" \
  -H "Content-Type: application/json"
```

**Expected Status:** `401 Unauthorized`

**Expected Response:**
```json
{
  "detail": "Invalid authentication credentials."
}
```

---

### **Test Case 13: Missing Required Field**

```bash
curl -X POST http://localhost:8000/api/v1/training-schedules/create_daywise/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "state": 6,
    "batch_no": "TEST-BATCH"
  }'
```

**Expected Status:** `400 Bad Request`

**Expected Response:**
```json
{
  "status_code": 400,
  "errors": {
    "district": ["This field is required."],
    "sessions": ["This field is required."]
  }
}
```

---

### **Test Case 14: Duplicate Batch Number**

```bash
curl -X POST http://localhost:8000/api/v1/training-schedules/create_daywise/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "state": 6,
    "district": 69,
    "batch_no": "TEST-E2E-BATCH-01",  # Same as earlier test
    "organization_name": "Another Org",
    "sessions": [...]
  }'
```

**Expected Status:** `400 Bad Request`

**Expected Response:**
```json
{
  "status_code": 400,
  "errors": {
    "batch_no": ["Batch number already exists."]
  }
}
```

---

## **Test Execution Checklist**

### **Pre-Test:**
- [ ] Django server running (`python manage.py runserver`)
- [ ] Frontend running (`npm start`)
- [ ] Database accessible
- [ ] Token saved in `$TOKEN` environment variable

### **During Test:**
- [ ] All 14 test cases pass
- [ ] All status codes match expected
- [ ] All response structures match expected
- [ ] No 500 errors

### **Post-Test:**
- [ ] All test data cleaned up (batch deleted)
- [ ] Database integrity verified
- [ ] No orphaned sessions/media
- [ ] No corruption in other tables

### **Results:**
- ✅ PASSED / ❌ FAILED
- Date: _______________
- Tester: Super Admin
- Issues Found: _______________


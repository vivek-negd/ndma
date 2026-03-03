# Volunteer API Complete Guide

## Overview

The Volunteer API provides endpoints for:
- **Single volunteer creation** via JSON
- **Bulk volunteer upload** via CSV files
- **Volunteer coverage statistics**

All endpoints require authentication.

---

## Quick Start

### 1. Get Access Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "password123"
  }'
```

### 2. Create a Single Volunteer

```bash
curl -X POST http://localhost:8000/api/v1/volunteer/create/ \
  -H "Authorization: Bearer <token>" \
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

### 3. Upload Many Volunteers

```bash
curl -X POST http://localhost:8000/api/v1/volunteer/bulk-upload/ \
  -H "Authorization: Bearer <token>" \
  -F "file=@volunteers.csv" \
  -F "organization_id=1"
```

---

## Endpoints

### POST /volunteer/create/

**Create a single volunteer**

**Auth Required:** Yes  
**Roles:** SUPER_ADMIN, NATIONAL_ADMIN, STATE_ADMIN, DISTRICT_ADMIN, YOUTH_ORG_ADMIN

#### Request

```json
{
    "organization_id": 1,
    "mis_id": 10001,
    "name": "John Smith",
    "salutation": "Mr.",
    "gender": "Male",
    "blood_group": "O+",
    "dob": "1995-05-15",
    "aadhar": "123456789012",
    "mobile": "9876543210",
    "email": "john@example.com",
    "mybharat_id": "MB123456",
    "maritalstatus": "Single",
    "emergency_contact": "9876543211",
    "education": "Bachelor",
    "education_field": "Computer Science",
    "skill": "First Aid",
    "state_name": "Maharashtra",
    "district_name": "Mumbai",
    "area_type": "Urban",
    "postal_code": "400001",
    "town": "Mumbai",
    "village": "Malad",
    "full_address": "123 Main St, Mumbai 400001",
    "id_card": "/uploads/id_card.pdf",
    "certificate": "/uploads/cert.pdf",
    "photo": "/uploads/photo.jpg"
}
```

#### Response (201 Created)

```json
{
    "message": "Volunteer uploaded successfully",
    "volunteer_id": 42,
    "organization": "Red Cross India"
}
```

#### Field Details

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| mis_id | Integer | Yes | Unique identifier |
| name | String | Yes | Full name (max 100 chars) |
| salutation | Choice/Int | No | Mr(1), Mrs(2), Ms(3), Dr(4), Prof(5) |
| gender | Choice/Int | No | Male(1), Female(2), Other(3) |
| blood_group | Choice/Int | No | A+(1)...AB-(8) |
| dob | Date | No | Format: YYYY-MM-DD |
| aadhar | String | No | 12 digits, unique |
| mobile | String | No | 10 digits |
| email | Email | No | Unique valid email |
| mybharat_id | String | No | Max 50 chars |
| maritalstatus | Choice/Int | No | Single(1)...Separated(5) |
| emergency_contact | String | No | 10 digits |
| education | Choice/Int | No | Below10th(1)...PhD(7) |
| education_field | String | No | Field of study |
| skill | Choice/Int | No | FirstAid(1)...Other(6) |
| organization_id | Integer | No | Organization ID (or use name) |
| state_name | String | No | Auto-creates if missing |
| district_name | String | No | Auto-creates if missing |
| area_type | Choice/Int | No | Urban(1), Rural(2), Semi-Urban(3) |
| postal_code | String | No | 6 digits |
| town | String | No | Max 100 chars |
| village | String | No | Max 100 chars |
| full_address | Text | No | Complete address |
| id_card | String | No | Document path/URL |
| certificate | String | No | Document path/URL |
| photo | String | No | Photo path/URL |

---

### POST /volunteer/bulk-upload/

**Upload multiple volunteers via CSV file**

**Auth Required:** Yes  
**Roles:** SUPER_ADMIN, NATIONAL_ADMIN, STATE_ADMIN, DISTRICT_ADMIN, YOUTH_ORG_ADMIN

#### Request

```
POST /volunteer/bulk-upload/
Content-Type: multipart/form-data

Parameters:
- file (required): CSV file
- organization_id (optional): Applied to all rows if not specified
- state_name (optional): Applied to all rows if not specified
- district_name (optional): Applied to all rows if not specified
- expected_count (optional): For validation
```

#### CSV Format

```csv
mis_id,name,salutation,gender,blood_group,dob,aadhar,mobile,email,mybharat_id,maritalstatus,emergency_contact,education,education_field,skill,organization_id,organization_name,state_name,district_name,area_type,postal_code,town,village,full_address,id_card,certificate,photo
10001,John Smith,Mr.,Male,O+,1995-05-15,123456789012,9876543210,john@example.com,MB10001,Single,9876543211,Bachelor,CS,First Aid,1,Red Cross,Maharashtra,Mumbai,Urban,400001,Mumbai,Malad,123 Main St,,
10002,Jane Doe,Ms.,Female,B+,1998-03-22,123456789013,8765432111,jane@example.com,MB10002,Married,8765432112,Master,MBA,Training,1,Red Cross,Maharashtra,Pune,Urban,411001,Pune,Kalyani,456 Park Lane,,
```

#### Response (201 Created)

```json
{
    "created_count": 2,
    "created_mis_ids": [10001, 10002],
    "error_count": 0,
    "errors": [],
    "warnings": []
}
```

#### Response With Errors

```json
{
    "created_count": 1,
    "created_mis_ids": [10001],
    "error_count": 1,
    "errors": [
        {
            "index": 2,
            "errors": {
                "email": ["This field must be unique."],
                "aadhar": ["This field must be unique."]
            }
        }
    ],
    "warnings": []
}
```

#### CSV Column Guide

**Required:**
- mis_id (must be unique)
- name

**Personal Information (8 optional):**
- salutation
- gender
- blood_group
- dob (YYYY-MM-DD)
- aadhar (12 digits)
- mobile (10 digits)
- email
- mybharat_id

**Status & Contact (2 optional):**
- maritalstatus
- emergency_contact (10 digits)

**Education & Skills (3 optional):**
- education
- education_field
- skill

**Organization & Location (5 optional):**
- organization_id OR organization_name
- state_name
- district_name
- area_type

**Address (4 optional):**
- postal_code (6 digits)
- town
- village
- full_address

**Documents (3 optional):**
- id_card
- certificate
- photo

---

### GET /volunteer/coverage/

**Get volunteer coverage statistics by organization**

**Auth Required:** Yes  
**Roles:** SUPER_ADMIN, NATIONAL_ADMIN, STATE_ADMIN, DISTRICT_ADMIN, YOUTH_ORG_ADMIN

#### Response (200 OK)

```json
{
    "organizations": [
        {
            "organization_id": 1,
            "organization_name": "Red Cross India",
            "total_volunteers": 250,
            "states": [
                {
                    "state_id": 1,
                    "state_name": "Maharashtra",
                    "volunteer_count": 150,
                    "districts": [
                        {
                            "district_id": 5,
                            "district_name": "Mumbai",
                            "volunteer_count": 100
                        },
                        {
                            "district_id": 6,
                            "district_name": "Pune",
                            "volunteer_count": 50
                        }
                    ]
                },
                {
                    "state_id": 2,
                    "state_name": "Gujarat",
                    "volunteer_count": 100,
                    "districts": [
                        {
                            "district_id": 10,
                            "district_name": "Ahmedabad",
                            "volunteer_count": 100
                        }
                    ]
                }
            ]
        }
    ]
}
```

---

## Choice Field Values

### Salutation (salutation)
```
Text: Mr., Mrs., Ms., Dr., Prof.
Code: 1, 2, 3, 4, 5
```

### Gender (gender)
```
Text: Male, Female, Other
Code: 1, 2, 3
```

### Blood Group (blood_group)
```
Text: A+, A-, B+, B-, O+, O-, AB+, AB-
Code: 1, 2, 3, 4, 5, 6, 7, 8
```

### Marital Status (maritalstatus)
```
Text: Single, Married, Divorced, Widowed, Separated
Code: 1, 2, 3, 4, 5
```

### Education (education)
```
Text: Below 10th, 10th Pass, 12th Pass, Diploma, Bachelor, Master, PhD, Other
Code: 1, 2, 3, 4, 5, 6, 7, 8
```

### Skill (skill)
```
Text: First Aid, Disaster Management, Rescue Operations, Community Care, Training, Other
Code: 1, 2, 3, 4, 5, 6
```

### Area Type (area_type)
```
Text: Urban, Rural, Semi-Urban
Code: 1, 2, 3
```

---

## Validation Rules

| Field | Rule |
|-------|------|
| mis_id | Must be unique, Integer, Required |
| name | Required, Max 100 characters |
| email | Must be unique, Valid email format |
| aadhar | Must be unique, 12 digits |
| mobile | 10 digits only |
| emergency_contact | 10 digits only |
| dob | Valid YYYY-MM-DD format |
| postal_code | 6 digits |
| organization | Must exist (or use organization_name) |
| state | Auto-creates if doesn't exist |
| district | Auto-creates if doesn't exist and state provided |
| Choice fields | Must be valid text or code |

---

## Common Errors

### Duplicate mis_id

```json
{
    "mis_id": ["This field must be unique."]
}
```

**Fix:** Use a unique value for each volunteer

---

### Invalid Email

```json
{
    "email": ["Enter a valid email address."]
}
```

**Fix:** Provide valid email format (user@domain.com)

---

### Organization Not Found

```json
{
    "organization_name": ["Organization not found"]
}
```

**Fix:** Either provide valid organization_id or existing organization_name

---

### Invalid Blood Group

```json
{
    "blood_group": ["Invalid blood group"]
}
```

**Fix:** Use valid code (1-8) or text (A+, B-, etc.)

---

### Aadhar Already Exists

```json
{
    "aadhar": ["This field must be unique."]
}
```

**Fix:** Aadhar must be unique across all volunteers

---

## Best Practices

### CSV Upload Tips

1. **Validate data first** - Ensure all data is correct before uploading
2. **Use numeric codes** - Faster processing than text for choice fields
3. **Test with small batch** - Upload 5-10 records to verify before bulk upload
4. **Include state/district** - Helps with proper organization of data
5. **Keep format consistent** - Dates as YYYY-MM-DD, 10-digit mobiles
6. **No extra spaces** - Trim whitespace from all fields
7. **Check for duplicates** - Ensure unique mis_ids, emails, aadhar
8. **Use organization defaults** - Set organization_id at upload level

### Single Upload Tips

1. **Required fields first** - Ensure mis_id and name are provided
2. **Validate phone numbers** - Should be 10 digits
3. **Use state/district names** - Auto-creation is faster than IDs
4. **Choice codes faster** - Use numeric codes for faster processing

---

## Bulk Upload Workflow

```
1. Prepare CSV file with all volunteer data
   ↓
2. Get access token via /auth/login/
   ↓
3. POST to /volunteer/bulk-upload/ with file
   ↓
4. API processes and returns results:
   - created_count: successfully created
   - created_mis_ids: list of created IDs
   - error_count: number of errors
   - errors: array of specific errors
   - warnings: warnings about data mismatches
   ↓
5. Check errors and fix/re-upload if needed
```

---

## Performance Considerations

- **Single API call:** ~50-100ms per volunteer
- **Bulk upload:** ~5-10ms per volunteer (faster)
- **Max recommended batch:** 1000 volunteers per file
- **Optimal strategy:** 
  - < 10 volunteers: Use single upload
  - 10-100 volunteers: Use bulk upload with multiple files
  - 100+ volunteers: Use bulk upload (may split into 1000-record chunks)

---

## Troubleshooting

### Upload returns "created_count: 0"

**Cause:** All records had validation errors

**Solution:**
1. Check error array for details
2. Fix data according to error messages
3. Re-upload corrected file

---

### Some volunteers not created

**Cause:** Invalid data in some rows causing partial upload

**Solution:**
1. Check error array to see which rows failed
2. Fix those specific rows
3. Re-upload just the failed rows with new unique identifiers

---

### "Organization not found"

**Cause:** Invalid organization_id or name

**Solution:**
- Verify organization exists first: GET /organizations/
- Use existing organization_id
- Or spell organization name exactly as it appears in system

---


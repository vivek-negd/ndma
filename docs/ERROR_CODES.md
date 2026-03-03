# API Error Codes & Handling Guide

## Overview

The API uses standard HTTP status codes combined with detailed error messages in response bodies. All errors follow a consistent format.

---

## Standard Error Response Format

### Single Field Error

```json
{
    "field_name": ["Error message"]
}
```

### Multiple Errors

```json
{
    "field1": ["Error 1", "Error 2"],
    "field2": ["Error 3"]
}
```

### Non-Field Error

```json
{
    "detail": "Error message",
    "error_code": "ERROR_CODE"
}
```

---

## HTTP Status Codes

| Code | Name | Meaning | Fix |
|------|------|---------|-----|
| 200 | OK | Request succeeded | None needed |
| 201 | Created | Resource created successfully | None needed |
| 400 | Bad Request | Invalid request data | Check request format and data |
| 401 | Unauthorized | Missing or invalid authentication | Provide valid token |
| 403 | Forbidden | User lacks required permissions | Use account with proper role |
| 404 | Not Found | Resource doesn't exist | Verify resource ID/path exists |
| 409 | Conflict | Resource already exists | Use different unique value |
| 413 | Payload Too Large | File/data too big | Reduce file size or split into chunks |
| 422 | Unprocessable Entity | Request validation failed | Fix validation errors shown |
| 429 | Too Many Requests | Rate limit exceeded | Wait before making new request |
| 500 | Server Error | Internal server error | Check server logs, retry later |

---

## Authentication Errors (401)

### Missing Token

**Error:**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**Fix:**
```bash
# Add Authorization header
curl -H "Authorization: Bearer YOUR_TOKEN" ...
```

---

### Invalid Token

**Error:**
```json
{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is invalid or expired"
        }
    ]
}
```

**Fix:**
1. Get new token: `POST /api/v1/auth/login/`
2. Extract `access` token from response
3. Use in Authorization header

---

### Expired Token

**Error:**
```json
{
    "detail": "Token is invalid or expired"
}
```

**Fix:**
```bash
# Refresh the token
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "REFRESH_TOKEN"}'
```

---

## Permission Errors (403)

### Insufficient Permissions

**Error:**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

**Causes:**
- User role doesn't have access
- User's geographic scope doesn't include resource
- User's organization doesn't own resource

**Fix:**
1. Contact admin to grant required role
2. Ensure user has access to state/district
3. Verify user's organization is correct

---

### Role Not Authorized

**Error:**
```json
{
    "detail": "Only admins can perform this action."
}
```

**Required Roles by Endpoint:**
- `/volunteer/create/`: ADMIN, NATIONAL_ADMIN, STATE_ADMIN, DISTRICT_ADMIN, YOUTH_ORG_ADMIN
- `/organizations/`: SUPER_ADMIN, NATIONAL_ADMIN, STATE_ADMIN only
- `/rbac/`: SUPER_ADMIN only

**Fix:** Use admin account with required role

---

## Validation Errors (422/400)

### Unique Constraint Violated

**Error:**
```json
{
    "mis_id": ["This field must be unique."]
}
```

**Cause:** Another volunteer already exists with this value

**Fix:** Use unique value for each volunteer

---

### Invalid Email Format

**Error:**
```json
{
    "email": ["Enter a valid email address."]
}
```

**Valid Formats:**
- user@domain.com ✓
- first.name@company.co.uk ✓
- user+tag@domain.com ✓

**Invalid Formats:**
- user@domain ✗
- @domain.com ✗
- user@.com ✗

**Fix:** Provide valid email address

---

### Invalid Date Format

**Error:**
```json
{
    "dob": ["Date has wrong format. Use one of these formats instead: YYYY-MM-DD"]
}
```

**Valid:**
- 1995-05-15 ✓
- 2000-12-31 ✓

**Invalid:**
- 05/15/1995 ✗
- 15-05-1995 ✗
- 15 May 1995 ✗

**Fix:** Use YYYY-MM-DD format

---

### Invalid Choice Value

**Error:**
```json
{
    "blood_group": ["Invalid choice"]
}
```

**Valid Blood Groups:**
- Text: A+, A-, B+, B-, O+, O-, AB+, AB- ✓
- Code: 1, 2, 3, 4, 5, 6, 7, 8 ✓

**Invalid:**
- AB (missing sign) ✗
- 9 (code doesn't exist) ✗
- AB- (correct but different case) - Actually valid ✓

**Fix:** Use valid code or text value

---

### Field Too Long

**Error:**
```json
{
    "name": ["Ensure this field has no more than 100 characters."]
}
```

**Field Limits:**
| Field | Max Length |
|-------|-----------|
| name | 100 |
| education_field | 100 |
| town | 100 |
| village | 100 |
| mybharat_id | 50 |
| postal_code | 10 |

**Fix:** Truncate value to max length

---

### Invalid Phone Number

**Error:**
```json
{
    "mobile": ["Must be 10 digits"]
}
```

**Valid:**
- 9876543210 ✓
- 0876543210 ✓

**Invalid:**
- 987654321 (only 9 digits) ✗
- +919876543210 (includes country code) ✗
- 98-7654-3210 (includes dashes) ✗

**Fix:** Use only 10 digits

---

### Invalid Aadhar

**Error:**
```json
{
    "aadhar": ["Must be 12 digits and unique"]
}
```

**Valid:**
- 123456789012 ✓
- 999888777666 ✓

**Invalid:**
- 12345678901 (only 11 digits) ✗
- 1234567890123 (13 digits) ✗
- 123456789A12 (contains letter) ✗

**Fix:** Provide exactly 12 digits, ensure uniqueness

---

## Resource Not Found (404)

### Volunteer Not Found

**Error:**
```json
{
    "detail": "Not found."
}
```

**Endpoint:** GET /volunteer/42/

**Fix:** Verify volunteer ID in request

---

### Organization Not Found

**Error:**
```json
{
    "organization": ["Organization with id 999 not found"]
}
```

**Fix:**
1. Get valid org IDs: `GET /organizations/`
2. Use ID from response

---

### State Not Found

**Error:**
```json
{
    "state_name": ["State not found"]
}
```

**Valid States:**
Get list: `GET /states/`

Or use auto-creation:
```json
{
    "state_name": "New State Name"
}
```
Auto-creates if doesn't exist

**Fix:** Use existing state name or let API auto-create

---

### District Not Found

**Error:**
```json
{
    "district_name": ["District not found"]
}
```

**Fix:**
1. Provide state_name also
2. API will auto-create district under state

---

## Bulk Upload Errors (422)

### CSV Format Invalid

**Error:**
```json
{
    "file": ["File must be in CSV format"]
}
```

**Fix:** Save as .csv file

---

### Missing Required File

**Error:**
```json
{
    "file": ["No file part in the request"]
}
```

**Fix:** Include file in multipart form data:
```bash
curl -F "file=@volunteers.csv" ...
```

---

### CSV Headers Wrong

**Error:**
```json
{
    "errors": ["Missing columns: X, Y, Z"]
}
```

**Required Columns:** mis_id, name

**Optional Columns:** All others (see VOLUNTEERS.md)

**Fix:** Ensure CSV has correct headers

---

### Row Validation Error in Bulk Upload

**Error:**
```json
{
    "created_count": 2,
    "created_mis_ids": [10001, 10002],
    "error_count": 2,
    "errors": [
        {
            "index": 3,
            "errors": {
                "email": ["This field must be unique."],
                "organization": ["Organization not found"]
            }
        },
        {
            "index": 5,
            "errors": {
                "mis_id": ["This field must be unique."]
            }
        }
    ]
}
```

**Meaning:**
- Rows 1-2 created successfully
- Row 3 failed (2 errors shown)
- Row 5 failed (1 error shown)

**Fix:**
1. Row indices are 1-based in CSV (row 3 = line 4 including header)
2. Fix errors in those rows
3. Re-upload fixed rows

---

## Conflict Errors (409)

### Resource Already Exists

**Error:**
```json
{
    "detail": "Volunteer with mis_id 10001 already exists"
}
```

**Cause:** Creating duplicate mis_id

**Fix:** Use unique mis_id

---

## Rate Limiting (429)

**Error:**
```json
{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```

**Meaning:** Too many requests from same user/IP

**Fix:** Wait before making requests (rate limit: 1000/hour typical)

---

## Server Errors (500)

### Internal Server Error

**Error:**
```json
{
    "detail": "Internal server error"
}
```

**Cause:** Bug or server issue

**Fix:**
1. Check error logs on server
2. Contact support with:
   - Request headers
   - Request body
   - Error timestamp
   - Error message

---

## Error Handling Best Practices

### 1. Check all errors before retrying

```python
if response.status_code != 200:
    errors = response.json()
    for field, messages in errors.items():
        print(f"{field}: {', '.join(messages)}")
    # Don't retry until all errors fixed
```

---

### 2. Handle each error type

```python
if response.status_code == 401:
    # Get new token and retry
    token = get_new_token()
elif response.status_code == 403:
    # Check permissions
    print("Insufficient permissions")
elif response.status_code == 422:
    # Fix validation errors
    errors = response.json()
    print(f"Validation errors: {errors}")
```

---

### 3. Implement exponential backoff

```python
import time

max_retries = 3
retry_count = 0
backoff = 1

while retry_count < max_retries:
    try:
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            time.sleep(backoff)
            backoff *= 2
            retry_count += 1
        else:
            break
    except:
        time.sleep(backoff)
        backoff *= 2
        retry_count += 1
```

---

### 4. Log errors with context

```python
import logging

logger = logging.getLogger(__name__)

response = requests.post(url, data=data)
if response.status_code != 200:
    logger.error(
        f"API Error: {response.status_code}",
        extra={
            "endpoint": url,
            "method": "POST",
            "error_response": response.text,
            "timestamp": datetime.now()
        }
    )
```

---

## Common Troubleshooting

### "Authentication credentials were not provided"
- **Cause:** Missing Authorization header
- **Fix:** Add `Authorization: Bearer YOUR_TOKEN` to all requests

---

### "You do not have permission"
- **Cause:** User role doesn't have access
- **Fix:** Login with admin account or request role upgrade

---

### "This field must be unique"
- **Cause:** Value already exists in database
- **Fix:** Generate unique value (auto-increment, UUID, etc.)

---

### "Invalid choice"
- **Cause:** Wrong choice value provided
- **Fix:** Check valid choices for that field (see VOLUNTEERS.md)

---

### "Enter a valid email address"
- **Cause:** Email format invalid
- **Fix:** Use standard email format (user@domain.com)

---

### "Request was throttled"
- **Cause:** Too many requests
- **Fix:** Wait, then implement rate limiting in client

---


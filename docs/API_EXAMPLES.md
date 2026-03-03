# API Examples - Code Samples

## Table of Contents
1. [Authentication](#authentication)
2. [Create Volunteer (Single)](#create-volunteer-single)
3. [Bulk Upload Volunteers](#bulk-upload-volunteers)
4. [Organization Management](#organization-management)
5. [RBAC Management](#rbac-management)
6. [Training Schedules](#training-schedules)

---

## Authentication

### Python Example - Login and Get Token

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Step 1: Login
login_response = requests.post(
    f"{BASE_URL}/auth/login/",
    json={
        "email": "admin@example.com",
        "password": "admin123"
    }
)

auth_data = login_response.json()
access_token = auth_data['access']
refresh_token = auth_data['refresh']

print(f"Access Token: {access_token}")
print(f"Refresh Token: {refresh_token}")

# Save tokens for subsequent requests
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Step 2: Get user profile
profile_response = requests.get(
    f"{BASE_URL}/auth/profile/",
    headers=headers
)

print(json.dumps(profile_response.json(), indent=2))
```

---

### cURL Example - Login

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'

# Response:
# {
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "user": {
#     "id": 1,
#     "email": "admin@example.com",
#     "user_role": "SUPER_ADMIN"
#   }
# }

# Get Profile (authenticated)
curl -X GET http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer <access_token>"
```

---

### JavaScript Example - Login

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

async function login(email, password) {
    const response = await fetch(`${BASE_URL}/auth/login/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: email,
            password: password
        })
    });

    const data = await response.json();
    return {
        access: data.access,
        refresh: data.refresh,
        user: data.user
    };
}

// Usage
login('admin@example.com', 'admin123')
    .then(auth => {
        console.log('Access Token:', auth.access);
        console.log('User:', auth.user);
        // Store token in localStorage
        localStorage.setItem('accessToken', auth.access);
    });
```

---

## Create Volunteer (Single)

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGc..."

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

volunteer_data = {
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
    "full_address": "123 Main St, Mumbai 400001"
}

response = requests.post(
    f"{BASE_URL}/volunteer/create/",
    json=volunteer_data,
    headers=headers
)

if response.status_code == 201:
    result = response.json()
    print(f"✓ Volunteer created!")
    print(f"  ID: {result['volunteer_id']}")
    print(f"  Organization: {result['organization']}")
else:
    print(f"✗ Error: {response.json()}")
```

---

### cURL Example

```bash
curl -X POST http://localhost:8000/api/v1/volunteer/create/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": 1,
    "mis_id": 10001,
    "name": "John Smith",
    "gender": "Male",
    "blood_group": "O+",
    "dob": "1995-05-15",
    "aadhar": "123456789012",
    "mobile": "9876543210",
    "email": "john@example.com",
    "state_name": "Maharashtra",
    "district_name": "Mumbai"
  }'
```

---

### JavaScript Example

```javascript
async function createVolunteer(volunteerData, token) {
    const response = await fetch('http://localhost:8000/api/v1/volunteer/create/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(volunteerData)
    });

    const data = await response.json();
    
    if (response.ok) {
        console.log('✓ Volunteer created:', data.volunteer_id);
        return data;
    } else {
        console.error('✗ Error:', data);
        throw data;
    }
}

// Usage
const volunteerData = {
    organization_id: 1,
    mis_id: 10001,
    name: "John Smith",
    gender: "Male",
    blood_group: "O+",
    dob: "1995-05-15",
    aadhar: "123456789012",
    mobile: "9876543210",
    email: "john@example.com",
    state_name: "Maharashtra",
    district_name: "Mumbai"
};

const token = localStorage.getItem('accessToken');
createVolunteer(volunteerData, token)
    .then(result => console.log('Success:', result))
    .catch(err => console.log('Failed:', err));
```

---

## Bulk Upload Volunteers

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGc..."

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# Prepare CSV file
csv_file_path = "volunteers.csv"

# File content (27 columns)
csv_content = """mis_id,name,salutation,gender,blood_group,dob,aadhar,mobile,email,mybharat_id,maritalstatus,emergency_contact,education,education_field,skill,organization_id,organization_name,state_name,district_name,area_type,postal_code,town,village,full_address,id_card,certificate,photo
10001,John Smith,Mr.,Male,O+,1995-05-15,111111111111,9876543210,john@example.com,MB10001,Single,9876543211,Bachelor,CS,First Aid,1,Red Cross,Maharashtra,Mumbai,Urban,400001,Mumbai,Malad,123 Main St,,
10002,Jane Doe,Ms.,Female,B+,1998-03-22,222222222222,9876543211,jane@example.com,MB10002,Married,9876543212,Master,MBA,Training,1,Red Cross,Maharashtra,Pune,Urban,411001,Pune,Kalyani,456 Park Lane,,
10003,Bob Wilson,Mr.,Other,AB-,1992-07-10,333333333333,9876543212,bob@example.com,MB10003,Single,9876543213,Diploma,Commerce,Disaster Management,1,Red Cross,Maharashtra,Mumbai,Urban,400002,Mumbai,Andheri,789 Business Ave,,
"""

# Write CSV file
with open(csv_file_path, 'w') as f:
    f.write(csv_content)

# Upload
with open(csv_file_path, 'rb') as f:
    files = {'file': f}
    data = {
        'organization_id': 1,
        'expected_count': 3
    }
    
    response = requests.post(
        f"{BASE_URL}/volunteer/bulk-upload/",
        files=files,
        data=data,
        headers=headers
    )

result = response.json()
print(f"Created: {result['created_count']}")
print(f"Errors: {result['error_count']}")
print(f"Created IDs: {result['created_mis_ids']}")

if result['error_count'] > 0:
    print("\nErrors encountered:")
    for error in result['errors']:
        print(f"  Row {error['index']}: {error['errors']}")
```

---

### cURL Example

```bash
# Create CSV file first
cat > volunteers.csv << 'EOF'
mis_id,name,gender,blood_group,dob,aadhar,mobile,email,state_name,district_name
10001,John Smith,Male,O+,1995-05-15,111111111111,9876543210,john@example.com,Maharashtra,Mumbai
10002,Jane Doe,Female,B+,1998-03-22,222222222222,9876543211,jane@example.com,Maharashtra,Pune
10003,Bob Wilson,Other,AB-,1992-07-10,333333333333,9876543212,bob@example.com,Maharashtra,Mumbai
EOF

# Upload bulk file
curl -X POST http://localhost:8000/api/v1/volunteer/bulk-upload/ \
  -H "Authorization: Bearer <token>" \
  -F "file=@volunteers.csv" \
  -F "organization_id=1" \
  -F "expected_count=3"
```

---

## Organization Management

### Create Organization

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGc..."

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

org_data = {
    "name": "Red Cross - New Chapter",
    "org_type": "NSS",
    "state": 1,
    "district": 5,
    "contact_person": "Rajesh Kumar",
    "contact_email": "rajesh@redcross.com",
    "contact_phone": "9876543210",
    "address": "Mumbai Head Office",
    "website": "https://redcross.org",
    "is_active": True
}

response = requests.post(
    f"{BASE_URL}/organizations/",
    json=org_data,
    headers=headers
)

if response.status_code == 201:
    org = response.json()
    print(f"✓ Organization created: {org['id']} - {org['name']}")
else:
    print(f"✗ Error: {response.json()}")
```

---

### List Organizations with Filters

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGc..."

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# List with filters
params = {
    'state': 1,
    'org_type': 'NSS',
    'is_active': 'true',
    'search': 'Red Cross',
    'ordering': 'name'
}

response = requests.get(
    f"{BASE_URL}/organizations/",
    params=params,
    headers=headers
)

orgs = response.json()
print(f"Found {orgs['count']} organizations")
for org in orgs['results']:
    print(f"  - {org['name']} ({org['org_type']}) - {org['volunteer_count']} volunteers")
```

---

## RBAC Management

### Create Custom Role

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGc..."

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# First, get permission IDs
perms_response = requests.get(
    f"{BASE_URL}/rbac/permissions/",
    headers=headers
)
permissions = perms_response.json()['results']

# Get IDs for specific permissions
volunteer_perms = []
for perm in permissions:
    if 'VOLUNTEER' in perm['name']:
        volunteer_perms.append(perm['id'])

# Create role
role_data = {
    "name": "VOLUNTEER_MANAGER",
    "description": "Can manage volunteers",
    "permissions": volunteer_perms[:5]  # Assign first 5 permissions
}

response = requests.post(
    f"{BASE_URL}/rbac/roles/",
    json=role_data,
    headers=headers
)

if response.status_code == 201:
    role = response.json()
    print(f"✓ Role created: {role['id']} - {role['name']}")
else:
    print(f"✗ Error: {response.json()}")
```

---

### Assign Role to User

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGc..."

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

assignment_data = {
    "user_id": 5,
    "role_id": 3
}

response = requests.post(
    f"{BASE_URL}/rbac/user-roles/",
    json=assignment_data,
    headers=headers
)

if response.status_code == 201:
    print("✓ Role assigned to user")
else:
    print(f"✗ Error: {response.json()}")
```

---

## Training Schedules

### Create Training Schedule

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGc..."

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

training_data = {
    "title": "Advanced First Aid Training",
    "training_type": "FIRST_AID",
    "description": "Comprehensive first aid training program",
    "start_date": "2026-04-01",
    "end_date": "2026-04-05",
    "location": "Mumbai Training Center",
    "trainer": 2,
    "max_capacity": 50,
    "state": 1
}

response = requests.post(
    f"{BASE_URL}/training-schedules/",
    json=training_data,
    headers=headers
)

if response.status_code == 201:
    training = response.json()
    print(f"✓ Training created: {training['id']} - {training['title']}")
else:
    print(f"✗ Error: {response.json()}")
```

---

### List and Search Training

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGc..."

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# Search for active trainings
params = {
    'status': 'SCHEDULED',
    'state': 1,
    'search': 'First Aid',
    'ordering': 'start_date'
}

response = requests.get(
    f"{BASE_URL}/training-schedules/",
    params=params,
    headers=headers
)

trainings = response.json()
print(f"Found {trainings['count']} trainings")
for training in trainings['results']:
    print(f"  - {training['title']}")
    print(f"    Date: {training['start_date']} to {training['end_date']}")
    print(f"    Location: {training['location']}")
    print(f"    Enrollment: {training['current_enrollment']}/{training['max_capacity']}")
```

---

## Error Handling

### Handle Errors in Python

```python
import requests

def make_api_call(method, endpoint, data=None, token=None):
    """Make API call with proper error handling"""
    
    BASE_URL = "http://localhost:8000/api/v1"
    headers = {
        "Content-Type": "application/json"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        # Handle rate limiting
        if response.status_code == 429:
            print("Rate limited. Please retry after:", response.headers.get('Retry-After'))
            return None
        
        # Handle authentication errors
        if response.status_code == 401:
            print("Unauthorized. Please check your token.")
            return None
        
        # Handle permission errors
        if response.status_code == 403:
            print("Forbidden. You don't have permission for this action.")
            return None
        
        # Handle not found
        if response.status_code == 404:
            print("Resource not found.")
            return None
        
        # Handle validation errors
        if response.status_code == 400:
            errors = response.json()
            print("Validation errors:")
            for field, msgs in errors.items():
                print(f"  {field}: {msgs}")
            return None
        
        # Handle server errors
        if response.status_code >= 500:
            print("Server error. Please try again later.")
            return None
        
        # Success
        return response.json()
    
    except requests.exceptions.ConnectionError:
        print("Connection error. Please check the API URL.")
        return None
    except requests.exceptions.Timeout:
        print("Request timeout. Please try again.")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage
result = make_api_call(
    'POST',
    '/volunteer/create/',
    data={
        'organization_id': 1,
        'mis_id': 10001,
        'name': 'Test'
    },
    token='your_token_here'
)

if result:
    print("Success:", result)
```

---

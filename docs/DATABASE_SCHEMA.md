# Database Schema Reference

## Overview

Complete database schema for the NDMA Volunteer Management API.

**Database Type:** MySQL 5.7+  
**Character Set:** utf8mb4  
**Collation:** utf8mb4_unicode_ci

---

## Tables

### 1. Volunteer

Store volunteer information and personal details.

```sql
CREATE TABLE volunteer (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    organization_id BIGINT NOT NULL,
    mis_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    salutation_id INT,
    gender_id INT,
    blood_group_id INT,
    dob DATE,
    aadhar VARCHAR(50) UNIQUE,
    mobile VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    mybharat_id VARCHAR(50),
    maritalstatus_id INT,
    emergency_contact VARCHAR(20),
    education_id INT,
    education_field VARCHAR(100),
    skill_id INT,
    state_id BIGINT,
    district_id BIGINT,
    area_type_id INT,
    postal_code VARCHAR(10),
    town VARCHAR(100),
    village VARCHAR(100),
    full_address TEXT,
    id_card VARCHAR(500),
    certificate VARCHAR(500),
    photo VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (organization_id) REFERENCES organization(id),
    FOREIGN KEY (state_id) REFERENCES state(id),
    FOREIGN KEY (district_id) REFERENCES district(id),
    INDEX idx_mis_id (mis_id),
    INDEX idx_email (email),
    INDEX idx_organization (organization_id),
    INDEX idx_state (state_id),
    INDEX idx_deleted_at (deleted_at)
);
```

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| id | BIGINT | PK, AUTO | Unique identifier |
| organization_id | BIGINT | FK, NOT NULL | Organization reference |
| mis_id | BIGINT | UNIQUE, NOT NULL | Management Information System ID |
| name | VARCHAR(100) | NOT NULL | Volunteer full name |
| salutation_id | INT | Optional | Mr(1), Mrs(2), Ms(3), Dr(4), Prof(5) |
| gender_id | INT | Optional | Male(1), Female(2), Other(3) |
| blood_group_id | INT | Optional | A+(1)...AB-(8) |
| dob | DATE | Optional | Date of birth |
| aadhar | VARCHAR(50) | UNIQUE, Optional | 12-digit Aadhar ID |
| mobile | VARCHAR(20) | Optional | 10-digit phone |
| email | VARCHAR(100) | UNIQUE, Optional | Email address |
| mybharat_id | VARCHAR(50) | Optional | MyBharat platform ID |
| maritalstatus_id | INT | Optional | Single(1)...Separated(5) |
| emergency_contact | VARCHAR(20) | Optional | Emergency contact number |
| education_id | INT | Optional | Education level |
| education_field | VARCHAR(100) | Optional | Field of study |
| skill_id | INT | Optional | Primary skill |
| state_id | BIGINT | FK, Optional | State reference |
| district_id | BIGINT | FK, Optional | District reference |
| area_type_id | INT | Optional | Urban(1), Rural(2), Semi-Urban(3) |
| postal_code | VARCHAR(10) | Optional | 6-digit postal code |
| town | VARCHAR(100) | Optional | Town/city name |
| village | VARCHAR(100) | Optional | Village name |
| full_address | TEXT | Optional | Complete address |
| id_card | VARCHAR(500) | Optional | Document path/URL |
| certificate | VARCHAR(500) | Optional | Certificate path/URL |
| photo | VARCHAR(500) | Optional | Photo path/URL |
| created_at | TIMESTAMP | NOT NULL | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |
| deleted_at | TIMESTAMP | NULL | Soft delete timestamp |

#### Indexes

```sql
CREATE INDEX idx_volunteer_mis_id ON volunteer(mis_id);
CREATE INDEX idx_volunteer_email ON volunteer(email);
CREATE INDEX idx_volunteer_organization ON volunteer(organization_id);
CREATE INDEX idx_volunteer_state ON volunteer(state_id);
CREATE INDEX idx_volunteer_district ON volunteer(district_id);
CREATE INDEX idx_volunteer_deleted_at ON volunteer(deleted_at);
```

---

### 2. Organization

Store organization/NGO information.

```sql
CREATE TABLE organization (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    organization_name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    website VARCHAR(500),
    email VARCHAR(100),
    phone VARCHAR(20),
    established_year INT,
    registration_number VARCHAR(100) UNIQUE,
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    INDEX idx_organization_name (organization_name),
    INDEX idx_status (status)
);
```

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| id | BIGINT | PK, AUTO | Unique identifier |
| organization_name | VARCHAR(255) | UNIQUE, NOT NULL | Organization name |
| description | TEXT | Optional | About organization |
| website | VARCHAR(500) | Optional | Website URL |
| email | VARCHAR(100) | Optional | Contact email |
| phone | VARCHAR(20) | Optional | Contact phone |
| established_year | INT | Optional | Year founded |
| registration_number | VARCHAR(100) | UNIQUE, Optional | Government registration |
| status | ENUM | Default 'active' | active, inactive, suspended |
| created_at | TIMESTAMP | NOT NULL | Record creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |
| deleted_at | TIMESTAMP | NULL | Soft delete timestamp |

---

### 3. State

Store Indian states.

```sql
CREATE TABLE state (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    state_name VARCHAR(100) UNIQUE NOT NULL,
    state_code VARCHAR(5) UNIQUE,
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_state_name (state_name)
);
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| id | BIGINT | Unique identifier |
| state_name | VARCHAR(100) | State name (unique) |
| state_code | VARCHAR(5) | 2-letter state code |
| region | VARCHAR(50) | Region (North/South/East/West) |
| created_at | TIMESTAMP | When record was created |

#### Sample Data

```sql
INSERT INTO state (state_name, state_code, region) VALUES
('Maharashtra', 'MH', 'West'),
('Gujarat', 'GJ', 'West'),
('Tamil Nadu', 'TN', 'South'),
('Uttar Pradesh', 'UP', 'North'),
('Bihar', 'BR', 'East');
```

---

### 4. District

Store Indian districts.

```sql
CREATE TABLE district (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    district_name VARCHAR(100) NOT NULL,
    state_id BIGINT NOT NULL,
    district_code VARCHAR(5),
    population BIGINT,
    area_in_sqkm DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES state(id),
    UNIQUE KEY unique_district_state (district_name, state_id),
    INDEX idx_state_id (state_id)
);
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| id | BIGINT | Unique identifier |
| district_name | VARCHAR(100) | District name |
| state_id | BIGINT | State reference |
| district_code | VARCHAR(5) | District code |
| population | BIGINT | Population count |
| area_in_sqkm | DECIMAL | Area in square kilometers |
| created_at | TIMESTAMP | When record was created |

#### Constraints

- Unique combination of (district_name, state_id)

---

### 5. User

Django/application user accounts.

```sql
CREATE TABLE auth_user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME,
    is_superuser TINYINT(1) DEFAULT 0,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    email VARCHAR(254) UNIQUE,
    is_staff TINYINT(1) DEFAULT 0,
    is_active TINYINT(1) DEFAULT 1,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_is_active (is_active)
);
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| id | INT | Unique identifier |
| password | VARCHAR(128) | Hashed password (PBKDF2) |
| last_login | DATETIME | Last login timestamp |
| is_superuser | TINYINT | Django superuser flag |
| username | VARCHAR(150) | Unique username |
| first_name | VARCHAR(150) | User's first name |
| last_name | VARCHAR(150) | User's last name |
| email | VARCHAR(254) | Unique email |
| is_staff | TINYINT | Django staff flag |
| is_active | TINYINT | Active status (1=active, 0=disabled) |
| date_joined | DATETIME | Account creation time |

---

### 6. Role

Define roles in RBAC system.

```sql
CREATE TABLE role (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_system_role TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_role_name (role_name)
);
```

#### Predefined Roles

| Role | Description | Level |
|------|-------------|-------|
| SUPER_ADMIN | Full system access | 1 (Highest) |
| NATIONAL_ADMIN | National-level NDMA admin | 2 |
| STATE_ADMIN | State-level disaster management | 3 |
| DISTRICT_ADMIN | District-level admin | 4 |
| YOUTH_ORG_ADMIN | Organization admin | 5 |
| VOLUNTEER | Volunteer user | 6 |
| TRAINER | Training coordinator | 7 |
| TECHNICAL_ADMIN | System maintenance | 8 |

---

### 7. Permission

Define granular permissions.

```sql
CREATE TABLE permission (
    id INT PRIMARY KEY AUTO_INCREMENT,
    codename VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    module VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Sample Permissions

| Codename | Name | Module |
|----------|------|--------|
| view_volunteer | Can view volunteer | volunteer |
| add_volunteer | Can add volunteer | volunteer |
| edit_volunteer | Can edit volunteer | volunteer |
| delete_volunteer | Can delete volunteer | volunteer |
| bulk_upload_volunteer | Can bulk upload | volunteer |
| view_organization | Can view organization | organization |
| manage_users | Can manage users | user |
| manage_roles | Can manage roles | rbac |
| view_reports | Can view reports | reports |

---

### 8. RolePermission

Junction table for role-permission mapping.

```sql
CREATE TABLE role_permission (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    role_id BIGINT NOT NULL,
    permission_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES role(id),
    FOREIGN KEY (permission_id) REFERENCES permission(id),
    UNIQUE KEY unique_role_permission (role_id, permission_id),
    INDEX idx_role_id (role_id)
);
```

---

### 9. RoleAssignment

Assign roles to users.

```sql
CREATE TABLE role_assignment (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    role_id BIGINT NOT NULL,
    state_id BIGINT,
    district_id BIGINT,
    organization_id BIGINT,
    start_date DATE DEFAULT CURDATE(),
    end_date DATE,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user(id),
    FOREIGN KEY (role_id) REFERENCES role(id),
    FOREIGN KEY (state_id) REFERENCES state(id),
    FOREIGN KEY (district_id) REFERENCES district(id),
    FOREIGN KEY (organization_id) REFERENCES organization(id),
    INDEX idx_user_id (user_id),
    INDEX idx_role_id (role_id)
);
```

#### Example

- User 5 → DISTRICT_ADMIN role for Maharashtra state + Mumbai district
- User 7 → YOUTH_ORG_ADMIN role for Red Cross organization

---

### 10. Training

Training program details.

```sql
CREATE TABLE training (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    organization_id BIGINT NOT NULL,
    training_name VARCHAR(255) NOT NULL,
    description TEXT,
    training_type VARCHAR(50),
    start_date DATE NOT NULL,
    end_date DATE,
    location VARCHAR(255),
    capacity INT,
    trainer_id INT,
    state_id BIGINT,
    district_id BIGINT,
    status ENUM('planned', 'ongoing', 'completed') DEFAULT 'planned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organization(id),
    FOREIGN KEY (trainer_id) REFERENCES auth_user(id),
    FOREIGN KEY (state_id) REFERENCES state(id),
    FOREIGN KEY (district_id) REFERENCES district(id)
);
```

---

### 11. TrainingAttendance

Track volunteer attendance.

```sql
CREATE TABLE training_attendance (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    training_id BIGINT NOT NULL,
    volunteer_id BIGINT,
    user_id INT,
    attended TINYINT(1) DEFAULT 0,
    attendance_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (training_id) REFERENCES training(id),
    FOREIGN KEY (volunteer_id) REFERENCES volunteer(id),
    FOREIGN KEY (user_id) REFERENCES auth_user(id)
);
```

---

### 12. AuditLog

Track all changes for compliance.

```sql
CREATE TABLE audit_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    entity_type VARCHAR(50) NOT NULL,
    entity_id BIGINT,
    action VARCHAR(50) NOT NULL,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_created_at (created_at)
);
```

#### Actions Logged

- CREATE
- UPDATE  
- DELETE
- BULK_IMPORT
- DOWNLOAD
- EXPORT
- LOGIN
- LOGOUT

---

## Choice Field Values

### Salutation (salutation_id)

| Code | Text |
|------|------|
| 1 | Mr. |
| 2 | Mrs. |
| 3 | Ms. |
| 4 | Dr. |
| 5 | Prof. |

### Gender (gender_id)

| Code | Text |
|------|------|
| 1 | Male |
| 2 | Female |
| 3 | Other |

### Blood Group (blood_group_id)

| Code | Text |
|------|------|
| 1 | A+ |
| 2 | A- |
| 3 | B+ |
| 4 | B- |
| 5 | O+ |
| 6 | O- |
| 7 | AB+ |
| 8 | AB- |

### Marital Status (maritalstatus_id)

| Code | Text |
|------|------|
| 1 | Single |
| 2 | Married |
| 3 | Divorced |
| 4 | Widowed |
| 5 | Separated |

### Education (education_id)

| Code | Text |
|------|------|
| 1 | Below 10th |
| 2 | 10th Pass |
| 3 | 12th Pass |
| 4 | Diploma |
| 5 | Bachelor |
| 6 | Master |
| 7 | PhD |
| 8 | Other |

### Skill (skill_id)

| Code | Text |
|------|------|
| 1 | First Aid |
| 2 | Disaster Management |
| 3 | Rescue Operations |
| 4 | Community Care |
| 5 | Training |
| 6 | Other |

### Area Type (area_type_id)

| Code | Text |
|------|------|
| 1 | Urban |
| 2 | Rural |
| 3 | Semi-Urban |

---

## Relationships

```
Volunteer
├── organization_id → Organization
├── state_id → State
├── district_id → District
└── skill_id → (choice)

Organization
├── volunteers (reverse FK)
├── training (reverse FK)
└── users (through RoleAssignment)

User
├── roles (through RoleAssignment)
├── trainings
├── audit logs
└── role_assignments

Role
├── permissions (through RolePermission)
└── role_assignments (reverse)

Training
├── organization_id → Organization
├── trainer_id → User
├── state_id → State
├── district_id → District
└── attendance (reverse FK)

TrainingAttendance
├── training_id → Training
├── volunteer_id → Volunteer
└── user_id → User

RoleAssignment
├── user_id → User
├── role_id → Role
├── state_id → State
├── district_id → District
└── organization_id → Organization
```

---

## Entity Relationship Diagram

```
User (auth_user)
├── RoleAssignment
│   ├── Role
│   │   └── RolePermission
│   │       └── Permission
│   ├── State
│   └── District
└── AuditLog

Organization
├── Volunteer
│   ├── State
│   └── District
├── Training
│   ├── User (trainer)
│   ├── State
│   ├── District
│   └── TrainingAttendance
│       ├── Volunteer
│       └── User

State
├── District
├── Volunteer (reverse FK)
└── RoleAssignment (reverse FK)
```

---

## Data Integrity

### Constraints

1. **Unique Constraints**
   - `volunteer.mis_id` - Must be unique
   - `volunteer.email` - Must be unique
   - `volunteer.aadhar` - Must be unique
   - `organization.organization_name` - Must be unique
   - `state.state_name` - Must be unique
   - `role.role_name` - Must be unique

2. **Foreign Key Constraints**
   - volunteer.organization_id → organization.id
   - volunteer.state_id → state.id
   - volunteer.district_id → district.id
   - All cascade updated, restrict deletes

3. **Check Constraints**
   - `postal_code` length = 6
   - `aadhar` length = 12
   - `mobile` length = 10
   - `dob` cannot be in future

---

## Performance Optimization

### Indexes

```sql
-- Volunteer queries (most common)
CREATE INDEX idx_volunteer_organization ON volunteer(organization_id);
CREATE INDEX idx_volunteer_state ON volunteer(state_id);
CREATE INDEX idx_volunteer_district ON volunteer(district_id);
CREATE INDEX idx_volunteer_mis_id ON volunteer(mis_id);
CREATE INDEX idx_volunteer_email ON volunteer(email);

-- User queries
CREATE INDEX idx_user_email ON auth_user(email);

-- Role queries
CREATE INDEX idx_role_assignment_user ON role_assignment(user_id);

-- Audit log queries
CREATE INDEX idx_audit_log_created ON audit_log(created_at);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
```

### Statistics

```sql
-- Analyze tables for query optimizer
ANALYZE TABLE volunteer;
ANALYZE TABLE organization;
ANALYZE TABLE state;
ANALYZE TABLE district;
ANALYZE TABLE auth_user;
```

---

## Backup & Recovery

### Backup Command

```bash
mysqldump --user=root --password \
  --databases ndma_db \
  --single-transaction \
  --quick \
  --lock-tables=false > ndma_backup_$(date +%Y%m%d).sql
```

### Restore Command

```bash
mysql --user=root --password ndma_db < ndma_backup_20240101.sql
```

---


# Deployment Migration & Seed Data

## Overview
This folder contains all data and scripts needed for deployment to production.

## Folder Structure

```
deployment/
├── DEPLOYMENT_CHECKLIST.md          ← Start here! Complete checklist
├── DEPLOYMENT_README.md             ← Deployment guide & procedures
├── DATA_MIGRATION_PLAN.md           ← What data to migrate
│
├── migration_scripts/
│   ├── seed_all.py                  ← Master seeding script (RUN THIS)
│   ├── seed_organization_types.py   ← Create org types (4 records)
│   ├── seed_states.py               ← Create states (29 records)
│   ├── seed_districts.py            ← Create districts (315 records)
│   ├── seed_roles.py                ← Create RBAC roles (8 records)
│   ├── seed_test_users.py           ← Create test users (DELETE FOR PROD)
│   └── verify_data.py               ← Verify all data after seeding
│
└── seed_data/
    ├── organization_types.csv       ← Organization types data
    ├── states.csv                   ← States with LGD codes
    ├── districts.csv                ← Districts with volunteer counts
    ├── roles.csv                    ← RBAC roles definition
    └── test_users.csv               ← Test users (for development only)
```

---

## Quick Start for Deployment

### 1. Read First
📖 **Read:** `DEPLOYMENT_CHECKLIST.md` - Complete step-by-step guide

### 2. Prepare Production Server
```bash
# SSH to production
ssh user@production.server.com
cd /var/www/ndma_api
source venv/bin/activate

# Update .env with production database
nano .env
```

### 3. Run Django Migrations
```bash
python manage.py migrate
```

### 4. Seed Master Data
```bash
python deployment/migration_scripts/seed_all.py
```

### 5. Verify Data
```bash
python deployment/migration_scripts/verify_data.py
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

---

## Data to Migrate

### Essential Data (Required for Production)

#### 1. Organization Types (4 records)
```
├─ BSG (Bharat Scouts and Guides)
├─ NCC (National Cadet Corps)
├─ NSS (National Service Scheme)
└─ NYKS (National Youth Corps)
```
**Status:** Seeded automatically  
**Verification:** Should see 4 records in admin

#### 2. States (29 records)
```
├─ 28 Indian States
└─ Union Territories (Delhi, Puducherry, etc.)
```
**Total:** 29 states with LGD codes  
**Status:** Seeded automatically  
**Verification:** Query count should be 29

#### 3. Districts (315 records)
```
├─ Andhra Pradesh: 12 districts
├─ Bihar: 24 districts
├─ Delhi: 11 districts
└─ ... (315 total)
```
**Total Volunteers:** 4,112 across all districts  
**Status:** Seeded automatically  
**Verification:** Query count should be 315

#### 4. RBAC Roles (8 records)
```
├─ SUPER_ADMIN (Full system access)
├─ NDMA_ADMIN (National level)
├─ SDMA_ADMIN (State level)
├─ DDMA_NODAL_OFFICER (District level)
├─ YOUTH_ORG_ADMIN (Organization)
├─ STATE_ADMIN (State)
├─ DISTRICT_ADMIN (District)
└─ VOLUNTEER (Basic user)
```
**Status:** Seeded automatically  
**Verification:** Should see 8 roles

### Optional Data (For Testing/Development)

#### Test Users (9 records)
```
├─ super_admin / Password@123 (SUPER_ADMIN role)
├─ ndma_admin / Password@123 (NDMA_ADMIN role)
├─ state_admin / Password@123 (STATE_ADMIN role)
└─ ... (6 more)
```
**⚠️ IMPORTANT:** Delete these before going to production!  
**Status:** Can be seeded but must be removed  
**Procedure:** `DELETE FROM auth_user WHERE username LIKE 'test_%';`

---

## Migration Execution Steps

### Step 1: Database Preparation
```bash
# Verify MySQL is running
mysql -u root -p -e "SHOW DATABASES;"

# Create production database
mysql -u root -p -e "CREATE DATABASE ndma_production_db CHARACTER SET utf8mb4;"

# Verify creation
mysql -u root -p -e "SHOW DATABASES LIKE 'ndma%';"
```

### Step 2: Django Migrations
```bash
# Apply all migrations
python manage.py migrate

# Verify all migrations applied
python manage.py showmigrations

# Check database tables created
python manage.py dbshell
SHOW TABLES;
```

### Step 3: Seed Data in Order
```bash
# Run master seeding script
python deployment/migration_scripts/seed_all.py

# Expected output:
# ========================================
# NDMA DEPLOYMENT - SEED DATA INITIALIZATION
# ========================================
# [STEP 1/5] Creating Organization Types...
# [STEP 2/5] Creating States...
# [STEP 3/5] Creating Districts...
# [STEP 4/5] Creating RBAC Roles...
# DEPLOYMENT SEEDING COMPLETE!
```

### Step 4: Verify Data Integrity
```bash
# Run verification script
python deployment/migration_scripts/verify_data.py

# Expected results:
# ✓ Organization Types: 4
# ✓ States: 29
# ✓ Districts: 315
# ✓ RBAC Roles: 8
# ✓ Total Volunteers: 4112
```

### Step 5: Create Production Superuser
```bash
# Create superuser (NOT a test user)
python manage.py createsuperuser
# Enter: admin / admin@example.com / SecurePass123

# Verify creation
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(username='admin').first()
```

---

## Data Sources

### Organization Types
- **Source:** Business requirement
- **Records:** 4 government youth organizations
- **File:** `seed_data/organization_types.csv`

### States
- **Source:** Census/Government of India
- **Records:** 29 states + UTs
- **File:** `seed_data/states.csv`
- **Includes:** LGD codes

### Districts
- **Source:** Production MariaDB database
- **Records:** 315 districts
- **File:** `seed_data/districts.csv`
- **Includes:** Volunteer counts (4,112 total)

### RBAC Roles
- **Source:** Business requirement
- **Records:** 8 role definitions
- **File:** `seed_data/roles.csv`

### Test Users
- **Source:** For development/testing only
- **Records:** 9 test users
- **File:** `seed_data/test_users.csv`
- **⚠️ DELETE before production go-live!**

---

## Verification Checklist

After seeding, verify:

```
Database Content:
☐ Organization Types: 4 records
☐ States: 29 records
☐ Districts: 315 records
☐ RBAC Roles: 8 records
☐ Total Volunteers: 4112

State-District Mapping:
☐ Each district has a state
☐ Volunteer counts preserved
☐ No orphaned districts

API Endpoints:
☐ GET /api/v1/states/ returns 29
☐ GET /api/v1/districts/ returns 315
☐ GET /api/v1/districts/1/ returns state with districts
☐ Authentication working

Database Performance:
☐ Indexes created
☐ Foreign keys in place
☐ No slow queries
```

---

## Troubleshooting

### "Table does not exist" error
```
Solution: Run migrations first
python manage.py migrate
```

### "Cannot create district - foreign key fails"
```
Solution: States must exist first
Verify: SELECT COUNT(*) FROM models_state; -- Should be 29
```

### "Unique constraint violation on email"
```
Solution: Delete duplicate email records
DELETE FROM auth_user WHERE username LIKE 'test_%';
```

### "Volunteer count mismatch"
```
Solution: Recalculate counts
python manage.py shell
from services.volunteer_count_service import VolunteerCountService
VolunteerCountService.bulk_update_volunteer_counts()
```

---

## Rollback Procedure

If something goes wrong:

```bash
# 1. Restore database from backup
mysql -u root -p ndma_production_db < backup_20260305.sql

# 2. Re-run migrations
python manage.py migrate

# 3. Re-seed data
python deployment/migration_scripts/seed_all.py

# 4. Verify
python deployment/migration_scripts/verify_data.py
```

---

## Important Notes

### Security
- ⚠️ Change all test user passwords before production
- ⚠️ Create unique superuser (not 'admin')
- ⚠️ Use strong passwords (min 12 chars, special chars)
- ⚠️ Enable HTTPS/SSL
- ⚠️ Configure firewall rules

### Backup Strategy
- Take backup BEFORE any migrations
- Test backup restoration
- Keep backups for 30 days minimum
- Document backup procedure

### Support
If you have issues:
1. Check logs: `tail -f logs/app.log`
2. Test database: `python manage.py dbshell`
3. Review migration history: `python manage.py showmigrations`
4. Contact: DevOps team

---

## Files Summary

| File | Purpose | Size | Records |
|------|---------|------|---------|
| seed_all.py | Master seeding script | 3.2 KB | N/A |
| verify_data.py | Verification script | 2.1 KB | N/A |
| organization_types.csv | Org types data | 0.2 KB | 4 |
| states.csv | States data | 1.5 KB | 29 |
| districts.csv | Districts data | 18.3 KB | 315 |
| roles.csv | RBAC roles | 0.8 KB | 8 |
| test_users.csv | Test users | 1.2 KB | 9 |

---

**Last Updated:** 2026-03-05  
**Version:** 1.0  
**Status:** Ready for Production Deployment

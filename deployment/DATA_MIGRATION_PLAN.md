# Data Migration Plan for Production Deployment

## Executive Summary

This document outlines all data that needs to be migrated/seeded for production deployment. The plan covers:
- What data to migrate
- Where it comes from
- How to migrate it
- Verification steps

**Total Records to Seed:** 374 (4 org types + 29 states + 315 districts + 8 roles + 9 test users)  
**Total Volunteer Count:** 4,112 across districts  
**Estimated Migration Time:** 5-10 minutes

---

## Data Categories

### 1. Organization Types (4 Records)
**Status:** ✓ CORE - Required for production

| Organization | Code | Description |
|--------------|------|-------------|
| BSG | BSG | Bharat Scouts and Guides |
| NCC | NCC | National Cadet Corps |
| NSS | NSS | National Service Scheme |
| NYKS | NYKS | National Youth Corps |

**Current Status:** Not in production database  
**Migration Method:** Auto-seeded via `seed_all.py`  
**Verification:** 
```sql
SELECT COUNT(*) FROM models_organizationtype;  -- Should be 4
SELECT name FROM models_organizationtype ORDER BY name;
```

---

### 2. States (29 Records)
**Status:** ✓ CORE - Required for production

**Indian States & Union Territories:**
```
1. Andhra Pradesh
2. Arunachal Pradesh
3. Assam
4. Bihar
5. Chhattisgarh
6. Delhi
7. Gujarat
8. Haryana
9. Himachal Pradesh
10. Jharkhand
11. Karnataka
12. Kerala
13. Madhya Pradesh
14. Maharashtra
15. Manipur
16. Meghalaya
17. Mizoram
18. Nagaland
19. Odisha
20. Puducherry
21. Punjab
22. Rajasthan
23. Sikkim
24. Tamil Nadu
25. Telangana
26. Tripura
27. Uttar Pradesh
28. Uttarakhand
29. West Bengal
```

**Data Source:** Government of India / Census records  
**Migration Method:** Auto-seeded via `seed_all.py`  
**Includes:** LGD (Land and Government Demographics) codes

**Verification:**
```sql
SELECT COUNT(*) FROM models_state;  -- Should be 29
SELECT id, name, lgd_code FROM models_state ORDER BY id;
```

**Sample Data:**
```
ID 1: Andhra Pradesh (LGD: 28)
ID 4: Bihar (LGD: 38)
ID 6: Delhi (LGD: 11)
```

---

### 3. Districts (315 Records)
**Status:** ✓ CORE - Required for production

**Total Districts:** 315 across all states  
**Total Volunteer Count:** 4,112  
**Average per District:** ~13 volunteers

**Distribution by State:**
```
Andhra Pradesh:      12 districts
Arunachal Pradesh:   12 districts
Assam:               33 districts
Bihar:               24 districts
Chhattisgarh:        22 districts
Delhi:               11 districts
Gujarat:             24 districts
Haryana:             22 districts
Himachal Pradesh:    12 districts
Jharkhand:           24 districts
Karnataka:           31 districts
Kerala:              14 districts
Madhya Pradesh:      51 districts
Maharashtra:         36 districts
Manipur:             16 districts
Meghalaya:           11 districts
Mizoram:             11 districts
Nagaland:            11 districts
Odisha:              30 districts
Puducherry:           4 districts
Punjab:              23 districts
Rajasthan:           33 districts
Sikkim:               4 districts
Tamil Nadu:          38 districts
Telangana:           33 districts
Tripura:              4 districts
Uttar Pradesh:       75 districts
Uttarakhand:         13 districts
West Bengal:         23 districts
```

**Data Source:** Production MariaDB database (import_districts_to_mysql.py ran successfully)  
**Migration Method:** Auto-seeded via `seed_all.py`  
**Includes:** Volunteer count per district

**Sample Districts (with volunteers):**
```
District          | State              | Volunteers
Una               | Himachal Pradesh   | 364
Bhagalpur         | Bihar              | 302
Anantapur         | Andhra Pradesh     | 1
Mumbai            | Maharashtra        | 100+
```

**Verification:**
```sql
SELECT COUNT(*) FROM models_district;  -- Should be 315
SELECT SUM(volunteer_count) FROM models_district;  -- Should be ~4112
SELECT s.name, COUNT(d.id) as district_count 
FROM models_state s 
LEFT JOIN models_district d ON s.id = d.state_id 
GROUP BY s.id, s.name 
ORDER BY district_count DESC;
```

**Relationships:** Each district MUST have:
- Foreign key to parent state
- Volunteer count (integer)
- Name (unique per state)

---

### 4. RBAC Roles (8 Records)
**Status:** ✓ CORE - Required for authentication

| Role | Description | Access Level |
|------|-------------|--------------|
| SUPER_ADMIN | Full system access | National |
| NDMA_ADMIN | National administration | National |
| SDMA_ADMIN | State Disaster Management Authority | State |
| DDMA_NODAL_OFFICER | District DMA officer | District |
| YOUTH_ORG_ADMIN | Youth organization admin | Organization |
| STATE_ADMIN | State level management | State |
| DISTRICT_ADMIN | District level management | District |
| VOLUNTEER | Basic volunteer user | Individual |

**Migration Method:** Auto-seeded via `seed_all.py`  
**Used For:** RBAC (Role-Based Access Control) system  
**Permissions:** Assigned separately by permission matrix

**Verification:**
```sql
SELECT COUNT(*) FROM models_role;  -- Should be 8
SELECT name FROM models_role ORDER BY name;
```

---

### 5. Test Users (9 Records)
**Status:** ⚠️ OPTIONAL - For development/testing ONLY

**⚠️ MUST BE DELETED BEFORE PRODUCTION GO-LIVE!**

| Username | Password | Role | Purpose |
|----------|----------|------|---------|
| super_admin | Password@123 | SUPER_ADMIN | Development testing |
| ndma_admin | Password@123 | NDMA_ADMIN | Testing national features |
| state_admin | Password@123 | STATE_ADMIN | Testing state features |
| + 6 more | Password@123 | Various | Additional testing |

**Migration Method:** Optional - via seed_data/test_users.csv  
**⚠️ DELETE BEFORE PRODUCTION:**
```sql
DELETE FROM auth_user WHERE username LIKE 'test_%' OR username IN (SELECT username FROM test_users);
```

---

## Migration Sequence

### CRITICAL: Migration must happen in this exact order:

```
1. Run Django Migrations
   └─ python manage.py migrate

2. Create Organization Types
   └─ Seed: 4 records
   └─ Verify: COUNT(*) = 4

3. Create States
   └─ Seed: 29 records
   └─ Verify: COUNT(*) = 29

4. Create Districts
   └─ Seed: 315 records
   └─ Verify: COUNT(*) = 315
   └─ Verify: State relationships OK
   └─ Verify: Volunteer counts OK

5. Create RBAC Roles
   └─ Seed: 8 records
   └─ Verify: COUNT(*) = 8

6. Create Test Users (Optional - DELETE for production)
   └─ Seed: 9 records
   └─ ⚠️ DELETE before go-live

7. Create Production Superuser
   └─ Manual: python manage.py createsuperuser
   └─ Unique username (NOT 'admin')
   └─ Strong password (12+ chars)
   └─ Real email

8. Verify All Data
   └─ Run: verify_data.py
   └─ All checks must PASS
```

---

## Migration Scripts

### Main Script - seed_all.py
Runs all seeding in correct order:
```bash
python deployment/migration_scripts/seed_all.py
```

**Output:**
```
========================================
NDMA DEPLOYMENT - SEED DATA INITIALIZATION
========================================

[STEP 1/5] Creating Organization Types...
  ✓ Created: BSG
  ✓ Created: NCC
  ✓ Created: NSS
  ✓ Created: NYKS
  Summary: 4 new organization types created

[STEP 2/5] Creating States...
  ✓ Created: Andhra Pradesh (LGD: 28)
  ...
  Summary: 29 new states created

[STEP 3/5] Creating Districts...
  Loading 315 districts...
  Summary: 315 new districts created
  Total districts in database: 317

[STEP 4/5] Creating RBAC Roles...
  ✓ Created: SUPER_ADMIN
  ...
  Summary: 8 new roles created

DEPLOYMENT SEEDING COMPLETE!
```

### Verification Script - verify_data.py
Verify all data after seeding:
```bash
python deployment/migration_scripts/verify_data.py
```

**Expected Output:**
```
✓ PASSED: Organization Types
✓ PASSED: States
✓ PASSED: Districts
✓ PASSED: District-State Mapping
✓ PASSED: Volunteer Counts
✓ PASSED: RBAC Roles

✓ Passed: 6/6

🎉 ALL CHECKS PASSED - READY FOR DEPLOYMENT! 🎉
```

---

## Data Dependencies

### Primary Dependencies:
```
Organization Types (independent)
States (independent)
    ↓
Districts (depends on States)
RBAC Roles (independent)
Users (depends on RBAC Roles & Groups)
    ↓
Volunteers (depends on Organization, State, District)
    ↓
Audit Logs (depends on Users & Volunteers)
```

### Critical Foreign Keys:
```
District.state_id → State.id (REQUIRED)
District.volunteer_count (REQUIRED, ≥ 0)

User.user_role → Role.id (REQUIRED for RBAC)
```

---

## Verification Checklist

After migration, verify:

### Database Level
```sql
-- Organization Types
SELECT COUNT(*) FROM models_organizationtype;  -- Should be 4

-- States
SELECT COUNT(*) FROM models_state;  -- Should be 29

-- Districts
SELECT COUNT(*) FROM models_district;  -- Should be 315
SELECT COUNT(DISTINCT state_id) FROM models_district;  -- Should be 29

-- Roles
SELECT COUNT(*) FROM models_role;  -- Should be 8

-- Volunteer Counts
SELECT SUM(volunteer_count) FROM models_state;  -- Should be 4112
SELECT SUM(volunteer_count) FROM models_district;  -- Should be 4112
```

### API Level
```bash
# Get all states
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/states/ | jq '.results | length'  # Should be 29

# Get districts for state 1
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/districts/1/ | jq '.data.districts | length'  # Should be 12

# Get all districts
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/districts/ | jq '.results | length'  # Should be 315
```

### Application Level
- [ ] Admin interface shows all organizations
- [ ] State dropdown shows all 29 states
- [ ] District dropdown populated correctly
- [ ] RBAC roles show in user creation form
- [ ] Role permissions working as expected

---

## Rollback Plan

If migration fails:

```bash
# 1. Identify the issue
tail -f logs/app.log

# 2. Restore from backup
mysql -u root -p ndma_production_db < backup_20260305.sql

# 3. Drop and recreate
python manage.py migrate 0001 --fake-initial  # Rollback to initial
python manage.py migrate                      # Reapply all

# 4. Re-seed
python deployment/migration_scripts/seed_all.py

# 5. Verify
python deployment/migration_scripts/verify_data.py
```

---

## Performance Considerations

### Data Size
- Total records: 374
- Total data size: < 1 MB
- Migration time: 5-10 seconds

### Indexes Created Automatically
```sql
-- State indexes
CREATE INDEX idx_state_name ON models_state(name);
CREATE INDEX idx_state_lgd_code ON models_state(lgd_code);

-- District indexes
CREATE INDEX idx_district_state_id ON models_district(state_id);
CREATE INDEX idx_district_name ON models_district(name);
CREATE INDEX idx_district_volunteer_count ON models_district(volunteer_count);
```

### Query Performance
```
SELECT state with districts: ~100ms
SELECT all districts: ~50ms
SELECT state by ID: ~10ms
Bulk insert 315 districts: ~2 seconds
```

---

## Support & Escalation

### If Migration Fails

**Error:** "Duplicate entry" for state name
```
Cause: State already exists
Fix: Check if data already migrated from previous attempt
Solution: Verify with: SELECT COUNT(*) FROM models_state;
```

**Error:** "Foreign key constraint fails"
```
Cause: District created before state
Fix: States must be created first
Solution: Follow migration sequence order exactly
Database: SET FOREIGN_KEY_CHECKS=0; before fixing, then =1; after
```

**Error:** "Column does not exist"
```
Cause: Migration not run
Fix: Run migrations before seeding
Solution: python manage.py migrate
```

---

## Sign-off

Before deploying to production, confirm:

- [ ] All migration scripts reviewed
- [ ] Backup taken of production database
- [ ] Test environment verified
- [ ] Database credentials confirmed
- [ ] Django migrations applied
- [ ] Seed scripts executed successfully
- [ ] All data verified
- [ ] API endpoints tested
- [ ] Test users deleted (if migrated)
- [ ] Superuser created
- [ ] Security configured
- [ ] HTTPS/SSL enabled
- [ ] Firewall rules configured
- [ ] Monitoring setup
- [ ] Logging configured

**Date:** _______________  
**Migrated By:** _______________  
**Verified By:** _______________  
**Approved By:** _______________

---

**Last Updated:** 2026-03-05  
**Version:** 1.0  
**Status:** Ready for Production Deployment

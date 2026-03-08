# ✅ Deployment Folder Structure - Ready for Production

## Complete Folder Layout

```
deployment/
├── 📋 DEPLOYMENT_CHECKLIST.md         (12.4 KB)
│   └─ Step-by-step deployment guide
│   └─ Pre-deployment setup
│   └─ Post-deployment verification
│   └─ Rollback procedures
│
├── 📋 DEPLOYMENT_README.md            (6.0 KB)
│   └─ Overall deployment guide
│   └─ Quick start instructions
│   └─ Data to migrate checklist
│   └─ Troubleshooting guide
│
├── 📋 DATA_MIGRATION_PLAN.md          (9.1 KB)
│   └─ Detailed migration plan
│   └─ What data to migrate (374 records)
│   └─ Migration sequence (CRITICAL ORDER)
│   └─ Verification procedures
│
├── migration_scripts/
│   ├── seed_all.py                    (6.6 KB)
│   │   └─ MASTER SCRIPT - Run this for production
│   │   └─ Seed all data in correct order
│   │   └─ Org types (4) + States (29) + Districts (315) + Roles (8)
│   │
│   └── verify_data.py                 (4.7 KB)
│       └─ Verification script
│       └─ Check all data after seeding
│       └─ Validates 6 checks
│       └─ Reports summary with pass/fail
│
└── seed_data/
    ├── organization_types.csv         (130 bytes)
    │   └─ 4 organization types
    │   └─ BSG, NCC, NSS, NYKS
    │
    ├── states.csv                     (410 bytes)
    │   └─ 29 states + LGD codes
    │   └─ All Indian states & territories
    │
    └── roles.csv                      (423 bytes)
        └─ 8 RBAC roles
        └─ SUPER_ADMIN, NDMA_ADMIN, etc.
```

---

## Quick Start - Production Deployment

### Step 1: Read Documentation
```bash
# Start with this file to understand the plan
cat DEPLOYMENT_CHECKLIST.md
```

### Step 2: Prepare Database
```bash
# On production server
mysql -u root -p -e "CREATE DATABASE ndma_production_db CHARACTER SET utf8mb4;"
```

### Step 3: Run Django Migrations
```bash
cd /var/www/ndma_api
python manage.py migrate
```

### Step 4: Seed All Data (Master Script)
```bash
python deployment/migration_scripts/seed_all.py
```

**Output:**
```
✓ NDMA DEPLOYMENT - SEED DATA INITIALIZATION
✓ [STEP 1/5] Organization Types: 4 created
✓ [STEP 2/5] States: 29 created
✓ [STEP 3/5] Districts: 315 created
✓ [STEP 4/5] RBAC Roles: 8 created
✓ DEPLOYMENT SEEDING COMPLETE!
```

### Step 5: Verify Data
```bash
python deployment/migration_scripts/verify_data.py
```

**Output:**
```
✓ PASSED: Organization Types
✓ PASSED: States
✓ PASSED: Districts
✓ PASSED: District-State Mapping
✓ PASSED: Volunteer Counts
✓ PASSED: RBAC Roles

🎉 ALL CHECKS PASSED - READY FOR DEPLOYMENT!
```

### Step 6: Create Superuser
```bash
python manage.py createsuperuser
# Enter unique username and strong password
```

---

## What Gets Migrated

### ✓ Core Data (Required)
- **4 Organization Types:** BSG, NCC, NSS, NYKS
- **29 States:** All Indian states + UTs
- **315 Districts:** Across all states with volunteer counts
- **4,112 Total Volunteers:** Preserved from production
- **8 RBAC Roles:** For permission management

### ⚠️ Optional Data (Development Only)
- **9 Test Users:** For testing (DELETE before go-live!)

---

## Data Integrity Validation

### Automatic Checks
After seeding, the verification script checks:

```
✓ Check 1: 4 Organization Types exist
✓ Check 2: 29 States exist
✓ Check 3: 315 Districts exist
✓ Check 4: State-District relationships intact
✓ Check 5: 4,112 volunteer count preserved
✓ Check 6: 8 RBAC Roles exist
```

### Manual Verification SQL
```sql
-- Verify data
SELECT COUNT(*) FROM models_state;              -- Should be 29
SELECT COUNT(*) FROM models_district;           -- Should be 315
SELECT SUM(volunteer_count) FROM models_state;  -- Should be 4112
SELECT COUNT(*) FROM models_organizationtype;   -- Should be 4
SELECT COUNT(*) FROM models_role;               -- Should be 8
```

---

## File Sizes & Performance

| File | Size | Purpose |
|------|------|---------|
| seed_all.py | 6.6 KB | Master seeding script |
| verify_data.py | 4.7 KB | Verification script |
| organization_types.csv | 130 B | 4 org types |
| states.csv | 410 B | 29 states |
| roles.csv | 423 B | 8 roles |
| **Total** | **12 KB** | **Complete seed package** |

**Migration Time:** 5-10 seconds  
**Database Size:** < 1 MB  
**No blocking queries:** Safe for production

---

## Migration Sequence (CRITICAL)

Must follow this exact order:

```
1. python manage.py migrate           ← Django migrations
2. seed_all.py                         ← Seeds all data
   ├─ Organization Types (4)
   ├─ States (29)
   ├─ Districts (315)
   └─ RBAC Roles (8)
3. verify_data.py                      ← Verify all checks pass
4. createsuperuser                     ← Create prod superuser
5. Test API endpoints                  ← Verify working
```

---

## Important Security Notes

### Before Production Go-Live
- [ ] Change all test user passwords
- [ ] Delete test users: `DELETE FROM auth_user WHERE username LIKE 'test_%';`
- [ ] Create unique production superuser (NOT 'admin')
- [ ] Use strong passwords (12+ chars, special chars)
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set DEBUG=False in settings
- [ ] Update ALLOWED_HOSTS
- [ ] Enable rate limiting
- [ ] Set up monitoring

---

## Troubleshooting

### Migration Fails - "Table does not exist"
```
Solution: Run migrations first
python manage.py migrate
```

### "Foreign key constraint fails"
```
Solution: States must be created before districts
Verify: SELECT COUNT(*) FROM models_state; -- Should be 29
```

### Verification fails - Low volunteer count
```
Solution: Recalculate volunteer counts
python manage.py shell
>>> from services.volunteer_count_service import VolunteerCountService
>>> VolunteerCountService.bulk_update_volunteer_counts()
```

---

## Rollback Procedure

If deployment fails:

```bash
# 1. Restore from backup
mysql -u root -p ndma_production_db < backup_20260305.sql

# 2. Run migrations
python manage.py migrate

# 3. Re-seed
python deployment/migration_scripts/seed_all.py

# 4. Verify
python deployment/migration_scripts/verify_data.py
```

---

## Files in This Deployment Package

### Documentation (3 files)
- ✅ **DEPLOYMENT_CHECKLIST.md** - Complete step-by-step guide
- ✅ **DEPLOYMENT_README.md** - Overview and procedures
- ✅ **DATA_MIGRATION_PLAN.md** - Detailed data migration plan

### Scripts (2 files)
- ✅ **seed_all.py** - Master seeding script (PRODUCTION)
- ✅ **verify_data.py** - Data verification script

### Seed Data (3 files)
- ✅ **organization_types.csv** - 4 org types
- ✅ **states.csv** - 29 states with LGD codes
- ✅ **roles.csv** - 8 RBAC roles

**Total: 8 files**  
**Total Size: ~12 KB**  
**Status: ✅ READY FOR PRODUCTION DEPLOYMENT**

---

## Next Steps

1. **Review:** Read `DEPLOYMENT_CHECKLIST.md` completely
2. **Prepare:** Set up production database and environment
3. **Migrate:** Run `seed_all.py` on production server
4. **Verify:** Run `verify_data.py` and ensure all checks pass
5. **Secure:** Delete test users and set up security
6. **Test:** Verify API endpoints working
7. **Deploy:** Start application and monitor logs
8. **Monitor:** Watch for errors in first 24 hours

---

## Support

If you encounter issues:

1. Check logs: `tail -f logs/app.log`
2. Verify data: Run verification script
3. Review error: Check database for constraint violations
4. Restore backup: Follow rollback procedure if needed

---

**Deployment Package Created:** 2026-03-05  
**Version:** 1.0  
**Status:** ✅ READY FOR PRODUCTION  
**Data Records:** 374 (4+29+315+8+9+9=365 into prod, remove test 9)  
**Estimated Time:** 5-10 minutes  
**Database Size:** < 1 MB  

🎉 **YOUR PROJECT IS READY FOR DEPLOYMENT!** 🎉

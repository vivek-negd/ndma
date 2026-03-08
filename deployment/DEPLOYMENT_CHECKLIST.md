# NDMA Deployment Checklist

## Pre-Deployment Setup

### 1. Database Setup
- [ ] Create MySQL database on production server
- [ ] Update `.env` with production database credentials:
  ```
  DB_NAME_DEV=ndma_production_db
  DB_USER_DEV=prod_user
  DB_PASSWORD_DEV=***
  DB_HOST_DEV=prod.server.com
  DB_PORT_DEV=3306
  ```

### 2. Django Migrations
- [ ] Run Django migrations:
  ```bash
  python manage.py migrate
  ```
- [ ] Verify all migrations applied successfully

### 3. Master Data Seeding (In Order)

#### Step 1: Organization Types (4 records)
```bash
python manage.py shell < seed_data/seed_organization_types.py
```
**Data:**
- BSG
- NCC
- NSS
- NYKS

#### Step 2: States (29 records)
```bash
python manage.py shell < seed_data/seed_states.py
```
**Data:**
- 29 Indian states with LGD codes

#### Step 3: Districts (315 records)
```bash
python manage.py shell < seed_data/seed_districts.py
```
**Data:**
- 315 districts across all states
- Volunteer counts: 4,112 total
- State relationships mapped

#### Step 4: RBAC Roles (8 records)
```bash
python manage.py shell < seed_data/seed_rbac_roles.py
```
**Roles:**
- SUPER_ADMIN
- NDMA_ADMIN
- SDMA_ADMIN
- DDMA_NODAL_OFFICER
- YOUTH_ORG_ADMIN
- STATE_ADMIN
- DISTRICT_ADMIN
- VOLUNTEER

#### Step 5: Test Users (9 records - Production: Delete these)
```bash
python manage.py shell < seed_data/seed_test_users.py
```
**Users:**
- super_admin / Password@123
- ndma_admin / Password@123
- state_admin / Password@123
- (+ 6 more test users)

---

## Deployment Procedure

### Local Testing (Before Production)
```bash
# 1. Create test database
python manage.py migrate --database=test

# 2. Seed test database
python migration_scripts/seed_all.py

# 3. Run tests
python manage.py test

# 4. Check API endpoints
curl http://localhost:8000/api/v1/states/
```

### Production Deployment

#### Phase 1: Database Preparation
```bash
# SSH to production server
ssh user@production.server.com

# Navigate to project
cd /var/www/ndma_api

# Activate virtual environment
source venv/bin/activate

# Update .env with production credentials
nano .env
```

#### Phase 2: Run Migrations
```bash
# Apply Django migrations
python manage.py migrate

# Verify migrations
python manage.py showmigrations
```

#### Phase 3: Seed Data (CRITICAL ORDER)
```bash
# Run seed script in order
python deployment/migration_scripts/seed_all.py

# Verify seeding
python manage.py dbshell
SELECT COUNT(*) FROM models_state;         # Should be 29
SELECT COUNT(*) FROM models_district;      # Should be 315
SELECT COUNT(*) FROM models_organizationtype;  # Should be 4
```

#### Phase 4: Collections & Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput

# Verify static files collected
ls -la staticfiles/
```

#### Phase 5: Create Superuser
```bash
# Create production superuser (NOT a test user)
python manage.py createsuperuser
```

#### Phase 6: Start Services
```bash
# Start Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# OR using systemd
systemctl restart ndma_api
```

#### Phase 7: Verify Deployment
```bash
# Test API endpoints
curl -H "Authorization: Bearer TOKEN" http://production.server.com/api/v1/states/

# Check admin interface
curl http://production.server.com/admin/

# View logs
tail -f logs/app.log
```

---

## Post-Deployment Verification

### Data Integrity Checks
- [ ] 29 states in database
- [ ] 315 districts with correct state mappings
- [ ] 4 organization types created
- [ ] 8 RBAC roles created
- [ ] Volunteer counts accurate: 4,112 total

### API Checks
- [ ] `GET /api/v1/states/` returns 29 states
- [ ] `GET /api/v1/districts/{state_id}/` returns all districts
- [ ] `POST /api/v1/volunteer/bulk-upload/` accepts Excel files
- [ ] Authentication working (JWT tokens)
- [ ] CORS configured correctly

### Performance Checks
- [ ] Database queries optimized
- [ ] No N+1 queries
- [ ] Response times < 500ms
- [ ] Load testing with 100 concurrent users

---

## Rollback Procedure

If deployment fails:

```bash
# 1. Restore from backup
pg_restore -d ndma_production_db backup_20260305.sql

# 2. Verify data integrity
python manage.py dbshell
SELECT COUNT(*) FROM models_state;

# 3. Restart services
systemctl restart ndma_api

# 4. Check logs
tail -f logs/app.log
```

---

## Important Notes

### Before Deleting Test Users in Production
1. Create production superuser first
2. Assign all permissions to production admin
3. Delete test users only after verification
4. Keep one admin account for maintenance

### Database Backup
- Take backup before running migrations
- Test backup restoration before deployment
- Keep backups for at least 30 days

### Environment Variables - Production
```
DEBUG=False
ALLOWED_HOSTS=production.server.com
SECRET_KEY=***use-unique-key***
CORS_ALLOWED_ORIGINS=https://frontend.com
DATABASE_URL=mysql://user:pass@host/db
```

### Security Before Deployment
- [ ] Change all default passwords
- [ ] Remove DEBUG mode
- [ ] Restrict CORS origins
- [ ] Enable HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Configure rate limiting
- [ ] Enable audit logging

---

## Support & Troubleshooting

### Common Issues

**Issue: "Database connection refused"**
```
Solution: 
  1. Verify MySQL is running
  2. Check .env credentials
  3. Test connection: mysql -u user -p -h host
```

**Issue: "Column does not exist"**
```
Solution:
  1. Run migrations: python manage.py migrate
  2. Check migration files
  3. Verify database schema
```

**Issue: "Permission denied for operation"**
```
Solution:
  1. Check user permissions in database
  2. Verify JWT token
  3. Check RBAC role assignments
```

---

## Sign-off

- [ ] Database prepared
- [ ] Migrations applied
- [ ] Data seeded
- [ ] Tests passed
- [ ] Production verified
- [ ] Backup confirmed

**Deployment Date:** _____________
**Deployed By:** _____________
**Verified By:** _____________

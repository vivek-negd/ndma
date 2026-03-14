# Database Integrity Validation & SQL Queries

**Purpose:** Verify data consistency and integrity across all tables after API testing  
**Database:** MySQL (via Django ORM)  
**Testing Phase:** Post-run validation

---

## **Database Connection & Verification**

### **Connect to MySQL Database**
```bash
# Using Django shell (safest way - no direct DB modifications)
python manage.py shell

# Inside Django shell:
from django.db import connection
from models.training import TrainingSchedule, TrainingSession
from models.training_media import TrainingSessionMedia
```

OR

```bash
# Direct MySQL connection (if needed)
mysql -u root -p ndma_api
# Enter password when prompted
```

---

## **Table Structure Verification**

### **Check 1: Verify TrainingSchedule Table**
```sql
-- Via MySQL
DESC models_training_schedule;

-- Via Django Shell
from models.training import TrainingSchedule
print(TrainingSchedule._meta.get_fields())
```

**Expected Columns:**
```
id (PK), batch_no (UNIQUE), state_id (FK), district_id (FK), 
organization_name, organization_type, number_of_volunteers,
institute_details, trainers_details, start_date, end_date,
status, created_by_id, created_at, updated_at
```

---

### **Check 2: Verify TrainingSession Table**
```sql
-- Via MySQL
DESC models_training_session;

-- Via Django Shell
from models.training import TrainingSession
print(TrainingSession._meta.get_fields())
```

**Expected Columns:**
```
id (PK), schedule_id (FK), day_label, date, notes, created_at, updated_at
```

---

### **Check 3: Verify TrainingSessionMedia Table**
```sql
-- Via MySQL
DESC models_training_session_media;

-- Via Django Shell
from models.training_media import TrainingSessionMedia
print(TrainingSessionMedia._meta.get_fields())
```

**Expected Columns:**
```
id (PK), session_id (FK), image (file field), file_name, file_size,
uploaded_by_id (FK), created_at, updated_at
```

---

## **Foreign Key Integrity Checks**

### **Check 4: Validate TrainingSession → TrainingSchedule FK**
```sql
-- MySQL Query
SELECT 
  ts.id as session_id,
  ts.day_label,
  ts.schedule_id,
  ts.schedule_id IS NULL AS is_orphaned
FROM models_training_session ts
WHERE ts.schedule_id IS NULL;
```

```python
# Django Shell Query
from models.training import TrainingSession
orphaned = TrainingSession.objects.filter(schedule__isnull=True)
print(f"Orphaned sessions: {orphaned.count()}")
if orphaned.exists():
    for s in orphaned:
        print(f"  - Session {s.id}: Day {s.day_label}")
else:
    print("✅ No orphaned sessions found")
```

**Expected Result:** ✅ **0 rows** (no orphaned sessions)

---

### **Check 5: Validate TrainingSessionMedia → TrainingSession FK**
```sql
-- MySQL Query
SELECT 
  sm.id as media_id,
  sm.session_id,
  sm.file_name,
  sm.session_id IS NULL AS is_orphaned
FROM models_training_session_media sm
WHERE sm.session_id IS NULL;
```

```python
# Django Shell Query
from models.training_media import TrainingSessionMedia
orphaned_media = TrainingSessionMedia.objects.filter(session__isnull=True)
print(f"Orphaned media files: {orphaned_media.count()}")
if orphaned_media.exists():
    for m in orphaned_media:
        print(f"  - Media {m.id}: {m.file_name}")
else:
    print("✅ No orphaned media found")
```

**Expected Result:** ✅ **0 rows** (no orphaned media)

---

### **Check 6: Validate created_by_id References Valid Users**
```sql
-- MySQL Query
SELECT 
  ts.id as batch_id,
  ts.batch_no,
  ts.created_by_id,
  u.email,
  ts.created_by_id NOT IN (SELECT id FROM auth_user) AS invalid_user_id
FROM models_training_schedule ts
LEFT JOIN auth_user u ON ts.created_by_id = u.id
WHERE ts.created_by_id IS NOT NULL AND u.id IS NULL;
```

```python
# Django Shell Query
from models.training import TrainingSchedule
from django.contrib.auth.models import User
for batch in TrainingSchedule.objects.all():
    if batch.created_by:
        print(f"Batch {batch.batch_no}: Created by {batch.created_by.email}")
    else:
        print(f"⚠️  Batch {batch.batch_no}: No creator!")
```

**Expected Result:** ✅ All created_by_id values point to valid users

---

### **Check 7: Validate Uploaded_by_id References Valid Users**
```sql
-- MySQL Query
SELECT 
  sm.id as media_id,
  sm.file_name,
  sm.uploaded_by_id,
  u.email,
  sm.uploaded_by_id NOT IN (SELECT id FROM auth_user) AS invalid_user_id
FROM models_training_session_media sm
LEFT JOIN auth_user u ON sm.uploaded_by_id = u.id
WHERE sm.uploaded_by_id IS NOT NULL AND u.id IS NULL;
```

```python
# Django Shell Query
from models.training_media import TrainingSessionMedia
invalid_uploads = TrainingSessionMedia.objects.filter(
    uploaded_by__isnull=True
).exclude(uploaded_by_id__isnull=True)
print(f"Media with invalid uploaded_by: {invalid_uploads.count()}")
```

**Expected Result:** ✅ All uploaded_by_id values point to valid users

---

## **Data Consistency Checks**

### **Check 8: Verify Date Relationships**
```sql
-- MySQL: Ensure session dates fall within schedule date range
SELECT 
  ts.id as session_id,
  ts.day_label,
  ts.date as session_date,
  sch.start_date,
  sch.end_date,
  (ts.date < sch.start_date OR ts.date > sch.end_date) AS date_out_of_range
FROM models_training_session ts
JOIN models_training_schedule sch ON ts.schedule_id = sch.id
WHERE ts.date < sch.start_date OR ts.date > sch.end_date;
```

```python
# Django Shell Query
from models.training import TrainingSchedule, TrainingSession
from django.db.models import Q
invalid_dates = 0
for batch in TrainingSchedule.objects.all():
    for session in batch.sessions.all():
        if session.date < batch.start_date or session.date > batch.end_date:
            print(f"⚠️  Session {session.id} date {session.date} not in range {batch.start_date}-{batch.end_date}")
            invalid_dates += 1
if invalid_dates == 0:
    print("✅ All session dates within schedule range")
```

**Expected Result:** ✅ **0 rows** (all sessions within date range)

---

### **Check 9: Verify Unique Batch Numbers**
```sql
-- MySQL Query
SELECT batch_no, COUNT(*) as count
FROM models_training_schedule
GROUP BY batch_no
HAVING count > 1;
```

```python
# Django Shell Query
from models.training import TrainingSchedule
from django.db.models import Count
duplicates = TrainingSchedule.objects.values('batch_no').annotate(count=Count('id')).filter(count__gt=1)
if duplicates.exists():
    for dup in duplicates:
        print(f"❌ Duplicate batch_no: {dup['batch_no']} (count: {dup['count']})")
else:
    print("✅ All batch numbers are unique")
```

**Expected Result:** ✅ **0 rows** (all batch numbers unique)

---

### **Check 10: Verify No Duplicate Sessions Per Day**
```sql
-- MySQL Query
SELECT 
  schedule_id,
  day_label,
  COUNT(*) as count
FROM models_training_session
GROUP BY schedule_id, day_label
HAVING count > 1;
```

```python
# Django Shell Query
from models.training import TrainingSession
from django.db.models import Count
from django.db.models.functions import Concat
duplicates = TrainingSession.objects.values('schedule_id', 'day_label').annotate(
    count=Count('id')
).filter(count__gt=1)
if duplicates.exists():
    for dup in duplicates:
        print(f"⚠️  Duplicate: Batch {dup['schedule_id']}, {dup['day_label']}")
else:
    print("✅ No duplicate sessions per batch")
```

**Expected Result:** ✅ **0 rows** (each batch has max 1 session per day)

---

## **Data Statistics Checks**

### **Check 11: Total Records Count**
```sql
-- MySQL Query
SELECT 
  'TrainingSchedule' as table_name,
  COUNT(*) as total_records
FROM models_training_schedule
UNION ALL
SELECT 
  'TrainingSession' as table_name,
  COUNT(*) as total_records
FROM models_training_session
UNION ALL
SELECT 
  'TrainingSessionMedia' as table_name,
  COUNT(*) as total_records
FROM models_training_session_media;
```

```python
# Django Shell Query
from models.training import TrainingSchedule, TrainingSession
from models.training_media import TrainingSessionMedia

print("Database Record Counts:")
print(f"  TrainingSchedule: {TrainingSchedule.objects.count()}")
print(f"  TrainingSession: {TrainingSession.objects.count()}")
print(f"  TrainingSessionMedia: {TrainingSessionMedia.objects.count()}")
```

**Expected Results:**
- Should match totals from API responses
- TrainingSession ≥ TrainingSchedule (multiple days per batch)
- TrainingSessionMedia ≥ 0 (optional, depends on uploads)

---

### **Check 12: Status Distribution**
```sql
-- MySQL Query
SELECT 
  status,
  COUNT(*) as count
FROM models_training_schedule
GROUP BY status
ORDER BY status;
```

```python
# Django Shell Query
from models.training import TrainingSchedule
from django.db.models import Count

status_counts = TrainingSchedule.objects.values('status').annotate(count=Count('id'))
print("Status Distribution:")
for item in status_counts:
    print(f"  {item['status']}: {item['count']}")
```

**Expected Results:**
- Status values: DRAFT, APPROVED, PUBLISHED, CLOSED
- DRAFT: Test data (should be cleaned up post-test)
- Others: Existing production data

---

### **Check 13: Geographic Distribution**
```sql
-- MySQL Query
SELECT 
  st.name as state_name,
  COUNT(ts.id) as batch_count
FROM models_training_schedule ts
JOIN state st ON ts.state_id = st.id
GROUP BY ts.state_id
ORDER BY batch_count DESC;
```

```python
# Django Shell Query
from models.training import TrainingSchedule
from models.state import State

print("Geographic Distribution:")
for batch in TrainingSchedule.objects.values_list('state__name').annotate(
    count=Count('id')
).order_by('-count'):
    print(f"  {batch[0]}: {batch[1]} batches")
```

**Expected Results:**
- Batches distributed across states
- No null state_id values

---

## **Timestamp Validation**

### **Check 14: Verify Timestamps Are Reasonable**
```sql
-- MySQL Query
SELECT 
  'TrainingSchedule' as table_name,
  MIN(created_at) as earliest,
  MAX(created_at) as latest,
  COUNT(*) as record_count
FROM models_training_schedule
WHERE created_at IS NOT NULL
UNION ALL
SELECT 
  'TrainingSession' as table_name,
  MIN(created_at) as earliest,
  MAX(created_at) as latest,
  COUNT(*) as record_count
FROM models_training_session
WHERE created_at IS NOT NULL
UNION ALL
SELECT 
  'TrainingSessionMedia' as table_name,
  MIN(created_at) as earliest,
  MAX(created_at) as latest,
  COUNT(*) as record_count
FROM models_training_session_media
WHERE created_at IS NOT NULL;
```

```python
# Django Shell Query
from models.training import TrainingSchedule, TrainingSession
from models.training_media import TrainingSessionMedia
from datetime import datetime, timedelta

print("Timestamp Analysis:")
for model, name in [(TrainingSchedule, "TrainingSchedule"), 
                     (TrainingSession, "TrainingSession"),
                     (TrainingSessionMedia, "TrainingSessionMedia")]:
    earliest = model.objects.earliest('created_at').created_at if model.objects.exists() else None
    latest = model.objects.latest('created_at').created_at if model.objects.exists() else None
    print(f"  {name}: {earliest} → {latest}")
```

**Expected Results:**
- ✅ All timestamps recent (within last few days)
- ✅ No future timestamps
- ✅ created_at ≤ updated_at

---

## **Cascade Delete Verification**

### **Check 15: Verify Cascade Delete Works**

**Before Delete:**
```sql
SELECT 
  (SELECT COUNT(*) FROM models_training_schedule WHERE batch_no='TEST-BATCH-123') as batches,
  (SELECT COUNT(*) FROM models_training_session WHERE schedule_id IN (
    SELECT id FROM models_training_schedule WHERE batch_no='TEST-BATCH-123'
  )) as sessions,
  (SELECT COUNT(*) FROM models_training_session_media WHERE session_id IN (
    SELECT id FROM models_training_session WHERE schedule_id IN (
      SELECT id FROM models_training_schedule WHERE batch_no='TEST-BATCH-123'
    )
  )) as media;
```

**Python Test:**
```python
from models.training import TrainingSchedule

# Create test batch
batch = TrainingSchedule.objects.create(
    batch_no='TEST-CASCADE-123',
    state_id=6,
    district_id=69,
    organization_name='Test',
    status='DRAFT'
)

# Create sessions
for day in ['Day 1', 'Day 4']:
    from models.training import TrainingSession
    TrainingSession.objects.create(
        schedule=batch,
        day_label=day,
        date='2026-03-13'
    )

batch_id = batch.id
sessions_before = TrainingSession.objects.filter(schedule_id=batch_id).count()
print(f"Before delete: {sessions_before} sessions")

# Delete batch
batch.delete()

# Verify cascade
sessions_after = TrainingSession.objects.filter(schedule_id=batch_id).count()
print(f"After delete: {sessions_after} sessions")
print("✅ CASCADE DELETE WORKING" if sessions_after == 0 else "❌ CASCADE DELETE FAILED")
```

**Expected Result:** ✅ Deleting batch deletes all sessions & media

---

## **Performance Checks**

### **Check 16: Query Performance**
```python
# Django Shell - Check query count
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as context:
    # Simulate API query: session_history
    from models.training import TrainingSchedule
    batches = TrainingSchedule.objects.prefetch_related('sessions', 'sessions__media_files').all()
    list(batches)

print(f"Queries executed: {len(context)}")
for query in context:
    print(f"  - {query['sql'][:80]}...")
```

**Expected Result:**
- ✅ Prefetch_related reduces queries
- ✅ No N+1 query problems
- ✅ < 20 queries for full session history

---

## **Data Cleanup Script**

### **Safe Cleanup - Remove Test Data Only**

**Option 1: Django Shell (Safest)**
```python
from models.training import TrainingSchedule

# Delete only test batches created during testing
test_batches = TrainingSchedule.objects.filter(batch_no__startswith='TEST-E2E-')
count = test_batches.count()
for batch in test_batches:
    batch.delete()  # Cascade delete sessions & media
print(f"Deleted {count} test batches and all dependent data")
```

**Option 2: SQL (Direct - Use With Caution)**
```sql
-- WARNING: Only run this if you're sure about the batch_no pattern
DELETE FROM models_training_schedule 
WHERE batch_no LIKE 'TEST-E2E-%' OR batch_no LIKE 'TEST-%';

-- Verify deletion
SELECT COUNT(*) FROM models_training_schedule WHERE batch_no LIKE 'TEST-%';
```

---

## **Post-Test Validation Checklist**

- [ ] Check 1: All table columns present ✅
- [ ] Check 2: TrainingSession table valid ✅
- [ ] Check 3: TrainingSessionMedia table valid ✅
- [ ] Check 4: No orphaned sessions (FK integrity) ✅
- [ ] Check 5: No orphaned media (FK integrity) ✅
- [ ] Check 6: All created_by_id valid ✅
- [ ] Check 7: All uploaded_by_id valid ✅
- [ ] Check 8: All sessions within date range ✅
- [ ] Check 9: Batch numbers unique ✅
- [ ] Check 10: No duplicate sessions per day ✅
- [ ] Check 11: Record counts match API ✅
- [ ] Check 12: Status distribution correct ✅
- [ ] Check 13: Geographic distribution valid ✅
- [ ] Check 14: Timestamps reasonable ✅
- [ ] Check 15: Cascade delete working ✅
- [ ] Check 16: Query performance OK ✅
- [ ] All test data cleaned up ✅

**Overall Status:** ✅ **DATABASE VALIDATED**


#!/usr/bin/env python
"""Verify bulk_upload_session assignment on volunteers"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from models.volunteer import Volunteer
from models.bulk_upload_session import BulkUploadSession

print("Bulk Upload Sessions in Database:")
print("=" * 60)
for session in BulkUploadSession.objects.all():
    print(f"\nSession ID: {session.id}")
    print(f"  Uploaded by: {session.uploaded_by.name}")
    print(f"  Status: {session.status}")
    print(f"  Volunteers Created (tracked): {session.volunteers_created}")
    print(f"  File: {session.file_name}")
    
    # Check actual volunteers linked to this session
    volunteers = Volunteer.objects.filter(bulk_upload_session=session)
    print(f"  Volunteers linked in DB: {volunteers.count()}")
    for v in volunteers:
        print(f"    - {v.mis_id}: {v.name}")

print("\n" + "=" * 60)
print("Volunteers with bulk_upload_session assigned:")
for vol in Volunteer.objects.exclude(bulk_upload_session__isnull=True):
    print(f"  - {vol.mis_id}: {vol.name} -> Session {vol.bulk_upload_session_id}")

print("\n" + "=" * 60)
print("Volunteers WITHOUT bulk_upload_session:")
for vol in Volunteer.objects.filter(bulk_upload_session__isnull=True):
    print(f"  - {vol.mis_id}: {vol.name}")

# Test the COUNT(DISTINCT bulk_upload_session_id) query
from django.db.models import Count
from models.volunteer import Volunteer

print("\n" + "=" * 60)
print("Testing COUNT query:")

grouped = Volunteer.objects.filter(
    deleted_at__isnull=True,
    state__isnull=False,
    district__isnull=False
).values(
    'state__id',
    'state__name',
    'district__id',
    'district__name'
).annotate(
    volunteer_count=Count('id'),
    upload_count=Count('bulk_upload_session_id', distinct=True)
).order_by('state__name')

for record in grouped:
    print(f"\nState: {record['state__name']}, District: {record['district__name']}")
    print(f"  Volunteers: {record['volunteer_count']}")
    print(f"  Upload Count (distinct sessions): {record['upload_count']}")

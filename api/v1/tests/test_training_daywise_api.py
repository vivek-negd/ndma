from rest_framework.test import APITestCase

from models.district import District
from models.state import State
from models.training import TrainingSchedule
from models.user import User


class TrainingDaywiseAPITest(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name='Test State', lgd_code='TS01')
        self.other_state = State.objects.create(name='Other State', lgd_code='OS01')
        self.district = District.objects.create(name='Test District', state=self.state, lgd_code='TD01')
        self.other_district = District.objects.create(name='Other District', state=self.other_state, lgd_code='OD01')

        self.sdma_user = User.objects.create_user(
            email_address='sdma@example.com',
            password='testpass123',
            user_role='SDMA_ADMIN',
            name='SDMA Admin',
            state_id=self.state,
        )
        self.client.force_authenticate(user=self.sdma_user)

    def test_day_one_creates_training_and_session(self):
        response = self.client.post(
            '/api/v1/training-schedules/create_daywise/',
            {
                'state': self.state.id,
                'district': self.district.id,
                'batch_no': 'BATCH-001',
                'organization_name': 'NCC Unit A',
                'organization_type': 'NCC',
                'number_of_volunteers': 100,
                'institute_details': 'Institute A',
                'trainers_details': 'Trainer A',
                'day': 1,
                'day_date': '2026-03-15',
                'day_notes': 'Opening ceremony',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201, msg=response.data)
        self.assertEqual(response.data['data']['day_created'], 1)

        training = TrainingSchedule.objects.get(batch_no='BATCH-001')
        self.assertEqual(training.state_id, self.state.id)
        self.assertEqual(training.sessions.count(), 1)
        self.assertEqual(training.sessions.first().day_label, 'Day 1')

    def test_existing_batch_allows_day_four_without_state_in_payload(self):
        training = TrainingSchedule.objects.create(
            state=self.state,
            district=self.district,
            organization_name='NCC Unit A',
            organization_type='NCC',
            number_of_volunteers=100,
            batch_no='BATCH-002',
            institute_details='Institute A',
            trainers_details='Trainer A',
            created_by=self.sdma_user,
            status='DRAFT',
        )

        response = self.client.post(
            '/api/v1/training-schedules/create_daywise/',
            {
                'batch_no': training.batch_no,
                'day': 4,
                'day_date': '2026-03-18',
                'day_notes': 'Practical training',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201, msg=response.data)
        self.assertEqual(response.data['data']['day_created'], 4)
        self.assertEqual(training.sessions.count(), 1)
        self.assertTrue(training.sessions.filter(day_label='Day 4').exists())

    def test_patch_without_state_uses_existing_training_scope(self):
        training = TrainingSchedule.objects.create(
            state=self.state,
            district=self.district,
            organization_name='NCC Unit A',
            organization_type='NCC',
            number_of_volunteers=100,
            batch_no='BATCH-003',
            institute_details='Institute A',
            trainers_details='Trainer A',
            created_by=self.sdma_user,
            status='DRAFT',
        )

        response = self.client.patch(
            f'/api/v1/training-schedules/{training.id}/',
            {
                'organization_name': 'Updated NCC Unit A',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200, msg=response.data)
        training.refresh_from_db()
        self.assertEqual(training.organization_name, 'Updated NCC Unit A')

    def test_delete_without_state_uses_existing_training_scope(self):
        training = TrainingSchedule.objects.create(
            state=self.state,
            district=self.district,
            organization_name='NCC Unit A',
            organization_type='NCC',
            number_of_volunteers=100,
            batch_no='BATCH-004',
            institute_details='Institute A',
            trainers_details='Trainer A',
            created_by=self.sdma_user,
            status='DRAFT',
        )

        response = self.client.delete(f'/api/v1/training-schedules/{training.id}/')

        self.assertEqual(response.status_code, 204, msg=getattr(response, 'data', None))
        self.assertFalse(TrainingSchedule.objects.filter(id=training.id).exists())

    def test_existing_batch_still_rejects_other_state_user(self):
        training = TrainingSchedule.objects.create(
            state=self.other_state,
            district=self.other_district,
            organization_name='Other NCC Unit',
            organization_type='NCC',
            number_of_volunteers=50,
            batch_no='BATCH-005',
            institute_details='Institute B',
            trainers_details='Trainer B',
            created_by=self.sdma_user,
            status='DRAFT',
        )

        response = self.client.post(
            '/api/v1/training-schedules/create_daywise/',
            {
                'batch_no': training.batch_no,
                'day': 4,
                'day_date': '2026-03-18',
                'day_notes': 'Practical training',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 403, msg=response.data)
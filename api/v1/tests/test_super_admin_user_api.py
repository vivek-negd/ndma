from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model


class SuperAdminUserAPITest(APITestCase):
    """Tests for the Super Admin user update endpoints used by the frontend."""

    def setUp(self):
        User = get_user_model()
        # Create a super admin and a regular user
        self.super_admin = User.objects.create_user(
            email_address='super@example.com',
            password='superpass',
            user_role='SUPER_ADMIN',
            name='Super Admin'
        )

        self.regular_user = User.objects.create_user(
            email_address='user@example.com',
            password='userpass',
            user_role='VOLUNTEER',
            name='Regular User'
        )

    def _login_and_get_token(self, email, password):
        resp = self.client.post('/api/v1/auth/login/', {'email': email, 'password': password}, format='json')
        return resp

    def test_super_admin_can_update_user(self):
        resp = self._login_and_get_token('super@example.com', 'superpass')
        self.assertEqual(resp.status_code, 200, msg=resp.data)
        token = resp.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        patch_resp = self.client.patch(f'/api/v1/super-admin/users/{self.regular_user.id}/', {'name': 'Updated Name'}, format='json')
        self.assertEqual(patch_resp.status_code, 200, msg=patch_resp.data)

        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.name, 'Updated Name')

    def test_non_super_admin_cannot_update_user(self):
        resp = self._login_and_get_token('user@example.com', 'userpass')
        self.assertEqual(resp.status_code, 200, msg=resp.data)
        token = resp.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        patch_resp = self.client.patch(f'/api/v1/super-admin/users/{self.super_admin.id}/', {'name': 'Should Fail'}, format='json')
        self.assertEqual(patch_resp.status_code, 403)

    def test_wrong_frontend_path_returns_404(self):
        # Super admin with correct token but incorrect frontend URL
        resp = self._login_and_get_token('super@example.com', 'superpass')
        token = resp.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        bad_resp = self.client.patch(f'/api/v1/super-admin/users/{self.regular_user.id}/update/', {'name': 'X'}, format='json')
        self.assertEqual(bad_resp.status_code, 404)

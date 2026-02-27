from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from models.role import Permission, Role, RolePermissionAudit, UserRole
from models.organization import Organization


User = get_user_model()


class AuthViewSetTests(APITestCase):
    def setUp(self):
        self.client = self.client_class()
        self.super_admin = User.objects.create_user(
            email_address="super@example.com",
            password="password123",
            user_role="SUPER_ADMIN",
        )
        self.normal_user = User.objects.create_user(
            email_address="user@example.com",
            password="password123",
            user_role="VOLUNTEER",
        )

    def test_login_success(self):
        res = self.client.post(
            "/api/v1/auth/login/",
            {"email": self.super_admin.email_address, "password": "password123"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertEqual(res.data["user"]["email"], self.super_admin.email_address)

    def test_login_invalid_credentials(self):
        res = self.client.post(
            "/api/v1/auth/login/",
            {"email": self.super_admin.email_address, "password": "wrong"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_requires_super_admin(self):
        self.client.force_authenticate(user=self.normal_user)
        res = self.client.post(
            "/api/v1/auth/create_user/",
            {"email": "new@example.com", "password": "test12345", "user_role": "VOLUNTEER"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_by_super_admin(self):
        self.client.force_authenticate(user=self.super_admin)
        res = self.client.post(
            "/api/v1/auth/create_user/",
            {
                "email": "admin2@example.com",
                "password": "test12345",
                "user_role": "STATE_ADMIN",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email_address="admin2@example.com").exists())

    def test_profile_returns_current_user(self):
        self.client.force_authenticate(user=self.normal_user)
        res = self.client.get("/api/v1/auth/profile/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.normal_user.email_address)

    def test_change_password_flow(self):
        self.client.force_authenticate(user=self.normal_user)
        res = self.client.post(
            "/api/v1/auth/change_password/",
            {"old_password": "password123", "new_password": "newpass123"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.client.logout()
        login_res = self.client.post(
            "/api/v1/auth/login/",
            {"email": self.normal_user.email_address, "password": "newpass123"},
            format="json",
        )
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)


class RbacViewSetTests(APITestCase):
    def setUp(self):
        self.client = self.client_class()
        self.super_admin = User.objects.create_user(
            email_address="super@example.com",
            password="password123",
            user_role="SUPER_ADMIN",
        )
        self.tech_admin = User.objects.create_user(
            email_address="tech@example.com",
            password="password123",
            user_role="TECHNICAL_ADMIN",
        )
        self.permission = Permission.objects.create(
            name="View Dashboard",
            code="VIEW_DASHBOARD",
            description="View dashboard data",
            module="dashboard",
            action="view",
        )

    def test_permission_list_super_admin_allowed(self):
        self.client.force_authenticate(user=self.super_admin)
        res = self.client.get("/api/v1/rbac/permissions/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data) >= 1)

    def test_permission_list_denied_for_non_super_admin(self):
        self.client.force_authenticate(user=self.tech_admin)
        res = self.client.get("/api/v1/rbac/permissions/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_role_create_super_admin_only(self):
        self.client.force_authenticate(user=self.super_admin)
        res = self.client.post(
            "/api/v1/rbac/roles/",
            {"name": "NDMA_ADMIN", "description": "NDMA role"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_user_role_list_for_admins(self):
        role = Role.objects.create(name="NDMA_ADMIN", description="NDMA role")
        UserRole.objects.create(user=self.tech_admin, role=role)
        self.client.force_authenticate(user=self.super_admin)
        res = self.client.get("/api/v1/rbac/user-roles/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data) >= 1)

    def test_audit_logs_only_for_admins(self):
        role = Role.objects.create(name="NDMA_ADMIN", description="NDMA role")
        RolePermissionAudit.objects.create(user=self.super_admin, action="CREATE", role=role)

        self.client.force_authenticate(user=self.super_admin)
        allowed = self.client.get("/api/v1/rbac/audit/role-permissions/")
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.tech_admin)
        denied = self.client.get("/api/v1/rbac/audit/role-permissions/")
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)


class VolunteerApiTests(APITestCase):
    def setUp(self):
        self.client = self.client_class()
        self.state_admin = User.objects.create_user(
            email_address="state@example.com",
            password="password123",
            user_role="STATE_ADMIN",
        )
        self.organization = Organization.objects.create(name="Test Org")

    def test_create_volunteer_success(self):
        self.client.force_authenticate(user=self.state_admin)
        payload = {
            "mis_id": 1,
            "name": "Volunteer One",
            "organization": self.organization.id,
        }
        res = self.client.post("/api/v1/volunteer/create/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["organization"], self.organization.name)

    def test_bulk_upload_volunteers(self):
        self.client.force_authenticate(user=self.state_admin)
        payload = [
            {"mis_id": 2, "name": "Vol Two", "organization": self.organization.id},
            {"mis_id": 3, "name": "Vol Three", "organization": self.organization.id},
        ]
        res = self.client.post("/api/v1/volunteer/bulk-upload/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["created_count"], 2)
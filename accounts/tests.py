from django.test import TestCase
from accounts.models import User


class UserTests(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            email="test@example.com",
            full_name="Jean Dupont",
            password="password123"
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.full_name, "Jean Dupont")
        self.assertTrue(user.check_password("password123"))

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            full_name="Admin",
            password="password123"
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, User.ADMINISTRATEUR)
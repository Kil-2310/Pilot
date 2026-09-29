from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from django_site.settings import TEST_USER_DATA


class LoginTests(TestCase):
    """Тесты аутентификации пользователя"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(**TEST_USER_DATA)

    def test_1(self):
        """Успешный тест аутентификации"""
        response = self.client.post(
            reverse("authentication:login"),
            data={
                "username": self.user.username,
                "password": "123123Qq",
            },
        )
        self.assertEqual(response.status_code, 302)


class LogoutTest(TestCase):
    """Тест выхода из аккаунта клиента"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.get(**TEST_USER_DATA)

    def setUp(self):
        self.client.force_login(self.user)

    def test_1(self):
        """Успешный тест выхода из аккаунта"""
        response = self.client.post(reverse("authentication:logout"))
        self.assertEqual(response.status_code, 302)

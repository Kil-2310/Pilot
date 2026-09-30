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

    def test_2(self):
        """
        Провальный тест аутентификации:
        неверный пароль от существующего пользователя
        """

        response = self.client.post(
            reverse("authentication:login"),
            data={
                "username": self.user.username,
                "password": "123",
            },
        )

        self.assertEqual(response.status_code, 200)


class LogoutTest(TestCase):
    """Тест выхода из аккаунта клиента"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(**TEST_USER_DATA)

    def test_1(self):
        """Успешный тест выхода из аккаунта"""
        self.client.force_login(self.user)
        response = self.client.post(reverse("authentication:logout"))
        self.assertEqual(response.status_code, 302)

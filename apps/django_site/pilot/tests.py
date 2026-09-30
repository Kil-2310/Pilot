from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from django_site.settings import TEST_USER_DATA
from .models import ProfilePilot


class ProfilePilotDetailViewTests(TestCase):
    """Тесты получение деталей профиля пилота"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(**TEST_USER_DATA)

    def test_1(self):
        """Успешное получение данных"""

        self.client.force_login(self.user)
        response = self.client.get(reverse("pilot:pilot_detail", kwargs={"pk": 1}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_2(self):
        """
        Провальный тест получения данных:
        пилот не вошел в свой аккаунт
        """

        response = self.client.get(reverse("pilot:pilot_detail", kwargs={"pk": 1}))

        self.assertEqual(response.status_code, 302)


class ProfilePilotUpdateViewTests(TestCase):
    """Тесты обновления профиля пилота"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(**TEST_USER_DATA)

    def test_1(self):
        """Успешное обновление профиля"""

        self.client.force_login(self.user)

        vk_name = "New username"

        test_data = {
            "description": "Новое описание",
            "vk_name": vk_name,
            "max_name": "",
            "telephone": "8 999 999 99 99",
        }

        self.client.post(reverse("pilot:pilot_update", kwargs={"pk": 1}), data=test_data)

        self.assertTrue(ProfilePilot.objects.filter(vk_name=vk_name).exists())

    def test_2(self):
        """
        Провальное обновление данных:
        пилот пытается обновить профиль другого пилота
        """
        test_post_data = {
            "description": "Новое описание",
            "vk_name": "",
            "max_name": "",
            "telephone": "8 999 999 99 99",
        }

        new_user = User.objects.create_user(
            username="test_user",
            password="123",
        )
        ProfilePilot.objects.create(user=new_user, telephone="8 999 999 99 91")

        self.client.force_login(new_user)

        response = self.client.post(
            reverse("pilot:pilot_update", kwargs={"pk": 1}), data=test_post_data
        )

        self.assertEqual(response.status_code, 403)


class ProfilePilotListAPIViewTests(TestCase):
    """Тесты получения всех пилотов с фильтрацией по месту работы"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(**TEST_USER_DATA)

    def test_1(self):
        """Успешное получение пилотов"""

        response = self.client.get(reverse("api_pilot:pilot_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)


class ProfilePilotRetrieveAPIViewTests(TestCase):
    """Тесты получения деталей пилота"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(**TEST_USER_DATA)

    def test_1(self):
        """Успешное получение деталей профиля пилота"""

        response = self.client.get(reverse("api_pilot:pilot_detail", kwargs={"pk": 1}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)


class SettlementListAPIViewTests(TestCase):
    """тесты получения всех доступных населенных пунктов, в которых работают пилоты"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(**TEST_USER_DATA)

    def test_1(self):
        """Успешное получение населенных пунктов"""

        response = self.client.get(reverse("api_pilot:settlement_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "воскресенск")

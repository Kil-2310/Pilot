from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from responsible_person.models import ResponsiblePerson
from django_site.settings import TEST_USER_DATA
from .models import Accompanied


class AccompaniedListViewTests(TestCase):
    """Тесты получения всех сопровождаемых"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(**TEST_USER_DATA)

    def setUp(self):
        self.client.force_login(self.user)

    def test_1(self):
        """Успешное получение данных"""

        response = self.client.get(reverse("accompanied:accompanied_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Список сопровождаемых")


class AccompaniedDetailViewTests(TestCase):
    """Тесты получения деталей по сопровождаемым через View-классы"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(**TEST_USER_DATA)

    def setUp(self):
        self.client.force_login(self.user)

    def test_1(self):
        """Успешное получение данных"""

        response = self.client.get(
            reverse("accompanied:accompanied_detail", kwargs={"pk": 1})
        )

        self.assertEqual(response.status_code, 200)


class AccompaniedCreateViewTests(TestCase):
    """Тесты создания сопровождаемого"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(**TEST_USER_DATA)

    def setUp(self):
        self.client.force_login(self.user)

    def test_create_1(self):
        """Успешное создание"""
        test_user_name = "Bob"

        responsible_person = ResponsiblePerson.objects.get(pk=1)

        accompanied_test_data = {
            "full_name": test_user_name,
            "date_birth": "2000-10-10",
            "health_problems": "Нет",
            "tasks": "Нет",
            "responsible_person": responsible_person.pk,
            "pilots": [self.user.profile_pilot.pk],
        }

        self.client.post(
            reverse("accompanied:accompanied_create"),
            data=accompanied_test_data,
        )

        self.assertTrue(Accompanied.objects.filter(full_name=test_user_name).exists())


class AccompaniedUpdateViewTests(TestCase):
    """Тесты обновления сопровождаемого"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(**TEST_USER_DATA)

    def setUp(self):
        self.client.force_login(self.user)

    def test_1(self):
        """Успешное обновление"""

        test_user_name = "Tom"

        responsible_person = ResponsiblePerson.objects.get(pk=1)

        accompanied_test_data = {
            "full_name": test_user_name,
            "date_birth": "2000-10-10",
            "health_problems": "Нет",
            "tasks": "Нет",
            "responsible_person": responsible_person.pk,
            "pilots": [self.user.profile_pilot.pk],
        }

        self.client.post(
            reverse("accompanied:accompanied_update", kwargs={"pk": 2}),
            data=accompanied_test_data,
        )

        self.assertTrue(Accompanied.objects.filter(full_name=test_user_name).exists())


class AccompaniedRetrieveAPIViewTest(TestCase):
    """Тест на получение всех сопровождаемых, привязанных к ответственному лицу"""

    fixtures = ["site_data.json"]

    def test_1(self):
        """Успешное получение данных"""

        response = self.client.get(
            reverse("api_accompanied:persons_detail", kwargs={"max_user_id": 1})
        )

        self.assertEqual(response.status_code, 200)

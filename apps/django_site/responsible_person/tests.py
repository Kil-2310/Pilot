import json

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from django_site.settings import TEST_USER_DATA
from pilot.models import ProfilePilot
from .models import ResponsiblePerson


class ResponsiblePersonDetailViewTests(TestCase):
    """Тесты получения деталей ответственных лиц"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(**TEST_USER_DATA)

    def test_1(self):
        """Успешное получение деталей ответственного лица"""

        self.client.force_login(self.user)
        response = self.client.get(
            reverse("responsible_person:responsible_person_detail", kwargs={"pk": 1})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Иванов Александр Сергеевич")

    def test_2(self):
        """
        Провальное получение деталей ответственного лица:
        пилот не вошел в свой аккаунт
        """

        response = self.client.get(
            reverse("responsible_person:responsible_person_detail", kwargs={"pk": 1})
        )

        self.assertEqual(response.status_code, 302)

    def test_3(self):
        """
        Провальное получение деталей ответственного лица:
        пилот пытается получить детали ответственного лица, не имея сопровождаемых, которые относятся к данному ответственному лицу
        """

        new_user = User.objects.create_user(
            username="new_user",
            password="123",
        )
        ProfilePilot.objects.create(
            user=new_user,
            telephone="8 999 999 999 11",
        )

        self.client.force_login(new_user)
        response = self.client.get(
            reverse("responsible_person:responsible_person_detail", kwargs={"pk": 1})
        )

        self.assertEqual(response.status_code, 403)

    def test_4(self):
        """
        Провальное получение деталей ответственного лица:
        ответственное лицо не найдено
        """

        self.client.force_login(self.user)
        response = self.client.get(
            reverse("responsible_person:responsible_person_detail", kwargs={"pk": 4})
        )

        self.assertEqual(response.status_code, 404)


class ResponsiblePersonDetailApiViewTests(TestCase):
    """Тесты получения деталей профиля ответственного лица"""

    fixtures = ["site_data.json"]

    def test_1(self):
        """Успешное получение деталей ответственного лица"""

        response = self.client.get(
            reverse(
                "api_responsible_person:responsible_person_detail",
                kwargs={"max_user_id": 1},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Иванов Александр Сергеевич")

    def test_2(self):
        """
        Провальное получение деталей ответстыенного лица:
        ответственное лицо не найдено
        """

        response = self.client.get(
            reverse(
                "api_responsible_person:responsible_person_detail",
                kwargs={"max_user_id": 10},
            )
        )

        self.assertEqual(response.status_code, 404)


class ResponsiblePersonCreateApiViewTests(TestCase):
    """Тесты создания ответственного лица"""

    fixtures = ["site_data.json"]

    def test_1(self):
        """Успешное создание ответственного лица"""

        test_max_user_id = 2
        test_post_data = {
            "max_user_id": test_max_user_id,
            "full_name": "Воронов Георгий Эльдарович",
            "status": "друг",
            "max_name": "",
            "telephone": "8 999 999 99 11",
            "description": "",
        }

        self.client.post(
            reverse("api_responsible_person:responsible_person_create"),
            data=json.dumps(test_post_data),
            content_type="application/json",
        )

        self.assertTrue(
            ResponsiblePerson.objects.filter(max_user_id=test_max_user_id).exists()
        )

    def test_2(self):
        """
        Провальное создание ответственного лица:
        нарушена уникальность max_user_id
        """

        test_full_name = "Воронов Артем Эльдарович"
        test_post_data = {
            "max_user_id": 1,
            "full_name": test_full_name,
            "status": "друг",
            "max_name": "",
            "telephone": "8 999 999 99 99",
            "description": "",
        }

        response = self.client.post(
            reverse("api_responsible_person:responsible_person_create"),
            data=json.dumps(test_post_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)


class ResponsiblePersonUpdateApiViewTests(TestCase):
    """Тесты обновления ответственного лица"""

    fixtures = ["site_data.json"]

    def test_1(self):
        """Успешное обновление"""

        test_full_name = "Воронов Артем Эльдарович"
        test_post_data = {
            "full_name": test_full_name,
            "status": "друг",
            "max_name": "",
            "telephone": "8 999 999 99 99",
            "description": "",
        }

        self.client.patch(
            reverse(
                "api_responsible_person:responsible_person_update",
                kwargs={"max_user_id": 1},
            ),
            data=json.dumps(test_post_data),
            content_type="application/json",
        )

        self.assertTrue(
            ResponsiblePerson.objects.filter(full_name=test_full_name).exists()
        )

    def test_2(self):
        """
        Провальное обновление:
        ответственное лицо не найдено
        """

        test_full_name = "Воронов Артем Эльдарович"
        test_post_data = {
            "full_name": test_full_name,
            "status": "друг",
            "max_name": "",
            "telephone": "8 999 999 99 99",
            "description": "",
        }

        response = self.client.patch(
            reverse(
                "api_responsible_person:responsible_person_update",
                kwargs={"max_user_id": 3},
            ),
            data=json.dumps(test_post_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)

    def test_3(self):
        """
        Провальное обновление:
        неверное значение в поле модели status
        """

        test_full_name = "Воронов Артем Эльдарович"
        test_post_data = {
            "full_name": test_full_name,
            "status": "неверное значение",
            "max_name": "",
            "telephone": "8 999 999 99 99",
            "description": "",
        }

        response = self.client.patch(
            reverse(
                "api_responsible_person:responsible_person_update",
                kwargs={"max_user_id": 1},
            ),
            data=json.dumps(test_post_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from responsible_person.models import ResponsiblePerson
from django_site.settings import TEST_USER_DATA
from .models import Accompanied
from pilot.models import ProfilePilot


class AccompaniedListViewTests(TestCase):
    """Тесты получения всех сопровождаемых"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(**TEST_USER_DATA)

    def test_1(self):
        """Успешное получение всех сопровождаемых"""

        self.client.force_login(self.user)
        response = self.client.get(reverse("accompanied:accompanied_list"))

        self.assertEqual(response.status_code, 200)

    def test_2(self):
        """
        Провальное получение всех сопровождаемых:
        пилот не вошел в аккаунт
        """

        response = self.client.get(reverse("accompanied:accompanied_list"))

        self.assertEqual(response.status_code, 302)


class AccompaniedDetailViewTests(TestCase):
    """Тесты получения деталей по сопровождаемым"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(**TEST_USER_DATA)

    def test_1(self):
        """Успешное получение данных"""

        self.client.force_login(self.user)
        response = self.client.get(
            reverse("accompanied:accompanied_detail", kwargs={"pk": 1})
        )

        self.assertEqual(response.status_code, 200)

    def test_2(self):
        """
        Провальное получение деталей по сопровождаемым:
        пилот не вошел в аккаунт
        """

        response = self.client.get(
            reverse("accompanied:accompanied_detail", kwargs={"pk": 1})
        )

        self.assertEqual(response.status_code, 302)

    def test_3(self):
        """
        Провальное получение деталей по сопровождаемым:
        сопровождаемый не найден
        """

        self.client.force_login(self.user)
        response = self.client.get(
            reverse("accompanied:accompanied_detail", kwargs={"pk": 6})
        )

        self.assertEqual(response.status_code, 404)

    def test_4(self):
        """
        Провальное получение деталей по сопровождаемым:
        пилот пытается получить данные по сопровождаемому, к которому у него нет связи в БД
        """

        new_user = User.objects.create_user(
            username="new_user",
            password="123",
        )
        ProfilePilot.objects.create(
            user=new_user,
            telephone="8 999 999 99 11",
        )

        self.client.force_login(new_user)
        response = self.client.get(
            reverse("accompanied:accompanied_detail", kwargs={"pk": 1})
        )

        self.assertEqual(response.status_code, 403)


class AccompaniedCreateViewTests(TestCase):
    """Тесты создания сопровождаемого"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(**TEST_USER_DATA)

        cls.test_user_name = "new_user"
        cls.responsible_person = ResponsiblePerson.objects.get(pk=1)
        cls.accompanied_test_data = {
            "full_name": cls.test_user_name,
            "date_birth": "2000-10-10",
            "health_problems": "Нет",
            "tasks": "Нет",
            "responsible_person": cls.responsible_person.pk,
            "pilots": [cls.user.profile_pilot.pk],
        }

    def test_1(self):
        """Успешное создание сопровождаемого"""

        self.client.force_login(self.user)
        self.client.post(
            reverse("accompanied:accompanied_create"),
            data=self.accompanied_test_data,
        )

        self.assertTrue(
            Accompanied.objects.filter(full_name=self.test_user_name).exists()
        )

    def test_2(self):
        """
        Провальное создание сопровождаемого:
        пилот не вошел в аккаунт
        """

        response = self.client.post(
            reverse("accompanied:accompanied_create"),
            data=self.accompanied_test_data,
        )

        self.assertEqual(response.status_code, 302)

    def test_3(self):
        """
        Провальное создание сопровождаемого:
        ошибка валидации даты
        """

        accompanied_test_data = self.accompanied_test_data.copy()
        accompanied_test_data["date_birth"] = "invalid"

        self.client.force_login(self.user)
        response = self.client.post(
            reverse("accompanied:accompanied_create"),
            data=accompanied_test_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Accompanied.objects.filter(full_name=self.test_user_name).exists()
        )


class AccompaniedUpdateViewTests(TestCase):
    """Тесты обновления сопровождаемого"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(**TEST_USER_DATA)

        cls.responsible_person = ResponsiblePerson.objects.get(pk=1)
        cls.test_user_name = "new_user"
        cls.accompanied_test_data = {
            "full_name": cls.test_user_name,
            "date_birth": "2000-10-10",
            "health_problems": "Нет",
            "tasks": "Нет",
            "responsible_person": cls.responsible_person.pk,
            "pilots": [cls.user.profile_pilot.pk],
        }

    def test_1(self):
        """Успешное обновление сопровождаемого"""

        self.client.force_login(self.user)
        self.client.post(
            reverse("accompanied:accompanied_update", kwargs={"pk": 2}),
            data=self.accompanied_test_data,
        )

        self.assertTrue(
            Accompanied.objects.filter(full_name=self.test_user_name).exists()
        )

    def test_2(self):
        """
        Провальное обновление сопровождаемого:
        пилот не вошел в свой аккаунт
        """

        response = self.client.post(
            reverse("accompanied:accompanied_update", kwargs={"pk": 2}),
            data=self.accompanied_test_data,
        )

        self.assertEqual(response.status_code, 302)

    def test_3(self):
        """
        Провальное обновление сопровождаемого:
        пилот пытается обновить несуществующего сопровождаемого
        """

        self.client.force_login(self.user)
        response = self.client.post(
            reverse("accompanied:accompanied_update", kwargs={"pk": 6}),
            data=self.accompanied_test_data,
        )

        self.assertEqual(response.status_code, 404)

    def test_4(self):
        """
        Провальное обновление сопровождаемого:
        ошибка валидации даты
        """

        self.client.force_login(self.user)
        accompanied_test_data = self.accompanied_test_data.copy()
        accompanied_test_data["date_birth"] = "invalid"

        self.client.post(
            reverse("accompanied:accompanied_update", kwargs={"pk": 1}),
            data=accompanied_test_data,
        )

        self.assertFalse(
            Accompanied.objects.filter(full_name=self.test_user_name).exists()
        )

    def test_5(self):
        """
        Провальное обновление сопровождаемого:
        пилот, не имающий связи в БД с сопровождаемым, пытается обновить его данные
        """

        new_user = User.objects.create_user(
            username="new_user",
            password="123",
        )
        ProfilePilot.objects.create(
            user=new_user,
            telephone="8 999 999 99 11",
        )

        self.client.force_login(new_user)

        response = self.client.post(
            reverse("accompanied:accompanied_update", kwargs={"pk": 1}),
            data=self.accompanied_test_data,
        )

        self.assertEqual(response.status_code, 403)


class AccompaniedRetrieveAPIViewTests(TestCase):
    """Тесты на получение всех сопровождаемых, привязанных к ответственному лицу по max_user_id"""

    fixtures = ["site_data.json"]

    def test_1(self):
        """Успешное получение сопровождаемых"""

        response = self.client.get(
            reverse("api_accompanied:persons_detail", kwargs={"max_user_id": 1})
        )

        self.assertEqual(response.status_code, 200)

    def test_2(self):
        """
        Провальное получение сопровождаемых:
        сопровождаемые не найдены
        """

        response = self.client.get(
            reverse("api_accompanied:persons_detail", kwargs={"max_user_id": 4})
        )

        self.assertEqual(response.status_code, 404)

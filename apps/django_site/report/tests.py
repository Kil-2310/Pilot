from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from django_site.settings import TEST_USER_DATA
from pilot.models import ProfilePilot


class ReportListByAccompaniedViewTests(TestCase):
    """Тесты получения ежедневных отетов по сопровождаемому"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(**TEST_USER_DATA)

    def test_1(self):
        """Успешное получение списка отчетов"""

        self.client.force_login(self.user)

        response = self.client.get(
            reverse("report:report_by_accompanied", kwargs={"accompanied_pk": 1})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(timezone.now().date()))

    def test_2(self):
        """
        Провальное получение списка отчетов:
        пилот не вошел в свой аккаунт
        """

        response = self.client.get(
            reverse("report:report_by_accompanied", kwargs={"accompanied_pk": 1})
        )

        self.assertEqual(response.status_code, 302)

    def test_3(self):
        """
        Провальное получение списка отчетов:
        пилот, не имающий права доступа, пытается получить детали отчета сопровождаемого, к которому у него нет доступа
        """

        new_user = User.objects.create_user(
            username="new_user",
            password="123",
        )
        ProfilePilot.objects.create(
            telephone="8 999 999 99 11",
            user=new_user,
        )

        self.client.force_login(new_user)

        response = self.client.get(
            reverse("report:report_by_accompanied", kwargs={"accompanied_pk": 1})
        )

        self.assertEqual(response.status_code, 403)


class ReportDetailViewTests(TestCase):
    """Тесты получения деталей отчета"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(**TEST_USER_DATA)

    def test_1(self):
        """Успешное получение деталей отчета"""

        self.client.force_login(self.user)
        response = self.client.get(reverse("report:report_detail", kwargs={"pk": 1}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2026-09-22")

    def test_2(self):
        """
        Провальное получение деталей отчета:
        пилот не вошел в свой аккаунт
        """

        response = self.client.get(reverse("report:report_detail", kwargs={"pk": 1}))

        self.assertEqual(response.status_code, 302)

    def test_3(self):
        """
        Провальное получение деталей отчета:
        пилот, не имающий права доступа, пытается получить детали отчета сопровождаемого, к которому у него нет доступа
        """

        new_user = User.objects.create_user(
            username="new_user",
            password="123",
        )
        ProfilePilot.objects.create(
            telephone="8 999 999 99 11",
            user=new_user,
        )

        self.client.force_login(new_user)

        response = self.client.get(reverse("report:report_detail", kwargs={"pk": 1}))

        self.assertEqual(response.status_code, 403)


class ReportNoteCreateViewTests(TestCase):
    """Тесты создания замктки"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(**TEST_USER_DATA)

    def test_1(self):
        """Успешное создание заметки"""

        self.client.force_login(self.user)
        test_post_data = {
            "title": "Покупка продуктов",
            "text": "Купил молоко, хлеб, кефир",
        }

        response = self.client.post(
            reverse("report:report_note_create", kwargs={"pk": 1}), data=test_post_data
        )

        self.assertEqual(response.status_code, 302)

    def test_2(self):
        """
        Провальное получение создание заметки:
        пилот не вошел в свой аккаунт
        """

        test_post_data = {
            "title": "Покупка продуктов",
            "text": "Купил молоко, хлеб, кефир",
        }

        response = self.client.post(
            reverse("report:report_note_create", kwargs={"pk": 1}), data=test_post_data
        )

        self.assertEqual(response.status_code, 302)

    def test_3(self):
        """
        Провальное получение создание заметки:
        пилот пытается добавить заметку к чужому отчету
        """

        new_user = User.objects.create_user(
            username="new_user",
            password="123",
        )

        ProfilePilot.objects.create(
            telephone="8 999 999 99 11",
            user=new_user,
        )

        self.client.force_login(new_user)

        response = self.client.get(reverse("report:report_note_create", kwargs={"pk": 1}))

        self.assertEqual(response.status_code, 403)


class ReportDetailByDateViewTests(TestCase):
    """Тесты получения отчета по сопровождаемому"""

    fixtures = ["site_data.json"]

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(**TEST_USER_DATA)

    def test_1(self):
        """Успешное получение отчета"""

        response = self.client.get(
            reverse(
                "api_report:report_detail_by_date",
                kwargs={"date": "2026-09-22", "accompanied_id": 2},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "На сопровождаемого напал табун цыган. Я избил каждого цыгана и защитил человека от нападения.",
        )

    def test_2(self):
        """Успешное получение отчета, который не был создан"""

        response = self.client.get(
            reverse(
                "api_report:report_detail_by_date",
                kwargs={"date": "2026-09-20", "accompanied_id": 2},
            )
        )

        self.assertContains(response, "Пилот не создал отчет в этот день")

    def test_3(self):
        """
        Провальное получени отчета:
        ошибка в формате даты
        """

        response = self.client.get(
            reverse(
                "api_report:report_detail_by_date",
                kwargs={"date": "invalid-date", "accompanied_id": 2},
            )
        )

        self.assertEqual(response.status_code, 400)

from django.db import models


class Accompanied(models.Model):
    """Модель сопровождаемого"""

    preview = models.ImageField('Фото сопровождаемого', upload_to='accompanies/', blank=True, null=True)
    full_name = models.CharField('ФИО', max_length=255)
    date_birth = models.DateField('Дата рождения')
    description = models.TextField('Описание сопровождаемого', max_length=500, blank=True)
    health_problems = models.TextField('Проблемы со здоровьем', max_length=800)
    tasks = models.TextField('Задачи пилота', max_length=800)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    updated_at = models.DateTimeField('Время последнего изменения', auto_now=True)

    pilots = models.ManyToManyField('pilot.ProfilePilot', related_name='accompanied')
    responsible_person = models.ForeignKey('responsible_person.ResponsiblePerson', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Сопровождаемый: {self.full_name}'

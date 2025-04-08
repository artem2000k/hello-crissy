from django.contrib.auth import get_user_model
from django.db import models, IntegrityError

from user_management.models import User


# Create your models here.
class ChatContext(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    context = models.JSONField('Контекст',default=list)  # Хранит контекст как JSON
    class Meta:
        verbose_name = 'Контекст'
        verbose_name_plural = 'Контексты'

class ChatMessage(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    message = models.TextField('Сообщение')
    response = models.TextField('Ответ',null=True, blank=True)
    timestamp = models.DateTimeField('Дата и время',auto_now_add=True)
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class AiParametrs(models.Model):
    TEMPERATURE_CHOICES = [
        (0.1, '0.1'),
        (0.2, '0.2'),
        (0.3, '0.3'),
        (0.4, '0.4'),
        (0.5, '0.5'),
        (0.6, '0.6'),
        (0.7, '0.7'),
        (0.8, '0.8'),
        (0.9, '0.9'),
        (1.0, '1.0'),
    ]

    character = models.TextField('Характер')
    temperature = models.FloatField('Температура',choices=TEMPERATURE_CHOICES)

    def __str__(self):
        return f"{self.character} (Temperature: {self.temperature})"

    def save(self, *args, **kwargs):
        # Удаляем все существующие записи, оставляя только одну
        AiParametrs.objects.all().delete()
        super(AiParametrs, self).save(*args, **kwargs)
    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'

class InterestCategory(models.Model):
    name = models.CharField('Название', max_length=50, unique=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Категория интересов'
        verbose_name_plural = 'Категории интересов'

class Interest(models.Model):
    name = models.CharField('Название',max_length=100)
    category = models.ForeignKey(InterestCategory, on_delete=models.CASCADE, related_name='interests')
    class Meta:
        verbose_name = 'Интерес'
        verbose_name_plural = 'Интересы'

    def __str__(self):
        return self.name

class UserInterest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_interests')
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'interest')
        verbose_name = 'Интерес пользователя'
        verbose_name_plural = 'Интересы пользователей'

    def save(self, *args, **kwargs):
        if self.user.user_interests.count() >= 10:
            raise IntegrityError("Нельзя иметь больше 10 интересов")
        super().save(*args, **kwargs)

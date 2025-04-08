from django.db import models
from django.contrib.auth import get_user_model

from hsweb import settings
# from user_management.models import Currency

#User = settings.AUTH_USER_MODEL


class TariffType(models.Model):
    name = models.CharField('Наименование',max_length=50, unique=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Тип тарифа'
        verbose_name_plural = 'Типы тарифов'


class Tariff(models.Model):
    name = models.CharField('Название',max_length=100)
    site_name = models.CharField('Название на сайте',max_length=20, default="")
    description = models.TextField('Описание')
    tariff_type = models.ForeignKey(TariffType, on_delete=models.CASCADE, verbose_name="Тип тарифа", null=True)
    duration_days = models.PositiveIntegerField('Длительность, дней',default=30)
    query_length = models.PositiveIntegerField('Длина запроса', default=140)
    chat_access = models.BooleanField('Доступ к чатам',default=False)
    magic_room_access = models.BooleanField('Доступ к волшебной комнате',default=False)
    can_change_avatar = models.BooleanField('Можно менять аватарку',default=False)
    can_change_avatar_color = models.BooleanField('Можно менять цвет аватарки',default=False)
    can_change_nickname = models.BooleanField('Можно менять никнейм',default=False)
    private_rooms_max_count = models.IntegerField('Сколько приватных комнат можно создать',default=1)
    can_read_posts = models.BooleanField('Можно читать посты',default=False)
    messages_coubt = models.IntegerField('Количество сообщений',default=1)
    fast_delete = models.BooleanField('Мгновенное удаление', default=False)
    
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'


class Payment(models.Model):
    payment_id = models.CharField('ID платежа',max_length=100, unique=True)
    user = models.ForeignKey('user_management.User', on_delete=models.CASCADE)
    amount = models.DecimalField('Сумма',max_digits=10, decimal_places=2, default=0)
    amount_crypto = models.DecimalField('Сумма',max_digits=12, decimal_places=8, default=0)
    currency = models.CharField('Валюта',max_length=10, default="USD")
    status = models.CharField('Статус',max_length=50, default="pending")
    created_at = models.DateTimeField('Создано',auto_now_add=True)
    tariff = models.ForeignKey(Tariff, related_name='tariff', on_delete=models.CASCADE, null=True, default=None)
    # logs = models.TextField(null=True)
    
    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'

    def __str__(self):
        return f"Payment {self.payment_id} - {self.status}"
    
    def mark_as_paid(self):
        self.status = 'paid'
        self.save()
    

class Currency(models.Model):
    code = models.CharField('Код', max_length=3, unique=True)
    name = models.CharField('Наименование',max_length=50)
    symbol = models.CharField('Символ', max_length=3, default="$")
    def save(self, *args, **kwargs):
        # Преобразуем код в верхний регистр перед сохранением
        self.code = self.code.upper()
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'


class TariffPrice(models.Model):
    tariff = models.ForeignKey(Tariff, related_name='prices', on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('tariff', 'currency')
        verbose_name = 'Цена'
        verbose_name_plural = 'Цены'

    def __str__(self):
        return f"{self.tariff.name} - {self.currency.code}: {self.price}"



# class PaymentLog(models.Model):
#     logs = models.TextField(null=True)

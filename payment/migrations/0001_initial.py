# Generated by Django 5.0.7 on 2025-03-14 08:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3, unique=True, verbose_name='Код')),
                ('name', models.CharField(max_length=50, verbose_name='Наименование')),
            ],
            options={
                'verbose_name': 'Валюта',
                'verbose_name_plural': 'Валюты',
            },
        ),
        migrations.CreateModel(
            name='Tariff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('duration_days', models.PositiveIntegerField(default=30, verbose_name='Длительность, дней')),
                ('query_length', models.PositiveIntegerField(default=140, verbose_name='Длина запроса')),
                ('chat_access', models.BooleanField(default=False, verbose_name='Доступ к чатам')),
                ('magic_room_access', models.BooleanField(default=False, verbose_name='Доступ к волшебной комнате')),
                ('can_change_avatar', models.BooleanField(default=False, verbose_name='Можно менять аватарку')),
                ('private_rooms_max_count', models.IntegerField(default=1, verbose_name='Сколько приватных комнат можно создать')),
                ('can_read_posts', models.BooleanField(default=False, verbose_name='Можно читать посты')),
                ('messages_coubt', models.IntegerField(default=1, verbose_name='Количество сообщений')),
                ('fast_delete', models.BooleanField(default=False, verbose_name='Мгновенное удаление')),
            ],
            options={
                'verbose_name': 'Тариф',
                'verbose_name_plural': 'Тарифы',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_id', models.CharField(max_length=100, unique=True, verbose_name='ID платежа')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сумма')),
                ('currency', models.CharField(default='USD', max_length=10, verbose_name='Валюта')),
                ('status', models.CharField(default='pending', max_length=50, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('tariff', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tariff', to='payment.tariff')),
            ],
            options={
                'verbose_name': 'Платеж',
                'verbose_name_plural': 'Платежи',
            },
        ),
        migrations.CreateModel(
            name='TariffPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payment.currency')),
                ('tariff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='payment.tariff')),
            ],
            options={
                'verbose_name': 'Цена',
                'verbose_name_plural': 'Цены',
                'unique_together': {('tariff', 'currency')},
            },
        ),
    ]

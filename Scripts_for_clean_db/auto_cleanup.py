# scripts/auto_cleanup.py

import os
import django

# Инициализация Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hsweb.settings')
django.setup()
from django.utils import timezone
from datetime import timedelta
from users_chats.models import Message, PrivateChat  # Замените на реальный путь к вашим моделям


def delete_old_images():
    one_month_ago = timezone.now() - timedelta(days=30)
    messages_with_images = Message.objects.filter(image__isnull=False, timestamp__lte=one_month_ago)

    for message in messages_with_images:
        if message.image:
            message.image.delete(save=False)  # Удаляем файл изображения
            message.image = None
            message.save()
    print(f"Удалено {messages_with_images.count()} изображений старше одного месяца")


def delete_old_messages():
    three_months_ago = timezone.now() - timedelta(days=90)
    old_messages = Message.objects.filter(timestamp__lte=three_months_ago)
    count = old_messages.count()
    old_messages.delete()
    print(f"Удалено {count} сообщений старше трех месяцев")


def delete_old_private_chats():
    one_day_ago = timezone.now() - timedelta(days=1)
    old_chats = PrivateChat.objects.filter(created_at__lte=one_day_ago)
    count = old_chats.count()
    old_chats.delete()
    print(f"Удалено {count} приватных чатов старше 24 часов")


def run_cleanup():
    delete_old_images()
    delete_old_messages()
    delete_old_private_chats()


if __name__ == "__main__":
    run_cleanup()

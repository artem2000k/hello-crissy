import os
import django

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hsweb.settings')
django.setup()
from django.utils import timezone
from datetime import timedelta
from user_management.models import User

# Получаем текущую дату и время
now = timezone.now()

# Находим всех пользователей
users = User.objects.all()

# Фильтруем пользователей по условию
expired_users = [user for user in users if user.last_activity < now - timedelta(days=user.max_inactive_days)]

# Удаляем expired_users
if expired_users:
    # Получаем только ID пользователей
    expired_user_ids = [user.id for user in expired_users]
    User.objects.filter(id__in=expired_user_ids).delete()
else:
    pass

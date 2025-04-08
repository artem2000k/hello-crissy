from django.utils import timezone
from user_management.models import User
now = timezone.now()
users_with_expired_tariffs = User.objects.filter(tariff_end_date__lt=now, user_tariff__isnull=False)

for user in users_with_expired_tariffs:
    user.user_tariff = None
    user.save()
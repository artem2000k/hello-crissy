from django.contrib import admin
from .models import Tariff, Currency, TariffPrice, Payment, TariffType

admin.site.register(Payment)
# admin.site.register(PaymentLog)
# Создаем Inline для цен тарифа
class TariffPriceInline(admin.TabularInline):  # Также можно использовать admin.StackedInline
    model = TariffPrice
    extra = 1  # Сколько пустых полей будет показываться для добавления новых объектов
    min_num = 1  # Минимальное количество записей
    # max_num = len(Currency.objects.all())  # Это вызвало ошибку, убираем

    # Если нужно ограничить количество валют динамически, сделаем это в методе
    def get_max_num(self, request, obj=None, **kwargs):
        return Currency.objects.count()

# Регистрация модели Tariff с использованием TariffPriceInline
@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    inlines = [TariffPriceInline]

admin.site.register(Currency)

admin.site.register(TariffType)
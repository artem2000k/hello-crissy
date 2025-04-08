from django.urls import path
from .views import *


urlpatterns = [
    # path('freekassa-generate-payment-link/<str:order_id>/<str:amount>/', freekassa_generate_payment_link, name='freekassa_generate_payment_link'),
    # path('freekassa-payment-notification/', freekassa_payment_notification, name='freekassa_payment_notification'),
    path('crypto/<str:coin>/', crypto_generate_payment_link, name='crypto'),
    path('paykassa-confirm/', paykassa_handler, name='paykassa-confirm'),
    path('freekassa-pay/', freekassa_pay, name='freekassa-pay'),
    path('freekassa-confirm/', freekassa_payment_notification, name='freekassa-confirm'),
    path('freekassa-success/', freekassa_success, name='freekassa-success'),
    path('freekassa-failure/', freekassa_failure, name='freekassa-failure'),
]
import json
import requests
from django.conf import settings
import random
import string
from .models import Payment


# CURRENCY_SYMBOLS = {"USD": "$", "RUB": "₽", "EUR": "€"}


def check_api_status():
    url = "https://api.nowpayments.io/v1/status"
    headers = {
        "x-api-key": settings.NOWPAYMENTS_API_KEY
    }
    response = requests.get(url, headers=headers)
    return response.status_code == 200


def get_available_currencies():
    url = "https://api.nowpayments.io/v1/currencies"
    headers = {
        "x-api-key": settings.NOWPAYMENTS_API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('currencies', [])
    else:
        raise Exception(f"Ошибка получения доступных валют: {response.json().get('message')}")


def get_minimum_payment_amount(currency_from, fiat_equivalent='usd'):
    url = f"https://api.nowpayments.io/v1/min-amount?currency_from={currency_from}&currency_to=btc&fiat_equivalent={fiat_equivalent}"
    headers = {
        "x-api-key": settings.NOWPAYMENTS_API_KEY
    }

    response = requests.get(url, headers=headers)
    response_data = response.json()

    if response.status_code == 200:
        print("////////")
        print(response_data.get('min_amount'))
        return response_data.get('min_amount')
    else:
        raise Exception(f"Ошибка получения минимальной суммы платежа: {response_data.get('message')}")


def get_estimated_price(amount, currency):
    url = f"https://api.nowpayments.io/v1/estimate?amount={amount}&currency_from=usd&currency_to={currency}"
    headers = {
        "x-api-key": settings.NOWPAYMENTS_API_KEY
    }
    payload = {}
    response = requests.get(url, headers=headers, data=payload)
    response_data = response.json()
    if response.status_code == 200:
        print('расчетная цена')
        print('расчетная цена')
        print(response_data)
        return response_data.get('estimated_amount')
    else:
        raise Exception(f"Ошибка получения оценочной стоимости: {response_data.get('message')}")


def create_payment(amount, callback_url, currency,tariff_id, order_id):
    print('amount, get currency')
    url = "https://api.nowpayments.io/v1/invoice"
    payload = json.dumps({
        "price_amount": amount,
        "price_currency": currency,# валюта, в которой указана сумма
        # "pay_currency": 'btc',# валюта, в которой будет осуществлена оплата, не нужно указывать чтобы юзер сам мог выбрать
        "ipn_callback_url": callback_url,
        "order_id": order_id,
        "order_description":f"tariff_id:{tariff_id}",
        "success_url": "https://uat.hellosissy.com/chat/",
        #сделать страницу для ошибки платежа ниже
        "cancel_url": "https://uat.hellosissy.com/chat/",
        "is_fee_paid_by_user": "true"
    })
    headers = {
        "x-api-key": settings.NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=payload)
    response_data = response.json()

    if response.status_code == 200:
        return response_data
    else:
        raise Exception(f"Ошибка создания платежа: {response_data.get('message', response.text)}")


def generate_order_id():
    """Генерирует уникальный идентификатор заказа."""
    while True:
        order_id = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
        if not Payment.objects.filter(payment_id=order_id).exists():
            return order_id


def get_available_currencies_merchant():
    url = 'https://api.merchant001.io/v2/payment-method/merchant/available?makeArray=1'
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJkNHFiR21INnR3WERqdXZ0V1lBakIzTTVGcXAxIiwiZGF0ZSI6IjIwMjQtMTAtMTZUMTI6NDg6MTkuMDEzWiIsImlhdCI6MTcyOTA4Mjg5OX0.n91aqd732-2fgtYdPPW8ftICskwBcERy0iNHs97VK7I",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    result = requests.get(url, headers=headers).json()
    avaible_currencies = []
    for i in result:
        avaible_currencies.append(i['currency'])
    return avaible_currencies

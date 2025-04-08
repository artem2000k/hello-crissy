# import os
# from dotenv import load_dotenv
import requests
from pprint import pprint
import hashlib
import urllib.parse
from django.conf import settings


# Разрешенные IP FreeKassa
FREEKASSA_IPS = {"168.119.157.136", "168.119.60.227", "178.154.197.79", "51.250.54.238"}


class FreeKassa:
    BASE_URL = "https://pay.fk.money/"

    def __init__(self, merchant_id: str, secret_word_1: str, currency: str = "RUB"):
        """
        :param merchant_id: ID магазина в FreeKassa
        :param secret_word: Секретное слово для подписи (секретное слово 1)
        :param currency: Валюта по умолчанию (RUB, USD, EUR и т. д.)
        """
        self.merchant_id = merchant_id
        self.secret_word_1 = secret_word_1
        self.currency = currency

    def generate_signature(self, amount: float, order_id: str) -> str:
        """
        Создает подпись для платежа.
        :param amount: Сумма платежа
        :param order_id: Уникальный номер заказа
        :return: Хеш-подпись SHA-256
        """
        sign_string = f"{self.merchant_id}:{amount}:{self.secret_word_1}:{self.currency}:{order_id}"
        return hashlib.md5(sign_string.encode()).hexdigest()

    def get_payment_url(self, amount: float, order_id: str, **kwargs) -> str:
        """
        Генерирует URL для оплаты.
        :param amount: Сумма платежа
        :param order_id: Уникальный номер заказа
        :param kwargs: Дополнительные параметры (phone, em, lang, us_* и т. д.)
        :return: Ссылка на оплату
        """
        signature = self.generate_signature(amount, order_id)

        params = {
            "m": self.merchant_id,
            "oa": amount,
            "currency": self.currency,
            "o": order_id,
            "s": signature,
        }

        # Добавляем дополнительные параметры (например, email, phone, us_*)
        for key, value in kwargs.items():
            if key.startswith("us_") or key in ["phone", "em", "lang", "i"]:
                params[key] = value

        query_string = urllib.parse.urlencode(params)
        return f"{self.BASE_URL}?{query_string}"

# === Пример использования ===
# merchant_id = 'ddddd'
# secret_word = '444f3f4f'

# fk = FreeKassa(merchant_id, secret_word)

# # Генерация ссылки на оплату
# payment_url = fk.get_payment_url(
#     amount=100.50,
#     order_id="ORDER_123",
#     # em="user@example.com",
#     # phone="79991234567",
#     # lang="ru",
#     # us_key="custom_data"
# )

# print("Ссылка на оплату:", payment_url)



# class FreeKassa000:
#     SCI_URL = 'https://pay.fk.money/'

#     def __init__(self, sci_id, sci_key, domain, test=False):
#         self.sci_id = sci_id
#         self.sci_key = sci_key
#         self.domain = domain
#         self.test = 'true' if test else 'false'

#     def sci_create_order(self, order_id, amount, currency, system, comment="", phone="false", paid_commission="shop"):
#         """
#         Creates a deposit payment link for the user.
#         :param order_id: Unique payment ID in your system
#         :param amount: Amount to be received
#         :param currency: Currency (e.g., USD, RUB, BTC, etc.)
#         :param system: ID of the payment system (e.g., 11 for BTC, 12 for ETH)
#         :param comment: Optional comment for transaction history
#         :param phone: Must be "false" (required by PayKassa)
#         :param paid_commission: Who pays the commission (default: "shop")
#         :return: JSON response with payment link
#         """
#         return self.make_request({
#             'func': 'sci_create_order',
#             'order_id': order_id,
#             'amount': amount,
#             'currency': currency,
#             'system': system,
#             'comment': comment,
#             'phone': phone,
#             'paid_commission': paid_commission
#         })

#     def sci_confirm_order(self, private_hash):
#         """
#         Confirms an incoming payment.
#         :param private_hash: The hash received in the IPN request
#         :return: JSON response with payment confirmation status
#         """
#         return self.make_request({
#             'func': 'sci_confirm_order',
#             'private_hash': private_hash
#         })

#     def make_request(self, params):
#         """
#         Sends a request to PayKassa API.
#         :param params: Dictionary with request parameters
#         :return: JSON response from the API
#         """
#         fields = {
#             'sci_id': self.sci_id,
#             'sci_key': self.sci_key,
#             'domain': self.domain,
#             'test': self.test
#         }
#         fields.update(params)

#         try:
#             response = requests.post(self.SCI_URL, data=fields, headers={'Content-Type': 'application/x-www-form-urlencoded'})
#             response.raise_for_status()  # Raise error if response is not 200
#             return response.json()  # Convert response to JSON
#         except requests.RequestException as e:
#             return {'error': str(e)}
        




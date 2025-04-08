import json
import random
import string
import jwt
import requests
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils import timezone

import hmac
import hashlib
from urllib.parse import unquote
from datetime import datetime, timedelta
import uuid
from decimal import Decimal

from user_management.forms import CodeInputForm
from user_management.models import User
from login.forms import CurrencyForm
from .forms import PaymentForm
from .services import create_payment, get_minimum_payment_amount, get_estimated_price, check_api_status, get_available_currencies, generate_order_id, get_available_currencies_merchant
from .models import Payment, Tariff, TariffPrice, Currency

from .paykassa import PAYKASSA_CURRENCIES_FOR_SELECT, PAYKASSA_COIN_SYSTEMS, PayKassa, get_paykassa_currency_rate_for_pair
from .freekassa import FREEKASSA_IPS, FreeKassa

import traceback
from pprint import pprint


def get_client_ip(request):
    """Получает IP отправителя запроса."""
    return request.META.get("HTTP_X_REAL_IP", request.META.get("REMOTE_ADDR"))


def freekassa_pay(request):
    """Создание платежа для оплаты через FreeKassa."""
    # Считываем имя тарифа
    tariff_name = ""
    if request.method == 'GET':
        tariff_name = unquote(request.GET.get('tariff', 'wrong_tariff'))
        currency_code = unquote(request.GET.get('currency', 'wrong_currency'))
    print(tariff_name)
    # Считываем тариф
    tariff = Tariff.objects.get(name=tariff_name)
    # Считываем объект валюты для USD
    currency = Currency.objects.get(code=currency_code)

    # Получаем значение тарифа
    tariff_price = TariffPrice.objects.get(tariff=tariff, currency=currency)
    price = tariff_price.price
    pprint(tariff_price)
    print(float(price))

    payment = Payment.objects.create(payment_id=uuid.uuid4(),
                                     user=request.user, 
                                     amount=price, 
                                     amount_crypto=0, 
                                     currency=currency_code,
                                     status="pending",
                                     tariff=tariff)

    print(f"payment.payment_id ", payment.payment_id)
    # Создаем объект для FreeKassa

    freekassa = FreeKassa(
        merchant_id=settings.FREEKASSA_MERCHANT_ID, 
        secret_word_1=settings.FREEKASSA_SECRET_1,
        currency=currency_code
    )
    
    # Generate payment link
    response = freekassa.get_payment_url(
        amount=str(price).replace(",", "."),
        order_id=str(payment.payment_id)
    )

    # print(response['data']['url'])
    pprint(response)  # Check response for payment URL
    if response and response.startswith("https://pay.fk.money/"):
        return redirect(response)
    else:
        return HttpResponse("Ошибка при проведении оплаты 6!", status=400)


@csrf_exempt  # Отключаем CSRF для приема уведомлений
def freekassa_payment_notification(request):
    print("Freekassa notification. request.method: ", request.method)
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    # Проверяем IP отправителя
    print("Freekassa notification. Check IP")
    client_ip = get_client_ip(request)
    if client_ip not in FREEKASSA_IPS:
        print("Freekassa notification. Hacking attempt!")
        return HttpResponse("hacking attempt!", status=403)

    # Получаем данные из уведомления
    merchant_id = request.POST.get("MERCHANT_ID")
    amount = request.POST.get("AMOUNT")
    order_id = request.POST.get("MERCHANT_ORDER_ID")
    received_sign = request.POST.get("SIGN")

    print("Freekassa notification. merchant_id: ", merchant_id)

    # Проверяем, что все параметры переданы
    if not all([merchant_id, amount, order_id, received_sign]):
        print("Freekassa notification. Missing parameters.")
        return JsonResponse({"error": "Missing parameters"}, status=400)

    # Проверяем подпись
    expected_sign = hashlib.md5(f"{settings.FREEKASSA_MERCHANT_ID}:{amount}:{settings.FREEKASSA_SECRET_2}:{order_id}".encode()).hexdigest()
    if received_sign != expected_sign:
        print("Freekassa notification. Wrong sign.")
        return HttpResponse("wrong sign", status=400)

    # Платеж успешен, обновляем статус в базе данных и добавляем функционал пользователю
    print("Freekassa notification. Start payment processing.")
    try:
        payment = Payment.objects.get(payment_id=order_id, status="pending")
        payment.payment_id = order_id
        payment.status = "paid"
        # Определяем пользователя
        user = payment.user
        tariff = payment.tariff
        if tariff.duration_days > 0:
            user.user_tariff = tariff
            user.tariff_end_date = datetime.now() + timedelta(days=tariff.duration_days)
        if tariff.messages_coubt > 0:
            user.remaining_messages = user.remaining_messages + tariff.messages_coubt

        print("Freekassa notification. Start data saving.")
        payment.save()
        user.save()
        print("Freekassa notification. Finish data saving.")

    except Payment.DoesNotExist:
        print("Freekassa notification. ERROR. Order not found.")
        return JsonResponse({"error": "Order not found"}, status=404)

    # Если все хорошо, подтверждаем платеж
    return HttpResponse("YES")  # FreeKassa будет присылать уведомления до тех пор, пока не получит "YES"


@csrf_exempt  # Отключаем CSRF для приема уведомлений
def freekassa_success(request):
    messages.success(request, "Оплата успешно произведена! В ближайшие несколько минут Ваш тариф изменится.")
    return redirect("settings")


@csrf_exempt  # Отключаем CSRF для приема уведомлений
def freekassa_failure(request):
    messages.error(request, "Ошибка при проведении оплаты!")
    return redirect("settings")


def crypto_generate_payment_link(request, coin):
    # Определяем курс криптовалюты относительно USD
    currency_rate = get_paykassa_currency_rate_for_pair('USD', coin)

    # Считываем имя тарифа
    tariff_name = ""
    if request.method == 'GET':
        tariff_name = request.GET.get('tariff', 'wrong_tariff')
    # Считываем тариф
    tariff = Tariff.objects.get(name=tariff_name)
    # Считываем объект валюты для USD
    currency = Currency.objects.get(code="USD")

    # Получаем значение тарифа
    tariff_price = TariffPrice.objects.get(tariff=tariff, currency=currency)
    price = tariff_price.price
    pprint(tariff_price)
    print(float(price))
    print(float(currency_rate))
    print(round(float(price) * float(currency_rate), 8))
    # Величина тарифа в криптовалюте
    price_crypto = round(float(price) * float(currency_rate), 8)
    print(f"price_crypto ", price_crypto)

    payment = Payment.objects.create(payment_id=uuid.uuid4(),
                                     user=request.user, 
                                     amount=0, 
                                     amount_crypto=price_crypto, 
                                     currency=coin,
                                     status="pending",
                                     tariff=tariff)

    print(f"payment.id ", payment.id)
    # Создаем объект для PayKassa
    # print(f"settings.PAYKASSA_SCI_ID ", settings.PAYKASSA_SCI_ID)
    # print(f"settings.PAYKASSA_SCI_KEY ", settings.PAYKASSA_SCI_KEY)
    # print(f"settings.PAYKASSA_DOMAIN ", settings.PAYKASSA_DOMAIN)
    paykassa = PayKassa(
        sci_id=settings.PAYKASSA_SCI_ID ,
        sci_key=settings.PAYKASSA_SCI_KEY,
        domain=settings.PAYKASSA_DOMAIN,
        test=False
    )

    # Generate payment link
    response = paykassa.sci_create_order(
        order_id=str(payment.id),
        amount=str(price_crypto).replace(",", "."),
        currency=coin,
        system=PAYKASSA_COIN_SYSTEMS[coin]
    )

    # print(response['data']['url'])
    print(response)  # Check response for payment URL
    if response['error']:
        return HttpResponse("Ошибка при проведении оплаты 6!", status=400)
    else:
        return redirect(response["data"]["url"])


@csrf_exempt  # Отключаем CSRF для работы с внешними запросами
def paykassa_handler(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    # Получаем данные из POST-запроса
    private_hash = request.POST.get("private_hash")
    order_id = request.POST.get("order_id")
    currency = request.POST.get("currency")
    system = request.POST.get("system")

    if not private_hash or not order_id:
        return JsonResponse({"error": "Missing required parameters"}, status=400)

    # Создаем объект для PayKassa
    paykassa = PayKassa(
        sci_id=settings.PAYKASSA_SCI_ID ,
        sci_key=settings.PAYKASSA_SCI_KEY,
        domain=settings.PAYKASSA_DOMAIN,
        test=False
    )

    # Отправляем запрос на PayKassa для подтверждения платежа
    response = paykassa.sci_confirm_order(private_hash)

    result = response.json()

    if result.get("error") == False and result.get("message") == "sci_confirm_order":
        # Платеж успешен, обновляем статус в базе данных
        try:
            payment = Payment.objects.get(id=int(order_id))
            payment.payment_id = order_id
            payment.status = "paid"
            payment.save()
            return HttpResponse(f"{order_id}|success")
        except Payment.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)

    return JsonResponse({"error": "Payment verification failed"}, status=400)



@csrf_exempt
def payment_callback_with_nowpaiments(request):
    try:

        if request.method == 'POST':
            # Шаг 1: Разбор тела запроса
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'message': 'Invalid JSON'}, status=400)

            # Шаг 2: Получение подписи
            received_signature = request.headers.get('X-Nowpayments-Sig')
            if not received_signature:
                return JsonResponse({'message': 'Missing signature'}, status=400)

            sorted_data = json.dumps(data, separators=(',', ':'), sort_keys=True)

            secret = settings.NOWPAYMENTS_IPN_KEY.encode()
            calculated_signature = hmac.new(secret, f'{sorted_data}'.encode(), hashlib.sha512).hexdigest()
            if not hmac.compare_digest(calculated_signature, received_signature):
                return JsonResponse({'message': 'Invalid signature'}, status=400)

            # Шаг 6: Обработка платежа
            payment_id = data.get('order_id')
            status = data.get('payment_status')
            try:
                payment = Payment.objects.get(payment_id=payment_id)
                if status == 'finished':
                    user = payment.user
                    tariff_id = data.get('order_description')
                    tariff_id = tariff_id.split(":")[1]
                    # Назначение тарифа
                    user.user_tariff = Tariff.objects.get(id=tariff_id)
                    duration_days = user.user_tariff.duration_days
                    user.tariff_end_date = timezone.now() + timedelta(days=duration_days)
                    user.remaining_messages += user.user_tariff.messages_count
                    user.save()

                payment.status = status
                payment.save()

                return JsonResponse({'message': 'Success'})
            except Payment.DoesNotExist:
                return JsonResponse({'message': 'Payment not found'}, status=404)
        else:
            return JsonResponse({'message': 'Invalid request method'}, status=405)
    except Exception as e:
        print(e)
        return JsonResponse({'message': 'Internal Server Error'}, status=500)


@login_required
def buy_list_view(request, slug):
    user = request.user
    if request.method == 'POST':
        form = CurrencyForm(request.POST)
        if form.is_valid():
            selected_currency = form.cleaned_data['currency']
            user.preferred_currency = selected_currency
            user.save()
            return redirect('/buy/' + slug + '/')
    
    preferred_currency = user.preferred_currency if user.preferred_currency else Currency.objects.get(code="USD")
    # Получаем все тарифы
    match slug:
        case 'messages':
            tariffs = Tariff.objects.filter(tariff_type__name="Текстовые сообщения")
        case 'voice_messages':
            tariffs = Tariff.objects.all()
        case 'video_messages':
            tariffs = Tariff.objects.all()
        case 'donates':
            tariffs = Tariff.objects.all()
        case 'subscription':
            tariffs = Tariff.objects.filter(tariff_type__name="Подписка")
    # pprint(tariffs)
    # tariffs = Tariff.objects.all()
    # Создаем список тарифов с ценами в предпочтительной валюте пользователя
    tariffs_with_prices = []
    for tariff in tariffs:
        tariff_price = TariffPrice.objects.get(tariff=tariff, currency=preferred_currency)
        tariffs_with_prices.append({
            'tariff': tariff,
            'price': tariff_price.price,
            'currency': preferred_currency,
            'tariff_price': tariff_price,
            # 'currency_symbol': CURRENCY_SYMBOLS[preferred_currency.code]
        })

    tariffs_with_prices.sort(key=lambda x: x['price'], reverse=True)
    pprint(tariffs_with_prices)
    
    form = CodeInputForm()
    currency_form = CurrencyForm()
    
    template_name = 'buy.html'
    
    match slug:
        case 'messages':
            template_name = 'buy_messages.html'
        case 'voice_messages':
            template_name = 'buy_voice_messages.html'
        case 'video_messages':
            template_name = 'buy_video_messages.html'
        case 'donates':
            template_name = 'buy_donates.html'
        case 'subscription':
            template_name = 'buy_subscription.html'
        
    return render(request, 
                  template_name, 
                  {'tariffs_with_prices': tariffs_with_prices,
                   'tariff_s': tariffs_with_prices[3], 
                   'tariff_m': tariffs_with_prices[2],
                   'tariff_l': tariffs_with_prices[1],
                   'tariff_xl': tariffs_with_prices[0],
                   'form': form, 
                   'currency_form': currency_form, 
                   'currencies': Currency.objects.all(),
                   'crypto_list': PAYKASSA_CURRENCIES_FOR_SELECT
                   })


@login_required
def view_payment_methods(request, tariff_price):
    tariff_price_ = TariffPrice.objects.get(id=tariff_price)
    currency = tariff_price_.currency.code
    if currency == 'rub':
        return render(request, 'payment_methods_ru.html', {'tariff_price': tariff_price_})
    else:
        return render(request, 'payment_methods_ru.html', {'tariff_price': tariff_price_})


@login_required
def start_tariff_payment_with_nowpaiments(request, tariff_price):
    tariff_price = TariffPrice.objects.get(id=tariff_price)
    user = request.user
    callback_url = request.build_absolute_uri('/payment_callback/')
    #работает
    # callback_url = 'https://uat.hellosissy.com/payment_callback/'
    currency = tariff_price.currency.code
    tariff_id = tariff_price.tariff.id
    order_id = generate_order_id()
    # Convert tariff.price to float
    payment_data = create_payment(amount=float(tariff_price.price), callback_url= callback_url,
                                  currency=currency, tariff_id = tariff_id, order_id = order_id)
    Payment.objects.create(
        user=user,
        amount=tariff_price.price,
        payment_id=order_id,
        currency=currency,
        status='pending'
    )
    return redirect(payment_data['invoice_url'])


@login_required
def start_tariff_payment_with_merchant001(request, tariff_price):
    tariff_price = TariffPrice.objects.get(id=tariff_price)
    user = request.user

    callback_url = request.build_absolute_uri('/merchant001_payment_callback/')
    # callback_url = 'http://91.107.120.3:8000/payment_callback/'
    client_id = str(user.id)  # Уникальный идентификатор пользователя
    print("client id : ", client_id)
    order_id = generate_order_id()
    amount = float(tariff_price.price)
    available_codes = get_available_currencies_merchant()
    currency = tariff_price.currency.code
    if currency not in available_codes:
        return redirect('/{страница с уведомлением о том, что валюта пользователя недоступна в этой платежке}/')
    payment_data = {
        "pricing": {
            "local": {
                "amount": amount,
                "currency": currency
            }
        },
        "selectedProvider": {"method": "ALL"},
        "clientId": client_id,
        "invoiceId": order_id,
        "callbackUrl": callback_url,
        "redirectUrl": request.build_absolute_uri('/chat/'),
        "cancelUrl": request.build_absolute_uri('/tariffs/')
    }
    # Отправляем запрос на создание транзакции
    response = requests.post("https://api.merchant001.io/v2/transaction/merchant", json=payment_data, headers={
  "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJkNHFiR21INnR3WERqdXZ0V1lBakIzTTVGcXAxIiwiZGF0ZSI6IjIwMjQtMTAtMTZUMTI6NDg6MTkuMDEzWiIsImlhdCI6MTcyOTA4Mjg5OX0.n91aqd732-2fgtYdPPW8ftICskwBcERy0iNHs97VK7I",
  "Content-Type": "application/json"
})
    if response.status_code != 200 and response.status_code != 201:
        if response.status_code == 404:
            return redirect('/страница с сообщением о том, что сейчас нет доступных реквизитов/')
        else:
            return redirect(f'/{response.status_code}/')
    transaction = response.json()
    redirect_url = transaction.get('transaction')['paymentUrl']
    # Создаем запись в базе данных
    Payment.objects.create(
        user=user,
        amount=tariff_price.price,
        payment_id=order_id,
        currency=currency,
        status=transaction.get("status", "PENDING"),
        tariff=tariff_price.tariff
    )
    # Перенаправляем пользователя на URL для завершения оплаты
    return redirect(redirect_url)


@csrf_exempt
def payment_callback_with_merchant001(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method'}, status=405)

    # Шаг 1: Разбор тела запроса
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    print(data)
    # Шаг 2: Получение подписи
    received_signature = request.headers.get('X-SIGNATURE')
    if not received_signature:
        return JsonResponse({'message': 'Missing signature'}, status=400)

    # Шаг 3: Декодирование X-SIGNATURE
    transaction_id = data.get('transaction', {}).get('id')
    api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJkNHFiR21INnR3WERqdXZ0V1lBakIzTTVGcXAxIiwiZGF0ZSI6IjIwMjQtMTAtMTZUMTI6NDg6MTkuMDEzWiIsImlhdCI6MTcyOTA4Mjg5OX0.n91aqd732-2fgtYdPPW8ftICskwBcERy0iNHs97VK7I'  # Замените на ваш фактический API ключ
    public_key = transaction_id + api_key
    if not transaction_id or not api_key:
        return JsonResponse({'message': 'Missing transaction ID or API key'}, status=400)
    try:
        decoded_data = jwt.decode(
            received_signature,
            public_key,
            algorithms=["HS256"]
        )
    except jwt.InvalidSignatureError:
        return JsonResponse({'message': 'Missing transaction ID or API key'}, status=400)

    # Шаг 4: Обработка платежа
    status = data.get('transaction', {}).get('status')
    #ИЗ ДОКУМЕНТАЦИИ
    # Какие статусы есть у транзакции:
    # CREATED - Новые
    # PENDING - Ожидает оплаты
    # PAID - Оплачен
    # IN_PROGRESS - Ожидает подтверждения
    # FAILED - Ошибка
    # EXPIRED - Истек срок оплаты
    # CANCELED - Отменено
    # CONFIRMED - Завершен(Зачисление транзакции на баланс)
    payment = data.get('transaction', {}).get('invoiceId')
    try:
        payment = Payment.objects.get(payment_id=payment)
    except Payment.DoesNotExist:
        print('Payment does not exist')
        return JsonResponse({'message': 'Payment not found'}, status=404)
    if status == 'CONFIRMED':
        # Пример обработки: назначение тарифа, обновление информации о пользователе
        user = payment.user
        user.user_tariff = Tariff.objects.get(id=payment.tariff.id)
        duration_days = user.user_tariff.duration_days
        user.tariff_end_date = timezone.now() + timedelta(days=duration_days)
        user.remaining_messages += user.user_tariff.messages_count
        user.save()
        payment.status = status
        payment.save()
        print('succes payment')
        return JsonResponse({'message': 'Success'})
    payment.status = status
    payment.save()
    return JsonResponse({'message': 'Unhandled status'}, status=400)

@csrf_exempt
def error_page(request):
    return render(request,'payerror.html')


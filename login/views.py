import json
import random
import string

from django.contrib.auth.forms import PasswordResetForm

from .forms import RegisterForm, PasswordResetVerifyCodeForm, PasswordResetRequestForm, CurrencyForm
from .utils import send_verification_email, create_temp_nickname, generate_avatar
from django.http import JsonResponse
from django.utils import timezone
from urllib import request

from django.contrib.auth import logout, get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from .forms import LoginForm, RegisterForm
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

def check_permissions(request):
    # Проверяем дату/время окончания тарифа
    if (not request.user.tariff_end_date) or (request.user.tariff_end_date < timezone.now()) or (not request.user.user_tariff):
        # Если тариф истек, перенаправляем на оплату
        return redirect('/buy/subscription/')


def sign(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            login_user = authenticate(username=username, password=password)
            # Если юзер не авторизован - проверяем email
            if not login_user:
                try:
                    user = get_user_model().objects.get(email=username)
                    login_user = authenticate(username=user.username, password=password)
                except:
                    login_user = None
            if login_user:
                login(request, login_user)
                check_permissions(request)
                return redirect('/chat')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=4))


def registration(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = create_temp_nickname()
            user.username = username
            user.is_active = False

            # Generate avatar using 'u' and a random digit from the username
            if username.startswith('user_') and len(username) > 6:
                initials = username[5:7]
            elif len(username) > 1:
                initials = username[:2]
            else:
                initials = username[:1]
            initials = initials.upper()
            # background_color = 'red'
            # text_color = "blue"
            # avatar = generate_avatar(initials, background_color=background_color, text_color=text_color)
            avatar = generate_avatar(initials)
            user.avatar.save(f'{username}_avatar.png', avatar, save=False)

            user.save()

            password = form.cleaned_data['password1']
            code = generate_verification_code()
            send_verification_email(user.email, code, username, password)
            request.session['verification_code'] = code
            request.session['user_id'] = user.id

            messages.info(request, 'На вашу электронную почту отправлен код подтверждения.')

            return redirect('verify_code')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def verify_code(request):
    if request.method == 'POST':
        code = request.POST.get('verification_code')
        session_code = request.session.get('verification_code')
        user_id = request.session.get('user_id')

        if code == session_code:
            user = get_user_model().objects.get(id=user_id)
            user.is_active = True
            user.save()
            messages.success(request, 'Ваша регистрация завершена!')
            login(request, user)
            return redirect('/buy/subscription')
        else:
            messages.error(request, 'Неверный код подтверждения.')
    return render(request, 'registration/verify_code.html')


def choose_currency(request):
    if request.method == 'POST':
        form = CurrencyForm(request.POST)
        if form.is_valid():
            selected_currency = form.cleaned_data['currency']
            user = request.user
            user.preferred_currency = selected_currency
            user.save()
            return redirect('/tariffs')
    else:
        form = CurrencyForm()

    return render(request, 'choose_currency.html', {'form': form})


def reset_password_get_mail(request):
    if request.method == 'POST':
        if 'email' in request.POST:
            form = PasswordResetRequestForm(request.POST)
            if form.is_valid():
                code = generate_verification_code()
                email = form.cleaned_data['email']
                send_verification_email(email, code,username=None, password=None)
                # Сохраняем email и код в сессии для дальнейшей проверки
                request.session['reset_email'] = email
                request.session['verification_code'] = code
                return redirect('/password_reset_verify_code')  # Перенаправление на страницу с вводом кода и нового пароля
    else:
        form = PasswordResetRequestForm()

    return render(request, 'password_reset_form.html', {'form': form})


def password_reset_verify_code(request):
    if request.method == 'POST':
        form = PasswordResetVerifyCodeForm(request.POST)
        if form.is_valid():
            code = request.session.get('verification_code')
            verification_code = form.cleaned_data['verification_code']
            if code == verification_code:
                email = request.session.get('reset_email')
                password = form.cleaned_data['password1']
                user = get_user_model().objects.get(email=email)
                user.set_password(password)
                user.save()
                return redirect('chat')  # Перенаправление после успешного сброса пароля
            else:
                form.add_error('verification_code', 'Код подтверждения неверен')
        else:
            print('invalid')
            # Обработка ошибок формы (например, пароли не совпадают)
    else:
        form = PasswordResetVerifyCodeForm()

    return render(request, 'password_reset_verify_code.html', {'form': form})


def agreement(request):
    return render(request, 'registration/agreement.html', {'page_class': 'not-apply-body-height'})



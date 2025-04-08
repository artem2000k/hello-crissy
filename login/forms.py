from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from payment.models import Currency


class LoginForm(forms.Form):
    username = forms.CharField(label='Введите Ваш логин или email', required=True)
    password = forms.CharField(label='Введите Ваш пароль', required=True, widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        if not get_user_model().objects.filter(username=username).exists(): 
            if not get_user_model().objects.filter(email=username).exists():
                raise forms.ValidationError('Пользователь с таким логином не зарегистрирован!')
            else:
                user = get_user_model().objects.get(email=username)
        else:
            user = get_user_model().objects.get(username=username)
        if user and not user.check_password(password):
            raise forms.ValidationError('Неверный логин или пароль!')
        

class CurrencyForm(forms.Form):
    currency = forms.ModelChoiceField(
        queryset=Currency.objects.all(),  # список доступных валют
        widget=forms.Select,              # виджет выпадающего списка (по умолчанию)
        label="Выберите валюту"           # название поля в форме
    )


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(label='E-mail')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ['email', 'password1']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()

        # Проверка, существует ли уже пользователь с таким email
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот адрес электронной почты уже занят.")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Введите вашу почту",
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Проверяем, существует ли пользователь с таким email
        if not get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email не найден.")
        return email


class PasswordResetVerifyCodeForm(forms.Form):
    verification_code = forms.CharField(label="Введите код из письма")
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # Проверяем, совпадают ли введенные пароли
        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают")

        return cleaned_data
#class SignUpForm(forms.Form):
#    username = forms.CharField(label='Логин')
#    email = forms.CharField(label='e-mail')
#    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
#    password2 = forms.CharField(label='Подтверждение', widget=forms.PasswordInput)
#
#    class Meta:
#        model = User
#        fields = ('username', 'email', 'password1', 'password2', )
#    def valid(self):
#        reg_data = super(SignUpForm, self)
#        username = self.reg_data['username']
#        email = self.reg_data['email']
#        password1 = self.reg_data['password1']
#        password2 = self.reg_data['password1']
#        if User.objects.filter(username=username).exists():
#            raise forms.ValidationError('Пользователь с таким логином уже зарегистрирован!')
#
#        user = User.objects.get(username=username)
#        if password1 != password2:
#            raise forms.ValidationError('Пароли не совпадают!')

# class PasswordChangeForm(forms.ModelForm):
#     # email = forms.EmailField(label='E-mail')
#     password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)

#     class Meta:
#         model = get_user_model()
#         fields = ['password1']

#     # def clean_email(self):
#     #     email = self.cleaned_data.get('email')
#     #     User = get_user_model()

#     #     # Проверка, существует ли уже пользователь с таким email
#     #     if User.objects.filter(email=email).exists():
#     #         raise ValidationError("Этот адрес электронной почты уже занят.")

#     #     return email

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data['password1'])
#         if commit:
#             user.save()
#         return user

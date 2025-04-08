"""hsweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from chat.views import chat, remove_context, assign_interests
from hsweb import settings
from login.views import sign, registration, logout_view, verify_code, reset_password_get_mail, \
    password_reset_verify_code, choose_currency, agreement
from django.urls import include, path
from django.conf.urls.static import static
from django.views.generic import TemplateView
from user_management.views import time_counter, change_nick_color 
# change_email, change_nickname, change_password
from user_management.views import delete_user, my_time, change_avatar, activate_tariff, no_acess, user_settings
from my_magic_room.views import achievements_list, memes_list, tales_list, stories_list, magic_room, tale_detail, \
    storie_detail, meme_detail, new_post, preview_tale, \
    krissy_blog_list, krissy_blog_detail, posts_list, post_detail, preview_post
from payment.views import payment_callback_with_nowpaiments, buy_list_view, start_tariff_payment_with_nowpaiments, \
    view_payment_methods, start_tariff_payment_with_merchant001, payment_callback_with_merchant001, error_page
from users_chats.views import users_chats, create_privat_chat, invite_user_to_chat, report_message, join_public_chat

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', chat, name='chat'),
    path('remove_context/', remove_context, name='remove_context'),
    path('', sign, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', registration, name='registration'),
    path('verify_code/', verify_code, name='verify_code'),
    path('reset_password/', reset_password_get_mail, name='reset_password'),
    path('password_reset_verify_code/', password_reset_verify_code, name='password_reset_verify_code'),
    path('accounts/', include("django.contrib.auth.urls")),
    path('time_counter/', time_counter, name='time_counter'),

    # path('change_nickname/', change_nickname, name='change_nickname'),
    path('change_nick_color/', change_nick_color, name='change_nick_color'),
    # path('change_email/', change_email, name='change_email'),
    # path('change_password/', change_password, name='change_password'),
    path('delete_user/', delete_user, name='delete_user'),
    
    path('magic_room/', magic_room, name='magic_room'),
    # path('admin/stories/preview/<int:pk>/', preview_storie, name='storie_preview'),
    path('stories_list/', stories_list, name='stories_list'),
    path('stories/<slug:slug>/', storie_detail, name='storie_detail'),

    path('krissy_blog_list/', krissy_blog_list, name='krissy_blog_list'),
    path('krissy_blog/<slug:slug>/', krissy_blog_detail, name='krissy_blog_detail'),
    # path('preview_krissy_blog/', preview_krissy_blog, name='preview_krissy_blog'),

    path('posts_list/', posts_list, name='posts_list'),
    path('posts/<slug:slug>/', post_detail, name='post_detail'),
    path('preview_post/', preview_post, name='preview_post'),

    path('tales_list/', tales_list, name='tales_list'),
    path('tales/<slug:slug>/', tale_detail, name='tale_detail'),
    path('preview_tale/', preview_tale, name='preview_tale'),

    path('memes_list/', memes_list, name='memes_list'),
    path('memes/<slug:slug>/', meme_detail, name='meme_detail'),
    path('new_post/', new_post, name='new_post'), # Артем: Создал url для нового поста
    path('achievements_list/', achievements_list, name='achievements_list'),
    
    path('my_time/', my_time, name='my_time'),
    # path('payment/', payment_view, name='payment'),
    path('users_chats/', users_chats, name='users_chats'),
    path('create_privat_chat/', create_privat_chat, name='create_privat_chat'),
    path('invite_user_to_chat/<int:chat_id>/', invite_user_to_chat, name='invite_user_to_chat'),
    path('report_message/<int:message_id>/', report_message, name='report_message'),
    path('join_public_chat/<int:chat_id>/', join_public_chat, name='join_public_chat'),
    path('buy/<slug:slug>/', buy_list_view, name='buy_list'),
    # path('tariffs/', tariff_list_view, name='tariff_list'),
    path('tariff_payment_nowpaiments/<int:tariff_price>/', start_tariff_payment_with_nowpaiments, name='start_tariff_payment_nowpaiments'),
    path('tariff_payment_merchant/<int:tariff_price>/', start_tariff_payment_with_merchant001, name='start_tariff_payment_merchant001'),
    path('activate-tariff/', activate_tariff, name='activate_tariff'),
    path('choose_currency/', choose_currency, name='choose_currency'),
    path('view_payment_methods/<int:tariff_price>/', view_payment_methods, name='view_payment_methods'),
    path('assign_interests/', assign_interests, name='assign_interests'),
    path('settings/', user_settings, name='settings'),
    path('no_acess/', no_acess, name='no_acess'),
    path('change_avatar/', change_avatar, name='change_avatar'),
    path('payerror/', error_page, name='payerror'),
    path('agreement/', agreement, name='agreement'),

    path('payment_callback/', payment_callback_with_nowpaiments, name='payment_callback'),
    path('merchant001_payment_callback/', payment_callback_with_merchant001, name='merchant001_payment_callback'),
    # path('my_magic_room/', include('my_magic_room.urls')),
    path('payment/', include('payment.urls')),

    path("ckeditor5/", include('django_ckeditor_5.urls')),

    path("fk-verify.html", TemplateView.as_view(template_name="fk-verify.html")),


] + static(settings.STATIC_URL, document_root=settings.STATIC_URL) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

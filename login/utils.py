# utils.py
import random

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from PIL import Image, ImageDraw, ImageFont
import io
import os
from django.core.files.base import ContentFile
from django.conf import settings

def send_verification_email(email, code, username, password):
    subject = 'Ваш код подтверждения'

    message = f"""Привет! 

Добро пожаловать на сайт!

Твой код подтверждения: {code}

Имя пользователя: {username}

Пароль: {password}

Жду тебя! 

Крисси

————————

Hi there!

Welcome to the site!

Here’s your confirmation code: {code}

Username: {username}

Password: {password}

Can’t wait to see you!

XOXO, Krissy"""
    # message = f'Ваш код подтверждения: {code}, ваш пароль   {password}  , ваш username {username}'
    from_email = f"Welcome! <{settings.EMAIL_HOST_USER}>"
    print(message)
    send_mail(subject, message, from_email, [email])


def create_temp_nickname():

    while True:
        nick = 'user_' + get_random_string(10)

        # Проверяем, существует ли пользователь с таким ником
        if not get_user_model().objects.filter(username=nick).exists():
            return nick




from PIL import Image, ImageDraw, ImageFont
import io
from django.core.files.base import ContentFile


import random
import colorsys


def get_contrasting_colors():
    """Генерирует случайные контрастные цвета для фона и текста"""

    # 1. Генерируем случайный цвет фона (RGB)
    background_rgb = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

    # 2. Вычисляем яркость (Luminance)
    luminance = 0.299 * background_rgb[0] + 0.587 * background_rgb[1] + 0.114 * background_rgb[2]

    # 3. Переводим RGB → HSL, чтобы получить противоположный оттенок
    r, g, b = [x / 255.0 for x in background_rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    
    # 4. Инвертируем оттенок (цветовой круг на 180°)
    h = (h + 0.5) % 1.0  # Смещение на 180° (0.5 в диапазоне 0-1)
    
    # 5. Корректируем яркость (чтобы текст выделялся)
    if luminance > 180:  
        l = max(l - 0.3, 0)  # Затемняем текст, если фон светлый
    elif luminance < 75:
        l = min(l + 0.3, 1)  # Осветляем текст, если фон тёмный

    # 6. Переводим обратно HSL → RGB
    text_rgb = colorsys.hls_to_rgb(h, l, s)
    text_rgb = tuple(int(x * 255) for x in text_rgb)

    # 7. Преобразуем в HEX
    background_hex = '#{:02x}{:02x}{:02x}'.format(*background_rgb)
    text_hex = '#{:02x}{:02x}{:02x}'.format(*text_rgb)

    return background_hex, text_hex



# def get_contrasting_colors():
#     """Генерирует случайные контрастные цвета для фона и текста"""
    
#     # 1. Случайный цвет фона (RGB)
#     background_color = (
#         random.randint(0, 255),
#         random.randint(0, 255),
#         random.randint(0, 255)
#     )

#     # 2. Вычисляем яркость (Luminance)
#     luminance = 0.299 * background_color[0] + 0.587 * background_color[1] + 0.114 * background_color[2]

#     # 3. Определяем цвет текста (контрастный)
#     text_color = (0, 0, 0) if luminance > 128 else (255, 255, 255)

#     # 4. Преобразуем в HEX формат
#     background_hex = '#{:02x}{:02x}{:02x}'.format(*background_color)
#     text_hex = '#{:02x}{:02x}{:02x}'.format(*text_color)

#     return background_hex, text_hex


def generate_avatar_for_user(user, background_color='', text_color=''):
    username = user.username
    # Generate avatar using 'u' and a random digit from the username
    if username.startswith('user_') and len(username) > 6:
        initials = username[5:7]
    elif len(username) > 1:
        initials = username[:2]
    else:
        initials = username[:1]
    initials = initials.upper()

    if not background_color:
        background_color, text_color = get_contrasting_colors()

    avatar = generate_avatar(initials=initials, background_color=background_color, text_color=text_color, border_thickness=5)
    # Удаляем старый файл, если он есть
    if user.avatar:
        old_avatar_path = user.avatar.path  # Полный путь к файлу
        if os.path.exists(old_avatar_path):
            os.remove(old_avatar_path)
    user.avatar.save(f'{username}_avatar.png', avatar, save=False)
    user.save()


def generate_avatar(initials, background_color='white', text_color='black', border_thickness=5):
    # Размер изображения
    image_size = (150, 150)
    
    # Создаем изображение с прозрачным фоном (RGBA)
    image = Image.new('RGBA', image_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    # Радиус круга
    radius = image_size[0] // 2

    # Рисуем ободок (толщина border_thickness)
    draw.ellipse(
        (border_thickness // 2, border_thickness // 2, image_size[0] - border_thickness // 2, image_size[1] - border_thickness // 2),
        outline=text_color, width=border_thickness
    )

    # Рисуем сам круг (внутри ободка)
    draw.ellipse(
        (border_thickness, border_thickness, image_size[0] - border_thickness, image_size[1] - border_thickness),
        fill=background_color
    )

    # Выбираем шрифт
    try:
        # font = ImageFont.truetype('arial.ttf', 60)
        font = ImageFont.truetype("DejaVuSans.ttf", 60)  # Универсальный вариант
    except IOError:
        font = ImageFont.load_default()
        print("Не найден шрифт. Использован: ===", font)

    # Рассчитываем размеры текста
    text_bbox = draw.textbbox((0, 0), initials, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Определяем координаты для центрирования текста
    text_position = ((image_size[0] - text_width) / 2, (image_size[1] - text_height) / 2 - text_bbox[1])

    # Добавляем текст
    draw.text(text_position, initials, fill=text_color, font=font)

    # Сохраняем изображение в память
    image_io = io.BytesIO()
    image.save(image_io, format='PNG')
    image_content = ContentFile(image_io.getvalue(), name=f'{initials}.png')

    return image_content



# from PIL import Image, ImageDraw, ImageFont
# import io
# from django.core.files.base import ContentFile

# def generate_avatar(initials, background_color='white', text_color='black'):
#     # Размер изображения
#     image_size = (100, 100)
    
#     # Создаем изображение с прозрачным фоном (RGBA)
#     image = Image.new('RGBA', image_size, (255, 255, 255, 0))
#     draw = ImageDraw.Draw(image)
    
#     # Рисуем круг
#     draw.ellipse((0, 0, image_size[0], image_size[1]), fill=background_color)

#     # Выбираем шрифт
#     try:
#         font = ImageFont.truetype('arial.ttf', 40)
#     except IOError:
#         font = ImageFont.load_default()
    
#     # Рассчитываем размеры текста
#     text_bbox = draw.textbbox((0, 0), initials, font=font)
#     text_width = text_bbox[2] - text_bbox[0]
#     text_height = text_bbox[3] - text_bbox[1]

#     # Определяем координаты для центрирования текста
#     text_position = ((image_size[0] - text_width) / 2, (image_size[1] - text_height) / 2 - text_bbox[1])

#     # Добавляем текст
#     draw.text(text_position, initials, fill=text_color, font=font)

#     # Сохраняем изображение в память
#     image_io = io.BytesIO()
#     image.save(image_io, format='PNG')
#     image_content = ContentFile(image_io.getvalue(), name=f'{initials}.png')

#     return image_content


# def generate_avatar(initials, background_color='white', text_color='black'):
#     # Create a blank image with a white background
#     image_size = (100, 100)
#     image = Image.new('RGB', image_size, color=background_color)
#     draw = ImageDraw.Draw(image)

#     # Choose a font (make sure you have a font file or use a default one)
#     try:
#         font = ImageFont.truetype('arial.ttf', 40)
#     except IOError:
#         font = ImageFont.load_default()

#     # Calculate text size and position
#     text_bbox = draw.textbbox((0, 0), initials, font=font)
#     text_width = text_bbox[2] - text_bbox[0]
#     text_height = text_bbox[3] - text_bbox[1]
#     text_position = ((image_size[0] - text_width) / 2, (image_size[1] - text_height) / 2)

#     # Draw the initials on the image
#     draw.text(text_position, initials, fill=text_color, font=font)

#     # Save the image to an in-memory file
#     image_io = io.BytesIO()
#     image.save(image_io, format='PNG')
#     image_content = ContentFile(image_io.getvalue(), name=f'{initials}.png')

#     return image_content
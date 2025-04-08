from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from my_magic_room.models import achivments, memes, stories, tales, krissy_blog, posts
from django.shortcuts import get_object_or_404
from pprint import pprint


def check_permissions(request):
    tariff = request.user.user_tariff
    if tariff == None:
        return redirect('tariff_list')
    if request.user.user_tariff.magic_room_access == False:
        return redirect('no_acess')
    

# Получение стандартного списка параметров публикаций для формирования списка публикаций
def get_publications_data(source):
    # Создаем новый список с дополнительным полем
    publications = []
    for index, pub in enumerate(source):
        if index % 16 == 0:
            a_type = 'a_1'
        elif index % 9 == 0:
            a_type = 'a_2'
        else:
            a_type = ''

        new_pub = {
            'title': pub.title,
            'anonce': pub.anonce,
            'image': None,
            'description': pub.description,
            'created_at': pub.created_at,
            'slug': pub.slug,
            'a_type': a_type,  # Тип анонса
        }
        if pub.image:
            new_pub['image'] = pub.image
        publications.append(new_pub)
    return publications


@login_required
def achievements_list(request):
    permission_check = check_permissions(request)
    if permission_check:
        return permission_check
    user = request.user
    achievements = user.achievements.all()
    return render(request, 'achievements_list.html', {'achievements': achievements, 'page_class': 'not-apply-body-height'})


@login_required
def memes_list(request):
    permission_check = check_permissions(request)
    if permission_check:
        return permission_check
    mems = memes.objects.all()
    return render(request, 'memes_list.html', {'memes': mems, 'page_class': 'not-apply-body-height'})


@login_required
def meme_detail(request, slug):
    permission_check = check_permissions(request)
    if permission_check:
        return permission_check
    meme = get_object_or_404(memes, slug=slug)
    return render(request, 'meme_detail.html', {'meme': meme, 'page_class': 'not-apply-body-height'})


@login_required
def tales_list(request):
    permission_check = check_permissions(request)
    if permission_check:
        return permission_check
    tals = tales.objects.all().order_by('-created_at')
    return render(request, 'tales_list.html', {'tales': tals, 'page_class': 'not-apply-body-height'})


@login_required
def tale_detail(request, slug):
    permission_check = check_permissions(request)
    if permission_check:
        return permission_check
    tale = get_object_or_404(tales, slug=slug)
    return render(request, 'tale_detail.html', {'tale': tale, 'page_class': 'not-apply-body-height'})



from django.template.loader import render_to_string
import logging
logger = logging.getLogger(__name__)
from django.utils.timezone import now
from django.http import HttpResponse


@login_required
def preview_tale(request):
    try:
        if request.method == 'POST':
            # Получаем данные из формы
            title = request.POST.get('title')
            anonce = request.POST.get('anonce')
            description = request.POST.get('description')
            # if description == "":
            #     description = "No description"

            # Создаем виртуальный объект "tale" для предпросмотра
            # Пример объекта:
            tale = {
                'title': title,
                'anonce': anonce,
                'description': description,
                'created_at': now(),  # Используем текущую дату как дату создания
            }

            # Генерируем HTML-контент для предпросмотра
            html_content = render_to_string('tale_detail.html', {'tale': tale, 'page_class': 'not-apply-body-height'})
            # pprint(html_content)

            # Возвращаем HTML в теле ответа
            return HttpResponse(html_content, content_type="text/html")
            # return render(request, 'tale_detail_preview.html', {'tale': tale, 'page_class': 'not-apply-body-height'})

        return HttpResponse('Invalid request method', status=400)

    except Exception as e:
        logger.error("Ошибка в preview_tale: %s", e)
        return HttpResponse('Server error', status=500)


# Показ СПИСКА публикаций КРИССИ БЛОГА
@login_required
def krissy_blog_list(request):
    permission_check = check_permissions(request)
    if permission_check:
        return permission_check
    krissy_blog_posts = krissy_blog.objects.all().order_by('-created_at')

    # Создаем новый список с дополнительным полем
    publications = get_publications_data(krissy_blog_posts)

    return render(request, 'krissy_blog_list.html', {'krissy_blogs': publications, 'page_class': 'not-apply-body-height'})


# Показ ОДИНОЧНОЙ публикации КРИССИ БЛОГА
@login_required
def krissy_blog_detail(request, slug):
    permission_check = check_permissions(request)
    if permission_check:
        return permission_check
    krissy_blog_post = get_object_or_404(krissy_blog, slug=slug)
    return render(request, 'krissy_blog_detail.html', {'krissy_blog': krissy_blog_post, 'page_class': 'not-apply-body-height'})


# Показ СПИСКА ПОСТОВ
@login_required
def posts_list(request):
    permission_check = check_permissions(request)
    if permission_check:
        return permission_check
    posts_data = posts.objects.all().order_by('-created_at')

    # Создаем новый список с дополнительным полем
    publications = get_publications_data(posts_data)

    return render(request, 'posts_list.html', {'publications': publications, 'page_class': 'not-apply-body-height'})


# Показ ОДИНОЧНОГО ПОСТА
@login_required
def post_detail(request, slug):
    # print(dir(request.user))
    permission_check = check_permissions(request)
    if permission_check:
        return permission_check
    publication = get_object_or_404(posts, slug=slug)
    return render(request, 'post_detail.html', {'publication': publication, 'page_class': 'not-apply-body-height'})


# Предпросмотр для ВСЕХ типов публикаций
@login_required
def preview_post(request):
    try:
        if request.method == 'POST':
            # Получаем данные из формы
            title = request.POST.get('title')
            anonce = request.POST.get('anonce')
            description = request.POST.get('description')
            preview_type = request.POST.get('preview_type')

            # Создаем виртуальный объект "krissy_blog" для предпросмотра
            # Пример объекта:
            publication = {
                'title': title,
                'anonce': anonce,
                'description': description,
                'created_at': now(),  # Используем текущую дату как дату создания
            }

            # Генерируем HTML-контент для предпросмотра
            html_content = ""
            if preview_type == 'post':
                html_content = render_to_string('post_detail.html', {'publication': publication, 'page_class': 'not-apply-body-height'})
            elif preview_type == 'crissy_blog':
                html_content = render_to_string('krissy_blog_detail.html', {'krissy_blog': publication, 'page_class': 'not-apply-body-height'})

            # Возвращаем HTML в теле ответа
            return HttpResponse(html_content, content_type="text/html")

        return HttpResponse('Invalid request method', status=400)

    except Exception as e:
        logger.error("Ошибка в preview_posts: %s", e)
        return HttpResponse('Server error', status=500)


@login_required
def stories_list(request):
    permission_check = check_permissions(request)
    if permission_check:
        return permission_check
    stores = stories.objects.all().order_by('-created_at')
    return render(request, 'stories_list.html', {'stories': stores, 'page_class': 'not-apply-body-height'})


@login_required
def storie_detail(request, slug):
    permission_check = check_permissions(request)
    if permission_check:
        return permission_check
    storie = get_object_or_404(stories, slug=slug)
    return render(request, 'storie_detail.html', {'storie': storie, 'page_class': 'not-apply-body-height'})


# Артем: Создал для страницы нового поста
@login_required
def new_post(request):
    permission_check = check_permissions(request)
    if permission_check:
        return permission_check
    return render(request, 'new_post.html', {'page_class': 'not-apply-body-height'})


@login_required
def magic_room(request):
    permission_check = check_permissions(request)
    if permission_check:
        return permission_check
    user = request.user
    remaining_time = user.remaining_paid_time
    oll_time_site = user.oll_time_in_site
    return render(request, 'magic_room.html', {'remaining_time': remaining_time, 'oll_time_site' : oll_time_site})


# @login_required
# def preview_storie(request, pk):
#     storie = get_object_or_404(stories, pk=pk)
#     return render(request, 'storie_detail.html', {'storie': storie})

import json

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .forms import UserInterestForm
from .utils import ask_ai
from chat.models import ChatContext, ChatMessage, AiParametrs, UserInterest, InterestCategory


@login_required
def chat(request):
    tariff = request.user.user_tariff
    if tariff == None:
        return redirect('tariff_list')
    if request.method == 'POST':
        if request.user.remaining_messages <= 0:
            return JsonResponse({'error': 'Закончились сообщения'}, status=400)
        json_data = json.loads(request.body)
        text_data = json_data.get("text_data")
        if text_data:
            user = request.user
            user_len_request = user.user_tariff.query_length
            if len(text_data) > user_len_request:
                return JsonResponse({'error': 'Длина текста превышает разрешённый лимит'}, status=400)
            processed_text = ask_ai(message=text_data, user=user)
            text = processed_text["text"]

            # audio_url = processed_text["audio"]
            # response_data = {
            #     "text": text,
            #     "audio": audio_url
            # }
            response_data = {
                "text": text
            }
            return JsonResponse(response_data)
        else:
            return HttpResponse('Ошибка: Пустой текст', content_type='text/plain')

    chat_context, _ = ChatContext.objects.get_or_create(user=request.user)
    messages = chat_context.context  # Здесь будут все сообщения
    max_len_msg = request.user.user_tariff.query_length
    # Передаем сообщения в шаблон
    return render(request, 'chat/chat.html', {'messages': messages, 'max_len_msg': max_len_msg})


@login_required
def remove_context(request):
    user = request.user
    User = get_user_model()
    try:
        # Получаем экземпляр ChatContext для данного пользователя
        chat_context = ChatContext.objects.get(user_id=user.id)
        # Удаляем запись
        chat_context.delete()
        print("Запись успешно удалена.")
    except ChatContext.DoesNotExist:
        print("Запись не найдена.")
    return redirect('chat')


def assign_interests(request):
    if request.method == 'POST':
        form = UserInterestForm(request.POST, user=request.user)
        if form.is_valid():
            interests = form.cleaned_data['interests']
            # Артем: Поменял логику добавления интересов
            UserInterest.objects.filter(user=request.user).delete()
            for interest in interests:
                UserInterest.objects.create(user=request.user, interest=interest)
            return redirect('chat')
    else:
        form = UserInterestForm(user=request.user)

    categories = InterestCategory.objects.prefetch_related('interests').all()
    
    # Артем: Добавил интересы пользователя, чтобы проверять их наличие в верстке
    user_interests = UserInterest.objects.filter(user_id=request.user.id).values_list("interest_id", flat=True)

    return render(request, 'assign_interests.html', {
        'form': form,
        'categories': categories,
        'user_interests': user_interests
    })

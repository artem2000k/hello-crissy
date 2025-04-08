import tiktoken  # Не забудьте установить tiktoken через pip install tiktoken
from cohere import Client
from chat.models import ChatMessage, AiParametrs, ChatContext, UserInterest
from pprint import pprint

model_id = "command-r-plus"
client = Client(api_key='asexPJmG3I08mjaCkERlcA8MxYV5yypjlFRLbGlj')


def count_tokens(text):
    encoder = tiktoken.get_encoding("cl100k_base")  # Используем универсальный токенизатор
    return len(encoder.encode(text))


def summarize_context(context):
    messages = "\n".join([f"{entry['role']}: {entry['message']}" for entry in context])

    # Получаем сводку от GPT
    summary_response = client.chat(
        message="Summarize the following conversation in a way that keeps important information about the user and the latest points of discussion:\n" + messages,
        model="command-r-plus-08-2024",
        preamble="Summarizer",
        temperature=0.5,
        max_tokens=1000  # Ограничиваем длину ответа
    )

    return summary_response.text.strip()


def trim_message_to_max_tokens(message, max_tokens=300):
    token_count = count_tokens(message)
    if token_count > max_tokens:
        words = message.split()
        trimmed_message = ""
        current_token_count = 0

        for word in words:
            word_token_count = count_tokens(word)
            if current_token_count + word_token_count > max_tokens:
                break
            trimmed_message += word + " "
            current_token_count += word_token_count

        return trimmed_message.strip()

    return message


def ask_ai(message, user):
    chat_context, created = ChatContext.objects.get_or_create(user=user)
    context = chat_context.context
    aiparams, created = AiParametrs.objects.get_or_create(
        defaults={"character": "ты тестовый ассистент, напоминай юзеру о необходимости сменить характер",
                  "temperature": 0.7}
    )
    # user_interests = UserInterest.objects.filter(user=user).select_related('interest')
    #!todo перенести в сам чат кнопки
    # interest_names = [interest.interest.name for interest in user_interests]

    # Формируем описание характера с учетом интересов пользователя
    character = aiparams.character
    # if interest_names:
    #     character += f" Пользователь интересуется следующими темами: {', '.join(interest_names)}."
    temperature = aiparams.temperature
    # Обрезаем сообщение пользователя, если оно слишком длинное
    message = trim_message_to_max_tokens(message)

    # Добавляем новое сообщение пользователя в контекст
    context.append({"role": "User", "message": message})
    # Проверяем, если контекст достиг 700 токенов, создаем суммаризацию
    if count_tokens("\n".join([entry['message'] for entry in context])) >= 1600:
        print("done")
        summary = summarize_context(context)
        # Сохраняем только последние два сообщения и добавляем сводку в начало
        context = context[-3:]  # Берем последние два сообщения
        context.insert(0, {"role": "Chatbot", "message": summary})
    response = client.chat(
        message=message,
        model="command-r-plus-08-2024",
        preamble=character,
        temperature=temperature,
        max_tokens=500,  # Ограничиваем длину ответа
        prompt_truncation='AUTO',
        chat_history=context
    )

    user.remaining_messages -= 1
    user.save()
    ai_answer = response.text.strip()

    # Добавляем ответ Chatbot'а в контекст
    context.append({"role": "Chatbot", "message": ai_answer})

    # Сохраняем обновленный контекст
    chat_context.context = context
    chat_context.save()

    # Сохраняем сообщение в базе данных
    ChatMessage.objects.create(user=user, message=message, response=ai_answer)

    return {"text": ai_answer}

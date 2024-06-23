from django.conf import settings

from celery import shared_task
import requests


@shared_task
def send_email(subject: str, message: str, to_email: str) -> bool:
    """
    Отправляет электронное письмо асинхронно с использованием API Elastic Email.

    Аргументы:
    - subject: Тема письма.
    - message: Текст письма.
    - to_email: Адрес получателя.

    Возвращает:
    - True, если письмо было успешно отправлено.
    - False, если произошла ошибка при отправке.

    Подробности:
    Функция формирует данные для отправки, включая ключ API, адрес отправителя,
    адрес получателя, тему письма и текст письма в HTML и текстовом форматах.
    Затем она отправляет POST запрос на указанный URL для отправки писем.
    Если ответ от сервера Elastic Email указывает на успешную отправку
    (поле 'success' в JSON ответе), функция возвращает True.
    В противном случае возвращается False.
    """
    api_key: str = settings.ELASTIC_EMAIL_API_KEY
    from_email: str = settings.EMAIL_HOST_USER

    data: dict = {
        'apikey': api_key,
        'from': from_email,
        'to': to_email,
        'subject': subject,
        'bodyHtml': message,
        'bodyText': message,
    }

    response = requests.post(settings.URL_SEND, data=data)
    response_json: dict = response.json()

    if response_json.get('success'):
        return True
    else:
        return False

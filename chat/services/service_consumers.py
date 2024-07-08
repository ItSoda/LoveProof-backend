import json
from typing import Awaitable

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chat.models import Message


async def get_messages_chat(chat_id: int) -> list:
    """
    Загружает существующие сообщения чата из базы данных.

    Args:
        chat_id (int): Идентификатор чата для загрузки сообщений.

    Returns:
        list: Список объектов сообщений чата.
    """
    messages = await sync_to_async(list)(Message.objects.filter(chat=chat_id).order_by('created_at'))
    return messages

async def send_messages_chat(consumer: AsyncWebsocketConsumer, messages: list) -> Awaitable[None]:
    """
    Отправляет сообщения чата клиенту через WebSocket.

    Args:
        consumer (AsyncWebsocketConsumer): Потребитель WebSocket.
        messages (list): Список объектов сообщений чата.

    Returns:
        Awaitable[None]: Асинхронное ожидание завершения отправки сообщений клиенту.
    """
    for message in messages:
        user = await sync_to_async(lambda: message.user.username)()
        await consumer.send(text_data=json.dumps({
            'message': message.message,
            'user': user,
            'created_at': message.created_at.isoformat()
        }))

async def save_message(chat_id: int, user_id: int, message: str) -> Awaitable[Message]:
    """
    Сохраняет сообщение в базе данных чата и возвращает объект сообщения.

    Args:
        chat_id (int): Идентификатор чата, к которому относится сообщение.
        user_id (int): Идентификатор пользователя, отправившего сообщение.
        message (str): Текст сообщения.

    Returns:
        Awaitable[Message]: Асинхронное ожидание завершения создания сообщения в базе данных.
                            Возвращает объект сообщения (Message).
    """
    message_obj = await sync_to_async(Message.objects.create)(
        chat_id=chat_id,
        user_id=user_id,
        message=message
    )
    return message_obj

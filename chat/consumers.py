import json

from channels.generic.websocket import AsyncWebsocketConsumer

from chat.services.service_consumers import get_messages_chat, send_messages_chat, save_message


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket-потребитель для работы с чатом.

    Атрибуты:
        chat_id (str): id чата, связанного с этим потребителем.
        chat_group_name (str): Имя группы, соответствующее комнате чата.

    Методы:
        connect(): Вызывается при установке WebSocket-соединения.
        disconnect(close_code): Вызывается при закрытии WebSocket-соединения.
        receive(text_data): Вызывается при получении сообщения от клиента через WebSocket.
        chat_message(event): Обрабатывает и отправляет сообщения в группу чата.

    Использование:
        Этот потребитель управляет WebSocket-соединениями для конкретной комнаты чата.
        Позволяет клиентам подключаться, отправлять и получать сообщения в чате.
    """
    async def connect(self):
        """
        Вызывается при начале рукопожатия WebSocket в процессе установки соединения.
        Присоединяет потребителя к определенной группе чата и отправляет существующие сообщения клиенту.
        """
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f"chat_{self.chat_id}" 

        if self.scope['user'].is_anonymous:
            await self.close()

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.accept()

        messages = await get_messages_chat(self.chat_id)  # Получаются существующие сообщения чата
        await send_messages_chat(self, messages)  # Отправляются существующие сообщения чата клиенту

    async def disconnect(self, close_code: int):
        """
        Вызывается при закрытии WebSocket-соединения по любой причине.
        Удаляет потребителя из группы чата.
        """
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data: str):
        """
        Вызывается при получении сообщения от клиента через WebSocket.
        Сохраняет новое сообщение в базе данных и отправляет его в группу чата.
        """
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user_id = text_data_json['user_id']

        # Создается новое сообщение в базе данных
        new_message = await save_message(self.chat_id, user_id, message)

        # Отправляется новое сообщение в группу чата
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': new_message.message,
                'user_id': new_message.user_id,
                'created_at': new_message.created_at.isoformat()
            }
        )

    async def chat_message(self, event: dict):
        """
        Обрабатывает событие при получении сообщения чата из группы.
        Отправляет полученное сообщение клиенту через WebSocket.
        """
        message = event['message']
        user_id = event['user_id']

        await self.send(text_data=json.dumps({
            'message': message,
            'user': user_id,
        }))

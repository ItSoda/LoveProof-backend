from typing import Union

from django.db import close_old_connections
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken

from channels.auth import BaseMiddleware
from channels.db import database_sync_to_async

from users.models import User


class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware для аутентификации пользователей через JWT-токен.

    Если токен недействителен или отсутствует, в область WebSocket добавляется объект AnonymousUser.

    Параметры:
        app (Callable): Следующее приложение в цепочке middleware.

    Методы:
        - __call__: Обработка WebSocket соединения, проверка JWT-токена, извлечение пользователя
            из базы данных и добавление его в область scope.

        - get_user: Асинхронно получает пользователя из базы данных по его id.
    """

    def __init__(self, app):
        """
        Инициализация middleware с указанием следующего приложения в цепочке.

        Параметры:
            app (Callable): Следующее приложение в цепочке middleware.
        """
        self.app = app

    async def __call__(self, scope, receive, send):
        """
        Обработка WebSocket соединения для аутентификации через JWT-токен.

        Проверяет наличие и валидность JWT-токена в заголовках запроса. В случае успеха добавляет пользователя в
        область scope. В случае ошибки или отсутствия токена, добавляет AnonymousUser.

        Параметры:
            scope (dict): Область соединения WebSocket.
            receive (Callable): Функция для приема данных WebSocket.
            send (Callable): Функция для отправки данных WebSocket.

        Возвращает:
            await: Вызов следующего middleware в цепочке.
        """
        close_old_connections()

        headers = dict(scope['headers'])
        if b'authorization' in headers:
            try:
                # Извлечение токена из заголовков запроса
                token = headers[b'authorization'].decode().split()[1]
                is_valid = UntypedToken(token)
                decoded_data = is_valid.payload
                user_id = int(decoded_data.get('user_id'))
                # Получение пользователя из базы данных и добавление его в scope
                scope['user'] = await self.get_user(user_id)
            except (InvalidToken, TokenError, IndexError, KeyError) as e:
                print(e)
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        # Вызов следующего middleware в цепочке
        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id: int) -> Union[User, AnonymousUser]:
        """
        Асинхронно получает пользователя из базы данных по его id.

        Параметры:
            user_id (int): id пользователя.

        Возвращает:
            Union[User, AnonymousUser]: Объект пользователя или AnonymousUser, если пользователь не найден.
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()

from django.db import models

from users.models import User


class Chat(models.Model):
    participants = models.ManyToManyField(
        User,
        related_name='chats',
        verbose_name='Участники'
    )
    created_at = models.DateField(auto_now=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    def __str__(self):
        return f'Chat {self.id}'


class Message(models.Model):
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Чат'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default='Удаленный пользователь',
        related_name='sent_messages',
        verbose_name='Отправитель'
    )
    message = models.TextField(max_length=2500, verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время отправки')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f'Message {self.id} in {self.chat}'

from django.db import models

from users.models import User


class Mission(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В ожидании'),
        ('ongoing', 'Текущая'),
        ('passed', 'Пройдено')
    )

    client = models.ForeignKey(
        to=User,
        related_name='client_missions',
        on_delete=models.SET_DEFAULT,
        default='Удаленный пользователь',
        verbose_name='Клиент'
    )
    checker = models.ForeignKey(
        to=User,
        related_name='checker_missions',
        on_delete=models.SET_DEFAULT,
        default='Удаленный пользователь',
        verbose_name='Проверяющий'
    )
    price = models.PositiveSmallIntegerField(default=0, verbose_name='Цена')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Миссия'
        verbose_name_plural = 'Миссии'

    def __str__(self) -> str:
        return f'Mission #{self.id} for client {self.client.username}, checker {self.checker.username}'

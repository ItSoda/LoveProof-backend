from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator


class User(AbstractUser):
    GENDER_CHOICES = (
        ('male', 'Мужчина'),
        ('female', 'Женщина'),
        ('other', 'Другое'),
        ('prefer_not_to_say', 'Предпочитаю не говорить')
    )

    ROLE_CHOICES = (
        ('client', 'Клиент'),
        ('checker', 'Проверяющий'),
        ('moderator', 'Модератор'),
    )

    photo = models.ImageField(upload_to='users', verbose_name='Фото')
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, verbose_name='Гендер')
    description = models.TextField(verbose_name='Описание')
    age = models.PositiveSmallIntegerField(null=True, validators=[MinValueValidator(18)], verbose_name='Возраст')
    tags = models.ManyToManyField(to='Tag', related_name='users', verbose_name='Тег')
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='client', verbose_name='Роль')
    price = models.PositiveSmallIntegerField(default=0, verbose_name='Цена')
    email_confirmed = models.BooleanField(default=False, verbose_name='Email подтвержден')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class Tag(models.Model):
    title = models.CharField(max_length=15, verbose_name='Название')

    def __str__(self) -> str:
        return self.title

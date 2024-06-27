from datetime import timedelta
import uuid

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.utils.timezone import now

from users.tasks import send_email


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
    location = models.ForeignKey(to='Location', on_delete=models.SET_NULL, null=True, related_name='users', verbose_name='Локация')
    ethnicity = models.ForeignKey(to='Ethnicity', on_delete=models.SET_NULL, null=True, related_name='users', verbose_name='Этничность')
    social_media = models.ManyToManyField(to='SocialMedia', related_name='users', verbose_name='Социальная сеть')
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='client', verbose_name='Роль')
    price = models.PositiveSmallIntegerField(default=0, verbose_name='Цена')
    email_confirmed = models.BooleanField(default=False, verbose_name='Email подтвержден')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username

    def save(self, *args, **kwargs):
        """
        Сохраняет объект пользователя.

        Перед сохранением проверяет, является ли объект новым.
        После успешного сохранения инициирует отправку email с запросом на подтверждение
        адреса электронной почты, если пользователь только что зарегистрирован.
        """
        created = not self.pk 
        super().save(*args, **kwargs)

        # if created:
        #     self._send_email_verification()

    def _send_email_verification(self):
        """
        Создает объект EmailVerification для текущего пользователя.

        Отправляет email с запросом на подтверждение адреса электронной почты.
        """
        expiration = now() + timedelta(hours=24)
        email_verification = EmailVerification.objects.create(code=uuid.uuid4(), user=self, expiration=expiration)
        email_verification.send_verification_email()


class Tag(models.Model):
    title = models.CharField(max_length=15, verbose_name='Название')

    def __str__(self) -> str:
        return self.title


class Location(models.Model):
    title = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'

    def __str__(self) -> str:
        return self.title


class Ethnicity(models.Model):
    title = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'Этничность'
        verbose_name_plural = 'Этничности'

    def __str__(self) -> str:
        return self.title


class SocialMedia(models.Model):
    title = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Социальная сеть'
        verbose_name_plural = 'Социальные сети'


class EmailVerification(models.Model):
    """
    Модель для хранения кодов подтверждения email пользователей.

    Атрибуты:
    - code: UUIDField, уникальный идентификатор кода подтверждения.
    - user: ForeignKey, связь с моделью User, для которой создан код подтверждения.
    - created: DateTimeField, дата и время создания записи.
    - expiration: DateTimeField, дата и время истечения срока действия кода.

    Методы:
    - send_verification_email: Отправляет email для подтверждения адреса электронной почты пользователю.
    - is_expired: Проверяет, истек ли срок действия кода подтверждения.

    Связи:
    - User: Модель пользователя, для которой создаются коды подтверждения email.
    """
    code = models.UUIDField(unique=True)
    user = models.ForeignKey(to=User, related_name='email_verifications', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    def __str__(self):
        return f'Email verification for {self.user.email}'

    def send_verification_email(self):
        """
        Отправляет email для подтверждения адреса электронной почты.
        """
        link = reverse('email_verify', kwargs={'email': self.user.email, 'code': self.code})
        verification_url = f'{settings.DOMAIN_NAME}{link}'
        subjects = f'Пожалуйста, подтвердите свой адрес электронной почты'
        message = f'Для завершения регистрации, подтвердите свой адрес электронной почты, перейдите по ссылке: {verification_url}'

        send_email.delay(
            subject=subjects,
            message=message,
            to_email=self.user.email,
        )

    def is_expired(self):
        """
        Проверяет, истек ли срок действия кода подтверждения.

        Возвращает:
        - True, если срок действия истек.
        - False, если срок действия еще не истек.
        """
        return True if now() >= self.expiration else False

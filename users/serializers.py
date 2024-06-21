import re

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

import requests

from users.models import User


class UserLoginSerializer(serializers.Serializer):
    """
    Сериализатор для входа пользователя.

    Поля:
    - email: поле для ввода электронной почты пользователя.
    - password: поле для ввода пароля пользователя.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.

    Поля:
    - username: Имя пользователя.
    - email: Адрес электронной почты пользователя (обязательное поле, должно быть уникальным).
    - gender: Пол пользователя (обязательное поле).
    - password: Пароль пользователя (обязательное поле).
    - confirm_password: Подтверждение пароля (обязательное поле).

    Валидация:
    - Проверка совпадения полей `password` и `confirm_password`.
    - Проверка наличия хотя бы одной большой буквы, одной маленькой буквы и одной цифры в пароле.
    - Пароль должен содержать как минимум 6 символов.

    Создание пользователя:
    - Удаление `confirm_password` из `validated_data`.
    - Создание пользователя с использованием `create_user` метода модели `User`.
    - Отправка письма с подтверждением на указанный адрес электронной почты после успешной регистрации.
    """
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'gender', 'password', 'confirm_password')
        extra_kwargs = {
            'gender': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        errors = []

        if len(attrs['password']) < 6:
            errors.append('The password must contain at least 6 characters')
        if not re.search(r'[A-Z]', attrs['password']):
            errors.append('The password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', attrs['password']):
            errors.append('The password must contain at least one lowercase letter')
        if not re.search(r'\d', attrs['password']):
            errors.append('The password must contain at least one digit')

        if errors:
            raise serializers.ValidationError({'password': errors})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            **validated_data,
            is_active = False
        )
        self._send_email_verification(user)
        return user

    def _send_email_verification(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_url = f'http://yourdomain.com/verify-email/{uid}/{token}/'
        subject = 'Подтвердите ваш email'
        message = f'Для подтверждения вашего email перейдите по ссылке: {verification_url}'

        url = settings.URL_SEND
        api_key = settings.ELASTIC_EMAIL_API_KEY  # Подставьте ваш API ключ
        from_email = settings.EMAIL_HOST_USER  # Подставьте ваш email, от которого будет отправляться письмо

        data = {
            'apikey': api_key,
            'from': from_email,
            'to': user.email,
            'subject': subject,
            'bodyHtml': message,
            'bodyText': message,
        }

        response = requests.post(url, data=data)
        response_json = response.json()

        if response_json['success']:
            return True
        else:
            raise serializers.ValidationError({'email': 'Failed to send verification email'})

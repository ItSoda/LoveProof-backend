import re

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

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
        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления профиля пользователя.

    Поля:
    - username (str): Имя пользователя.
    - email (str): Адрес электронной почты пользователя.
    - gender (str): Пол пользователя.

    Поля:
    - password (str): Пароль, необходимый для удаления учетной записи пользователя. Является доступным только для записи и обязательным.
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'gender']


class UserDeleteSerializer(serializers.Serializer):
    """
    Cериализатор для удаления учетной записи пользователя

    Поля:
    - password (str): Пароль пользователя (обязательное поле).
    """
    password = serializers.CharField(write_only=True, required=True)


class CheckerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'photo', 'age', 'price']


class CheckerDetailSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ('username', 'gender', 'description', 'photo', 'tags', 'price')

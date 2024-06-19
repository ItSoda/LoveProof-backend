from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

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
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'gender', 'password', 'confirm_password')
        extra_kwargs = {
            'gender': {'required': True}
        }

    def validate(self, attrs):
        """
        Проверка совпадения полей пароля.
        """
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            **validated_data,
            is_active = False
        )
        return user

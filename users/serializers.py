from rest_framework import serializers


class UserLoginSerializer(serializers.Serializer):
    """
    Сериализатор для входа пользователя.

    Сериализует данные входа пользователя, включая электронную почту (email) и пароль (password).

    Поля:
    - email: поле для ввода электронной почты пользователя.
    - password: поле для ввода пароля пользователя.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.serializers import  UserLoginSerializer


class UserLoginAPIView(APIView):
    """
    API view для аутентификации пользователя.

    Принимает POST запрос с данными в формате:
    {
        'email': 'адрес_электронной_почты',
        'password': 'пароль'
    }

    Возвращает токены доступа в случае успешной аутентификации, или сообщение об ошибке в случае неудачи.

    HTTP коды ответа:
    - 200 OK: Успешная аутентификация, возвращает токены доступа.
    - 401 Unauthorized: Неверные учетные данные.
    - 404 NOT_FOUND: Пользователь с таким email не найден.
    """
    def post(self, request, *args, **kwargs):
        """
        Обработка POST запроса для аутентификации пользователя.
        """
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = User.objects.filter(email=email).first()
        if user is None:
                return Response({'detail': 'Пользователь с таким email не найден.'}, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({'detail': 'Неверные учетные данные'}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = RefreshToken.for_user(user)

        return Response({
            'refresh': str(tokens),
            'access': str(tokens.access_token),
        }, status=status.HTTP_200_OK)


class UserLogoutAPIView(APIView):
    """
    API view для выхода пользователя из аккаунта.

    Пользователь должен быть аутентифицирован и передать действительный refresh_token 
    для аннулирования токена доступа.

    Принимает POST запрос с данными в формате:
    {
        'refresh_token': 'refresh token пользователя'
    }

    HTTP коды ответа:
    - 200 OK: Токен успешно аннулирован, пользователь вышел из аккаунта.
    - 400 Bad Request: Ошибка в запросе, не удалось аннулировать токен.
    - 401 Unauthorized: Пользователь не аутентифицирован.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Обработка POST запроса для выхода пользователя из аккаунта.
        """
        try:
            refresh_token = request.data['refresh_token']
        except KeyError:
            refresh_token = None

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'detail': 'Вы успешно вышли из аккаунта.'}, status=status.HTTP_200_OK)

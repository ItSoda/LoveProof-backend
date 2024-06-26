from typing import Optional

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from users.models import User, EmailVerification
from users.serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserProfileUpdateSerializer, UserDeleteSerializer,
    CheckerListSerializer, CheckerDetailSerializer
    )
from users.services.views_service import get_list_checkers, get_checker
from users.filters import CheckerFilter


class UserRegistrationView(APIView):
    """
    API view для регистрации нового пользователя.

    Принимает POST запрос с данными в формате:
    {
        "username": "имя_пользователя",
        "email": "адрес_электронной_почты",
        "gender": "пол_пользователя",
        "password": "пароль",
        "confirm_password": "подтверждение_пароля"
    }

    HTTP коды ответа:
    - 201 Created: Пользователь успешно зарегистрирован.
    - 400 Bad Request: Ошибка в запросе или неверные данные для регистрации.
    """
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class VerifyEmailAPIView(APIView):
    """
    API view для подтверждения email пользователя.

    Проверяет токен подтверждения email и устанавливает статус подтверждения для пользователя.
    При успешном подтверждении email пользователь становится активным (is_active=True) и его email_confirmed
    устанавливается в True

    Параметры запроса:
    - code: UUID код подтверждения, связанный с email пользователя.
    - email: Email адрес пользователя, для которого выполняется подтверждение.

    HTTP коды ответа:
    - HTTP 200 OK: Email успешно подтвержден.
    - HTTP 400 Bad Request: Недействительный токен или URL.
    
    Связанные модели:
    - User: Модель пользователя, в которой хранится информация о подтверждении email.
    - EmailVerification: Модель для хранения кодов подтверждения email пользователей.
    """
    def get(self, request, *args, **kwargs):
        """
        Обработка GET-запросов для подтверждения email пользователя на основе предоставленного кода и email.

        Извлекает пользователя на основе предоставленного email и проверяет токен подтверждения email (code).
        При действительном и неистекшем токене устанавливает email_confirmed пользователя в True и активирует его.
        """
        code = request.GET.get('code')
        email = request.GET.get('email')
        user = get_object_or_404(User, email=email)
        email_verifications = EmailVerification.objects.filter(code=code, user=user)
        try:
            if email_verifications.exists() and not email_verifications.last().is_expired():
                user.email_confirmed = True
                user.is_active = True
                user.save()
                return Response({'detail': 'Email успешно подтвержден.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Токен для подтверждения email истек или не существует.'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, EmailVerification.DoesNotExist):
            return Response({'detail': 'Недействительный URL для подтверждения email.'}, status=status.HTTP_400_BAD_REQUEST)


class ProfileAPIView(APIView):
    """
    API view для управления профилем пользователя.

    Пользователь должен быть аутентифицирован для доступа к данным профиля.

    Параметры запроса:
    - PUT:
        {
            "username": "имя_пользователя",
            "email": "адрес_электронной_почты",
            "gender": "пол_пользователя",
        }
    - DELETE:
        {
            "password": "пароль"
        }

    HTTP коды ответа:
    - GET:
        - 200 OK: Возвращает данные профиля текущего пользователя.
    - PUT:
        - 200 OK: Данные профиля успешно обновлены.
        - 400 Bad Request: Ошибка в запросе или неверные данные для обновления профиля.
    - DELETE:
        - 204 No Content: Аккаунт пользователя удален успешно.
        - 400 Bad Request: Ошибка в запросе или неверный пароль для удаления аккаунта.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileUpdateSerializer(user)
        return Response(serializer.data, status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        serializer = UserDeleteSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            password = serializer.validated_data['password']

            if not user.check_password(password):
                return Response({'password': 'Неправильный пароль'}, status=status.HTTP_400_BAD_REQUEST)
            user.delete()
            return Response({'detail': 'Ваш аккаунт был удален'}, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckerListAPIView(APIView):
    """
    API view для получения списка пользователей с ролью 'checker',
    с возможностью фильтрации.

    Поддерживаемые фильтры:
    - genders: фильтрация по полу
    - ethnicities: фильтрация по этнической принадлежности
    - locations: фильтрация по локации
    - socials: фильтрация по социальным сетям
    - ages: фильтрация по возрасту (диапазон)

    Возвращает поля: id, username, photo, age и price.

    HTTP коды ответа:
    - 200 OK: Успешный запрос
    - 204 No Content: Пользователи не найдены
    """
    filter_backends = [DjangoFilterBackend]
    filterset_class = CheckerFilter

    def get(self, request):
        queryset = get_list_checkers()

        if any(request.query_params.values()):  # Проверка фильтрации в запросе
            filtered_queryset = self.filterset_class(request.query_params, queryset=queryset).qs
            if not filtered_queryset.exists():
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            filtered_queryset = queryset  # Если нет фильтров, используется исходный queryset

        serializer = CheckerListSerializer(filtered_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CheckerDetailAPIView(APIView):
    """
    API view для получения детальной информации о пользователе 'checker' по его имени пользователя(username).

    HTTP коды ответа:
    - 200 OK: Успешный запрос
    - 404 Not Found: Пользователь не найден
    """
    def get(self, request, username: str):
        user: Optional[User] = get_checker(username)

        if user:
            serializer = CheckerDetailSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

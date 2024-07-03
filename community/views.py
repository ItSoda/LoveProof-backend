from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from community.serializers import (
    PostSerializer, PostDetailSerializer,
    CommentSerializer, ReportSerializer,
    ReportDetailSerializer, PostReportCreateSerializer,
    ReportCreateCommentSerializer
)
from community.permissions import IsOwnerOrReadOnly, IsModeratorOrAdmin
from community.services.views_service import (
    get_list_post, get_post,
    get_list_comments, get_comment,
    get_or_create_comment_like, get_or_create_post_like,
    get_list_reports, get_report
)
from community.pagination import PostPagination
from community.filters import PostFilter, get_filtered_queryset


class PostListCreateAPIView(APIView):
    """
    API view для выдачи списка постов и создания новых.

    Пользователь должен быть аутентифицирован для доступа к данным постов.

    Параметры запроса:  
    {   
        "header": "Заголовок поста",
        "text": "Текст поста",
        "category": "id категории (необязательно)"
    } 

    HTTP коды ответа:
    - GET:
        - 200 OK: Возвращает список всех постов.
        - 400 Bad Request: Ошибка в запросе или неверные данные.
    - POST:
        - 201 Created: Пост успешно создан.
        - 400 Bad Request: Ошибка в запросе или неверные данные для создания поста.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = PostPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter

    def get(self, request):
        queryset = get_list_post()

        filtered_queryset = get_filtered_queryset(queryset, request.query_params, self.filterset_class)
        if filtered_queryset is None:
            return Response(status=status.HTTP_204_NO_CONTENT)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(filtered_queryset, request)
        if page is not None:
            serializer = PostSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = PostSerializer(filtered_queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailAPIView(APIView):
    """
    API view для детального просмотра, обновления и удаления поста.

    Пользователь должен быть аутентифицирован и иметь права доступа для изменения данных поста.

    Параметры запроса:
    - PUT
        {
            "header": "Новый заголовок",
            "text": "Новый текст",
            "category": "Новая категория (необязательно)"
        }  # Можно изменить 1 поле на выбор

    HTTP коды ответа:
    - GET:
        - 200 OK: Возвращает данные конкретного поста.
        - 404 Not Found: Пост не найден.
    - PUT:
        - 200 OK: Данные поста успешно обновлены.
        - 400 Bad Request: Ошибка в запросе или неверные данные для обновления поста.
        - 403 Forbidden: Пользователь не имеет прав доступа к изменению данных поста.
    - DELETE:
        - 204 No Content: Пост успешно удален.
        - 403 Forbidden: Пользователь не имеет прав доступа к удалению поста.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly, IsModeratorOrAdmin]

    def get(self, request, pk):
        post = get_post(pk)
        serializer = PostDetailSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk):
        post = get_post(pk)
        self.check_object_permissions(request, post)
        serializer = PostDetailSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = get_post(pk)
        self.check_object_permissions(request, post)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListCreateAPIView(APIView):
    """
    API view для списка комментариев под конкретным постом и создания новых комментариев.

    Пользователь должен быть аутентифицирован для доступа к данным комментариев.

    Параметры запроса:
    {
        "text": "Текст комментария"
    }

    HTTP коды ответа:
    - GET:
        - 200 OK: Возвращает список всех комментариев под конкретным постом.
        - 400 Bad Request: Ошибка в запросе или неверные данные.
    - POST:
        - 201 Created: Комментарий успешно создан.
        - 400 Bad Request: Ошибка в запросе или неверные данные для создания комментария.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, post_pk):
        """
        Возвращает список всех комментариев под конкретным постом.
        """
        comments = get_list_comments(post_pk)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, post_pk):
        """
        Создает новый комментарий под конкретным постом.
        """
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post_id=post_pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    """
    API view для детального просмотра, обновления и удаления комментария.

    Пользователь должен быть аутентифицирован и иметь права доступа для изменения данных комментария.

    Параметры запроса:
    - PUT
        {
            "text": "Новый текст комментария"
        }

    HTTP коды ответа:
    - GET:
        - 200 OK: Возвращает данные конкретного комментария.
        - 404 Not Found: Комментарий не найден.
    - PUT:
        - 200 OK: Данные комментария успешно обновлены.
        - 400 Bad Request: Ошибка в запросе или неверные данные для обновления комментария.
        - 403 Forbidden: Пользователь не имеет прав доступа к изменению данных комментария.
    - DELETE:
        - 204 No Content: Комментарий успешно удален.
        - 403 Forbidden: Пользователь не имеет прав доступа к удалению комментария.
        - 404 Not Found: Комментарий не найден.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly, IsModeratorOrAdmin]

    def get(self, request, pk):
        comment = get_comment(pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, pk):
        comment = get_comment(pk)
        self.check_object_permissions(request, comment)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        comment = get_comment(pk)
        self.check_object_permissions(request, comment)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikePostAPIView(APIView):
    """
    API view для управления лайками к постам.

    Пользователь должен быть аутентифицирован для ставки или удаления лайка к посту.

    HTTP коды ответа:
    - 200 OK: Лайк успешно поставлен или удален.
    - 403 Forbidden: Пользователь не имеет прав доступа.
    - 404 Not Found: Пост не найден.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, post_pk):
        """
        Устанавливает лайк или удаляет его с указанного поста.
        """
        post = get_post(post_pk)
        user = request.user
        like, created = get_or_create_post_like(user, post)
        if not created:
            like.delete()

        serializer = PostDetailSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikeCommentAPIView(APIView):
    """
    API view для управления лайками к комментариям.

    Пользователь должен быть аутентифицирован для ставки или удаления лайка к комментарию.

    HTTP коды ответа:
    - 200 OK: Лайк успешно поставлен или удален.
    - 403 Forbidden: Пользователь не имеет прав доступа.
    - 404 Not Found: Комментарий не найден.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_pk):
        """
        Устанавливает лайк или удаляет его с указанного комментария.
        """
        comment = get_comment(comment_pk)
        user = request.user
        like, created = get_or_create_comment_like(user, comment)
        if not created:
            like.delete()

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReportListAPIView(APIView):
    """
    API view для получения списка жалоб.

    Пользователь должен быть аутентифицирован как модератор или администратор.

    HTTP коды ответа:
        - 200 OK: Возвращает список всех жалоб.
    """
    permission_classes = [IsAuthenticated, IsModeratorOrAdmin]

    def get(self, request):
        reports = get_list_reports()
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReportDetailAPIView(APIView):
    """
    API view для детального просмотра и обновления жалобы.

    Пользователь должен быть аутентифицирован как модератор или администратор.

    HTTP коды ответа:
    - GET:
        - 200 OK: Возвращает данные конкретной жалобы.
        - 404 Not Found: Жалоба не найдена.
    - PUT:
        - 200 OK: Данные жалобы успешно обновлены.
        - 400 Bad Request: Ошибка в запросе или неверные данные для обновления жалобы.
    """
    permission_classes = [IsAuthenticated, IsModeratorOrAdmin]

    def get(self, request, pk):
        report = get_report(pk)
        serializer = ReportDetailSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        report = get_report(pk)
        serializer = ReportDetailSerializer(report, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

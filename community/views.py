from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from community.serializers import PostSerializer, PostDetailSerializer
from community.permissions import IsOwnerOrReadOnly, IsModeratorOrAdmin
from community.services.views_service import (
    get_list_post, get_post,
)
from community.pagination import PostPagination


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

    def get(self, request):
        posts = get_list_post()

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(posts, request)
        if page is not None:
            serializer = PostSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = PostSerializer(posts, many=True)
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

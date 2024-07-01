from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from community.serializers import PostSerializer
from community.services.views_service import (
    get_list_post
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

from typing import Optional

from django.db.models import Count, QuerySet
from django.shortcuts import get_object_or_404

from community.models import Post, Comment, Like
from users.models import User


def get_list_post() -> QuerySet[Post]:
    """
    Возвращает список всех постов с аннотированными данными о количестве комментариев и лайков под каждым постом.

    Возвращает:
        QuerySet: QuerySet объектов Post, с аннотациями comments_count и likes_count, и связанными данными user и category.
    """
    return Post.objects.annotate(
        comments_count=Count('comments'),
        likes_count=Count('likes')
    ).select_related(
        'user',
        'category'
    ).only(
        'user__id',
        'user__username',
        'category__id',
        'category__title',
        'id',
        'header',
        'text',
        'created_at'
    )

def get_post(pk: int) -> Optional[Post]:
    """
    Возвращает конкретный пост по его id.

    Параметры:
        pk (int): id поста.

    Возвращает:
        Post: Объект Post, если найден.
        None: Если пост не найден.
    """
    return get_object_or_404(
        Post.objects.annotate(
            comments_count=Count('comments'),
            likes_count=Count('likes')
        ).select_related(
            'user',
            'category'
        ).prefetch_related(
            'comments'
        ).only(
            'user__id',
            'user__username',
            'category__id',
            'category__title',
            'header',
            'text',
            'created_at'
        ),
        pk=pk
    )

def get_list_comments(post_pk: int) -> QuerySet[Comment]:
    """
    Возвращает список всех комментариев под конкретным постом.

    Параметры:
        post_pk (int): id поста, для которого нужно получить комментарии.

    Возвращает:
        QuerySet: QuerySet объектов Comment, связанных с заданным постом, с данными о пользователе.
    """
    return Comment.objects.filter(
        post_id=post_pk
        ).select_related(
            'user'
        ).only(
            'user__id',
            'user__username',
            'id',
            'text',
            'created_at'
        )

def get_comment(pk: int) -> Optional[Comment]:
    """
    Возвращает конкретный комментарий по его id.

    Параметры:
        pk (int): id комментария.

    Возвращает:
        Comment: Объект Comment, если найден.
        None: Если комментарий не найден.
    """
    return get_object_or_404(
        Comment.objects.select_related(
            'user'
        ).only(
            'user__id',
            'user__username',
            'id',
            'text',
        ),
        pk=pk
    )

def get_or_create_comment_like(user: User, comment: Comment) -> Like:
    """
    Получает или создает лайк для комментария от заданного пользователя.

    Параметры:
        user (User): Пользователь, который ставит лайк.
        comment (Comment): Комментарий, к которому ставится лайк.

    Возвращает:
        Like: Объект Like, созданный или найденный.
    """
    return Like.objects.get_or_create(user=user, comment=comment)

def get_or_create_post_like(user: User, post: Post) -> Like:
    """
    Получает или создает лайк для поста от заданного пользователя.

    Параметры:
        user (User): Пользователь, который ставит лайк.
        post (Post): Пост, к которому ставится лайк.

    Возвращает:
        Like: Объект Like, созданный или найденный.
    """
    return Like.objects.get_or_create(user=user, post=post)

from typing import Optional

from django.db.models import QuerySet, Prefetch

from users.models import User, Tag


def get_list_checkers() -> QuerySet:
    """
    Получает список проверяющих (пользователей с ролью 'checker')

    Returns:
        QuerySet: QuerySet объектов User, отфильтрованных по роли 'checker', с полями id, username, photo, age и price.
    """
    return User.objects.filter(role='checker').only(
        'id',
        'username', 
        'photo',
        'age',
        'price'
    )

def get_checker(username: str) -> Optional[User]:
    """
    Получает конкретного проверяющего (пользователя с ролью 'checker') по имени пользователя.

    Аргументы:
        username (str): Имя пользователя проверяющего, которого нужно получить.

    Возвращает:
        Optional[User]: Если пользователь с заданным именем пользователя и ролью 'checker' найден,
        возвращает объект User. Если пользователь не найден, возвращает None.
    """
    try:
        user = User.objects.prefetch_related(
            Prefetch('tags', queryset=Tag.objects.all())
        ).only(
            'id',
            'username',
            'gender',
            'description',
            'photo',
            'tags',
            'price'
        ).get(
            username=username,
            role='checker'
        )
        return user
    except User.DoesNotExist:
        return None

from typing import Optional

from django.db.models.query import QuerySet
from django.http import QueryDict
import django_filters

from community.models import Post


class PostFilter(django_filters.FilterSet):
    """
    Фильтры для модели Post.

    Позволяет фильтровать объекты Post по категории.

    Поля фильтрации:
    - category: фильтр по названию категории.
    """
    category = django_filters.CharFilter(field_name='category__title')

    class Meta:
        model = Post
        fields = ('category',)


def get_filtered_queryset(queryset: QuerySet, query_params: QueryDict, filterset_class: django_filters.FilterSet) -> Optional[QuerySet]:
    """
    Функция для фильтрации queryset на основе переданных параметров.

    Параметры:
        queryset (QuerySet): Исходный QuerySet, который требуется отфильтровать.
        query_params (QueryDict): Параметры запроса, используемые для фильтрации.
        filterset_class (FilterSet): Класс фильтра Django, который определяет, какие параметры использовать.

    Возвращает:
        Optional[QuerySet]: Отфильтрованный QuerySet. Если фильтрация не привела к результатам, возвращается None.
    """
    print(query_params)
    if any(query_params.values()):  # Проверка фильтрации в запросе
        filterset = filterset_class(query_params, queryset=queryset)
        filtered_queryset = filterset.qs
        if not filtered_queryset.exists():
            return None  # Возвращается None, если результат фильтрации пуст
    else:
        filtered_queryset = queryset  # Если нет фильтров, используется исходный queryset

    return filtered_queryset

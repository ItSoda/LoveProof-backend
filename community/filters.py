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

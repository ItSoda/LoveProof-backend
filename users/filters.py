from django_filters import (
    BaseInFilter, Filter, FilterSet,
    RangeFilter,
)

from users.models import User


class BaseInFilter(BaseInFilter, Filter):
    def filter(self, qs, value):
        """
        Фильтрует QuerySet `qs` на основе значения `value`, разделенного запятыми.

        Аргументы:
        - qs: QuerySet, который требуется отфильтровать
        - value: Значение для фильтрации; может быть строкой с разделенными запятыми значениями или списком строк

        Возвращает:
        - Отфильтрованный QuerySet `qs`.

        Если `value` не задано или пусто, возвращает исходный QuerySet без фильтрации.
        """
        if value:
            # Если значение является строкой, разбиваем её по запятым,
            # преобразуем каждое значение в нижний регистр и удаляем лишние пробелы
            if isinstance(value, str):
                values = [v.lower().strip() for v in value.split(',') if v.strip()]
            else:
                # Если значение не строка, предполагаем, что это список строк и
                # преобразуем каждое значение так же в нижний регистр
                values = [v.lower() for v in value if isinstance(v, str)]
            return super().filter(qs, values)
        else:
            # Если значение пусто или None, возвращаем исходный QuerySet без фильтрации
            return qs


class CheckerFilter(FilterSet):
    """
    Фильтр для модели User

    Поля:
    - genders: Фильтр по полу пользователя
    - ethnicities: Фильтр по этнической принадлежности пользователя
    - locations: Фильтр по местоположению пользователя
    - socials: Фильтр по социальным сетям пользователя
    - ages: Фильтр по возрасту пользователя в заданном диапазоне
    """
    genders = BaseInFilter(field_name='gender', lookup_expr='in')
    ethnicities = BaseInFilter(field_name='ethnicity__title', lookup_expr='in')
    locations = BaseInFilter(field_name='location__title', lookup_expr='in')
    socials = BaseInFilter(field_name='social_media__title', lookup_expr='in')
    ages = RangeFilter(field_name='age')

    class Meta:
        model = User
        fields = ('genders', 'ethnicities', 'locations', 'socials', 'ages')

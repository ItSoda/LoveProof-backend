from rest_framework.pagination import PageNumberPagination


class CheckerPagination(PageNumberPagination):
    page_size = 40
    page_size_query_param = 'page_size'
    max_page_size = 500

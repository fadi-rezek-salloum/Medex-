from rest_framework import pagination


class TransactionsPagination(pagination.PageNumberPagination):
    page_size = 10
    max_page_size = 20
    page_query_param = "p"
    page_size_query_param = "l"

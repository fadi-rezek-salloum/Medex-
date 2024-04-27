from rest_framework import pagination


class OrderItemPagination(pagination.PageNumberPagination):
    page_size = 10
    max_page_size = 20
    page_query_param = "p"
    page_size_query_param = "l"


class ReturnRequestPagination(pagination.PageNumberPagination):
    page_size = 10
    max_page_size = 20
    page_query_param = "p"
    page_size_query_param = "l"

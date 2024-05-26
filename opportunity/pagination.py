from rest_framework.pagination import CursorPagination


class OpportunityPagination(CursorPagination):
    page_size = 25
    cursor_query_param = "p"
    ordering = "-created"

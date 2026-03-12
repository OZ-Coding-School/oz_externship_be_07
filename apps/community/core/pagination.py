from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPaginationComment(PageNumberPagination):
    page_size = 10
    page_query_parma = "page"
    page_size_query_param = "size"
    max_page_size = 100

    def get_paginated_response(self, data: Any) -> Response:
        if self.page is None:
            raise ValueError("error")

        return Response(
            {
                "total_count": self.page.paginator.count,
                "size": self.page_size,
                "page": self.page.number,
                "results": data,
            }
        )

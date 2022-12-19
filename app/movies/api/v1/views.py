from movies.models import Filmwork
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAuthenticated)
from rest_framework.response import Response

from .serializers import FilmworkSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'next': self.page.next_page_number() if self.page.has_next() else None,
            'prev': self.page.previous_page_number() if self.page.has_previous() else None,
            'results': data,
        })


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class FilmworkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows filmworks to be viewed.
    """
    queryset = Filmwork.objects.prefetch_related(
        'genres',
        'personfilmwork_set__person'
    )
    serializer_class = FilmworkSerializer
    permission_classes = [IsAuthenticated | ReadOnly]
    pagination_class = StandardResultsSetPagination

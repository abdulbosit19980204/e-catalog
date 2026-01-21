"""
Optional Pagination for Backward Compatibility

This pagination class only activates when 'limit' or 'offset' parameters are provided.
Without these parameters, it returns the full queryset (backward compatible).

Usage:
    /api/v1/nomenklatura/              → Full dataset (7000 items)
    /api/v1/nomenklatura/?limit=50     → First 50 items
    /api/v1/nomenklatura/?limit=50&offset=50  → Items 51-100
"""
from rest_framework.pagination import LimitOffsetPagination


class OptionalLimitOffsetPagination(LimitOffsetPagination):
    """
    Standard LimitOffsetPagination with safety limits.
    
    - Default limit: 20 items
    - Max limit: 100 items
    - Prevents SQLite 'too many SQL variables' crashes on large datasets.
    """
    default_limit = 20
    max_limit = 100
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    
    def paginate_queryset(self, queryset, request, view=None):
        """Always paginate to prevent resource exhaustion"""
        return super().paginate_queryset(queryset, request, view)

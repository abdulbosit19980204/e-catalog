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
    Opt-in pagination that preserves backward compatibility
    
    - Only paginates when ?limit= or ?offset= is in query params
    - Returns full queryset otherwise
    - Max limit: 100 items
    """
    default_limit = None  # No default - returns full dataset
    max_limit = 100
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    
    def paginate_queryset(self, queryset, request, view=None):
        """
        Only paginate if 'limit' or 'offset' in query params
        Otherwise return None to skip pagination
        """
        # Check if pagination is requested
        if self.limit_query_param not in request.query_params and \
           self.offset_query_param not in request.query_params:
            return None  # No pagination - return full queryset
        
        # Pagination requested - use parent logic
        return super().paginate_queryset(queryset, request, view)

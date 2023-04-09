from rest_framework import filters


class GetFilterParamMixin:
    def get_filter_param(self, request, param_code):
        if request and param_code:
            return request.query_params.get(param_code)


class GenericFilter(filters.BaseFilterBackend, GetFilterParamMixin):
    """
    Общий набор механики для фильтров.
    """

    def filter_queryset(self, request, queryset, view):
        raise Exception('Must be overwritten.')
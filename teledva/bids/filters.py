from django.db.models import Q

from utils.filters import GenericFilter


class BidsFilter(GenericFilter):
    """
    Фильтровать по
    - статусe
    - последнему актуальному
    - по году
    """

    def get_schema_operation_parameters(self, view):
        return ['status',]

    def filter_queryset(self, request, queryset, view):
        filters = Q()

        if self.get_filter_param(request, 'status'):
            term = self.get_filter_param(request, 'status')
            filters &= Q(status=term)
        return queryset.filter(filters)
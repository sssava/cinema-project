from rest_framework.filters import BaseFilterBackend
from datetime import datetime, time


class CustomSessionSortingFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_fields = {
            "time_start": "time_start__gte",
            "hall": "hall",
        }

        for param, field in filter_fields.items():
            value = request.query_params.get(param)
            if value:
                if param == "time_start":
                    value = datetime.strptime(value, '%H:%M').time()
                queryset = queryset.filter(**{field: value})

        return queryset

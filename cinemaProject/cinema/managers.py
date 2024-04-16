from django.db import models
from django.db.models import Q


class SessionManager(models.Manager):
    def exists_session_by_time(self, time, session_date, hall, session_pk=None):
        queryset = self.model.objects.filter(
            Q(time_start__lte=time) & Q(time_end__gte=time),
            hall=hall,
            session_date=session_date
        )
        if session_pk is not None:
            queryset = queryset.exclude(pk=session_pk)
        print(queryset.exists())
        return queryset.exists()

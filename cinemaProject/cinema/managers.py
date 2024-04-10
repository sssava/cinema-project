from django.db import models
from django.db.models import Q


class SessionManager(models.Manager):
    def exists_session_by_time(self, time, session_date, hall):
        return self.model.objects.filter(
            Q(time_start__lte=time) & Q(time_end__gte=time),
            hall=hall,
            session_date=session_date
        ).exists()

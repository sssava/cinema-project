from django.shortcuts import render
from django.views.generic import ListView
from .models import Session
from datetime import date


class SessionList(ListView):
    model = Session
    context_object_name = "sessions"
    template_name = "cinema/sessions.html"
    paginate_by = 8

    def get_queryset(self):
        return Session.objects.filter(session_date=date.today()).select_related("hall", "movie")



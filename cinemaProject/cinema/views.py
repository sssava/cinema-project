from datetime import datetime

from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView
from .models import Session, MovieHall
from datetime import date, time
from .forms import MovieHallCreationForm, SessionCreationForm
from core.custom_mixins import StaffRequiredMixin
from django.utils import timezone


class SessionListToday(ListView):
    model = Session
    context_object_name = "sessions"
    template_name = "cinema/sessions.html"
    paginate_by = 8

    def get_queryset(self):
        return Session.objects.filter(
            session_date=date.today(),
            time_start__gte=datetime.now().time()
        ).select_related("hall", "movie")


class SessionListTomorrow(ListView):
    model = Session
    context_object_name = "sessions"
    template_name = "cinema/sessions.html"
    paginate_by = 8

    def get_queryset(self):
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        return Session.objects.filter(session_date=tomorrow).select_related("hall", "movie")


class MovieHallCreationView(StaffRequiredMixin, CreateView):
    model = MovieHall
    form_class = MovieHallCreationForm
    template_name = "cinema/create-movie-hall.html"
    success_url = '/'

    def form_valid(self, form):
        messages.success(self.request, "MovieHall has successfully created")
        return super().form_valid(form)

    def form_invalid(self, form):
        errors = form.errors.as_text()
        messages.error(self.request, errors)
        return redirect('/')


class SessionCreationView(CreateView):
    model = Session
    form_class = SessionCreationForm
    template_name = "cinema/create-session.html"
    success_url = "/"

    def form_valid(self, form):
        messages.success(self.request, "Session has successfully created")
        return super().form_valid(form)

    def form_invalid(self, form):
        errors = form.errors.as_text()
        messages.error(self.request, errors)
        return redirect('/')




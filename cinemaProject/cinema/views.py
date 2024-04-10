from datetime import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, DetailView
from .models import Session, MovieHall
from datetime import date, timedelta
from .forms import MovieHallCreationForm, SessionCreationForm
from core.custom_mixins import StaffRequiredMixin
from .utils import create_order, is_buying


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
        tomorrow = date.today() + timedelta(days=1)
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


class SessionCreationView(StaffRequiredMixin, CreateView):
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


class SessionDetail(LoginRequiredMixin, DetailView):
    model = Session
    template_name = "cinema/session-detail.html"
    context_object_name = "session"
    pk_url_kwarg = "session_id"
    login_url = "/login/"

    def post(self, request, *args, **kwargs):
        session_id = self.kwargs.get('session_id')
        session = Session.objects.get(pk=session_id)
        selected_seats = request.POST.getlist('selected_seats')

        if is_buying(self.request, selected_seats, session):
            create_order(self.request, selected_seats, session)
        else:
            messages.error(request, "You have not enough money")

        return redirect('session-detail', session_id=session_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["session_seats"] = self.object.session_seats.filter(is_booked=False)
        return context








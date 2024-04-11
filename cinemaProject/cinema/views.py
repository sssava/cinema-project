from datetime import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from .models import Session, MovieHall
from datetime import date, timedelta
from .forms import MovieHallCreationForm, SessionCreationForm, MovieHallUpdateForm
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
        response = super().form_valid(form)
        messages.success(self.request, "MovieHall has successfully created")
        instance = self.object
        hall = MovieHall.objects.get(pk=instance.pk)
        hall.create_seats_for_hall()
        return response

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
        response = super().form_valid(form)
        messages.success(self.request, "Session has successfully created")
        instance = self.object
        session = Session.objects.get(pk=instance.pk)
        session.create_session_seats()
        return response

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


class MovieHallUpdateView(StaffRequiredMixin, UpdateView):
    form_class = MovieHallUpdateForm
    model = MovieHall
    template_name = "cinema/update-hall.html"
    success_url = "/"

    def form_valid(self, form):
        form_instance = form.save(commit=False)
        form_instance.delete_session_seats()
        response = super().form_valid(form)
        instance = self.object
        hall = MovieHall.objects.get(pk=instance.pk)
        hall.update_seats_for_hall()
        messages.success(self.request, "Hall has successfully updated")
        return response

    def form_invalid(self, form):
        errors = form.errors.as_text()
        messages.error(self.request, errors)
        return redirect('/')

    def dispatch(self, request, *args, **kwargs):
        hall_instance = self.get_object()
        if not hall_instance.is_updateble():
            messages.error(request, "This hall can`t be updated, because it has booked sessions")
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)


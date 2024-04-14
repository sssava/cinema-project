from datetime import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from .models import Session, MovieHall, Order, SessionSeat
from datetime import date, timedelta
from .forms import MovieHallCreationForm, SessionCreationForm, MovieHallUpdateForm, SessionUpdateForm
from core.custom_mixins import StaffRequiredMixin
from .utils import create_order, is_buying, sort_by_price_or_time_start


class SessionListToday(ListView):
    model = Session
    context_object_name = "sessions"
    template_name = "cinema/sessions.html"
    paginate_by = 8

    def get_queryset(self):
        sessions = Session.objects.filter(
            session_date=date.today(),
            time_start__gte=datetime.now().time()
        ).select_related("hall", "movie")

        return sort_by_price_or_time_start(self.request, sessions)


class SessionListTomorrow(ListView):
    model = Session
    context_object_name = "sessions"
    template_name = "cinema/sessions.html"
    paginate_by = 8

    def get_queryset(self):
        tomorrow = date.today() + timedelta(days=1)
        sessions = Session.objects.filter(session_date=tomorrow).select_related("hall", "movie")
        return sort_by_price_or_time_start(self.request, sessions)


class MovieHallCreationView(StaffRequiredMixin, CreateView):
    model = MovieHall
    form_class = MovieHallCreationForm
    template_name = "cinema/create-movie-hall.html"
    success_url = '/'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "MovieHall has successfully created")
        hall = self.object
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
        session = self.object
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

    def get(self, request, *args, **kwargs):
        session = self.get_object()
        if not session.session_seats.filter(is_booked=False).exists():
            messages.error(request, "Seats on that session are sold")
            return redirect("index")
        return super().get(request, *args, **kwargs)

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
        form_instance.delete_seats_and_session_seats()
        response = super().form_valid(form)
        hall = self.object
        hall.update_seats_for_hall()
        messages.success(self.request, "Hall has successfully updated")
        return response

    def form_invalid(self, form):
        errors = form.errors.as_text()
        messages.error(self.request, errors)
        return redirect('/')

    def dispatch(self, request, *args, **kwargs):
        hall_instance = self.get_object()
        if not hall_instance.is_updateble_hall():
            messages.error(request, "This hall can`t be updated, because it has booked sessions")
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        hall_instance = self.get_object()
        if not hall_instance.is_updateble_hall():
            messages.error(request, "This hall can`t be updated, because it has booked sessions")
            return redirect("index")
        return super().post(request, *args, **kwargs)


class SessionUpdateView(StaffRequiredMixin, UpdateView):
    model = Session
    form_class = SessionUpdateForm
    template_name = "cinema/update-session.html"
    success_url = "/"

    def form_valid(self, form):
        form_instance = form.save(commit=False)
        form_instance.delete_session_seats()
        response = super().form_valid(form)
        session = self.object
        session.create_session_seats()
        messages.success(self.request, "Session has successfully updated")
        return response

    def form_invalid(self, form):
        errors = form.errors.as_text()
        messages.error(self.request, errors)
        return redirect('/')

    def dispatch(self, request, *args, **kwargs):
        session_instance = self.get_object()
        if not session_instance.is_updateble_session():
            messages.error(request, "This session can`t be updated, because it has booked seats")
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        session_instance = self.get_object()
        if not session_instance.is_updateble_session():
            messages.error(request, "This session can`t be updated, because it has booked seats")
            return redirect("index")
        return super().post(request, *args, **kwargs)


class UserOrdersView(LoginRequiredMixin, ListView):
    model = SessionSeat
    context_object_name = "session_seats"
    template_name = "cinema/orders.html"
    login_url = "login"
    paginate_by = 8

    def get_queryset(self):
        return SessionSeat.objects.select_related("order", "session__movie", "seat").filter(order__user=self.request.user)

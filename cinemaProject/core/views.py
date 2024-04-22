from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from core.forms import CustomAuthenticationForm, CustomUserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView


class Login(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "core/login.html"
    success_url = "/"


class Register(SuccessMessageMixin, CreateView):
    form_class = CustomUserCreationForm
    template_name = "core/register.html"
    success_url = reverse_lazy('login')
    success_message = "Your account have successfully created, now u need to login"


class Logout(LoginRequiredMixin, LogoutView):
    next_page = '/'
    login_url = 'login/'


class NoPermission(TemplateView):
    template_name = "core/no-permission.html"

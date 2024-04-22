from django.urls import path
from core.views import Login, Register, Logout, NoPermission

urlpatterns = [
    path('login/', Login.as_view(), name="login"),
    path('register/', Register.as_view(), name="register"),
    path('logout/', Logout.as_view(), name="logout"),
    path('no-permission/', NoPermission.as_view(), name="no-permission"),
]

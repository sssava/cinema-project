from django.urls import path
from core import views

urlpatterns = [
    path('login/', views.Login.as_view(), name="login"),
    path('register/', views.Register.as_view(), name="register"),
    path('logout/', views.Logout.as_view(), name="logout"),
    path('no-permission/', views.NoPermission.as_view(), name="no-permission"),
]

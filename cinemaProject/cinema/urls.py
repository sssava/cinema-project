from django.urls import path
from cinema.views import SessionList

urlpatterns = [
    path('', SessionList.as_view(), name='index'),
]

from django.urls import path
from cinema.views import index

urlpatterns = [
    path('', index, name='index')
]

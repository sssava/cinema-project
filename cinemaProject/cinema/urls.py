from django.urls import path
from cinema.views import SessionList, MovieHallCreationView

urlpatterns = [
    path('', SessionList.as_view(), name='index'),
    path('create-movie-hall/', MovieHallCreationView.as_view(), name='create-movie-hall'),
]

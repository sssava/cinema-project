from django.urls import path
from cinema.views import SessionListToday, SessionListTomorrow, MovieHallCreationView, SessionCreationView

urlpatterns = [
    path('', SessionListToday.as_view(), name='index'),
    path('tomorrow/', SessionListTomorrow.as_view(), name="tomorrow"),
    path('create-movie-hall/', MovieHallCreationView.as_view(), name='create-movie-hall'),
    path('create-session/', SessionCreationView.as_view(), name="create-session"),
]

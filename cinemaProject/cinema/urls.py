from django.urls import path
from cinema.views import (
    SessionListToday,
    SessionListTomorrow,
    MovieHallCreationView,
    SessionCreationView,
    SessionDetail,
    MovieHallUpdateView,
    SessionUpdateView,
    UserOrdersView
)

urlpatterns = [
    path('', SessionListToday.as_view(), name='index'),
    path('tomorrow/', SessionListTomorrow.as_view(), name="tomorrow"),
    path('create-movie-hall/', MovieHallCreationView.as_view(), name='create-movie-hall'),
    path('create-session/', SessionCreationView.as_view(), name="create-session"),
    path('session/<int:session_id>/', SessionDetail.as_view(), name="session-detail"),
    path('update-hall/<int:pk>/', MovieHallUpdateView.as_view(), name="update-hall"),
    path('update-session/<int:pk>', SessionUpdateView.as_view(), name="update-session"),
    path('orders/', UserOrdersView.as_view(), name="orders"),
]

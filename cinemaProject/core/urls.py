from django.urls import path
from core.views import index

urlpatterns = [
    path('core/', index, name='core')
]

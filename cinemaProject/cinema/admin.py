from django.contrib import admin
from cinema import models


admin.site.register(models.Director)
admin.site.register(models.Actor)
admin.site.register(models.Movie)
admin.site.register(models.Genre)
admin.site.register(models.MovieGenre)
admin.site.register(models.MovieDirector)
admin.site.register(models.MovieActor)
admin.site.register(models.MovieHall)
admin.site.register(models.Seat)
admin.site.register(models.Session)
admin.site.register(models.Order)
admin.site.register(models.SessionSeat)

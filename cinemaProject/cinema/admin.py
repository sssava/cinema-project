from django.contrib import admin
from cinema import models


class MovieGenreInline(admin.TabularInline):
    model = models.MovieGenre
    extra = 1


class MovieActorInline(admin.TabularInline):
    model = models.MovieActor
    extra = 2


class MovieDirectorInline(admin.TabularInline):
    model = models.MovieDirector
    extra = 1


@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    inlines = [MovieGenreInline, MovieActorInline, MovieDirectorInline]


admin.site.register(models.Director)
admin.site.register(models.Actor)
admin.site.register(models.Genre)
admin.site.register(models.MovieGenre)
admin.site.register(models.MovieDirector)
admin.site.register(models.MovieActor)
admin.site.register(models.MovieHall)
admin.site.register(models.Seat)
admin.site.register(models.Session)
admin.site.register(models.Order)
admin.site.register(models.SessionSeat)

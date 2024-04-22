import factory
from factory.fuzzy import FuzzyDate
from datetime import datetime, timedelta, time
import random
from django.contrib.auth import get_user_model
from cinema.models import Actor, Director, Genre, Movie, MovieGenre, MovieActor, MovieDirector, MovieHall, Session
from faker import Faker
from decimal import Decimal

User = get_user_model()
fake = Faker()


class DirectorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Director

    name = factory.Sequence(lambda n: f"Director {n}")
    surname = factory.Sequence(lambda n: f"Director {n}")


class ActorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Actor

    name = factory.Sequence(lambda n: f"Actor {n}")
    surname = factory.Sequence(lambda n: f"Actor {n}")


class GenreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Genre

    name = factory.Sequence(lambda n: f"Genre {n}")


class MovieFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Movie

    name = factory.Sequence(lambda n: f"Movie {n}")
    description = factory.Faker('text')
    image = factory.django.ImageField(width=100, height=100)
    rating = factory.Faker('pyfloat', left_digits=1, right_digits=1, positive=True)

    @factory.post_generation
    def directors(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for director in extracted:
                MovieDirector.objects.create(movie=self, director=director)

    @factory.post_generation
    def actors(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for actor in extracted:
                MovieActor.objects.create(movie=self, actor=actor)

    @factory.post_generation
    def genres(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for genre in extracted:
                MovieGenre.objects.create(movie=self, genre=genre)


class MovieHallFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MovieHall

    name = factory.Sequence(lambda n: f"Hall {n}")
    rows = factory.Faker('random_int', min=5, max=20)
    seats_per_row = factory.Faker('random_int', min=10, max=30)


def random_time():
    current_time = datetime.now()
    hours = current_time.hour
    minutes = current_time.minute
    return time(random.randint(hours, 23), random.randint(minutes, 59))


class SessionTodayFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Session

    movie = factory.SubFactory(MovieFactory)
    time_start = factory.LazyFunction(random_time)
    time_end = factory.LazyFunction(random_time)
    date_start = FuzzyDate(datetime.now().date())
    date_end = FuzzyDate(datetime.now().date() + timedelta(days=1), datetime.now().date() + timedelta(days=1))
    session_date = FuzzyDate(datetime.now().date())
    price = factory.Faker('random_number', digits=2)
    hall = factory.SubFactory(MovieHallFactory)


class SessionTomorrowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Session

    movie = factory.SubFactory(MovieFactory)
    time_start = factory.LazyFunction(random_time)
    time_end = factory.LazyFunction(random_time)
    date_start = FuzzyDate(datetime.now().date())
    date_end = FuzzyDate(datetime.now().date() + timedelta(days=1), datetime.now().date() + timedelta(days=1))
    session_date = FuzzyDate(datetime.now().date() + timedelta(days=1), datetime.now().date() + timedelta(days=1))
    price = factory.Faker('random_number', digits=2)
    hall = factory.SubFactory(MovieHallFactory)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.Faker('password')
    money = factory.Faker('random_int', min=100, max=1000)


class SuperUserFactory(UserFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    is_superuser = True
    is_staff = True

